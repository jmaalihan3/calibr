"""
Exam API endpoints.

REST API for exam operations:
- POST /api/exams/start: Create new exam
- POST /api/exams/{exam_id}/submit: Submit answers
- GET /api/exams/{exam_id}/results: Retrieve results

Design: Thin controller layer, delegates to services.py
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict
from app import services


router = APIRouter(prefix="/api/exams", tags=["exams"])


class StartExamRequest(BaseModel):
    """
    Request model for starting a new exam.
    
    Fields:
        num_questions: Number of questions to include (default 5)
    """
    num_questions: int = 5


class SubmitExamRequest(BaseModel):
    """
    Request model for submitting exam answers.
    
    Fields:
        answers: Dictionary mapping question_id (as string) to answer index
                 Example: {"5": 1, "7": 2, "3": 0}
        confidence: Dictionary mapping question_id (as string) to confidence
                    1 = Confident, 0 = Not Confident
                    Example: {"5": 1, "7": 0, "3": 1}
    
    Note: JSON object keys are always strings, converted to int in services layer
    """
    answers: Dict[str, int]
    confidence: Dict[str, int] = None


@router.post("/start")
async def start_exam(request: StartExamRequest = StartExamRequest()):
    """
    Start a new exam with random questions.
    
    Request body:
        {
            "num_questions": 5  // optional, defaults to 5
        }
    
    Response:
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
    
    Status codes:
        200: Success
        500: Server error (database issues, etc.)
    
    Note: Questions do not include correct answers (security)
    """
    try:
        result = services.start_exam(num_questions=request.num_questions)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start exam: {str(e)}")


@router.post("/{exam_id}/submit")
async def submit_exam(exam_id: int, request: SubmitExamRequest):
    """
    Submit exam answers and get results.
    
    Path parameters:
        exam_id: The exam instance ID
    
    Request body:
        {
            "answers": {
                "5": 1,  // question_id: answer_index
                "7": 2,
                "3": 0
            },
            "confidence": {
                "5": 1,  // question_id: confidence (1=Confident, 0=Not Confident)
                "7": 0,
                "3": 1
            }
        }
    
    Response:
        {
            "score": 3,
            "total": 5,
            "percentage": 60.0,
            "brier_score": 0.4,
            "results": [
                {
                    "question_id": 5,
                    "question_text": "What is 2 + 2?",
                    "options": ["3", "4", "5", "6"],
                    "user_answer": 1,
                    "correct_answer": 1,
                    "is_correct": true,
                    "confidence": 1,
                    "calibrated": true
                },
                ...
            ]
        }
    
    Status codes:
        200: Success
        404: Exam not found
        400: Invalid request data
        500: Server error
    """
    try:
        result = services.submit_exam(exam_id, request.answers, request.confidence)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit exam: {str(e)}")


@router.get("/{exam_id}/results")
async def get_results(exam_id: int):
    """
    Retrieve results for a completed exam.
    
    Path parameters:
        exam_id: The exam instance ID
    
    Response:
        {
            "score": 3,
            "total": 5,
            "percentage": 60.0,
            "results": [...],
            "completed_at": "2026-10-21T04:22:00"
        }
    
    Status codes:
        200: Success
        404: Exam not found
        500: Server error
    
    Use case: Allows users to review results after submission
    """
    try:
        result = services.get_exam_results(exam_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve results: {str(e)}")
