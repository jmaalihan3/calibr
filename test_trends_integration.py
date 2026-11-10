#!/usr/bin/env python
"""
Integration test for longitudinal tracking charts.
Tests the complete workflow from registration to viewing trends.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_trends_workflow():
    """Test complete trends workflow."""
    print("🧪 Testing Longitudinal Tracking Charts Integration\n")
    
    # 1. Register a test user
    print("1️⃣  Registering user...")
    email = f"test_trends_{int(time.time())}@example.com"
    password = "TestPass123!"
    
    register_response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={"email": email, "password": password}
    )
    assert register_response.status_code == 201, f"Registration failed with status {register_response.status_code}: {register_response.text}"
    print(f"   ✅ User registered: {email}")
    
    # 2. Login
    print("\n2️⃣  Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": email, "password": password}
    )
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    cookies = login_response.cookies
    user = login_response.json()["user"]
    print(f"   ✅ Logged in as: {user['email']}")
    
    # 3. Take multiple exams with different performance levels
    print("\n3️⃣  Taking exams...")
    exam_ids = []
    
    for i in range(3):
        # Start exam
        exam_response = requests.post(
            f"{BASE_URL}/api/exams/start",
            json={"num_questions": 5},
            cookies=cookies
        )
        assert exam_response.status_code == 200, f"Start exam failed: {exam_response.text}"
        exam_data = exam_response.json()
        exam_id = exam_data["exam_id"]
        questions = exam_data["questions"]
        exam_ids.append(exam_id)
        
        # Submit answers with varying confidence and accuracy
        answers = {}
        confidence = {}
        for j, q in enumerate(questions):
            # Simulate different performance patterns
            if i == 0:  # First exam: high accuracy, high confidence
                answers[str(q["id"])] = 0
                confidence[str(q["id"])] = 85
            elif i == 1:  # Second exam: medium accuracy, medium confidence
                answers[str(q["id"])] = 0 if j < 3 else 1
                confidence[str(q["id"])] = 65
            else:  # Third exam: lower accuracy, varying confidence
                answers[str(q["id"])] = 0 if j < 2 else 1
                confidence[str(q["id"])] = 50 + (j * 5)
        
        submit_response = requests.post(
            f"{BASE_URL}/api/exams/{exam_id}/submit",
            json={"answers": answers, "confidence": confidence},
            cookies=cookies
        )
        assert submit_response.status_code == 200, f"Submit exam failed: {submit_response.text}"
        results = submit_response.json()
        print(f"   ✅ Exam {i+1}: Score {results['score']}/{results['total']} ({results['percentage']:.1f}%)")
    
    # 4. Get trends data
    print("\n4️⃣  Fetching trends data...")
    trends_response = requests.get(
        f"{BASE_URL}/api/exams/trends",
        cookies=cookies
    )
    assert trends_response.status_code == 200, f"Get trends failed: {trends_response.text}"
    trends_data = trends_response.json()
    
    # 5. Verify trends data structure
    print("\n5️⃣  Validating trends data...")
    assert "trends" in trends_data, "Missing 'trends' key"
    trends = trends_data["trends"]
    assert len(trends) == 3, f"Expected 3 trends, got {len(trends)}"
    print(f"   ✅ Found {len(trends)} exam trends")
    
    # Verify each trend
    for i, trend in enumerate(trends):
        print(f"\n   📊 Exam {i+1} Trend:")
        assert trend["exam_id"] == exam_ids[i], "Wrong exam order"
        assert trend["exam_number"] == i + 1, "Wrong exam number"
        assert trend["total_questions"] == 5, "Wrong question count"
        
        # Check all metrics exist
        assert "accuracy" in trend, "Missing accuracy"
        assert "average_confidence" in trend, "Missing average_confidence"
        assert "brier_score" in trend, "Missing brier_score"
        assert "bias_score" in trend, "Missing bias_score"
        assert "completed_at" in trend, "Missing completed_at"
        
        print(f"      Accuracy: {trend['accuracy']:.1f}%")
        print(f"      Confidence: {trend['average_confidence']:.1f}%")
        print(f"      Brier Score: {trend['brier_score']:.3f}")
        print(f"      Bias Score: {trend['bias_score']:.3f}")
        print(f"      ✅ Trend {i+1} valid")
    
    # 6. Test statistics endpoint (should still work)
    print("\n6️⃣  Verifying statistics endpoint...")
    stats_response = requests.get(
        f"{BASE_URL}/api/exams/statistics",
        cookies=cookies
    )
    assert stats_response.status_code == 200, f"Get statistics failed: {stats_response.text}"
    stats = stats_response.json()
    assert stats["total_exams"] == 3, f"Expected 3 exams in stats, got {stats['total_exams']}"
    print(f"   ✅ Statistics endpoint working")
    print(f"      Total Exams: {stats['total_exams']}")
    print(f"      Overall Accuracy: {stats['accuracy']:.1f}%")
    print(f"      Overall Brier Score: {stats['average_brier_score']:.3f}")
    
    print("\n✨ All tests passed! Longitudinal tracking charts are working correctly.\n")
    return True


if __name__ == "__main__":
    try:
        test_trends_workflow()
        print("🎉 Integration test completed successfully!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
