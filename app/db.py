"""
Database module for SQLite (local) and PostgreSQL (production) operations.

This module handles:
- Database initialization and schema creation
- Question bank storage and retrieval
- Exam submission and result storage
- User authentication and session management

Architecture: Five-table design
- questions: Stores reusable question bank
- exams: Tracks exam instances (one per user attempt)
- exam_answers: Stores user responses (many-to-one with exams)
- users: User account information
- sessions: Active user sessions

Database Selection:
- If DATABASE_URL env var is set → PostgreSQL (production)
- Otherwise → SQLite (local development)
"""

import sqlite3
import os
from contextlib import contextmanager
from typing import List, Dict, Optional
import json
from datetime import datetime, timedelta
import uuid

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


def _load_statcal_questions(cursor):
    """
    Load StatCal categorical data questions from structured markdown file.
    Called internally by init_db() when database is empty.
    """
    import os
    
    # Path to questions file
    filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                           'statcal_categorical_data_unit_1_exam_structured.md')
    
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found, skipping StatCal questions")
        return
    
    try:
        # Read and parse markdown file
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Extract JSON from markdown code block
        json_start = content.find('```json\n') + 8
        json_end = content.find('\n```', json_start)
        json_content = content[json_start:json_end]
        data = json.loads(json_content)
        
        unit = data['unit']
        unit_name = data['unit_name']
        questions = data['questions']
        
        placeholder = "%s" if DATABASE_URL else "?"
        
        # Insert questions
        for q in questions:
            # Extract options text only
            options = [choice['text'] for choice in q['choices']]
            
            # Find correct answer index
            correct_answer = None
            explanation = None
            for idx, choice in enumerate(q['choices']):
                if choice['is_correct']:
                    correct_answer = idx
                    explanation = choice['explanation']
                    break
            
            # Serialize JSON fields
            options_json = json.dumps(options) if not DATABASE_URL else options
            choices_json = json.dumps(q['choices'])
            review_json = json.dumps(q.get('review', {}))
            
            cursor.execute(
                f"""
                INSERT INTO questions 
                (question_text, options, correct_answer, unit, unit_name, topic, explanation, choices_json, review_json)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                """,
                (
                    q['question'],
                    options_json,
                    correct_answer,
                    str(unit),
                    unit_name,
                    q.get('topic', ''),
                    explanation,
                    choices_json,
                    review_json
                )
            )
        
        print(f"Loaded {len(questions)} StatCal questions")
    
    except Exception as e:
        print(f"Error loading StatCal questions: {e}")
        # Continue with fallback questions


def init_db():
    """
    Initialize database schema and populate with sample questions.
    
    Creates five tables:
    - questions: The question bank (id, question_text, options, correct_answer, created_at)
    - exams: Tracks exam instances (id, question_ids, created_at, completed_at, score, user_id)
    - exam_answers: Stores user answers (id, exam_id, question_id, user_answer, confidence)
    - users: User accounts (id, email, password_hash, created_at, email_verified)
    - sessions: Active sessions (id, user_id, token_hash, created_at, expires_at, revoked)
    
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
            uuid_type = "UUID PRIMARY KEY DEFAULT gen_random_uuid()"
            json_type = "JSONB"
            timestamp_type = "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            text_type = "TEXT"
        else:
            # SQLite syntax
            id_type = "INTEGER PRIMARY KEY AUTOINCREMENT"
            uuid_type = "TEXT PRIMARY KEY"  # Store UUID as TEXT in SQLite
            json_type = "TEXT"
            timestamp_type = "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            text_type = "TEXT"
        
        # Users table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS users (
                id {uuid_type if not DATABASE_URL else 'UUID PRIMARY KEY DEFAULT gen_random_uuid()'},
                email {text_type} NOT NULL UNIQUE,
                password_hash {text_type} NOT NULL,
                created_at {timestamp_type},
                email_verified BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT TRUE
            )
        """)
        
        # Create case-insensitive email index
        if DATABASE_URL:
            cursor.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email_lower 
                ON users (LOWER(email))
            """)
        else:
            cursor.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email_lower 
                ON users (email COLLATE NOCASE)
            """)
        
        # Sessions table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS sessions (
                id {uuid_type if not DATABASE_URL else 'UUID PRIMARY KEY DEFAULT gen_random_uuid()'},
                user_id {text_type if not DATABASE_URL else 'UUID'} NOT NULL,
                token_hash {text_type} NOT NULL UNIQUE,
                created_at {timestamp_type},
                expires_at TIMESTAMP NOT NULL,
                revoked BOOLEAN DEFAULT FALSE,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Create index on token_hash for fast lookup
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_token_hash 
            ON sessions (token_hash)
        """)
        
        # Create index on user_id for session cleanup
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_user_id 
            ON sessions (user_id)
        """)
        
        # Question bank table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS questions (
                id {id_type},
                question_text TEXT NOT NULL,
                options {json_type} NOT NULL,
                correct_answer INTEGER NOT NULL,
                unit TEXT,
                unit_name TEXT,
                topic TEXT,
                explanation TEXT,
                choices_json TEXT,
                review_json TEXT,
                created_at {timestamp_type}
            )
        """)
        
        # Exams table (with user_id for authenticated users)
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS exams (
                id {id_type},
                question_ids {json_type} NOT NULL,
                created_at {timestamp_type},
                completed_at TIMESTAMP,
                score INTEGER,
                user_id {text_type if not DATABASE_URL else 'UUID'},
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Migration: Add user_id column if it doesn't exist (for existing deployments)
        if DATABASE_URL:
            # PostgreSQL: Check and add column
            cursor.execute("""
                DO $$ 
                BEGIN 
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='exams' AND column_name='user_id'
                    ) THEN
                        ALTER TABLE exams ADD COLUMN user_id UUID;
                    END IF;
                END $$;
            """)
        else:
            # SQLite: Check if column exists
            cursor.execute("PRAGMA table_info(exams)")
            columns = [row[1] if isinstance(row, tuple) else row['name'] for row in cursor.fetchall()]
            if 'user_id' not in columns:
                cursor.execute("ALTER TABLE exams ADD COLUMN user_id TEXT")
        
        # Create index on user_id for exam history queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_exams_user_id 
            ON exams (user_id)
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
        # Always ensure we have at least the basic sample questions
        cursor.execute("SELECT COUNT(*) as count FROM questions")
        count_result = cursor.fetchone()
        
        # Handle different return types for SQLite vs PostgreSQL
        if DATABASE_URL:
            # PostgreSQL with RealDictCursor returns dict
            question_count = count_result['count']
        else:
            # SQLite returns tuple-like Row
            question_count = count_result[0]
        
        # Load StatCal questions if none exist
        if question_count == 0:
            print("Loading StatCal categorical data questions...")
            _load_statcal_questions(cursor)
            print(f"Loaded StatCal questions successfully")
        
        # Fallback: Populate with basic sample questions if still empty
        # This handles migrations where tables exist but questions were never loaded
        cursor.execute("SELECT COUNT(*) as count FROM questions")
        count_result = cursor.fetchone()
        if DATABASE_URL:
            question_count = count_result['count']
        else:
            question_count = count_result[0]
            
        if question_count < 10:
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
            f"SELECT id, question_text, options, unit, unit_name, choices_json, review_json FROM questions ORDER BY RANDOM() LIMIT {placeholder}",
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
            
            # Parse choices_json and review_json
            choices = row_dict.get("choices_json")
            if choices:
                if isinstance(choices, str):
                    choices = json.loads(choices)
            
            review = row_dict.get("review_json")
            if review:
                if isinstance(review, str):
                    review = json.loads(review)
            
            questions.append({
                "id": row_dict["id"],
                "question_text": row_dict["question_text"],
                "options": options,
                "unit": row_dict.get("unit"),
                "unit_name": row_dict.get("unit_name"),
                "choices": choices,  # New: Rich choice data with explanations
                "review": review     # New: Review metadata
            })
        
        return questions


def create_exam(question_ids: List[int], user_id: str = None) -> int:
    """
    Create a new exam instance.
    
    Args:
        question_ids: List of question IDs for this exam
        user_id: Optional user ID to link exam to (None for anonymous)
    
    Returns:
        The newly created exam ID
    
    Side effects:
        Inserts row into exams table with current timestamp and optional user_id
    
    Used by: services.py start_exam()
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Use appropriate parameter placeholder
        placeholder = "%s" if DATABASE_URL else "?"
        
        if user_id:
            cursor.execute(
                f"INSERT INTO exams (question_ids, user_id) VALUES ({placeholder}, {placeholder})",
                (json.dumps(question_ids), user_id)
            )
        else:
            cursor.execute(
                f"INSERT INTO exams (question_ids) VALUES ({placeholder})",
                (json.dumps(question_ids),)
            )
        
        # Get last inserted ID (different for SQLite vs PostgreSQL)
        if DATABASE_URL:
            cursor.execute("SELECT lastval() as id")
            result = cursor.fetchone()
            return result['id']
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
            f"SELECT id, question_text, options, correct_answer, unit, unit_name, choices_json, review_json FROM questions WHERE id IN ({placeholders})",
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
            
            # Parse choices_json and review_json
            choices = row_dict.get("choices_json")
            if choices:
                if isinstance(choices, str):
                    choices = json.loads(choices)
            
            review = row_dict.get("review_json")
            if review:
                if isinstance(review, str):
                    review = json.loads(review)
            
            questions[row_dict["id"]] = {
                "question_text": row_dict["question_text"],
                "options": options,
                "correct_answer": row_dict["correct_answer"],
                "unit": row_dict.get("unit"),
                "unit_name": row_dict.get("unit_name"),
                "choices": choices,  # New: Rich choice data with explanations
                "review": review     # New: Review metadata
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


# ============================================================================
# User Management Functions
# ============================================================================

def create_user(email: str, password_hash: str) -> str:
    """
    Create a new user account.
    
    Args:
        email: User email address (must be unique)
        password_hash: Argon2id password hash
    
    Returns:
        User UUID as string
    
    Raises:
        Exception if email already exists
    
    Used by: auth router register endpoint
    """
    with get_db() as conn:
        cursor = conn.cursor()
        placeholder = "%s" if DATABASE_URL else "?"
        
        # Generate UUID for SQLite (PostgreSQL does it automatically)
        user_id = str(uuid.uuid4()) if not DATABASE_URL else None
        
        try:
            if DATABASE_URL:
                # PostgreSQL: Let database generate UUID
                cursor.execute(
                    f"INSERT INTO users (email, password_hash) VALUES ({placeholder}, {placeholder}) RETURNING id",
                    (email.lower(), password_hash)
                )
                result = cursor.fetchone()
                return str(result['id'])
            else:
                # SQLite: Generate UUID manually
                cursor.execute(
                    f"INSERT INTO users (id, email, password_hash) VALUES ({placeholder}, {placeholder}, {placeholder})",
                    (user_id, email.lower(), password_hash)
                )
                return user_id
        except Exception as e:
            # Check if it's a duplicate email error
            error_msg = str(e).lower()
            if 'unique' in error_msg or 'duplicate' in error_msg:
                raise ValueError("Email already registered")
            raise


def get_user_by_email(email: str) -> Optional[Dict]:
    """
    Retrieve user by email address.
    
    Args:
        email: User email address (case-insensitive)
    
    Returns:
        User dict with id, email, password_hash, created_at, email_verified
        Returns None if user not found
    
    Used by: auth router login endpoint
    """
    with get_db() as conn:
        cursor = conn.cursor()
        placeholder = "%s" if DATABASE_URL else "?"
        
        cursor.execute(
            f"SELECT id, email, password_hash, created_at, email_verified, is_active FROM users WHERE LOWER(email) = LOWER({placeholder})",
            (email,)
        )
        row = cursor.fetchone()
        
        if not row:
            return None
        
        # Convert to dict for uniform access
        if DATABASE_URL:
            return dict(row)
        else:
            return {key: row[key] for key in row.keys()}


def get_user_by_id(user_id: str) -> Optional[Dict]:
    """
    Retrieve user by ID.
    
    Args:
        user_id: User UUID
    
    Returns:
        User dict (without password_hash)
        Returns None if user not found
    
    Used by: session validation
    """
    with get_db() as conn:
        cursor = conn.cursor()
        placeholder = "%s" if DATABASE_URL else "?"
        
        cursor.execute(
            f"SELECT id, email, created_at, email_verified, is_active FROM users WHERE id = {placeholder}",
            (user_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            return None
        
        # Convert to dict for uniform access
        if DATABASE_URL:
            return dict(row)
        else:
            return {key: row[key] for key in row.keys()}


# ============================================================================
# Session Management Functions
# ============================================================================

def create_session(user_id: str, token_hash: str, expires_at: datetime) -> str:
    """
    Create a new user session.
    
    Args:
        user_id: User UUID
        token_hash: SHA-256 hash of session token
        expires_at: Session expiration timestamp
    
    Returns:
        Session UUID as string
    
    Used by: auth router login endpoint
    """
    with get_db() as conn:
        cursor = conn.cursor()
        placeholder = "%s" if DATABASE_URL else "?"
        
        # Generate UUID for SQLite (PostgreSQL does it automatically)
        session_id = str(uuid.uuid4()) if not DATABASE_URL else None
        
        if DATABASE_URL:
            # PostgreSQL: Let database generate UUID
            cursor.execute(
                f"INSERT INTO sessions (user_id, token_hash, expires_at) VALUES ({placeholder}, {placeholder}, {placeholder}) RETURNING id",
                (user_id, token_hash, expires_at.isoformat())
            )
            result = cursor.fetchone()
            return str(result['id'])
        else:
            # SQLite: Generate UUID manually
            cursor.execute(
                f"INSERT INTO sessions (id, user_id, token_hash, expires_at) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})",
                (session_id, user_id, token_hash, expires_at.isoformat())
            )
            return session_id


def get_session_by_token(token: str) -> Optional[Dict]:
    """
    Retrieve session by raw token.
    
    Args:
        token: Raw session token (will be hashed for lookup)
    
    Returns:
        Session dict with id, user_id, created_at, expires_at, revoked
        Returns None if session not found or invalid
    
    Used by: auth dependencies for validation
    """
    from app.auth import hash_token
    
    token_hash = hash_token(token)
    
    with get_db() as conn:
        cursor = conn.cursor()
        placeholder = "%s" if DATABASE_URL else "?"
        
        cursor.execute(
            f"SELECT id, user_id, token_hash, created_at, expires_at, revoked FROM sessions WHERE token_hash = {placeholder}",
            (token_hash,)
        )
        row = cursor.fetchone()
        
        if not row:
            return None
        
        # Convert to dict for uniform access
        if DATABASE_URL:
            return dict(row)
        else:
            return {key: row[key] for key in row.keys()}


def validate_session(token: str) -> Optional[Dict]:
    """
    Validate session token and return user data.
    
    Checks:
    - Session exists
    - Not revoked
    - Not expired
    - User is active
    
    Updates last_activity timestamp if valid.
    
    Args:
        token: Raw session token
    
    Returns:
        User dict if session valid, None otherwise
    
    Used by: get_current_user dependency
    """
    session = get_session_by_token(token)
    
    if not session:
        return None
    
    # Check if revoked
    if session['revoked']:
        return None
    
    # Check if expired
    expires_at = session['expires_at']
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    
    if datetime.now() >= expires_at:
        return None
    
    # Get user data
    user = get_user_by_id(session['user_id'])
    
    if not user or not user.get('is_active', True):
        return None
    
    # Update last activity
    update_session_activity(session['id'])
    
    return user


def update_session_activity(session_id: str):
    """
    Update session last_activity timestamp.
    
    Args:
        session_id: Session UUID
    
    Used by: validate_session
    """
    with get_db() as conn:
        cursor = conn.cursor()
        placeholder = "%s" if DATABASE_URL else "?"
        
        cursor.execute(
            f"UPDATE sessions SET last_activity = {placeholder} WHERE id = {placeholder}",
            (datetime.now().isoformat(), session_id)
        )


def revoke_session(token: str):
    """
    Revoke a session (logout).
    
    Args:
        token: Raw session token
    
    Used by: auth router logout endpoint
    """
    from app.auth import hash_token
    
    token_hash = hash_token(token)
    
    with get_db() as conn:
        cursor = conn.cursor()
        placeholder = "%s" if DATABASE_URL else "?"
        
        cursor.execute(
            f"UPDATE sessions SET revoked = TRUE WHERE token_hash = {placeholder}",
            (token_hash,)
        )


def revoke_all_user_sessions(user_id: str):
    """
    Revoke all sessions for a user.
    
    Args:
        user_id: User UUID
    
    Used by: logout all devices, password change, etc.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        placeholder = "%s" if DATABASE_URL else "?"
        
        cursor.execute(
            f"UPDATE sessions SET revoked = TRUE WHERE user_id = {placeholder}",
            (user_id,)
        )


def cleanup_expired_sessions():
    """
    Remove expired sessions from database.
    
    Should be called periodically (e.g., daily cron job).
    
    Returns:
        Number of sessions deleted
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute(
            "DELETE FROM sessions WHERE expires_at < ?",
            (datetime.now().isoformat(),)
        ) if not DATABASE_URL else cursor.execute(
            "DELETE FROM sessions WHERE expires_at < %s",
            (datetime.now().isoformat(),)
        )
        
        return cursor.rowcount


# ============================================================================
# Exam History Functions
# ============================================================================

def get_user_exams(user_id: str, limit: int = 50, offset: int = 0) -> List[Dict]:
    """
    Retrieve exam history for a user.
    
    Args:
        user_id: User UUID
        limit: Maximum number of exams to return (default 50)
        offset: Number of exams to skip (for pagination)
    
    Returns:
        List of exam dicts with:
        - id: Exam ID
        - created_at: Start timestamp
        - completed_at: Completion timestamp (may be None)
        - score: Final score (may be None if not completed)
        - total_questions: Number of questions in exam
        - percentage: Score percentage (may be None if not completed)
    
    Ordered by created_at DESC (newest first).
    
    Used by: services.py get_user_exam_history()
    """
    with get_db() as conn:
        cursor = conn.cursor()
        placeholder = "%s" if DATABASE_URL else "?"
        
        cursor.execute(f"""
            SELECT 
                id,
                question_ids,
                created_at,
                completed_at,
                score,
                user_id
            FROM exams
            WHERE user_id = {placeholder}
            ORDER BY created_at DESC
            LIMIT {placeholder} OFFSET {placeholder}
        """, (user_id, limit, offset))
        
        rows = cursor.fetchall()
        
        exams = []
        for row in rows:
            # Convert to dict
            if DATABASE_URL:
                row_dict = dict(row)
            else:
                row_dict = {key: row[key] for key in row.keys()}
            
            # Parse question_ids to get count
            question_ids_json = row_dict["question_ids"]
            if isinstance(question_ids_json, str):
                question_ids = json.loads(question_ids_json)
            else:
                question_ids = question_ids_json
            
            total_questions = len(question_ids)
            
            # Calculate percentage if completed
            percentage = None
            if row_dict["score"] is not None and total_questions > 0:
                percentage = round((row_dict["score"] / total_questions) * 100, 2)
            
            exams.append({
                "id": row_dict["id"],
                "created_at": row_dict["created_at"],
                "completed_at": row_dict["completed_at"],
                "score": row_dict["score"],
                "total_questions": total_questions,
                "percentage": percentage
            })
        
        return exams


def get_user_exam_count(user_id: str) -> int:
    """
    Get total number of exams for a user.
    
    Args:
        user_id: User UUID
    
    Returns:
        Total number of exams
    
    Used by: Pagination logic
    """
    with get_db() as conn:
        cursor = conn.cursor()
        placeholder = "%s" if DATABASE_URL else "?"
        
        cursor.execute(
            f"SELECT COUNT(*) as count FROM exams WHERE user_id = {placeholder}",
            (user_id,)
        )
        result = cursor.fetchone()
        
        if DATABASE_URL:
            return result['count']
        else:
            return result[0]


def get_user_exam_trends(user_id: str) -> List[Dict]:
    """
    Get time-series statistics for each completed exam.
    
    Args:
        user_id: User UUID
    
    Returns:
        List of dicts, one per exam, ordered chronologically:
        - exam_id: Exam ID
        - completed_at: Completion timestamp
        - exam_number: Sequential exam number (1, 2, 3...)
        - accuracy: Percentage correct for this exam
        - average_confidence: Average confidence for this exam
        - brier_score: Brier score for this exam
        - bias_score: Calibration bias for this exam
        - total_questions: Number of questions in exam
    
    Used by: Longitudinal tracking charts (Phase 3)
    """
    with get_db() as conn:
        cursor = conn.cursor()
        placeholder = "%s" if DATABASE_URL else "?"
        
        # Get all completed exams with their answers, ordered chronologically
        cursor.execute(f"""
            SELECT 
                e.id as exam_id,
                e.completed_at,
                ea.question_id,
                ea.user_answer,
                ea.confidence,
                q.correct_answer
            FROM exams e
            JOIN exam_answers ea ON e.id = ea.exam_id
            JOIN questions q ON ea.question_id = q.id
            WHERE e.user_id = {placeholder} AND e.completed_at IS NOT NULL
            ORDER BY e.completed_at ASC, e.id ASC
        """, (user_id,))
        
        rows = cursor.fetchall()
        
        if not rows:
            return []
        
        # Group by exam and calculate per-exam statistics
        exams_data = {}
        
        for row in rows:
            if DATABASE_URL:
                row_dict = dict(row)
            else:
                row_dict = {key: row[key] for key in row.keys()}
            
            exam_id = row_dict["exam_id"]
            
            if exam_id not in exams_data:
                exams_data[exam_id] = {
                    "exam_id": exam_id,
                    "completed_at": row_dict["completed_at"],
                    "correct_count": 0,
                    "total_questions": 0,
                    "confidence_sum": 0,
                    "confidence_count": 0,
                    "brier_sum": 0,
                    "brier_count": 0,
                    "bias_sum": 0,
                    "bias_count": 0
                }
            
            exam_data = exams_data[exam_id]
            exam_data["total_questions"] += 1
            
            user_answer = row_dict["user_answer"]
            correct_answer = row_dict["correct_answer"]
            confidence = row_dict["confidence"]
            
            is_correct = (user_answer == correct_answer)
            if is_correct:
                exam_data["correct_count"] += 1
            
            # Calculate metrics if confidence provided
            if confidence is not None:
                confidence_prob = confidence / 100.0
                correctness = 1 if is_correct else 0
                
                exam_data["confidence_sum"] += confidence
                exam_data["confidence_count"] += 1
                exam_data["brier_sum"] += (confidence_prob - correctness) ** 2
                exam_data["brier_count"] += 1
                exam_data["bias_sum"] += (confidence_prob - correctness)
                exam_data["bias_count"] += 1
        
        # Convert to list and calculate final statistics
        trends = []
        exam_number = 1
        
        for exam_id in sorted(exams_data.keys(), key=lambda eid: exams_data[eid]["completed_at"]):
            exam_data = exams_data[exam_id]
            
            accuracy = (exam_data["correct_count"] / exam_data["total_questions"] * 100) if exam_data["total_questions"] > 0 else None
            average_confidence = (exam_data["confidence_sum"] / exam_data["confidence_count"]) if exam_data["confidence_count"] > 0 else None
            brier_score = (exam_data["brier_sum"] / exam_data["brier_count"]) if exam_data["brier_count"] > 0 else None
            bias_score = (exam_data["bias_sum"] / exam_data["bias_count"]) if exam_data["bias_count"] > 0 else None
            
            trends.append({
                "exam_id": exam_id,
                "completed_at": exam_data["completed_at"],
                "exam_number": exam_number,
                "accuracy": round(accuracy, 2) if accuracy is not None else None,
                "average_confidence": round(average_confidence, 2) if average_confidence is not None else None,
                "brier_score": round(brier_score, 3) if brier_score is not None else None,
                "bias_score": round(bias_score, 3) if bias_score is not None else None,
                "total_questions": exam_data["total_questions"]
            })
            exam_number += 1
        
        return trends


def get_user_statistics(user_id: str) -> Dict:
    """
    Calculate basic statistics for a user's completed exams.
    
    Args:
        user_id: User UUID
    
    Returns:
        Dictionary with:
        - total_exams: Total number of completed exams
        - total_questions: Total questions answered
        - correct_answers: Total correct answers
        - accuracy: Overall accuracy percentage
        - average_confidence: Average confidence across all questions
        - average_brier_score: Average Brier score
        - average_bias_score: Average bias score
    
    Used by: Statistics endpoints (Phase 3 prep)
    """
    with get_db() as conn:
        cursor = conn.cursor()
        placeholder = "%s" if DATABASE_URL else "?"
        
        # Get completed exams with their answers
        cursor.execute(f"""
            SELECT 
                e.id as exam_id,
                e.score,
                ea.question_id,
                ea.user_answer,
                ea.confidence,
                q.correct_answer
            FROM exams e
            JOIN exam_answers ea ON e.id = ea.exam_id
            JOIN questions q ON ea.question_id = q.id
            WHERE e.user_id = {placeholder} AND e.completed_at IS NOT NULL
        """, (user_id,))
        
        rows = cursor.fetchall()
        
        if not rows:
            return {
                "total_exams": 0,
                "total_questions": 0,
                "correct_answers": 0,
                "accuracy": None,
                "average_confidence": None,
                "average_brier_score": None,
                "average_bias_score": None
            }
        
        # Process results
        exam_ids = set()
        correct_count = 0
        confidence_sum = 0
        confidence_count = 0
        brier_sum = 0
        brier_count = 0
        bias_sum = 0
        bias_count = 0
        
        for row in rows:
            if DATABASE_URL:
                row_dict = dict(row)
            else:
                row_dict = {key: row[key] for key in row.keys()}
            
            exam_ids.add(row_dict["exam_id"])
            
            user_answer = row_dict["user_answer"]
            correct_answer = row_dict["correct_answer"]
            confidence = row_dict["confidence"]
            
            is_correct = (user_answer == correct_answer)
            if is_correct:
                correct_count += 1
            
            # Calculate metrics if confidence provided
            if confidence is not None:
                confidence_sum += confidence
                confidence_count += 1
                
                # Brier score
                confidence_prob = confidence / 100.0
                correctness = 1 if is_correct else 0
                brier_sum += (confidence_prob - correctness) ** 2
                brier_count += 1
                
                # Bias score
                bias_sum += (confidence_prob - correctness)
                bias_count += 1
        
        total_questions = len(rows)
        accuracy = (correct_count / total_questions * 100) if total_questions > 0 else None
        average_confidence = (confidence_sum / confidence_count) if confidence_count > 0 else None
        average_brier = (brier_sum / brier_count) if brier_count > 0 else None
        average_bias = (bias_sum / bias_count) if bias_count > 0 else None
        
        return {
            "total_exams": len(exam_ids),
            "total_questions": total_questions,
            "correct_answers": correct_count,
            "accuracy": round(accuracy, 2) if accuracy is not None else None,
            "average_confidence": round(average_confidence, 1) if average_confidence is not None else None,
            "average_brier_score": round(average_brier, 3) if average_brier is not None else None,
            "average_bias_score": round(average_bias, 3) if average_bias is not None else None
        }
