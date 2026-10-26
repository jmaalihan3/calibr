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


def submit_exam(exam_id: int, answers: Dict[str, int], confidence: Dict[str, int] = None) -> Dict:
    """
    Process exam submission, calculate score and Brier Score, and return results.
    
    Args:
        exam_id: The exam instance ID
        answers: Dictionary mapping question_id (as string) -> answer_index
                 Example: {"5": 1, "7": 2, "3": 0}
        confidence: Dictionary mapping question_id (as string) -> confidence
                    0-100 = Confidence percentage
    
    Returns:
        Dictionary containing:
        - score: Number of correct answers
        - total: Total number of questions
        - percentage: Score as percentage (0-100)
        - brier_score: Calibration metric (0=perfect, 1=worst)
        - bias_score: Bias metric (-1 to 1, negative=underconfident, positive=overconfident)
        - results: List of result objects with question details
    
    Process:
    1. Convert answer keys to integers
    2. Save answers and confidence to database
    3. Retrieve questions with correct answers
    4. Calculate score by comparing user answers with correct answers
    5. Calculate Brier Score for calibration
    6. Update exam record with score
    7. Format results for frontend display
    
    Used by: routers/exams.py POST /api/exams/{exam_id}/submit
    
    Note: Frontend sends question IDs as strings (JSON keys), we convert to int
    """
    # Convert string keys to integers for database
    int_answers = {int(k): v for k, v in answers.items()}
    int_confidence = {int(k): v for k, v in confidence.items()} if confidence else None
    
    # Save user answers and confidence to database
    db.save_exam_answers(exam_id, int_answers, int_confidence)
    
    # Get exam with correct answers for scoring
    exam_data = db.get_exam_with_answers(exam_id)
    
    if not exam_data:
        raise ValueError(f"Exam {exam_id} not found")
    
    # Calculate score and build results
    score = 0
    results = []
    brier_sum = 0.0
    brier_count = 0
    bias_sum = 0.0
    bias_count = 0
    
    for question_id, question_data in exam_data["questions"].items():
        user_answer = exam_data["user_answers"].get(question_id)
        correct_answer = question_data["correct_answer"]
        is_correct = user_answer == correct_answer
        user_conf = exam_data["user_confidence"].get(question_id)
        
        if is_correct:
            score += 1
        
        # Calculate Brier Score and Bias Score contributions for this question
        # Brier = (confidence_probability - correctness)^2
        # Bias = (confidence_probability - correctness)
        # confidence: 0-100 percentage, converted to 0-1 probability
        # correctness: 1 = Correct, 0 = Incorrect
        if user_conf is not None:
            confidence_probability = user_conf / 100.0  # Convert percentage to probability
            correctness = 1 if is_correct else 0
            brier_sum += (confidence_probability - correctness) ** 2
            brier_count += 1
            bias_sum += (confidence_probability - correctness)
            bias_count += 1
        
        # Determine calibration match
        # Match = (confident ≥50% AND correct) OR (not confident <50% AND incorrect)
        calibrated = None
        if user_conf is not None:
            calibrated = (user_conf >= 50 and is_correct) or (user_conf < 50 and not is_correct)
        
        # Build result object for this question
        results.append({
            "question_id": question_id,
            "question_text": question_data["question_text"],
            "options": question_data["options"],
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "confidence": user_conf,
            "calibrated": calibrated,
            "unit": question_data.get("unit"),
            "unit_name": question_data.get("unit_name")
        })
    
    total_questions = len(exam_data["questions"])
    percentage = (score / total_questions * 100) if total_questions > 0 else 0
    
    # Calculate final Brier Score (average)
    brier_score = (brier_sum / brier_count) if brier_count > 0 else None
    
    # Calculate final Bias Score (average)
    # Bias > 0 = overconfident, Bias < 0 = underconfident, Bias = 0 = calibrated
    bias_score = (bias_sum / bias_count) if bias_count > 0 else None
    
    # Update exam with final score
    db.update_exam_score(exam_id, score)
    
    return {
        "score": score,
        "total": total_questions,
        "percentage": round(percentage, 2),
        "brier_score": round(brier_score, 3) if brier_score is not None else None,
        "bias_score": round(bias_score, 3) if bias_score is not None else None,
        "results": results
    }


def get_exam_results(exam_id: int) -> Dict:
    """
    Retrieve results for a completed exam.
    
    Args:
        exam_id: The exam instance ID
    
    Returns:
        Dictionary containing exam results (same structure as submit_exam)
        Includes Brier Score, Bias Score, and calibration data if confidence was recorded
    
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
    brier_sum = 0.0
    brier_count = 0
    bias_sum = 0.0
    bias_count = 0
    
    for question_id, question_data in exam_data["questions"].items():
        user_answer = exam_data["user_answers"].get(question_id)
        correct_answer = question_data["correct_answer"]
        is_correct = user_answer == correct_answer
        user_conf = exam_data["user_confidence"].get(question_id)
        
        if is_correct:
            score += 1
        
        # Calculate Brier Score and Bias Score contributions
        if user_conf is not None:
            confidence_probability = user_conf / 100.0  # Convert percentage to probability
            correctness = 1 if is_correct else 0
            brier_sum += (confidence_probability - correctness) ** 2
            brier_count += 1
            bias_sum += (confidence_probability - correctness)
            bias_count += 1
        
        # Determine calibration match
        calibrated = None
        if user_conf is not None:
            calibrated = (user_conf >= 50 and is_correct) or (user_conf < 50 and not is_correct)
        
        results.append({
            "question_id": question_id,
            "question_text": question_data["question_text"],
            "options": question_data["options"],
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "confidence": user_conf,
            "calibrated": calibrated,
            "unit": question_data.get("unit"),
            "unit_name": question_data.get("unit_name")
        })
    
    total_questions = len(exam_data["questions"])
    percentage = (score / total_questions * 100) if total_questions > 0 else 0
    
    # Calculate final Brier Score
    brier_score = (brier_sum / brier_count) if brier_count > 0 else None
    
    # Calculate final Bias Score
    bias_score = (bias_sum / bias_count) if bias_count > 0 else None
    
    return {
        "score": score,
        "total": total_questions,
        "percentage": round(percentage, 2),
        "brier_score": round(brier_score, 3) if brier_score is not None else None,
        "bias_score": round(bias_score, 3) if bias_score is not None else None,
        "results": results,
        "completed_at": exam_data["completed_at"]
    }
