# Calibration Feature Implementation Proposal

## Overview
Implement confidence tracking and Brier Score calculation to measure user calibration - how well users can judge their own knowledge.

## What is Calibration?
**Calibration** measures whether users accurately assess their confidence in their answers. A well-calibrated user:
- Says "confident" mostly when they're correct
- Says "not confident" mostly when they're incorrect

**Brier Score** quantifies calibration on a scale of 0 to 1:
- **0 = Perfect calibration** (always confident when correct, never when incorrect)
- **1 = Worst calibration** (always confident when incorrect, never when correct)
- **0.25 = Random guessing**

Formula: `Brier Score = (1/N) * Σ(f_i - o_i)²`
- f_i = confidence (Agree=1, Disagree=0)
- o_i = correctness (Correct=1, Incorrect=0)
- N = number of questions

## User Flow Changes

### Current Flow
```
1. Question → 2. Select Answer → 3. Next Question → ... → 5. Submit → 6. Results
```

### Proposed Flow with Calibration
```
1. Question → 2. Select Answer → 3. Confidence Prompt → 4. Record Confidence → 
5. Next Question → ... → Submit → Results with Brier Score
```

## Implementation Design

### Database Schema Changes

#### Option 1: Add to exam_answers table (Recommended)
```sql
ALTER TABLE exam_answers ADD COLUMN confidence INTEGER;  -- 1 = Agree, 0 = Disagree, NULL = not answered
```

**Pros:**
- Data lives with the answer (single source of truth)
- Simple queries (JOIN exam_answers to get everything)
- Easy to add/remove feature

**Cons:**
- Modifies existing table structure
- Need migration for existing records

#### Option 2: Separate calibration table
```sql
CREATE TABLE question_confidence (
    id INTEGER PRIMARY KEY,
    exam_id INTEGER,
    question_id INTEGER,
    confidence INTEGER,  -- 1 or 0
    FOREIGN KEY (exam_id) REFERENCES exams(id)
);
```

**Pros:**
- Doesn't modify existing schema
- Can be dropped if feature removed

**Cons:**
- Additional JOIN needed for queries
- More complex data model

**Recommendation**: Option 1 (add column). Simpler, confidence is conceptually part of the answer.

### Frontend Changes

#### 1. New Confidence Prompt UI
After user selects an answer, show:

```
┌─────────────────────────────────────────────┐
│  You selected: B) It is multiplied by c     │
│                                             │
│  I am confident in my answer to this       │
│  question                                   │
│                                             │
│  [ Agree ]    [ Disagree ]                 │
│                                             │
│  Question 2 of 5 (Unit 3)                  │
└─────────────────────────────────────────────┘
```

#### 2. State Management Updates (app.js)
```javascript
const state = {
    examId: null,
    questions: [],
    currentQuestionIndex: 0,
    userAnswers: {},        // existing
    userConfidence: {}      // NEW: questionId -> 1/0
};
```

#### 3. Workflow Changes
```javascript
// Current: answer → next question
// New: answer → confidence prompt → next question

function selectOption(index) {
    // Save answer
    state.userAnswers[questionId] = index;
    
    // Show confidence prompt
    showConfidencePrompt();
}

function recordConfidence(isConfident) {
    // Save confidence (1 or 0)
    state.userConfidence[questionId] = isConfident ? 1 : 0;
    
    // Move to next question
    nextQuestion();
}
```

#### 4. Results Display Enhancement
Add Brier Score section:

```
┌─────────────────────────────────────┐
│     Overall: 4 / 5 (80%)            │
│     Calibration Score: 0.20         │
│     (Lower is better, 0 = perfect)  │
└─────────────────────────────────────┘

╔═══════════════════════════════════════════════════════════╗
║ Unit 3: SUMMARIZING QUANTITATIVE DATA      2 / 2 correct  ║
╚═══════════════════════════════════════════════════════════╝
│ #  │ Question  │ Your Answer │ Confident? │ Result │ Match │
├────┼───────────┼─────────────┼────────────┼────────┼───────┤
│ 1  │ Which...  │ B           │ ✓ Agree    │ ✓      │ ✓     │
│ 2  │ If every..│ B           │ ✗ Disagree │ ✓      │ ✗     │
```

New columns:
- **Confident?**: Shows Agree/Disagree
- **Match**: ✓ if (confident AND correct) OR (not confident AND incorrect)
               ✗ if (confident AND incorrect) OR (not confident AND correct)

### Backend Changes

#### 1. API Request Model Update (routers/exams.py)
```python
class SubmitExamRequest(BaseModel):
    answers: Dict[str, int]
    confidence: Dict[str, int]  # NEW: questionId -> 1/0
```

#### 2. Database Layer (db.py)
```python
def save_exam_answers(exam_id: int, answers: Dict[int, int], confidence: Dict[int, int]):
    """
    Save answers and confidence levels.
    
    Args:
        exam_id: Exam ID
        answers: questionId -> answerIndex
        confidence: questionId -> 1 (Agree) or 0 (Disagree)
    """
    with get_db() as conn:
        cursor = conn.cursor()
        for question_id, user_answer in answers.items():
            conf = confidence.get(question_id)
            cursor.execute(
                "INSERT INTO exam_answers (exam_id, question_id, user_answer, confidence) VALUES (?, ?, ?, ?)",
                (exam_id, question_id, user_answer, conf)
            )
```

#### 3. Business Logic (services.py)
```python
def calculate_brier_score(results: List[Dict], confidence: Dict[int, int]) -> float:
    """
    Calculate Brier Score for calibration.
    
    Formula: (1/N) * Σ(f_i - o_i)²
    where f_i = confidence (1 or 0), o_i = correctness (1 or 0)
    
    Args:
        results: List of question results with is_correct
        confidence: questionId -> confidence level (1 or 0)
    
    Returns:
        Brier Score (0-1, lower is better)
    """
    if not results:
        return 0.0
    
    total_squared_diff = 0
    count = 0
    
    for result in results:
        qid = result['question_id']
        
        # Skip if no confidence recorded
        if qid not in confidence:
            continue
        
        f_i = confidence[qid]  # 1 or 0
        o_i = 1 if result['is_correct'] else 0
        
        squared_diff = (f_i - o_i) ** 2
        total_squared_diff += squared_diff
        count += 1
    
    if count == 0:
        return 0.0
    
    return total_squared_diff / count


def submit_exam(exam_id: int, answers: Dict[str, int], confidence: Dict[str, int]) -> Dict:
    """
    Process exam submission with confidence tracking.
    """
    # Convert keys to integers
    int_answers = {int(k): v for k, v in answers.items()}
    int_confidence = {int(k): v for k, v in confidence.items()}
    
    # Save answers with confidence
    db.save_exam_answers(exam_id, int_answers, int_confidence)
    
    # Get exam data and calculate score
    exam_data = db.get_exam_with_answers(exam_id)
    score, results = calculate_score(exam_data)
    
    # Calculate Brier Score
    brier_score = calculate_brier_score(results, int_confidence)
    
    # Update exam record
    db.update_exam_score(exam_id, score)
    
    return {
        "score": score,
        "total": len(results),
        "percentage": round((score / len(results) * 100), 2),
        "brier_score": round(brier_score, 3),
        "results": results
    }
```

## UI/UX Considerations

### Confidence Prompt Design

**Option A: Modal/Overlay (Recommended)**
- Appears after answer selection
- Blocks navigation until answered
- Clear focus on single decision
- Better for deliberate thinking

**Option B: Inline Below Options**
- Always visible
- Doesn't interrupt flow
- Risk: users might skip/ignore

**Recommendation**: Modal overlay. Forces deliberate calibration judgment.

### Confidence Wording

**Current**: "I am confident in my answer to this question"
- **Pro**: Clear, straightforward
- **Con**: Might bias toward "Agree" (people want to seem confident)

**Alternative**: "How confident are you in your answer?"
- **Pro**: More neutral
- **Con**: Requires 3+ options (Very/Somewhat/Not)

**Recommendation**: Keep binary (Agree/Disagree) for simplicity and clearer Brier Score calculation.

### Results Display

**Brier Score Interpretation Help:**
```
Your Calibration Score: 0.20

What does this mean?
• 0.00 = Perfect calibration
• 0.20 = Good calibration (you know when you know)
• 0.50 = Poor calibration (confidence doesn't match performance)
• 1.00 = Inverse calibration (confident when wrong, uncertain when right)

[Learn more about calibration]
```

## Implementation Plan

### Phase 1: Backend Foundation
1. Add `confidence` column to `exam_answers` table
2. Update `save_exam_answers()` to accept confidence parameter
3. Implement `calculate_brier_score()` function
4. Update `submit_exam()` to calculate and return Brier Score
5. Write tests for Brier Score calculation

### Phase 2: API Layer
1. Update `SubmitExamRequest` to include confidence field
2. Modify submit endpoint to pass confidence to services
3. Ensure API returns Brier Score in response
4. Test API with confidence data

### Phase 3: Frontend - Confidence Capture
1. Add confidence prompt UI (modal overlay)
2. Update state management to track confidence
3. Modify answer selection flow to show confidence prompt
4. Store confidence alongside answers
5. Send confidence data in submit request

### Phase 4: Frontend - Results Display
1. Display Brier Score in results summary
2. Add "Confident?" column to results table
3. Add "Match" indicator (confidence aligned with correctness)
4. Add interpretation guide for Brier Score
5. Style confidence indicators

### Phase 5: Testing & Polish
1. Test complete flow with various scenarios
2. Validate Brier Score calculations
3. Edge cases (skipped confidence, all confident, none confident)
4. Mobile responsiveness
5. Accessibility (keyboard navigation)

## Example Scenarios

### Scenario 1: Well-Calibrated User
```
Q1: Correct, Confident (1)    → (1-1)² = 0
Q2: Correct, Confident (1)    → (1-1)² = 0
Q3: Incorrect, Not Confident  → (0-0)² = 0
Q4: Correct, Not Confident    → (0-1)² = 1
Q5: Incorrect, Confident      → (1-0)² = 1

Brier Score = (0+0+0+1+1)/5 = 0.40
```

### Scenario 2: Poorly-Calibrated User (Overconfident)
```
Q1: Correct, Confident        → (1-1)² = 0
Q2: Incorrect, Confident      → (1-0)² = 1
Q3: Incorrect, Confident      → (1-0)² = 1
Q4: Correct, Confident        → (1-1)² = 0
Q5: Incorrect, Confident      → (1-0)² = 1

Brier Score = (0+1+1+0+1)/5 = 0.60 (poor calibration)
```

### Scenario 3: Perfectly-Calibrated User
```
Q1: Correct, Confident        → (1-1)² = 0
Q2: Correct, Confident        → (1-1)² = 0
Q3: Incorrect, Not Confident  → (0-0)² = 0
Q4: Incorrect, Not Confident  → (0-0)² = 0
Q5: Correct, Confident        → (1-1)² = 0

Brier Score = 0/5 = 0.00 (perfect!)
```

## Design Decisions

### Decision 1: When to Prompt for Confidence
**Chosen**: After answer selection, before next question

**Pros:**
- Fresh in user's mind
- Can't revise answer after reflecting on confidence
- Natural workflow

**Cons:**
- Adds step to each question
- Slight friction

**Alternative**: All confidence questions at end
- Pro: Smoother exam flow
- Con: Memory decay, less accurate

### Decision 2: Binary vs Multi-Level Confidence
**Chosen**: Binary (Agree/Disagree)

**Pros:**
- Simpler decision
- Cleaner Brier Score (0 or 1 inputs)
- Faster to answer

**Cons:**
- Less granular
- Doesn't capture "somewhat confident"

**Alternative**: 3-level (Very/Somewhat/Not) or 5-level scale
- Pro: More nuanced
- Con: Takes longer, harder to interpret

### Decision 3: Required vs Optional Confidence
**Chosen**: Required (must answer to proceed)

**Pros:**
- Complete data for Brier Score
- Forces reflection on knowledge

**Cons:**
- Adds friction
- Some users might resent it

**Alternative**: Optional with default
- Pro: Less friction
- Con: Missing data reduces calibration accuracy

## Potential Issues & Mitigations

**Issue 1: Survey Fatigue**
- Risk: Users get tired of confidence questions on every question
- Mitigation: Keep prompt simple, clear, fast (2 big buttons)
- Future: Make confidence tracking optional (checkbox on start page)

**Issue 2: Strategic Gaming**
- Risk: Users learn to game the system (always say "not confident")
- Mitigation: Educational framing - "This helps you learn, not graded"
- Future: Track calibration over time, show improvement

**Issue 3: Interpretation Confusion**
- Risk: Users don't understand what Brier Score means
- Mitigation: Clear explanation with examples
- Future: Use plain language ("Good calibration" vs "0.20")

**Issue 4: Mobile UX**
- Risk: Modal overlay might be awkward on small screens
- Mitigation: Responsive design, large tap targets
- Future: Consider inline prompt for mobile

**Issue 5: Incomplete Submissions**
- Risk: User refreshes page during confidence prompt
- Mitigation: Store in localStorage as backup
- Future: Auto-save confidence as answered

## Success Metrics

After implementation:
1. ✅ Users can indicate confidence after each question
2. ✅ Confidence data stored in database
3. ✅ Brier Score calculated correctly
4. ✅ Results show Brier Score and interpretation
5. ✅ Results table shows confidence for each question
6. ✅ Users understand what calibration means

## Open Questions

1. Should we show Brier Score for individual units or just overall?
2. Should we store historical Brier Scores to show trends?
3. Should confidence be optional or required?
4. Should we allow users to change their confidence before submitting?
5. Should we show calibration curve (confidence vs accuracy)?

## Next Steps

1. Review this proposal with stakeholders
2. Decide on optional vs required confidence
3. Choose interpretation guide wording
4. Begin Phase 1 implementation (database schema)
5. Create tests for Brier Score calculation
