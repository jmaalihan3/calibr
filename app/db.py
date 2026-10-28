"""
Database module for SQLite (local) and PostgreSQL (production) operations.

This module handles:
- Database initialization and schema creation
- Question bank storage and retrieval
- Exam submission and result storage

Architecture: Three-table design
- questions: Stores reusable question bank
- exams: Tracks exam instances (one per user attempt)
- exam_answers: Stores user responses (many-to-one with exams)

Database Selection:
- If DATABASE_URL env var is set → PostgreSQL (production)
- Otherwise → SQLite (local development)
"""

import sqlite3
import os
from contextlib import contextmanager
from typing import List, Dict, Optional
import json
from datetime import datetime

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")  # Set by Render for PostgreSQL
DATABASE_PATH = "exams.db"  # SQLite file for local development

# Import PostgreSQL driver only if needed
if DATABASE_URL:
    import psycopg2
    import psycopg2.extras
    # Render uses postgres:// but psycopg2 needs postgresql://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)


@contextmanager
def get_db():
    """
    Context manager for database connections.
    
    Handles both SQLite (local) and PostgreSQL (production).
    Yields a connection object and ensures proper cleanup.
    Enables dict-like row access via row_factory.
    
    Used by: All functions in this module
    
    Example:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM questions")
    """
    if DATABASE_URL:
        # PostgreSQL connection
        conn = psycopg2.connect(DATABASE_URL)
        conn.cursor_factory = psycopg2.extras.RealDictCursor
    else:
        # SQLite connection
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
    
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """
    Initialize database schema and populate with sample questions.
    
    Creates three tables:
    - questions: The question bank (id, question_text, options, correct_answer, created_at)
    - exams: Tracks exam instances (id, question_ids, created_at, completed_at, score)
    - exam_answers: Stores user answers (id, exam_id, question_id, user_answer, confidence)
    
    Side effects:
        - Creates tables if they don't exist
        - Populates questions table with 10 sample questions
    
    Safe to call multiple times (uses IF NOT EXISTS).
    Called by: app/main.py on startup
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Determine SQL dialect based on database type
        if DATABASE_URL:
            # PostgreSQL syntax
            id_type = "SERIAL PRIMARY KEY"
            json_type = "JSONB"
            timestamp_type = "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        else:
            # SQLite syntax
            id_type = "INTEGER PRIMARY KEY AUTOINCREMENT"
            json_type = "TEXT"
            timestamp_type = "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        
        # Question bank table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS questions (
                id {id_type},
                question_text TEXT NOT NULL,
                options {json_type} NOT NULL,
                correct_answer INTEGER NOT NULL,
                unit TEXT,
                unit_name TEXT,
                created_at {timestamp_type}
            )
        """)
        
        # Exams table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS exams (
                id {id_type},
                question_ids {json_type} NOT NULL,
                created_at {timestamp_type},
                completed_at TIMESTAMP,
                score INTEGER
            )
        """)
        
        # Exam answers table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS exam_answers (
                id {id_type},
                exam_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                user_answer INTEGER,
                confidence INTEGER,
                FOREIGN KEY (exam_id) REFERENCES exams (id),
                FOREIGN KEY (question_id) REFERENCES questions (id)
            )
        """)
        
        # Check if questions already exist to avoid duplicates
        cursor.execute("SELECT COUNT(*) FROM questions")
        count_result = cursor.fetchone()
        question_count = count_result[0] if DATABASE_URL else count_result[0]
        
        if question_count == 0:
            # Populate with sample questions
            sample_questions = [
                {
                    "question": "What is the capital of France?",
                    "options": ["London", "Berlin", "Paris", "Madrid"],
                    "correct": 2
                },
                {
                    "question": "What is 2 + 2?",
                    "options": ["3", "4", "5", "6"],
                    "correct": 1
                },
                {
                    "question": "Which planet is known as the Red Planet?",
                    "options": ["Venus", "Mars", "Jupiter", "Saturn"],
                    "correct": 1
                },
                {
                    "question": "What is the largest ocean on Earth?",
                    "options": ["Atlantic", "Indian", "Arctic", "Pacific"],
                    "correct": 3
                },
                {
                    "question": "Who wrote 'Romeo and Juliet'?",
                    "options": ["Charles Dickens", "William Shakespeare", "Jane Austen", "Mark Twain"],
                    "correct": 1
                },
                {
                    "question": "What is the chemical symbol for water?",
                    "options": ["H2O", "CO2", "O2", "NaCl"],
                    "correct": 0
                },
                {
                    "question": "How many continents are there?",
                    "options": ["5", "6", "7", "8"],
                    "correct": 2
                },
                {
                    "question": "What is the speed of light in vacuum (approximately)?",
                    "options": ["300,000 km/s", "150,000 km/s", "450,000 km/s", "600,000 km/s"],
                    "correct": 0
                },
                {
                    "question": "Which language is primarily spoken in Brazil?",
                    "options": ["Spanish", "Portuguese", "French", "English"],
                    "correct": 1
                },
                {
                    "question": "What year did World War II end?",
                    "options": ["1943", "1944", "1945", "1946"],
                    "correct": 2
                }
            ]
            
            for q in sample_questions:
                # Handle JSON serialization for both databases
                options_json = json.dumps(q["options"]) if not DATABASE_URL else q["options"]
                
                if DATABASE_URL:
                    # PostgreSQL: Use JSONB type directly
                    cursor.execute(
                        "INSERT INTO questions (question_text, options, correct_answer) VALUES (%s, %s, %s)",
                        (q["question"], json.dumps(q["options"]), q["correct"])
                    )
                else:
                    # SQLite: Store JSON as TEXT
                    cursor.execute(
                        "INSERT INTO questions (question_text, options, correct_answer) VALUES (?, ?, ?)",
                        (q["question"], json.dumps(q["options"]), q["correct"])
                    )


def get_random_questions(count: int = 5) -> List[Dict]:
    """
    Retrieve random questions from the question bank.
    
    Args:
        count: Number of questions to retrieve (default 5)
    
    Returns:
        List of question dictionaries with id, question_text, options, unit info.
        Does NOT include correct_answer (security: revealed only after submission).
    
    Used by: services.py start_exam()
    
    Note: Uses RANDOM() for randomization (works in both SQLite and PostgreSQL)
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Use appropriate parameter placeholder
        placeholder = "%s" if DATABASE_URL else "?"
        
        cursor.execute(
            f"SELECT id, question_text, options, unit, unit_name FROM questions ORDER BY RANDOM() LIMIT {placeholder}",
            (count,)
        )
        rows = cursor.fetchall()
        
        questions = []
        for row in rows:
            # Convert to dict for uniform access
            if DATABASE_URL:
                row_dict = dict(row)
            else:
                # SQLite Row object - convert to dict manually
                row_dict = {key: row[key] for key in row.keys()}
            
            # Parse JSON if needed (PostgreSQL returns dict, SQLite returns string)
            options = row_dict["options"]
            if isinstance(options, str):
                options = json.loads(options)
            
            questions.append({
                "id": row_dict["id"],
                "question_text": row_dict["question_text"],
                "options": options,
                "unit": row_dict.get("unit"),
                "unit_name": row_dict.get("unit_name")
            })
        
        return questions


def create_exam(question_ids: List[int]) -> int:
    """
    Create a new exam instance.
    
    Args:
        question_ids: List of question IDs for this exam
    
    Returns:
        The newly created exam ID
    
    Side effects:
        Inserts row into exams table with current timestamp
    
    Used by: services.py start_exam()
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Use appropriate parameter placeholder
        placeholder = "%s" if DATABASE_URL else "?"
        
        cursor.execute(
            f"INSERT INTO exams (question_ids) VALUES ({placeholder})",
            (json.dumps(question_ids),)
        )
        
        # Get last inserted ID (different for SQLite vs PostgreSQL)
        if DATABASE_URL:
            cursor.execute("SELECT lastval()")
            return cursor.fetchone()[0]
        else:
            return cursor.lastrowid


def save_exam_answers(exam_id: int, answers: Dict[int, int], confidence: Dict[int, int] = None):
    """
    Save user answers and confidence ratings for an exam.
    
    Args:
        exam_id: The exam instance ID
        answers: Dictionary mapping question_id -> user_answer_index
        confidence: Dictionary mapping question_id -> confidence (1=Confident, 0=Not Confident)
    
    Side effects:
        Inserts rows in exam_answers table (one per question)
    
    Used by: services.py submit_exam()
    
    Note: Does not validate answers against questions (handled by services layer)
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Use appropriate parameter placeholder
        placeholder = "%s" if DATABASE_URL else "?"
        placeholders = ", ".join([placeholder] * 4)
        
        for question_id, user_answer in answers.items():
            conf_value = confidence.get(question_id) if confidence else None
            cursor.execute(
                f"INSERT INTO exam_answers (exam_id, question_id, user_answer, confidence) VALUES ({placeholders})",
                (exam_id, question_id, user_answer, conf_value)
            )


def get_exam_with_answers(exam_id: int) -> Optional[Dict]:
    """
    Retrieve exam details including user answers, confidence, and correct answers.
    
    Args:
        exam_id: The exam instance ID
    
    Returns:
        Dictionary containing:
        - exam_id: The exam ID
        - questions: Dict of question_id -> {question_text, options, correct_answer}
        - user_answers: Dict of question_id -> user_answer_index
        - user_confidence: Dict of question_id -> confidence (1=Confident, 0=Not Confident)
        - score: Final score (may be None if not yet submitted)
        - completed_at: Completion timestamp (may be None)
        
        Returns None if exam not found.
    
    Used by: services.py get_exam_results()
    
    Note: Includes correct answers (safe after submission)
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Use appropriate parameter placeholder
        placeholder = "%s" if DATABASE_URL else "?"
        
        # Get exam metadata
        cursor.execute(f"SELECT * FROM exams WHERE id = {placeholder}", (exam_id,))
        exam_row = cursor.fetchone()
        
        if not exam_row:
            return None
        
        # Convert to dict for uniform access
        if DATABASE_URL:
            exam_dict = dict(exam_row)
        else:
            exam_dict = {key: exam_row[key] for key in exam_row.keys()}
        
        # Parse question_ids
        question_ids_json = exam_dict["question_ids"]
        if isinstance(question_ids_json, str):
            question_ids = json.loads(question_ids_json)
        else:
            question_ids = question_ids_json
        
        # Get questions with correct answers
        placeholders = ",".join([placeholder] * len(question_ids))
        cursor.execute(
            f"SELECT id, question_text, options, correct_answer, unit, unit_name FROM questions WHERE id IN ({placeholders})",
            question_ids
        )
        question_rows = cursor.fetchall()
        
        questions = {}
        for row in question_rows:
            # Convert to dict for uniform access
            if DATABASE_URL:
                row_dict = dict(row)
            else:
                row_dict = {key: row[key] for key in row.keys()}
            
            # Parse options if needed
            options = row_dict["options"]
            if isinstance(options, str):
                options = json.loads(options)
            
            questions[row_dict["id"]] = {
                "question_text": row_dict["question_text"],
                "options": options,
                "correct_answer": row_dict["correct_answer"],
                "unit": row_dict.get("unit"),
                "unit_name": row_dict.get("unit_name")
            }
        
        # Get user answers and confidence
        cursor.execute(
            f"SELECT question_id, user_answer, confidence FROM exam_answers WHERE exam_id = {placeholder}",
            (exam_id,)
        )
        answer_rows = cursor.fetchall()
        
        user_answers = {}
        user_confidence = {}
        for row in answer_rows:
            # Convert to dict for uniform access
            if DATABASE_URL:
                row_dict = dict(row)
            else:
                row_dict = {key: row[key] for key in row.keys()}
            user_answers[row_dict["question_id"]] = row_dict["user_answer"]
            user_confidence[row_dict["question_id"]] = row_dict["confidence"]
        
        return {
            "exam_id": exam_id,
            "questions": questions,
            "user_answers": user_answers,
            "user_confidence": user_confidence,
            "score": exam_dict["score"],
            "completed_at": exam_dict["completed_at"]
        }


def update_exam_score(exam_id: int, score: int):
    """
    Update exam with final score and completion time.
    
    Args:
        exam_id: The exam instance ID
        score: Final score (number of correct answers)
    
    Side effects:
        Updates exams table with score and completed_at timestamp
    
    Used by: services.py submit_exam()
    
    Note: Completion time is set to current time, not provided by client
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Use appropriate parameter placeholder
        placeholder = "%s" if DATABASE_URL else "?"
        placeholders = ", ".join([placeholder] * 3)
        
        cursor.execute(
            f"UPDATE exams SET score = {placeholder}, completed_at = {placeholder} WHERE id = {placeholder}",
            (score, datetime.now().isoformat(), exam_id)
        )
