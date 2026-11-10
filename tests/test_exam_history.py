"""
Tests for exam history and user statistics (Phase 2).

Tests:
- Exam linking to authenticated users
- Exam history retrieval
- User statistics calculation
- Anonymous vs authenticated exam flows
- Cross-user isolation
"""

import pytest
from fastapi.testclient import TestClient
import os


@pytest.fixture
def client():
    """
    Fixture providing FastAPI test client with fresh database.
    """
    # Remove old test database
    if os.path.exists("test_history.db"):
        os.remove("test_history.db")
    
    # Patch database path BEFORE importing app
    from app import db
    original_path = db.DATABASE_PATH
    original_url = db.DATABASE_URL
    db.DATABASE_PATH = "test_history.db"
    db.DATABASE_URL = None  # Force SQLite
    
    # Now import app (will use patched database)
    from app.main import app
    
    # Initialize test database
    db.init_db()
    
    # Clear rate limit store for test isolation
    from app.auth import _rate_limit_store
    _rate_limit_store.clear()
    
    yield TestClient(app)
    
    # Cleanup
    db.DATABASE_PATH = original_path
    db.DATABASE_URL = original_url
    if os.path.exists("test_history.db"):
        os.remove("test_history.db")


def test_authenticated_exam_links_to_user(client):
    """Test that exams are linked to authenticated users."""
    from app import db
    
    # Register and login
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "TestPass123!"
    })
    
    login_response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "TestPass123!"
    })
    user_id = login_response.json()["user"]["id"]
    
    # Start exam (authenticated)
    exam_response = client.post("/api/exams/start", json={
        "num_questions": 3
    })
    
    assert exam_response.status_code == 200
    exam_id = exam_response.json()["exam_id"]
    
    # Verify exam is linked to user in database
    with db.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM exams WHERE id = ?", (exam_id,))
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == user_id


def test_anonymous_exam_not_linked(client):
    """Test that anonymous exams are not linked to users."""
    from app import db
    
    # Start exam without authentication
    # Create new client without cookies
    from app.main import app
    anonymous_client = TestClient(app)
    
    exam_response = anonymous_client.post("/api/exams/start", json={
        "num_questions": 3
    })
    
    assert exam_response.status_code == 200
    exam_id = exam_response.json()["exam_id"]
    
    # Verify exam is NOT linked to user
    with db.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM exams WHERE id = ?", (exam_id,))
        result = cursor.fetchone()
        assert result is not None
        assert result[0] is None  # No user_id


def test_get_exam_history_empty(client):
    """Test getting exam history when user has no exams."""
    # Register and login
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "TestPass123!"
    })
    
    client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "TestPass123!"
    })
    
    # Get history
    response = client.get("/api/exams/history")
    
    assert response.status_code == 200
    data = response.json()
    assert data["exams"] == []
    assert data["total"] == 0


def test_get_exam_history_with_exams(client):
    """Test getting exam history with completed exams."""
    # Register and login
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "TestPass123!"
    })
    
    client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "TestPass123!"
    })
    
    # Take 3 exams
    exam_ids = []
    for i in range(3):
        # Start exam
        exam_response = client.post("/api/exams/start", json={
            "num_questions": 2
        })
        exam_data = exam_response.json()
        exam_id = exam_data["exam_id"]
        questions = exam_data["questions"]
        exam_ids.append(exam_id)
        
        # Submit exam
        answers = {str(q["id"]): 0 for q in questions}
        confidence = {str(q["id"]): 50 for q in questions}
        
        client.post(f"/api/exams/{exam_id}/submit", json={
            "answers": answers,
            "confidence": confidence
        })
    
    # Get history
    response = client.get("/api/exams/history")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["exams"]) == 3
    assert data["total"] == 3
    
    # Verify exam data
    for exam in data["exams"]:
        assert "id" in exam
        assert "created_at" in exam
        assert "completed_at" in exam
        assert "score" in exam
        assert "total_questions" in exam
        assert exam["total_questions"] == 2
        assert "percentage" in exam


def test_get_exam_history_pagination(client):
    """Test exam history pagination."""
    # Register and login
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "TestPass123!"
    })
    
    client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "TestPass123!"
    })
    
    # Take 5 exams
    for i in range(5):
        exam_response = client.post("/api/exams/start", json={
            "num_questions": 1
        })
        exam_data = exam_response.json()
        exam_id = exam_data["exam_id"]
        questions = exam_data["questions"]
        
        answers = {str(q["id"]): 0 for q in questions}
        confidence = {str(q["id"]): 50 for q in questions}
        
        client.post(f"/api/exams/{exam_id}/submit", json={
            "answers": answers,
            "confidence": confidence
        })
    
    # Get first 2 exams
    response = client.get("/api/exams/history?limit=2&offset=0")
    data = response.json()
    assert len(data["exams"]) == 2
    assert data["total"] == 5
    assert data["limit"] == 2
    assert data["offset"] == 0
    
    # Get next 2 exams
    response = client.get("/api/exams/history?limit=2&offset=2")
    data = response.json()
    assert len(data["exams"]) == 2
    assert data["total"] == 5
    assert data["offset"] == 2


def test_get_exam_history_requires_auth(client):
    """Test that exam history requires authentication."""
    # Try to get history without authentication
    from app.main import app
    anonymous_client = TestClient(app)
    
    response = anonymous_client.get("/api/exams/history")
    
    assert response.status_code == 401


def test_get_statistics_empty(client):
    """Test getting statistics when user has no completed exams."""
    # Register and login
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "TestPass123!"
    })
    
    client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "TestPass123!"
    })
    
    # Get statistics
    response = client.get("/api/exams/statistics")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_exams"] == 0
    assert data["total_questions"] == 0
    assert data["accuracy"] is None


def test_get_statistics_with_exams(client):
    """Test getting statistics with completed exams."""
    # Register and login
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "TestPass123!"
    })
    
    client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "TestPass123!"
    })
    
    # Take 2 exams
    for i in range(2):
        exam_response = client.post("/api/exams/start", json={
            "num_questions": 3
        })
        exam_data = exam_response.json()
        exam_id = exam_data["exam_id"]
        questions = exam_data["questions"]
        
        # Answer all with confidence
        answers = {str(q["id"]): 0 for q in questions}
        confidence = {str(q["id"]): 75 for q in questions}
        
        client.post(f"/api/exams/{exam_id}/submit", json={
            "answers": answers,
            "confidence": confidence
        })
    
    # Get statistics
    response = client.get("/api/exams/statistics")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_exams"] == 2
    assert data["total_questions"] == 6
    assert data["correct_answers"] >= 0
    assert data["accuracy"] is not None
    assert data["average_confidence"] is not None
    assert data["average_brier_score"] is not None
    assert data["average_bias_score"] is not None


def test_get_statistics_requires_auth(client):
    """Test that statistics require authentication."""
    # Try to get statistics without authentication
    from app.main import app
    anonymous_client = TestClient(app)
    
    response = anonymous_client.get("/api/exams/statistics")
    
    assert response.status_code == 401


def test_cross_user_exam_isolation(client):
    """Test that users can only see their own exams."""
    # Register and login as user 1
    client.post("/api/auth/register", json={
        "email": "user1@example.com",
        "password": "TestPass123!"
    })
    
    client.post("/api/auth/login", json={
        "email": "user1@example.com",
        "password": "TestPass123!"
    })
    
    # User 1 takes an exam
    exam_response = client.post("/api/exams/start", json={
        "num_questions": 2
    })
    exam_data = exam_response.json()
    exam_id = exam_data["exam_id"]
    questions = exam_data["questions"]
    
    answers = {str(q["id"]): 0 for q in questions}
    confidence = {str(q["id"]): 50 for q in questions}
    
    client.post(f"/api/exams/{exam_id}/submit", json={
        "answers": answers,
        "confidence": confidence
    })
    
    # User 1 sees their exam
    response = client.get("/api/exams/history")
    assert response.status_code == 200
    assert response.json()["total"] == 1
    
    # Logout user 1
    csrf_token = client.post("/api/auth/login", json={
        "email": "user1@example.com",
        "password": "TestPass123!"
    }).json()["csrf_token"]
    client.post("/api/auth/logout", headers={"X-CSRF-Token": csrf_token})
    
    # Register and login as user 2
    client.post("/api/auth/register", json={
        "email": "user2@example.com",
        "password": "TestPass123!"
    })
    
    client.post("/api/auth/login", json={
        "email": "user2@example.com",
        "password": "TestPass123!"
    })
    
    # User 2 should NOT see user 1's exams
    response = client.get("/api/exams/history")
    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_incomplete_exams_not_in_statistics(client):
    """Test that incomplete exams are not counted in statistics."""
    from app import db
    
    # Register and login
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "TestPass123!"
    })
    
    client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "TestPass123!"
    })
    
    # Start exam but don't complete it
    client.post("/api/exams/start", json={
        "num_questions": 2
    })
    
    # Start and complete another exam
    exam_response = client.post("/api/exams/start", json={
        "num_questions": 2
    })
    exam_data = exam_response.json()
    exam_id = exam_data["exam_id"]
    questions = exam_data["questions"]
    
    answers = {str(q["id"]): 0 for q in questions}
    confidence = {str(q["id"]): 50 for q in questions}
    
    client.post(f"/api/exams/{exam_id}/submit", json={
        "answers": answers,
        "confidence": confidence
    })
    
    # Get statistics - should only count completed exam
    response = client.get("/api/exams/statistics")
    data = response.json()
    assert data["total_exams"] == 1
    assert data["total_questions"] == 2


def test_get_exam_trends_empty(client):
    """Test getting trends with no completed exams."""
    # Register and login
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "TestPass123!"
    })
    
    client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "TestPass123!"
    })
    
    # Get trends
    response = client.get("/api/exams/trends")
    assert response.status_code == 200
    data = response.json()
    assert "trends" in data
    assert len(data["trends"]) == 0


def test_get_exam_trends_with_data(client):
    """Test getting trends with completed exams."""
    # Register and login
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "TestPass123!"
    })
    
    client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "TestPass123!"
    })
    
    # Complete 3 exams with different scores
    exam_ids = []
    for i in range(3):
        exam_response = client.post("/api/exams/start", json={
            "num_questions": 5
        })
        exam_data = exam_response.json()
        exam_id = exam_data["exam_id"]
        exam_ids.append(exam_id)
        questions = exam_data["questions"]
        
        # Answer with varying accuracy and confidence
        answers = {}
        confidence = {}
        for j, q in enumerate(questions):
            # First exam: all correct with high confidence
            # Second exam: some correct with medium confidence
            # Third exam: fewer correct with varying confidence
            if i == 0:
                answers[str(q["id"])] = 0  # Assume first option is correct for some
                confidence[str(q["id"])] = 80
            elif i == 1:
                answers[str(q["id"])] = 0 if j < 3 else 1
                confidence[str(q["id"])] = 60
            else:
                answers[str(q["id"])] = 0 if j < 2 else 1
                confidence[str(q["id"])] = 50 + (j * 10)
        
        client.post(f"/api/exams/{exam_id}/submit", json={
            "answers": answers,
            "confidence": confidence
        })
    
    # Get trends
    response = client.get("/api/exams/trends")
    assert response.status_code == 200
    data = response.json()
    
    # Verify structure
    assert "trends" in data
    assert len(data["trends"]) == 3
    
    # Verify each trend has required fields
    for i, trend in enumerate(data["trends"]):
        assert "exam_id" in trend
        assert "completed_at" in trend
        assert "exam_number" in trend
        assert trend["exam_number"] == i + 1  # Sequential numbering
        assert "accuracy" in trend
        assert "average_confidence" in trend
        assert "brier_score" in trend
        assert "bias_score" in trend
        assert "total_questions" in trend
        assert trend["total_questions"] == 5
        
        # Verify data types
        assert isinstance(trend["accuracy"], (int, float)) or trend["accuracy"] is None
        assert isinstance(trend["average_confidence"], (int, float)) or trend["average_confidence"] is None
        assert isinstance(trend["brier_score"], (int, float)) or trend["brier_score"] is None
        assert isinstance(trend["bias_score"], (int, float)) or trend["bias_score"] is None
    
    # Verify chronological order (first exam first)
    assert data["trends"][0]["exam_id"] == exam_ids[0]
    assert data["trends"][1]["exam_id"] == exam_ids[1]
    assert data["trends"][2]["exam_id"] == exam_ids[2]


def test_trends_requires_authentication(client):
    """Test that trends endpoint requires authentication."""
    response = client.get("/api/exams/trends")
    assert response.status_code == 401


def test_trends_cross_user_isolation(client):
    """Test that users only see their own trends."""
    # Register and login user 1
    client.post("/api/auth/register", json={
        "email": "user1@example.com",
        "password": "TestPass123!"
    })
    
    client.post("/api/auth/login", json={
        "email": "user1@example.com",
        "password": "TestPass123!"
    })
    
    # User 1 completes 2 exams
    for _ in range(2):
        exam_response = client.post("/api/exams/start", json={
            "num_questions": 3
        })
        exam_data = exam_response.json()
        exam_id = exam_data["exam_id"]
        questions = exam_data["questions"]
        
        answers = {str(q["id"]): 0 for q in questions}
        confidence = {str(q["id"]): 50 for q in questions}
        
        client.post(f"/api/exams/{exam_id}/submit", json={
            "answers": answers,
            "confidence": confidence
        })
    
    # Logout user 1
    csrf_response = client.get("/api/auth/csrf-token")
    csrf_token = csrf_response.json()["csrf_token"]
    client.post("/api/auth/logout", headers={"X-CSRF-Token": csrf_token})
    
    # Register and login user 2
    client.post("/api/auth/register", json={
        "email": "user2@example.com",
        "password": "TestPass123!"
    })
    
    client.post("/api/auth/login", json={
        "email": "user2@example.com",
        "password": "TestPass123!"
    })
    
    # User 2 should NOT see user 1's trends
    response = client.get("/api/exams/trends")
    assert response.status_code == 200
    data = response.json()
    assert len(data["trends"]) == 0


def test_trends_only_completed_exams(client):
    """Test that trends only include completed exams."""
    # Register and login
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "TestPass123!"
    })
    
    client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "TestPass123!"
    })
    
    # Start but don't complete an exam
    client.post("/api/exams/start", json={
        "num_questions": 3
    })
    
    # Start and complete another exam
    exam_response = client.post("/api/exams/start", json={
        "num_questions": 3
    })
    exam_data = exam_response.json()
    exam_id = exam_data["exam_id"]
    questions = exam_data["questions"]
    
    answers = {str(q["id"]): 0 for q in questions}
    confidence = {str(q["id"]): 50 for q in questions}
    
    client.post(f"/api/exams/{exam_id}/submit", json={
        "answers": answers,
        "confidence": confidence
    })
    
    # Get trends - should only include completed exam
    response = client.get("/api/exams/trends")
    data = response.json()
    assert len(data["trends"]) == 1
    assert data["trends"][0]["exam_id"] == exam_id
