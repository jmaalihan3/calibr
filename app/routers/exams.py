"""
Exam API endpoints.

REST API for exam operations:
- POST /api/exams/start: Create new exam (anonymous or authenticated)
- POST /api/exams/{exam_id}/submit: Submit answers
- GET /api/exams/{exam_id}/results: Retrieve results
- GET /api/exams/history: Get user's exam history (authenticated)
- GET /api/exams/statistics: Get user's statistics (authenticated)

Design: Thin controller layer, delegates to services.py
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Optional
from app import services
from app.auth import get_current_user, get_current_user_optional


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
async def start_exam(
    request: StartExamRequest = StartExamRequest(),
    user: Optional[Dict] = Depends(get_current_user_optional)
):
    """
    Start a new exam with random questions.
    
    Authentication: Optional
    - If authenticated, exam is linked to user for history tracking
    - If anonymous, exam works but won't appear in history
    
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
        # Extract user_id if authenticated
        user_id = user["id"] if user else None
        
        result = services.start_exam(
            num_questions=request.num_questions,
            user_id=user_id
        )
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


@router.get("/history")
async def get_exam_history(
    limit: int = 50,
    offset: int = 0,
    user: Dict = Depends(get_current_user)
):
    """
    Get exam history for authenticated user.
    
    Authentication: Required
    
    Query parameters:
        limit: Maximum number of exams to return (default 50, max 100)
        offset: Number of exams to skip for pagination (default 0)
    
    Response:
        {
            "exams": [
                {
                    "id": 123,
                    "created_at": "2026-11-09T17:30:00",
                    "completed_at": "2026-11-09T17:35:00",
                    "score": 4,
                    "total_questions": 5,
                    "percentage": 80.0
                },
                ...
            ],
            "total": 15,
            "limit": 50,
            "offset": 0
        }
    
    Status codes:
        200: Success
        401: Not authenticated
        500: Server error
    
    Note: Ordered by created_at DESC (newest first)
    """
    try:
        # Limit max to 100 for performance
        if limit > 100:
            limit = 100
        
        result = services.get_user_exam_history(
            user_id=user["id"],
            limit=limit,
            offset=offset
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve exam history: {str(e)}")


@router.get("/statistics")
async def get_statistics(user: Dict = Depends(get_current_user)):
    """
    Get overall statistics for authenticated user.
    
    Authentication: Required
    
    Response:
        {
            "total_exams": 10,
            "total_questions": 50,
            "correct_answers": 42,
            "accuracy": 84.0,
            "average_confidence": 75.5,
            "average_brier_score": 0.123,
            "average_bias_score": -0.045
        }
    
    Status codes:
        200: Success
        401: Not authenticated
        500: Server error
    
    Note: Only includes completed exams
    """
    try:
        result = services.get_user_statistics(user_id=user["id"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve statistics: {str(e)}")


@router.get("/trends")
async def get_exam_trends(user: Dict = Depends(get_current_user)):
    """
    Get time-series statistics for longitudinal tracking.
    
    Authentication: Required
    
    Response:
        {
            "trends": [
                {
                    "exam_id": 123,
                    "completed_at": "2026-11-09T17:30:00",
                    "exam_number": 1,
                    "accuracy": 80.0,
                    "average_confidence": 75.5,
                    "brier_score": 0.123,
                    "bias_score": -0.045,
                    "total_questions": 5
                },
                ...
            ]
        }
    
    Status codes:
        200: Success
        401: Not authenticated
        500: Server error
    
    Note: Ordered chronologically by completion date
    Used for: Longitudinal tracking charts showing trends over time
    """
    try:
        result = services.get_user_exam_trends(user_id=user["id"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve exam trends: {str(e)}")
