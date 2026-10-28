"""
Script to load questions from JSON format files into the database.

JSON Format:
{
  "unit": 1,
  "unit_name": "Unit Name",
  "questions": [
    {
      "id": 1,
      "topic": "Topic Name",
      "question": "Question text",
      "options": ["A", "B", "C", "D"],
      "correct": 0,
      "explanation": "Optional explanation"
    }
  ]
}
"""

import json
import sys
from app import db


def load_json_exam(filename):
    """
    Load questions from a JSON file into the database.
    
    Args:
        filename: Path to JSON file
    
    Returns:
        Number of questions loaded
    """
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    unit = data.get('unit')
    unit_name = data.get('unit_name')
    questions = data.get('questions', [])
    
    print(f"Loading {len(questions)} questions from {filename}")
    print(f"Unit {unit}: {unit_name}")
    
    with db.get_db() as conn:
        cursor = conn.cursor()
        
        # Ensure topic and explanation columns exist
        try:
            cursor.execute("ALTER TABLE questions ADD COLUMN topic TEXT")
            print("Added 'topic' column to questions table")
        except Exception:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE questions ADD COLUMN explanation TEXT")
            print("Added 'explanation' column to questions table")
        except Exception:
            pass  # Column already exists
        
        # Clear existing questions
        cursor.execute("DELETE FROM questions")
        print("Cleared existing questions")
        
        # Insert new questions
        for q in questions:
            cursor.execute(
                """INSERT INTO questions 
                   (question_text, options, correct_answer, unit, unit_name, topic, explanation) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    q['question'],
                    json.dumps(q['options']),
                    q['correct'],
                    unit,
                    unit_name,
                    q.get('topic'),
                    q.get('explanation')
                )
            )
        
        print(f"\n✓ Loaded {len(questions)} questions successfully")
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM questions")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT topic, COUNT(*) FROM questions GROUP BY topic")
        print("\nQuestions by topic:")
        for row in cursor.fetchall():
            topic, count = row
            print(f"  {topic}: {count} questions")
        
        return len(questions)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python load_json_exam.py <filename.json>")
        sys.exit(1)
    
    filename = sys.argv[1]
    load_json_exam(filename)
    
    print("\nDatabase updated successfully!")
    print("Server will auto-reload if running with --reload")
