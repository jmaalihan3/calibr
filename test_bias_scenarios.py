#!/usr/bin/env python3
"""
Test bias score with various confidence patterns.
"""

import requests
import json

API_BASE = "http://localhost:8000/api"

def test_scenario(name, confidence_pattern, description):
    """Test a specific confidence pattern scenario."""
    print(f"\n{'='*60}")
    print(f"Scenario: {name}")
    print(f"Description: {description}")
    print('='*60)
    
    # Start exam
    response = requests.post(f"{API_BASE}/exams/start", json={"num_questions": 5})
    exam_data = response.json()
    exam_id = exam_data["exam_id"]
    questions = exam_data["questions"]
    
    # Prepare answers (just pick first option for all)
    answers = {}
    confidence = {}
    
    for i, question in enumerate(questions):
        q_id = str(question["id"])
        answers[q_id] = 0  # Always pick first option
        confidence[q_id] = confidence_pattern[i]
    
    # Submit exam
    response = requests.post(
        f"{API_BASE}/exams/{exam_id}/submit",
        json={"answers": answers, "confidence": confidence}
    )
    
    results = response.json()
    
    # Display results
    print(f"\nScore: {results['score']} / {results['total']} ({results['percentage']}%)")
    print(f"Brier Score: {results['brier_score']:.3f}")
    print(f"Bias Score: {results['bias_score']:+.3f}")
    
    # Interpret bias
    bias = results['bias_score']
    if abs(bias) <= 0.10:
        interpretation = "Well-calibrated ⚖️"
    elif bias > 0.10:
        if bias <= 0.30:
            interpretation = "Slightly overconfident 📈"
        else:
            interpretation = "Overconfident 📈"
    else:
        if bias >= -0.30:
            interpretation = "Slightly underconfident 📉"
        else:
            interpretation = "Underconfident 📉"
    
    print(f"Interpretation: {interpretation}")
    
    # Show individual questions
    print(f"\nQuestion breakdown:")
    for i, result in enumerate(results["results"]):
        conf_label = "Confident" if result["confidence"] == 1 else "Not Confident"
        correct_label = "✓" if result["is_correct"] else "✗"
        print(f"  Q{i+1}: {correct_label} {conf_label}")

def main():
    print("\n" + "="*60)
    print("Testing Bias Score with Different Confidence Patterns")
    print("="*60)
    
    # Scenario 1: Always confident (likely overconfident unless perfect score)
    test_scenario(
        "Always Confident",
        [1, 1, 1, 1, 1],
        "User is confident on all questions"
    )
    
    # Scenario 2: Never confident (likely underconfident unless all wrong)
    test_scenario(
        "Never Confident",
        [0, 0, 0, 0, 0],
        "User is not confident on any question"
    )
    
    # Scenario 3: Alternating confidence
    test_scenario(
        "Alternating Confidence",
        [1, 0, 1, 0, 1],
        "User alternates between confident and not confident"
    )
    
    # Scenario 4: Mostly confident
    test_scenario(
        "Mostly Confident",
        [1, 1, 1, 1, 0],
        "User is confident on 4 out of 5 questions"
    )
    
    # Scenario 5: Mostly not confident
    test_scenario(
        "Mostly Not Confident",
        [0, 0, 0, 0, 1],
        "User is not confident on 4 out of 5 questions"
    )
    
    print("\n" + "="*60)
    print("✓ All scenarios tested successfully!")
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
