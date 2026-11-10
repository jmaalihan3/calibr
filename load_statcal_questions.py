"""
Load StatCal categorical data questions into the database.
Run this script to populate the production database with real exam questions.
"""

import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import db


def load_questions_from_markdown(filepath):
    """Parse the markdown file containing JSON questions."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Extract JSON from markdown code block
    json_start = content.find('```json\n') + 8
    json_end = content.find('\n```', json_start)
    json_content = content[json_start:json_end]
    
    return json.loads(json_content)


def transform_question(question_data, unit, unit_name):
    """Transform question from structured format to database format."""
    # Extract options text only for the options array
    options = [choice['text'] for choice in question_data['choices']]
    
    # Find correct answer index
    correct_answer = None
    for idx, choice in enumerate(question_data['choices']):
        if choice['is_correct']:
            correct_answer = idx
            break
    
    # Get explanation for correct answer
    explanation = None
    for choice in question_data['choices']:
        if choice['is_correct']:
            explanation = choice['explanation']
            break
    
    return {
        'question_text': question_data['question'],
        'options': json.dumps(options),
        'correct_answer': correct_answer,
        'unit': str(unit),
        'unit_name': unit_name,
        'topic': question_data.get('topic', ''),
        'explanation': explanation,
        'choices_json': json.dumps(question_data['choices']),
        'review_json': json.dumps(question_data.get('review', {}))
    }


def main():
    # Load questions from markdown
    print("Loading questions from markdown file...")
    filepath = 'statcal_categorical_data_unit_1_exam_structured.md'
    
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found!")
        return
    
    data = load_questions_from_markdown(filepath)
    unit = data['unit']
    unit_name = data['unit_name']
    questions = data['questions']
    
    print(f"Found {len(questions)} questions for Unit {unit}: {unit_name}")
    
    # Clear existing questions
    print("\nClearing existing questions from database...")
    with db.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM questions")
        print(f"Cleared existing questions")
    
    # Insert new questions
    print(f"\nInserting {len(questions)} new questions...")
    
    placeholder = "%s" if db.DATABASE_URL else "?"
    
    with db.get_db() as conn:
        cursor = conn.cursor()
        
        for q in questions:
            transformed = transform_question(q, unit, unit_name)
            
            cursor.execute(
                f"""
                INSERT INTO questions 
                (question_text, options, correct_answer, unit, unit_name, topic, explanation, choices_json, review_json)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                """,
                (
                    transformed['question_text'],
                    transformed['options'],
                    transformed['correct_answer'],
                    transformed['unit'],
                    transformed['unit_name'],
                    transformed['topic'],
                    transformed['explanation'],
                    transformed['choices_json'],
                    transformed['review_json']
                )
            )
        
        conn.commit()
    
    print(f"✅ Successfully loaded {len(questions)} questions!")
    print(f"\nDatabase: {'PostgreSQL (Production)' if db.DATABASE_URL else 'SQLite (Local)'}")
    
    # Verify
    with db.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM questions")
        result = cursor.fetchone()
        if db.DATABASE_URL:
            count = result['count']
        else:
            count = result[0]
        print(f"Verified: {count} questions in database")


if __name__ == '__main__':
    main()
