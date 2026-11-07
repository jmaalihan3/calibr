"""
Script to load questions from the revised JSON format into the database.

Revised JSON Format (per statcal_exam_json_format_guide.md):
{
  "unit": 1,
  "unit_name": "Unit Name",
  "questions": [
    {
      "id": 1,
      "topic": "Topic Name",
      "question": "Question text",
      "choices": [
        {
          "id": "A",
          "text": "Answer text",
          "is_correct": true/false,
          "explanation": "Explanation text",
          "misconception_id": "Q01-M01"  // Only for incorrect choices
        }
      ],
      "review": {
        "title": "Review title",
        "learning_objective": "Objective text",
        "related_concepts": ["Concept 1", "Concept 2"]
      }
    }
  ]
}
"""

import json
import sys
import re
from app import db


def extract_json_from_markdown(filename):
    """
    Extract JSON from a Markdown file with a json code block.
    
    Args:
        filename: Path to .md file
    
    Returns:
        Parsed JSON data
    """
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find JSON code block
    match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
    if not match:
        raise ValueError("No JSON code block found in Markdown file")
    
    json_str = match.group(1)
    return json.loads(json_str)


def load_revised_exam(filename):
    """
    Load questions from a revised JSON format file into the database.
    
    Args:
        filename: Path to JSON or Markdown file
    
    Returns:
        Number of questions loaded
    """
    # Determine if it's a Markdown or JSON file
    if filename.endswith('.md'):
        data = extract_json_from_markdown(filename)
        print(f"Extracted JSON from Markdown file: {filename}")
    else:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Loaded JSON file: {filename}")
    
    unit = data.get('unit')
    unit_name = data.get('unit_name')
    questions = data.get('questions', [])
    
    print(f"Loading {len(questions)} questions")
    print(f"Unit {unit}: {unit_name}")
    
    with db.get_db() as conn:
        cursor = conn.cursor()
        
        # Ensure required columns exist
        # Store the complete question data as JSON
        columns_to_add = [
            ('topic', 'TEXT'),
            ('explanation', 'TEXT'),  # Legacy column, may not be used
            ('choices_json', 'TEXT'),  # New: Complete choices array with explanations
            ('review_json', 'TEXT')    # New: Review metadata
        ]
        
        for column_name, column_type in columns_to_add:
            try:
                cursor.execute(f"ALTER TABLE questions ADD COLUMN {column_name} {column_type}")
                print(f"Added '{column_name}' column to questions table")
            except Exception:
                pass  # Column already exists
        
        # Clear existing questions
        cursor.execute("DELETE FROM questions")
        print("Cleared existing questions")
        
        # Insert new questions
        for q in questions:
            # Convert choices array to flat options array and find correct answer
            choices = q['choices']
            options = [choice['text'] for choice in choices]
            correct_answer = next(i for i, choice in enumerate(choices) if choice['is_correct'])
            
            # Store complete choices and review as JSON
            choices_json = json.dumps(choices)
            review_json = json.dumps(q['review'])
            
            cursor.execute(
                """INSERT INTO questions 
                   (question_text, options, correct_answer, unit, unit_name, topic, 
                    choices_json, review_json) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    q['question'],
                    json.dumps(options),  # Flat options for compatibility
                    correct_answer,       # Index for compatibility
                    unit,
                    unit_name,
                    q.get('topic'),
                    choices_json,         # Full choices with explanations
                    review_json           # Review metadata
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
        print("Usage: python load_revised_exam.py <filename.json|filename.md>")
        print("\nExample:")
        print("  python load_revised_exam.py statcal_categorical_data_unit_1_exam_structured.md")
        sys.exit(1)
    
    filename = sys.argv[1]
    load_revised_exam(filename)
    
    print("\nDatabase updated successfully!")
    print("Server will auto-reload if running with --reload")
