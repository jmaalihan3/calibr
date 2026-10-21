"""
Business logic layer for exam management.

This module sits between the API layer (routers) and database layer (db.py).
It handles:
- Exam generation and initialization
- Answer validation and scoring
- Result formatting for frontend display

Design principle: Keep routers thin, business logic here.
"""

from typing import Dict, List
from app import db


def start_exam(num_questions: int = 5) -> Dict:
    """
    Initialize a new exam with random questions.
    
    Args:
        num_questions: Number of questions to include (default 5)
    
    Returns:
        Dictionary containing:
        - exam_id: Newly created exam instance ID
        - questions: List of question objects (without correct answers)
    
    Process:
    1. Fetch random questions from database
    2. Create exam instance with question IDs
    3. Return exam data for frontend
    
    Used by: routers/exams.py POST /api/exams/start
    
    Example response:
    {
        "exam_id": 123,
        "questions": [
            {
                "id": 5,
                "question_text": "What is 2 + 2?",
                "options": ["3", "4", "5", "6"]
            },
            ...
        ]
    }
    """
    # Get random questions from database
    questions = db.get_random_questions(count=num_questions)
    
    # Extract question IDs for exam record
    question_ids = [q["id"] for q in questions]
    
    # Create exam instance
    exam_id = db.create_exam(question_ids)
    
    return {
        "exam_id": exam_id,
        "questions": questions
    }


def submit_exam(exam_id: int, answers: Dict[str, int]) -> Dict:
    """
    Process exam submission, calculate score, and return results.
    
    Args:
        exam_id: The exam instance ID
        answers: Dictionary mapping question_id (as string) -> answer_index
                 Example: {"5": 1, "7": 2, "3": 0}
    
    Returns:
        Dictionary containing:
        - score: Number of correct answers
        - total: Total number of questions
        - percentage: Score as percentage (0-100)
        - results: List of result objects with question details
    
    Process:
    1. Convert answer keys to integers
    2. Save answers to database
    3. Retrieve questions with correct answers
    4. Calculate score by comparing user answers with correct answers
    5. Update exam record with score
    6. Format results for frontend display
    
    Used by: routers/exams.py POST /api/exams/{exam_id}/submit
    
    Note: Frontend sends question IDs as strings (JSON keys), we convert to int
    """
    # Convert string keys to integers for database
    int_answers = {int(k): v for k, v in answers.items()}
    
    # Save user answers to database
    db.save_exam_answers(exam_id, int_answers)
    
    # Get exam with correct answers for scoring
    exam_data = db.get_exam_with_answers(exam_id)
    
    if not exam_data:
        raise ValueError(f"Exam {exam_id} not found")
    
    # Calculate score
    score = 0
    results = []
    
    for question_id, question_data in exam_data["questions"].items():
        user_answer = exam_data["user_answers"].get(question_id)
        correct_answer = question_data["correct_answer"]
        is_correct = user_answer == correct_answer
        
        if is_correct:
            score += 1
        
        # Build result object for this question
        results.append({
            "question_id": question_id,
            "question_text": question_data["question_text"],
            "options": question_data["options"],
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct
        })
    
    total_questions = len(exam_data["questions"])
    percentage = (score / total_questions * 100) if total_questions > 0 else 0
    
    # Update exam with final score
    db.update_exam_score(exam_id, score)
    
    return {
        "score": score,
        "total": total_questions,
        "percentage": round(percentage, 2),
        "results": results
    }


def get_exam_results(exam_id: int) -> Dict:
    """
    Retrieve results for a completed exam.
    
    Args:
        exam_id: The exam instance ID
    
    Returns:
        Dictionary containing exam results (same structure as submit_exam)
    
    Raises:
        ValueError: If exam not found
    
    Used by: routers/exams.py GET /api/exams/{exam_id}/results
    
    Note: This allows retrieving results after submission for review
    """
    exam_data = db.get_exam_with_answers(exam_id)
    
    if not exam_data:
        raise ValueError(f"Exam {exam_id} not found")
    
    # Rebuild results from stored data
    results = []
    score = 0
    
    for question_id, question_data in exam_data["questions"].items():
        user_answer = exam_data["user_answers"].get(question_id)
        correct_answer = question_data["correct_answer"]
        is_correct = user_answer == correct_answer
        
        if is_correct:
            score += 1
        
        results.append({
            "question_id": question_id,
            "question_text": question_data["question_text"],
            "options": question_data["options"],
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct
        })
    
    total_questions = len(exam_data["questions"])
    percentage = (score / total_questions * 100) if total_questions > 0 else 0
    
    return {
        "score": score,
        "total": total_questions,
        "percentage": round(percentage, 2),
        "results": results,
        "completed_at": exam_data["completed_at"]
    }
