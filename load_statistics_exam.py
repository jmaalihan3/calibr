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
    - Questions with "Question N"
    - Options as "  A) [text]"
    - Answer key at end as " N. X) [text]"
    
    Returns:
        List of question dictionaries
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
    
    # Parse questions
    questions = []
    question_blocks = re.split(r'\n(?=Question \d+\n)', main_content)
    
    for block in question_blocks:
        block = block.strip()
        if not block.startswith('Question'):
            continue
        
        # Extract question number
        first_line = block.split('\n')[0]
        q_num_match = re.match(r'Question (\d+)', first_line)
        if not q_num_match:
            continue
        
        question_num = int(q_num_match.group(1))
        
        # Split into lines
        lines = block.split('\n')[1:]  # Skip "Question N" line
        
        # Find where options start
        question_text_lines = []
        options = {'A': [], 'B': [], 'C': [], 'D': []}
        current_option = None
        
        for line in lines:
            # Check if this is an option line (starts with spaces and letter)
            opt_match = re.match(r'^\s+([A-D])\)\s*(.*)', line)
            if opt_match:
                current_option = opt_match.group(1)
                option_text = opt_match.group(2).strip()
                options[current_option] = [option_text] if option_text else []
                continue
            
            # Skip unit headers and separators
            if '===' in line or line.strip().startswith('UNIT'):
                break
            
            # If we're in an option and line doesn't start a new option, it's continuation
            if current_option and line.strip() and not re.match(r'^\s*[A-D]\)', line):
                options[current_option].append(line.strip())
                continue
            
            # If no options yet, this is question text
            if not any(options.values()) and line.strip():
                # Skip section headers
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
            
            questions.append({
                "question": question_text,
                "options": option_list,
                "correct": correct_index
            })
    
    return questions


def load_questions_to_db(questions):
    """
    Load parsed questions into database, replacing existing questions.
    
    Args:
        questions: List of question dictionaries
    """
    with db.get_db() as conn:
        cursor = conn.cursor()
        
        # Clear existing questions
        cursor.execute("DELETE FROM questions")
        print(f"Cleared existing questions")
        
        # Insert new questions
        for q in questions:
            cursor.execute(
                "INSERT INTO questions (question_text, options, correct_answer) VALUES (?, ?, ?)",
                (q["question"], json.dumps(q["options"]), q["correct"])
            )
        
        print(f"Loaded {len(questions)} questions from statistics_and_probability_exam.txt")


if __name__ == "__main__":
    # Parse statistics exam file
    questions = parse_statistics_exam("statistics_and_probability_exam.txt")
    
    print(f"Found {len(questions)} questions in statistics_and_probability_exam.txt")
    
    if questions:
        print("\nFirst question preview:")
        q = questions[0]
        print(f"Q: {q['question'][:100]}...")
        print(f"Options ({len(q['options'])}):")
        for i, opt in enumerate(q['options']):
            print(f"  {chr(65+i)}) {opt[:60]}...")
        print(f"Correct: {chr(65+q['correct'])}")
        
        print("\nLast question preview:")
        q = questions[-1]
        print(f"Q: {q['question'][:100]}...")
        print(f"Correct: {chr(65+q['correct'])}")
    
    # Load into database
    load_questions_to_db(questions)
    
    print("\nDatabase updated successfully!")
    print("Server will auto-reload if running with --reload")
