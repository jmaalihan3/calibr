"""
Migration script to add confidence column to exam_answers table.

This adds support for calibration tracking by storing user confidence
(1 = Confident, 0 = Not Confident) alongside each answer.
"""

import sqlite3

DATABASE_PATH = "exams.db"

def migrate():
    """Add confidence column to exam_answers table."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(exam_answers)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if "confidence" not in columns:
            print("Adding confidence column to exam_answers table...")
            cursor.execute("""
                ALTER TABLE exam_answers 
                ADD COLUMN confidence INTEGER
            """)
            conn.commit()
            print("✓ Migration completed successfully")
        else:
            print("✓ Confidence column already exists, skipping migration")
    
    except Exception as e:
        conn.rollback()
        print(f"✗ Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
