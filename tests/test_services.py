"""
Unit tests for business logic layer.

Tests:
- Exam starting process
- Exam submission and scoring
- Results retrieval

Mocks database calls for isolation.
"""

import pytest
from unittest.mock import patch, MagicMock
from app import services


@pytest.fixture
def mock_questions():
    """
    Fixture providing sample questions for tests.
    """
    return [
        {
            "id": 1,
            "question_text": "What is 2 + 2?",
            "options": ["3", "4", "5", "6"]
        },
        {
            "id": 2,
            "question_text": "What is the capital of France?",
            "options": ["London", "Berlin", "Paris", "Madrid"]
        }
    ]


@pytest.fixture
def mock_exam_data():
    """
    Fixture providing sample exam data with correct answers.
    """
    return {
        "exam_id": 1,
        "questions": {
            1: {
                "question_text": "What is 2 + 2?",
                "options": ["3", "4", "5", "6"],
                "correct_answer": 1
            },
            2: {
                "question_text": "What is the capital of France?",
                "options": ["London", "Berlin", "Paris", "Madrid"],
                "correct_answer": 2
            }
        },
        "user_answers": {1: 1, 2: 2},
        "score": None,
        "completed_at": None
    }


@patch('app.services.db')
def test_start_exam(mock_db, mock_questions):
    """
    Test starting an exam returns exam ID and questions.
    """
    # Setup mocks
    mock_db.get_random_questions.return_value = mock_questions
    mock_db.create_exam.return_value = 123
    
    # Call service
    result = services.start_exam(num_questions=2)
    
    # Verify result structure
    assert result['exam_id'] == 123
    assert result['questions'] == mock_questions
    
    # Verify database calls
    mock_db.get_random_questions.assert_called_once_with(count=2)
    mock_db.create_exam.assert_called_once_with([1, 2])


@patch('app.services.db')
def test_submit_exam_all_correct(mock_db, mock_exam_data):
    """
    Test submitting exam with all correct answers.
    """
    # Setup mocks
    mock_db.get_exam_with_answers.return_value = mock_exam_data
    
    # Submit with all correct answers
    answers = {"1": 1, "2": 2}  # String keys from JSON
    result = services.submit_exam(exam_id=1, answers=answers)
    
    # Verify score
    assert result['score'] == 2
    assert result['total'] == 2
    assert result['percentage'] == 100.0
    
    # Verify results structure
    assert len(result['results']) == 2
    for res in result['results']:
        assert res['is_correct'] == True
        assert 'question_text' in res
        assert 'options' in res
        assert 'user_answer' in res
        assert 'correct_answer' in res
    
    # Verify database calls
    mock_db.save_exam_answers.assert_called_once_with(1, {1: 1, 2: 2})
    mock_db.update_exam_score.assert_called_once_with(1, 2)


@patch('app.services.db')
def test_submit_exam_partial_correct(mock_db, mock_exam_data):
    """
    Test submitting exam with partial correct answers.
    """
    # Setup mocks
    mock_exam_data['user_answers'] = {1: 1, 2: 0}  # Second answer wrong
    mock_db.get_exam_with_answers.return_value = mock_exam_data
    
    # Submit with one wrong answer
    answers = {"1": 1, "2": 0}
    result = services.submit_exam(exam_id=1, answers=answers)
    
    # Verify score
    assert result['score'] == 1
    assert result['total'] == 2
    assert result['percentage'] == 50.0
    
    # Verify results
    assert result['results'][0]['is_correct'] == True
    assert result['results'][1]['is_correct'] == False
    
    # Verify score updated
    mock_db.update_exam_score.assert_called_once_with(1, 1)


@patch('app.services.db')
def test_submit_exam_not_found(mock_db):
    """
    Test submitting exam that doesn't exist raises error.
    """
    # Setup mock to return None (exam not found)
    mock_db.get_exam_with_answers.return_value = None
    
    # Should raise ValueError
    with pytest.raises(ValueError, match="Exam 999 not found"):
        services.submit_exam(exam_id=999, answers={"1": 0})


@patch('app.services.db')
def test_get_exam_results(mock_db, mock_exam_data):
    """
    Test retrieving exam results.
    """
    # Setup mock with completed exam
    mock_exam_data['score'] = 2
    mock_exam_data['completed_at'] = "2026-10-21T04:22:00"
    mock_db.get_exam_with_answers.return_value = mock_exam_data
    
    # Get results
    result = services.get_exam_results(exam_id=1)
    
    # Verify result structure
    assert result['score'] == 2
    assert result['total'] == 2
    assert result['percentage'] == 100.0
    assert result['completed_at'] == "2026-10-21T04:22:00"
    assert len(result['results']) == 2


@patch('app.services.db')
def test_get_exam_results_not_found(mock_db):
    """
    Test retrieving results for non-existent exam raises error.
    """
    # Setup mock to return None
    mock_db.get_exam_with_answers.return_value = None
    
    # Should raise ValueError
    with pytest.raises(ValueError, match="Exam 999 not found"):
        services.get_exam_results(exam_id=999)


@patch('app.services.db')
def test_submit_exam_converts_string_keys(mock_db, mock_exam_data):
    """
    Test that submit_exam correctly converts string keys to integers.
    
    JSON object keys are always strings, need to convert to int for database.
    """
    # Setup mock
    mock_db.get_exam_with_answers.return_value = mock_exam_data
    
    # Submit with string keys
    answers = {"1": 1, "2": 2}
    services.submit_exam(exam_id=1, answers=answers)
    
    # Verify save_exam_answers called with integer keys
    call_args = mock_db.save_exam_answers.call_args
    assert call_args[0][1] == {1: 1, 2: 2}


@patch('app.services.db')
def test_start_exam_default_question_count(mock_db, mock_questions):
    """
    Test starting exam with default number of questions (5).
    """
    # Setup mock to return 5 questions
    mock_questions_5 = mock_questions + [
        {"id": 3, "question_text": "Q3", "options": ["A", "B", "C", "D"]},
        {"id": 4, "question_text": "Q4", "options": ["A", "B", "C", "D"]},
        {"id": 5, "question_text": "Q5", "options": ["A", "B", "C", "D"]}
    ]
    mock_db.get_random_questions.return_value = mock_questions_5
    mock_db.create_exam.return_value = 123
    
    # Call with default parameter
    result = services.start_exam()
    
    # Verify default count of 5 was used
    mock_db.get_random_questions.assert_called_once_with(count=5)
