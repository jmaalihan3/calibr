#!/usr/bin/env python3
"""
Test script for calibration feature.
Tests the complete flow: start exam -> submit with confidence -> verify Brier Score and Bias Score calculation.
"""

import requests
import json

API_BASE = "http://localhost:8000/api"

def test_calibration_flow():
    print("=" * 60)
    print("Testing Calibration Feature")
    print("=" * 60)
    
    # Step 1: Start exam
    print("\n1. Starting exam...")
    response = requests.post(f"{API_BASE}/exams/start", json={"num_questions": 5})
    assert response.status_code == 200, f"Failed to start exam: {response.status_code}"
    
    exam_data = response.json()
    exam_id = exam_data["exam_id"]
    questions = exam_data["questions"]
    
    print(f"   ✓ Exam started with ID: {exam_id}")
    print(f"   ✓ Loaded {len(questions)} questions")
    
    # Step 2: Prepare answers and confidence
    # Test scenario: Mix of confident/not confident and correct/incorrect
    # to verify Brier Score calculation
    print("\n2. Preparing answers with confidence...")
    
    answers = {}
    confidence = {}
    
    for i, question in enumerate(questions):
        q_id = str(question["id"])
        
        # Simulate different scenarios:
        if i == 0:
            # Confident and correct (good)
            answers[q_id] = question["options"].index(question["options"][0])  # Just pick first option
            confidence[q_id] = 1  # Confident
        elif i == 1:
            # Confident (assume we pick correct)
            answers[q_id] = 0
            confidence[q_id] = 1
        elif i == 2:
            # Not confident
            answers[q_id] = 0
            confidence[q_id] = 0
        elif i == 3:
            # Confident
            answers[q_id] = 1
            confidence[q_id] = 1
        else:
            # Not confident
            answers[q_id] = 1
            confidence[q_id] = 0
    
    print(f"   ✓ Prepared answers for {len(answers)} questions")
    print(f"   ✓ Prepared confidence for {len(confidence)} questions")
    
    # Step 3: Submit exam
    print("\n3. Submitting exam with confidence...")
    response = requests.post(
        f"{API_BASE}/exams/{exam_id}/submit",
        json={"answers": answers, "confidence": confidence}
    )
    
    assert response.status_code == 200, f"Failed to submit exam: {response.status_code}"
    
    results = response.json()
    
    print(f"   ✓ Exam submitted successfully")
    
    # Step 4: Verify results
    print("\n4. Verifying results...")
    print(f"   Score: {results['score']} / {results['total']} ({results['percentage']}%)")
    
    if "brier_score" in results and results["brier_score"] is not None:
        print(f"   ✓ Brier Score calculated: {results['brier_score']}")
        
        # Verify Brier Score is in valid range [0, 1]
        assert 0 <= results["brier_score"] <= 1, f"Invalid Brier Score: {results['brier_score']}"
        print(f"   ✓ Brier Score in valid range [0, 1]")
        
        # Interpret calibration
        if results["brier_score"] <= 0.20:
            calibration = "Excellent"
        elif results["brier_score"] <= 0.40:
            calibration = "Good"
        elif results["brier_score"] <= 0.60:
            calibration = "Poor"
        else:
            calibration = "Very poor"
        
        print(f"   ✓ Calibration quality: {calibration}")
    else:
        print("   ✗ Brier Score not found in results!")
        return False
    
    # Step 5: Verify individual question results
    print("\n5. Verifying individual question results...")
    for i, result in enumerate(results["results"]):
        assert "confidence" in result, f"Question {i+1} missing confidence"
        assert "calibrated" in result, f"Question {i+1} missing calibrated flag"
        
        conf_label = "Confident" if result["confidence"] == 1 else "Not Confident"
        cal_label = "Match" if result["calibrated"] else "Mismatch"
        correct_label = "✓" if result["is_correct"] else "✗"
        
        print(f"   Q{i+1}: {correct_label} {conf_label} → {cal_label}")
    
    print(f"\n   ✓ All {len(results['results'])} questions have confidence and calibration data")
    
    # Step 6: Manually verify Brier Score calculation
    print("\n6. Manually verifying Brier Score calculation...")
    manual_brier_sum = 0.0
    for result in results["results"]:
        conf = result["confidence"]  # 0 or 1
        correctness = 1 if result["is_correct"] else 0
        brier_contribution = (conf - correctness) ** 2
        manual_brier_sum += brier_contribution
    
    manual_brier = manual_brier_sum / len(results["results"])
    calculated_brier = results["brier_score"]
    
    print(f"   Manual calculation: {manual_brier:.3f}")
    print(f"   API calculation: {calculated_brier:.3f}")
    
    # Allow small floating point difference
    assert abs(manual_brier - calculated_brier) < 0.001, \
        f"Brier Score mismatch: {manual_brier} != {calculated_brier}"
    
    print("   ✓ Brier Score calculation verified!")
    
    # Step 7: Manually verify Bias Score calculation
    print("\n7. Manually verifying Bias Score calculation...")
    
    if "bias_score" in results and results["bias_score"] is not None:
        manual_bias_sum = 0.0
        for result in results["results"]:
            conf = result["confidence"]  # 0 or 1
            correctness = 1 if result["is_correct"] else 0
            bias_contribution = conf - correctness  # Note: NOT squared
            manual_bias_sum += bias_contribution
        
        manual_bias = manual_bias_sum / len(results["results"])
        calculated_bias = results["bias_score"]
        
        print(f"   Manual calculation: {manual_bias:+.3f}")
        print(f"   API calculation: {calculated_bias:+.3f}")
        
        # Allow small floating point difference
        assert abs(manual_bias - calculated_bias) < 0.001, \
            f"Bias Score mismatch: {manual_bias} != {calculated_bias}"
        
        print("   ✓ Bias Score calculation verified!")
        
        # Verify Bias Score is in valid range [-1, 1]
        assert -1 <= results["bias_score"] <= 1, f"Invalid Bias Score: {results['bias_score']}"
        print(f"   ✓ Bias Score in valid range [-1, 1]")
        
        # Interpret bias
        if calculated_bias > 0.1:
            print(f"   → User is overconfident (bias = {calculated_bias:+.3f})")
        elif calculated_bias < -0.1:
            print(f"   → User is underconfident (bias = {calculated_bias:+.3f})")
        else:
            print(f"   → User is well-calibrated (bias = {calculated_bias:+.3f})")
    else:
        print("   ✗ Bias Score not found in results!")
        return False
    
    # Step 8: Test retrieval of results
    print("\n8. Testing results retrieval...")
    response = requests.get(f"{API_BASE}/exams/{exam_id}/results")
    assert response.status_code == 200, f"Failed to retrieve results: {response.status_code}"
    
    retrieved_results = response.json()
    assert retrieved_results["brier_score"] == results["brier_score"], \
        "Brier Score changed after retrieval"
    assert retrieved_results["bias_score"] == results["bias_score"], \
        "Bias Score changed after retrieval"
    
    print("   ✓ Results retrieved successfully with Brier Score and Bias Score")
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        test_calibration_flow()
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
