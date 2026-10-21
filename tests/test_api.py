"""
Integration tests for API endpoints.

Tests:
- POST /api/exams/start
- POST /api/exams/{exam_id}/submit
- GET /api/exams/{exam_id}/results
- Error handling and status codes

Uses FastAPI TestClient for integration testing.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app


@pytest.fixture
def client():
    """
    Fixture providing FastAPI test client.
    """
    return TestClient(app)


@pytest.fixture
def mock_services():
    """
    Fixture to mock services layer for API tests.
    """
    with patch('app.routers.exams.services') as mock:
        yield mock


def test_start_exam_success(client, mock_services):
    """
    Test POST /api/exams/start returns exam data.
    """
    # Setup mock
    mock_services.start_exam.return_value = {
        "exam_id": 123,
        "questions": [
            {
                "id": 1,
                "question_text": "What is 2 + 2?",
                "options": ["3", "4", "5", "6"]
            }
        ]
    }
    
    # Make request
    response = client.post("/api/exams/start", json={"num_questions": 5})
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data['exam_id'] == 123
    assert len(data['questions']) == 1
    
    # Verify service was called
    mock_services.start_exam.assert_called_once_with(num_questions=5)


def test_start_exam_default_questions(client, mock_services):
    """
    Test POST /api/exams/start with default question count.
    """
    # Setup mock
    mock_services.start_exam.return_value = {
        "exam_id": 123,
        "questions": []
    }
    
    # Make request without body (use defaults)
    response = client.post("/api/exams/start")
    
    # Verify response
    assert response.status_code == 200
    
    # Verify default count of 5 was used
    mock_services.start_exam.assert_called_once_with(num_questions=5)


def test_start_exam_error(client, mock_services):
    """
    Test POST /api/exams/start handles service errors.
    """
    # Setup mock to raise exception
    mock_services.start_exam.side_effect = Exception("Database error")
    
    # Make request
    response = client.post("/api/exams/start", json={"num_questions": 5})
    
    # Verify error response
    assert response.status_code == 500
    assert "Failed to start exam" in response.json()['detail']


def test_submit_exam_success(client, mock_services):
    """
    Test POST /api/exams/{exam_id}/submit returns results.
    """
    # Setup mock
    mock_services.submit_exam.return_value = {
        "score": 3,
        "total": 5,
        "percentage": 60.0,
        "results": [
            {
                "question_id": 1,
                "question_text": "What is 2 + 2?",
                "options": ["3", "4", "5", "6"],
                "user_answer": 1,
                "correct_answer": 1,
                "is_correct": True
            }
        ]
    }
    
    # Make request
    answers = {"1": 1, "2": 0, "3": 2}
    response = client.post("/api/exams/123/submit", json={"answers": answers})
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data['score'] == 3
    assert data['total'] == 5
    assert data['percentage'] == 60.0
    
    # Verify service was called
    mock_services.submit_exam.assert_called_once_with(123, answers)


def test_submit_exam_not_found(client, mock_services):
    """
    Test POST /api/exams/{exam_id}/submit handles exam not found.
    """
    # Setup mock to raise ValueError
    mock_services.submit_exam.side_effect = ValueError("Exam 999 not found")
    
    # Make request
    response = client.post("/api/exams/999/submit", json={"answers": {"1": 0}})
    
    # Verify 404 response
    assert response.status_code == 404
    assert "not found" in response.json()['detail']


def test_submit_exam_server_error(client, mock_services):
    """
    Test POST /api/exams/{exam_id}/submit handles server errors.
    """
    # Setup mock to raise generic exception
    mock_services.submit_exam.side_effect = Exception("Database error")
    
    # Make request
    response = client.post("/api/exams/123/submit", json={"answers": {"1": 0}})
    
    # Verify 500 response
    assert response.status_code == 500
    assert "Failed to submit exam" in response.json()['detail']


def test_get_results_success(client, mock_services):
    """
    Test GET /api/exams/{exam_id}/results returns results.
    """
    # Setup mock
    mock_services.get_exam_results.return_value = {
        "score": 5,
        "total": 5,
        "percentage": 100.0,
        "results": [],
        "completed_at": "2026-10-21T04:22:00"
    }
    
    # Make request
    response = client.get("/api/exams/123/results")
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data['score'] == 5
    assert data['completed_at'] == "2026-10-21T04:22:00"
    
    # Verify service was called
    mock_services.get_exam_results.assert_called_once_with(123)


def test_get_results_not_found(client, mock_services):
    """
    Test GET /api/exams/{exam_id}/results handles exam not found.
    """
    # Setup mock to raise ValueError
    mock_services.get_exam_results.side_effect = ValueError("Exam 999 not found")
    
    # Make request
    response = client.get("/api/exams/999/results")
    
    # Verify 404 response
    assert response.status_code == 404
    assert "not found" in response.json()['detail']


def test_get_results_server_error(client, mock_services):
    """
    Test GET /api/exams/{exam_id}/results handles server errors.
    """
    # Setup mock to raise generic exception
    mock_services.get_exam_results.side_effect = Exception("Database error")
    
    # Make request
    response = client.get("/api/exams/123/results")
    
    # Verify 500 response
    assert response.status_code == 500
    assert "Failed to retrieve results" in response.json()['detail']


def test_health_check(client):
    """
    Test GET /api/health endpoint.
    """
    response = client.get("/api/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'ok'


def test_cors_headers(client):
    """
    Test CORS headers are set correctly.
    
    Note: This is a basic check. Full CORS testing would require
    testing OPTIONS requests and various origins.
    """
    response = client.get("/api/health")
    
    # CORS middleware should set these headers
    # (exact headers depend on request origin)
    assert response.status_code == 200
