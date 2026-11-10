"""
Reset questions in the database - clears old questions and loads StatCal questions.
Run this on production via: python reset_questions.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import db

def main():
    print("Resetting questions database...")
    
    with db.get_db() as conn:
        cursor = conn.cursor()
        
        # Clear existing questions
        print("Deleting old questions...")
        cursor.execute("DELETE FROM questions")
        conn.commit()
        
        print("Old questions deleted")
    
    # Re-initialize (will load StatCal questions)
    print("\nRe-initializing database...")
    db.init_db()
    
    # Verify
    with db.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM questions")
        result = cursor.fetchone()
        if db.DATABASE_URL:
            count = result['count']
        else:
            count = result[0]
        
        print(f"\n✅ Done! Database now has {count} questions")
        print(f"Database type: {'PostgreSQL (Production)' if db.DATABASE_URL else 'SQLite (Local)'}")

if __name__ == '__main__':
    main()
