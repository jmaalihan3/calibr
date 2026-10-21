"""
Script to parse statistics_and_probability_exam.txt and load questions into database.

This file has a different format:
- Options formatted as "  A)" instead of "* A)"
- Answers in a separate ANSWER KEY section at the end
- Line numbers embedded in the text
"""

import re
import json
from app import db


def parse_statistics_exam(filename):
    """
    Parse statistics_and_probability_exam.txt file.
    
    Format:
    - Unit headers: "UNIT N: NAME"
    - Questions with "Question N"
    - Options as "  A) [text]"
    - Answer key at end as " N. X) [text]"
    
    Returns:
        List of question dictionaries with unit information
    """
    with open(filename, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    # Remove line numbers (pattern: whitespace + digits + |)
    content = re.sub(r'^\s*\d+\|', '', content, flags=re.MULTILINE)
    
    # Split into main content and answer key
    parts = content.split('ANSWER KEY')
    if len(parts) != 2:
        raise ValueError("Could not find ANSWER KEY section")
    
    main_content = parts[0]
    answer_key_text = parts[1]
    
    # Parse answer key first
    answer_key = {}
    for line in answer_key_text.split('\n'):
        line = line.strip()
        # Match pattern like " 1. B)" or "12. C)"
        match = re.match(r'^(\d+)\.\s*([A-D])\)', line)
        if match:
            question_num = int(match.group(1))
            answer_letter = match.group(2)
            answer_key[question_num] = answer_letter
    
    # Parse questions with unit tracking
    questions = []
    current_unit = None
    current_unit_name = None
    
    # Split by lines to track unit headers
    lines = main_content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Check for unit header (e.g., "UNIT 3: SUMMARIZING QUANTITATIVE DATA")
        unit_match = re.match(r'^UNIT\s+(\d+):\s*(.+)$', line)
        if unit_match:
            current_unit = int(unit_match.group(1))
            current_unit_name = unit_match.group(2).strip()
            i += 1
            continue
        
        # Check for question start
        if re.match(r'^Question \d+$', line):
            # Find the question block
            question_lines = []
            i += 1
            
            # Collect all lines until next Question or end
            while i < len(lines):
                if re.match(r'^Question \d+$', lines[i].strip()) or lines[i].strip().startswith('UNIT'):
                    break
                question_lines.append(lines[i])
                i += 1
            
            # Parse this question block
            question_block = '\n'.join(question_lines)
            question_num_match = re.search(r'Question (\d+)', line)
            if question_num_match:
                question_num = int(question_num_match.group(1))
                parsed = parse_question_block(question_block, question_num, answer_key)
                
                if parsed:
                    # Add unit information
                    parsed['unit'] = current_unit
                    parsed['unit_name'] = current_unit_name
                    questions.append(parsed)
            continue
        
        i += 1
    
    return questions


def parse_question_block(block, question_num, answer_key):
    """
    Parse a single question block.
    
    Args:
        block: Text containing question and options
        question_num: Question number
        answer_key: Dictionary of correct answers
    
    Returns:
        Dictionary with question data or None if invalid
    """
    lines = block.split('\n')
    
    question_text_lines = []
    options = {'A': [], 'B': [], 'C': [], 'D': []}
    current_option = None
    
    for line in lines:
        # Check if this is an option line
        opt_match = re.match(r'^\s+([A-D])\)\s*(.*)', line)
        if opt_match:
            current_option = opt_match.group(1)
            option_text = opt_match.group(2).strip()
            options[current_option] = [option_text] if option_text else []
            continue
        
        # Skip unit headers and separators
        if '===' in line or line.strip().startswith('UNIT'):
            break
        
        # If we're in an option, add continuation lines
        if current_option and line.strip() and not re.match(r'^\s*[A-D]\)', line):
            options[current_option].append(line.strip())
            continue
        
        # If no options yet, this is question text
        if not any(options.values()) and line.strip():
            if '===' not in line and 'UNIT' not in line:
                question_text_lines.append(line.strip())
    
    # Build question
    question_text = ' '.join(question_text_lines).strip()
    option_list = [
        ' '.join(options['A']).strip(),
        ' '.join(options['B']).strip(),
        ' '.join(options['C']).strip(),
        ' '.join(options['D']).strip()
    ]
    
    # Get correct answer from answer key
    if question_num in answer_key and question_text and all(option_list):
        correct_letter = answer_key[question_num]
        correct_index = ord(correct_letter) - ord('A')
        
        return {
            "question": question_text,
            "options": option_list,
            "correct": correct_index
        }
    
    return None


def load_questions_to_db(questions):
    """
    Load parsed questions into database, replacing existing questions.
    
    Args:
        questions: List of question dictionaries with unit information
    """
    with db.get_db() as conn:
        cursor = conn.cursor()
        
        # Add unit columns if they don't exist (migration)
        try:
            cursor.execute("ALTER TABLE questions ADD COLUMN unit INTEGER")
            print("Added 'unit' column to questions table")
        except Exception:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE questions ADD COLUMN unit_name TEXT")
            print("Added 'unit_name' column to questions table")
        except Exception:
            pass  # Column already exists
        
        # Clear existing questions
        cursor.execute("DELETE FROM questions")
        print(f"Cleared existing questions")
        
        # Insert new questions with unit information
        for q in questions:
            cursor.execute(
                "INSERT INTO questions (question_text, options, correct_answer, unit, unit_name) VALUES (?, ?, ?, ?, ?)",
                (q["question"], json.dumps(q["options"]), q["correct"], q.get("unit"), q.get("unit_name"))
            )
        
        print(f"Loaded {len(questions)} questions with unit information")
        
        # Show unit distribution
        cursor.execute("SELECT unit, unit_name, COUNT(*) FROM questions GROUP BY unit ORDER BY unit")
        print("\nQuestions by unit:")
        for row in cursor.fetchall():
            unit_num, unit_name, count = row
            print(f"  Unit {unit_num}: {unit_name} - {count} questions")


if __name__ == "__main__":
    # Parse statistics exam file
    questions = parse_statistics_exam("statistics_and_probability_exam.txt")
    
    print(f"Found {len(questions)} questions in statistics_and_probability_exam.txt")
    
    if questions:
        print("\nFirst question preview:")
        q = questions[0]
        print(f"Unit: {q.get('unit')} - {q.get('unit_name')}")
        print(f"Q: {q['question'][:100]}...")
        print(f"Options ({len(q['options'])}):")
        for i, opt in enumerate(q['options']):
            print(f"  {chr(65+i)}) {opt[:60]}...")
        print(f"Correct: {chr(65+q['correct'])}")
        
        print("\nLast question preview:")
        q = questions[-1]
        print(f"Unit: {q.get('unit')} - {q.get('unit_name')}")
        print(f"Q: {q['question'][:100]}...")
        print(f"Correct: {chr(65+q['correct'])}")
    
    # Load into database
    load_questions_to_db(questions)
    
    print("\nDatabase updated successfully!")
    print("Server will auto-reload if running with --reload")
