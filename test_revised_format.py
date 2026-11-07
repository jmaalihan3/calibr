#!/usr/bin/env python3
"""
Test script for the revised exam format implementation.

This script:
1. Starts an exam via the API
2. Submits answers (some correct, some incorrect)
3. Retrieves results
4. Verifies that the new format fields are present
"""

import requests
import json
import sys

API_BASE = "http://localhost:8000/api"

def test_revised_format():
    """Test the complete workflow with the revised format."""
    
    print("=" * 60)
    print("REVISED EXAM FORMAT TEST")
    print("=" * 60)
    print()
    
    # Step 1: Start exam
    print("1. Starting exam with 3 questions...")
    start_response = requests.post(
        f"{API_BASE}/exams/start",
        json={"num_questions": 3}
    )
    
    if start_response.status_code != 200:
        print(f"❌ Failed to start exam: {start_response.status_code}")
        return False
    
    start_data = start_response.json()
    exam_id = start_data["exam_id"]
    questions = start_data["questions"]
    
    print(f"   ✓ Exam started (ID: {exam_id})")
    print(f"   ✓ Received {len(questions)} questions")
    print()
    
    # Step 2: Verify questions have new format
    print("2. Verifying question format...")
    for i, q in enumerate(questions, 1):
        has_choices = "choices" in q and q["choices"] is not None
        has_review = "review" in q and q["review"] is not None
        
        if has_choices:
            print(f"   ✓ Question {i} has 'choices' array")
            # Verify choice structure
            for j, choice in enumerate(q["choices"]):
                required_fields = ["id", "text", "is_correct", "explanation"]
                missing = [f for f in required_fields if f not in choice]
                if missing:
                    print(f"      ⚠ Choice {j} missing fields: {missing}")
                else:
                    # Check for misconception_id on incorrect choices
                    if not choice["is_correct"]:
                        if "misconception_id" in choice:
                            print(f"      ✓ Incorrect choice has misconception_id: {choice['misconception_id']}")
        else:
            print(f"   ⚠ Question {i} missing 'choices' field")
        
        if has_review:
            print(f"   ✓ Question {i} has 'review' metadata")
            if "title" in q["review"]:
                print(f"      - Title: {q['review']['title']}")
        else:
            print(f"   ⚠ Question {i} missing 'review' field")
    
    print()
    
    # Step 3: Submit answers (mix of correct and incorrect)
    print("3. Submitting answers...")
    
    # Prepare answers: first question correct (if we can determine), others incorrect
    answers = {}
    confidence = {}
    
    for q in questions:
        q_id = str(q["id"])
        if "choices" in q and q["choices"]:
            # Find the correct answer
            correct_idx = next((i for i, c in enumerate(q["choices"]) if c["is_correct"]), 0)
            # Answer first question correctly, others incorrectly
            answers[q_id] = correct_idx if q == questions[0] else (correct_idx + 1) % len(q["choices"])
            confidence[q_id] = 80 if q == questions[0] else 60
        else:
            # Fallback for old format
            answers[q_id] = 0
            confidence[q_id] = 50
    
    submit_response = requests.post(
        f"{API_BASE}/exams/{exam_id}/submit",
        json={"answers": answers, "confidence": confidence}
    )
    
    if submit_response.status_code != 200:
        print(f"❌ Failed to submit exam: {submit_response.status_code}")
        return False
    
    results_data = submit_response.json()
    print(f"   ✓ Exam submitted")
    print(f"   ✓ Score: {results_data['score']}/{results_data['total']} ({results_data['percentage']}%)")
    print()
    
    # Step 4: Verify results format
    print("4. Verifying results format...")
    results = results_data["results"]
    
    for i, result in enumerate(results, 1):
        has_choices = "choices" in result and result["choices"] is not None
        has_review = "review" in result and result["review"] is not None
        
        print(f"   Question {i}:")
        print(f"      - Correct: {result['is_correct']}")
        
        if has_choices:
            print(f"      ✓ Has 'choices' array with {len(result['choices'])} choices")
            
            # If incorrect, verify misconception is available
            if not result["is_correct"] and result["user_answer"] is not None:
                user_choice = result["choices"][result["user_answer"]]
                if "misconception_id" in user_choice:
                    print(f"      ✓ Misconception available: {user_choice['misconception_id']}")
                    print(f"        '{user_choice['explanation'][:60]}...'")
                else:
                    print(f"      ⚠ No misconception for incorrect answer")
        else:
            print(f"      ⚠ Missing 'choices' field")
        
        if has_review:
            print(f"      ✓ Has 'review' metadata")
            if "title" in result["review"]:
                print(f"        Title: '{result['review']['title']}'")
        else:
            print(f"      ⚠ Missing 'review' field")
    
    print()
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    all_have_choices = all("choices" in r and r["choices"] for r in results)
    all_have_review = all("review" in r and r["review"] for r in results)
    
    if all_have_choices and all_have_review:
        print("✅ All questions have the revised format!")
        print()
        print("Next steps:")
        print("1. Open http://localhost:8000 in your browser")
        print("2. Take an exam")
        print("3. Verify the expandable question cards in results")
        print("4. Check that misconceptions show only for incorrect answers")
        return True
    else:
        print("⚠️  Some questions missing new format fields")
        if not all_have_choices:
            print("   - Missing 'choices' in some results")
        if not all_have_review:
            print("   - Missing 'review' in some results")
        print()
        print("Possible issues:")
        print("1. Database not updated with revised format")
        print("2. Run: python load_revised_exam.py statcal_categorical_data_unit_1_exam_structured.md")
        return False


if __name__ == "__main__":
    try:
        success = test_revised_format()
        sys.exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server at http://localhost:8000")
        print("Please start the server with: uvicorn app.main:app --reload --port 8000")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
