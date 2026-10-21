"""
Database module for SQLite operations.

This module handles:
- Database initialization and schema creation
- Question bank storage and retrieval
- Exam submission and result storage

Architecture: Three-table design
- questions: Stores reusable question bank
- exams: Tracks exam instances (one per user attempt)
- exam_answers: Stores user responses (many-to-one with exams)
"""

import sqlite3
from contextlib import contextmanager
from typing import List, Dict, Optional
import json
from datetime import datetime


DATABASE_PATH = "exams.db"


@contextmanager
def get_db():
    """
    Context manager for database connections.
    
    Yields a connection object and ensures proper cleanup.
    Enables dict-like row access via row_factory.
    
    Used by: All functions in this module
    
    Example:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM questions")
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Enable dict-like row access
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
    - exam_answers: Stores user answers (id, exam_id, question_id, user_answer)
    
    Side effects:
        - Creates exams.db file if it doesn't exist
        - Populates questions table with 10 sample questions
    
    Safe to call multiple times (uses IF NOT EXISTS).
    Called by: app/main.py on startup
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Question bank table
        # options stored as JSON array to avoid separate options table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_text TEXT NOT NULL,
                options TEXT NOT NULL,
                correct_answer INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Exams table
        # question_ids stored as JSON to preserve order and allow same question multiple times
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_ids TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                score INTEGER
            )
        """)
        
        # Exam answers table
        # Separate table allows querying individual answers and maintains referential integrity
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exam_answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exam_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                user_answer INTEGER,
                FOREIGN KEY (exam_id) REFERENCES exams (id),
                FOREIGN KEY (question_id) REFERENCES questions (id)
            )
        """)
        
        # Check if questions already exist to avoid duplicates
        cursor.execute("SELECT COUNT(*) FROM questions")
        if cursor.fetchone()[0] == 0:
            # Populate with sample questions
            # Mix of difficulty levels and subject areas for testing
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
    
    Note: Uses SQLite RANDOM() for randomization
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, question_text, options, unit, unit_name FROM questions ORDER BY RANDOM() LIMIT ?",
            (count,)
        )
        rows = cursor.fetchall()
        
        questions = []
        for row in rows:
            questions.append({
                "id": row["id"],
                "question_text": row["question_text"],
                "options": json.loads(row["options"]),
                "unit": row["unit"],
                "unit_name": row["unit_name"]
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
        cursor.execute(
            "INSERT INTO exams (question_ids) VALUES (?)",
            (json.dumps(question_ids),)
        )
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
        for question_id, user_answer in answers.items():
            conf_value = confidence.get(question_id) if confidence else None
            cursor.execute(
                "INSERT INTO exam_answers (exam_id, question_id, user_answer, confidence) VALUES (?, ?, ?, ?)",
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
        
        # Get exam metadata
        cursor.execute("SELECT * FROM exams WHERE id = ?", (exam_id,))
        exam_row = cursor.fetchone()
        
        if not exam_row:
            return None
        
        question_ids = json.loads(exam_row["question_ids"])
        
        # Get questions with correct answers
        # Using parameterized query to avoid SQL injection
        placeholders = ",".join("?" * len(question_ids))
        cursor.execute(
            f"SELECT id, question_text, options, correct_answer, unit, unit_name FROM questions WHERE id IN ({placeholders})",
            question_ids
        )
        question_rows = cursor.fetchall()
        
        questions = {}
        for row in question_rows:
            questions[row["id"]] = {
                "question_text": row["question_text"],
                "options": json.loads(row["options"]),
                "correct_answer": row["correct_answer"],
                "unit": row["unit"],
                "unit_name": row["unit_name"]
            }
        
        # Get user answers and confidence
        cursor.execute(
            "SELECT question_id, user_answer, confidence FROM exam_answers WHERE exam_id = ?",
            (exam_id,)
        )
        answer_rows = cursor.fetchall()
        
        user_answers = {}
        user_confidence = {}
        for row in answer_rows:
            user_answers[row["question_id"]] = row["user_answer"]
            user_confidence[row["question_id"]] = row["confidence"]
        
        return {
            "exam_id": exam_id,
            "questions": questions,
            "user_answers": user_answers,
            "user_confidence": user_confidence,
            "score": exam_row["score"],
            "completed_at": exam_row["completed_at"]
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
        cursor.execute(
            "UPDATE exams SET score = ?, completed_at = ? WHERE id = ?",
            (score, datetime.now().isoformat(), exam_id)
        )
