# Phase 3 Complete: Longitudinal Tracking Charts ✅

**Date:** November 9, 2026  
**Status:** ✅ Complete and Tested

---

## Summary

Phase 3 implements longitudinal tracking with interactive charts showing performance and calibration trends over time. Users can now visualize how their accuracy, confidence, Brier score, and calibration bias change across completed assessments.

### Key Features Implemented

✅ **Time-Series API Endpoint:** `/api/exams/trends` returns per-exam statistics  
✅ **Performance Charts:** Line charts showing accuracy and confidence over time  
✅ **Calibration Charts:** Dual-axis charts for Brier score and calibration bias  
✅ **Chart Toggle:** Switch between performance and calibration views  
✅ **Chart Explanations:** Inline tooltips explaining metrics  
✅ **Responsive Design:** Charts adapt to mobile and desktop screens  
✅ **Minimum Data Check:** Charts only display with 2+ completed exams  

---

## What Changed

### Backend Changes (3 files)

**1. `app/db.py`** - Added:
   - `get_user_exam_trends()` - Calculate per-exam statistics chronologically
   - Returns list of trends with accuracy, confidence, Brier score, bias for each exam
   - Properly orders by completion date and assigns sequential exam numbers

**2. `app/services.py`** - Added:
   - `get_user_exam_trends()` - Service layer wrapper for trends endpoint

**3. `app/routers/exams.py`** - Added:
   - `GET /api/exams/trends` - API endpoint for time-series data
   - Requires authentication
   - Returns chronologically ordered per-exam statistics

### Frontend Changes (3 files)

**1. `frontend/index.html`** - Added:
   - Chart.js library (CDN: Chart.js v4.4.0)
   - Performance History section with chart containers
   - Toggle buttons for switching between charts
   - Chart explanation text for metrics

**2. `frontend/styles.css`** - Added:
   - `.performance-history` - Chart section styling
   - `.chart-container` - Chart canvas container (400px height)
   - `.chart-toggle` - Toggle button styling
   - `.chart-explanation` - Metric explanation text styling
   - Responsive styles for mobile (300px height, stacked toggle)

**3. `frontend/app.js`** - Added:
   - `loadPerformanceCharts()` - Fetch trends and render both charts
   - `setupChartToggle()` - Handle chart view switching
   - `renderPerformanceChart()` - Create accuracy/confidence line chart
   - `renderCalibrationChart()` - Create Brier/bias dual-axis chart
   - Modified `showHistory()` to load charts automatically

### Test Changes (1 file)

**4. `tests/test_exam_history.py`** - Added 5 new tests:
   - `test_get_exam_trends_empty` - Empty trends for new users
   - `test_get_exam_trends_with_data` - Verify trend structure and ordering
   - `test_trends_requires_authentication` - Auth requirement
   - `test_trends_cross_user_isolation` - Users see only their trends
   - `test_trends_only_completed_exams` - Excludes incomplete exams

---

## API Endpoint

### GET /api/exams/trends

Get per-exam statistics for longitudinal tracking.

**Authentication:** Required

**Response:**
```json
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
```

**Ordering:** Chronological by completion date (oldest first)

**Status codes:**
- `200`: Success
- `401`: Not authenticated
- `500`: Server error

---

## Chart Implementations

### Performance Chart

**Type:** Line chart with dual datasets

**Metrics:**
- **Answer Accuracy** (green line): Percentage correct per exam
- **Average Confidence** (blue line): Mean confidence per exam

**Y-axis:** 0-100%  
**X-axis:** Exam number (Exam 1, Exam 2, ...)

**Features:**
- Filled area under lines (10% opacity)
- Smooth curves (tension: 0.3)
- Interactive tooltips with exact values
- Dark theme compatible colors

### Calibration Chart

**Type:** Line chart with dual y-axes

**Metrics:**
- **Brier Score** (orange line, left axis): 0-0.5 scale
- **Calibration Bias** (purple line, right axis): -0.5 to 0.5 scale

**X-axis:** Exam number (Exam 1, Exam 2, ...)

**Features:**
- Independent y-axes for different scales
- Colored axis labels matching line colors
- Explanatory tooltip showing metric meanings
- Proper handling of positive/negative bias values

### Chart Toggle

**Buttons:** Performance | Calibration

**Default:** Performance chart shown first

**Behavior:**
- Active button highlighted in blue (#4a9eff)
- Inactive buttons gray (#2a2a2a)
- Smooth instant switching (no animation)
- Explanation text updates with chart

---

## User Experience

### Before Phase 3
- View aggregate statistics across all exams
- See exam history list
- ❌ No way to visualize trends over time

### After Phase 3
- View aggregate statistics across all exams
- See exam history list
- ✅ **Performance History charts showing trends**
- ✅ **Toggle between performance and calibration views**
- ✅ **Inline explanations of metrics**
- ✅ **Interactive tooltips with exact values**

### Minimum Data Requirement

Charts display **only if user has completed 2+ exams** (minimum for trend visualization).

Users with 0-1 exams see statistics and history but no charts section.

---

## Chart Explanations

### Performance Metrics
- **Answer Accuracy:** Percentage of questions answered correctly
- **Average Confidence:** Your mean confidence level (0-100%)

### Calibration Metrics
- **Brier Score:** Mean squared difference between confidence and correctness  
  - Lower is better (0 = perfect calibration)
  - Range: 0 to 1 (displayed 0 to 0.5 for typical values)
  
- **Calibration Bias:** Average (confidence - accuracy)
  - Positive = overconfident (high confidence when wrong)
  - Negative = underconfident (low confidence when correct)
  - Zero = well-calibrated
  - Range: -100% to +100% (displayed -0.5 to 0.5 in decimal form)

---

## Testing

### Unit Tests

**New Tests:** 5 (all passing)
- Empty trends response
- Trends with multiple exams
- Authentication requirement
- Cross-user isolation
- Exclude incomplete exams

**Total Tests:** 82 passing ✅
- Phase 1: 38 tests
- Phase 2: 39 tests
- Phase 3: 5 tests

### Integration Test

**Script:** `test_trends_integration.py`

**Test Flow:**
1. Register new user
2. Login with credentials
3. Take 3 exams with varying performance
4. Fetch trends via API
5. Verify data structure and ordering
6. Verify statistics endpoint still works

**Result:** ✅ All checks passed

**Sample Output:**
```
📊 Exam 1 Trend:
   Accuracy: 20.0%
   Confidence: 85.0%
   Brier Score: 0.582
   Bias Score: 0.650

📊 Exam 2 Trend:
   Accuracy: 40.0%
   Confidence: 65.0%
   Brier Score: 0.303
   Bias Score: 0.250

📊 Exam 3 Trend:
   Accuracy: 80.0%
   Confidence: 60.0%
   Brier Score: 0.245
   Bias Score: -0.200
```

---

## How It Works

### Backend Flow

1. User requests `/api/exams/trends` (authenticated)
2. `get_user_exam_trends()` queries database:
   - Join exams, exam_answers, questions tables
   - Filter by user_id and completed_at IS NOT NULL
   - Order by completed_at ASC
3. Group answers by exam_id
4. Calculate per-exam statistics:
   - Accuracy = (correct / total) × 100
   - Average confidence = mean(all confidences)
   - Brier score = mean((confidence - correctness)²)
   - Bias score = mean(confidence - correctness)
5. Assign sequential exam numbers (1, 2, 3...)
6. Return ordered list of trends

### Frontend Flow

1. `showHistory()` calls `loadPerformanceCharts()`
2. Fetch trends from API
3. If 2+ trends exist:
   - Show performance history section
   - Setup toggle button handlers
   - Render both charts (one hidden)
4. If 0-1 trends:
   - Hide performance history section
5. User clicks toggle:
   - Switch active chart
   - Update explanation text

### Chart Rendering

**Chart.js Configuration:**
- Type: `'line'`
- Theme: Dark mode compatible
- Grid: #3a3a3a
- Text: #e0e0e0 / #b0b0b0
- Responsive: `maintainAspectRatio: false`
- Tooltips: Dark background with borders

**Data Preparation:**
```javascript
const labels = trends.map(t => `Exam ${t.exam_number}`);
const accuracy = trends.map(t => t.accuracy);
const confidence = trends.map(t => t.average_confidence);
```

---

## Responsive Design

### Desktop (>600px)
- Chart height: 400px
- Toggle buttons: horizontal row
- Full width container

### Mobile (≤600px)
- Chart height: 300px (reduced)
- Toggle buttons: stacked vertically
- Reduced padding (15px instead of 20px)
- Full-width buttons for easier tapping

---

## Performance Considerations

### Database Queries
- Single JOIN query per request
- Filtered by user_id (indexed)
- Filtered by completed_at IS NOT NULL
- Ordered by completed_at ASC (indexed)

### Chart Rendering
- Charts created once per page load
- Destroyed and recreated on data changes
- No animation on data updates (instant)
- Canvas rendering (hardware accelerated)

### Data Size
- Typical user: 10-50 exams
- Data size: ~1KB per trend
- Total: <50KB for 50 exams
- Chart.js bundle: ~200KB (CDN cached)

---

## Security

✅ **Authentication Required:** Trends endpoint requires valid session  
✅ **User Isolation:** SQL queries filter by authenticated user_id  
✅ **No Cross-User Access:** Users see only their own trends  
✅ **Tested:** Cross-user isolation test ensures separation  

---

## Backward Compatibility

✅ **No Breaking Changes:** All existing endpoints unchanged  
✅ **Optional Feature:** Charts section hidden if no data  
✅ **Existing Tests Pass:** All 77 Phase 1+2 tests still pass  
✅ **Database Schema:** No changes required  

---

## Requirements Fulfilled

All requirements from `new_feature.txt` Section 3 (Longitudinal Tracking):

✅ **Historical charts** showing statistics across assessments  
✅ **Calibration charts:** Brier score and calibration bias  
✅ **Performance charts:** Answer accuracy and average confidence  
✅ **X-axis:** Chronological assessment numbers (Exam 1, 2, 3...)  
✅ **Clear labels:** Axes, units, and metrics labeled  
✅ **Simple toggle:** Performance ↔ Calibration switching  
✅ **Metric explanations:** Tooltips for Brier score and bias  

---

## Future Enhancements (Out of Scope)

- Date-based X-axis (currently using exam numbers)
- Zoom/pan controls for large datasets
- Export chart as image
- Compare trends to average user
- Topic-specific trend analysis
- Moving average trend lines

---

## Local Testing

### 1. Start Server
```bash
uvicorn app.main:app --reload --port 8000
```

### 2. Run Integration Test
```bash
python test_trends_integration.py
```

### 3. Manual Testing
1. Open http://localhost:8000
2. Register/login
3. Take 2-3 exams with different scores
4. Click "View My Exam History"
5. See "Performance History" section
6. Toggle between Performance and Calibration charts
7. Hover over data points for tooltips

### 4. Run Unit Tests
```bash
pytest tests/test_exam_history.py -v
```

**Expected:** 16 tests passing (11 Phase 2 + 5 Phase 3)

---

## Deployment

### No Additional Configuration

Phase 3 requires **no new environment variables** or dependencies beyond what's already deployed.

**Render Deployment:**
1. Push to GitHub
2. Auto-deploys (same as Phase 1+2)
3. Chart.js loaded from CDN (no server-side change)
4. New endpoint automatically available

---

## Files Summary

### Created (2 files)
1. `test_trends_integration.py` - Integration test script
2. `PHASE3_LONGITUDINAL_TRACKING.md` - This documentation

### Modified (6 files)
1. `app/db.py` - Added `get_user_exam_trends()`
2. `app/services.py` - Added `get_user_exam_trends()`
3. `app/routers/exams.py` - Added `/api/exams/trends` endpoint
4. `frontend/index.html` - Added Chart.js and chart section
5. `frontend/styles.css` - Added chart styles
6. `frontend/app.js` - Added chart rendering functions
7. `tests/test_exam_history.py` - Added 5 trend tests

### Statistics
- **Lines added:** ~650
- **API endpoints added:** 1
- **Database functions added:** 1
- **Charts implemented:** 2
- **Tests added:** 5 (+ 1 integration test)
- **Total tests passing:** 82 ✅

---

## Success Criteria

All Phase 3 objectives completed:

✅ **Objective 1:** Time-series API endpoint implemented  
✅ **Objective 2:** Performance chart (accuracy + confidence)  
✅ **Objective 3:** Calibration chart (Brier + bias)  
✅ **Objective 4:** Chart toggle functionality  
✅ **Objective 5:** Metric explanations included  
✅ **Objective 6:** Responsive mobile design  
✅ **Objective 7:** Comprehensive testing (5 unit + 1 integration)  

---

## Troubleshooting

### Charts Not Appearing
- **Cause:** User has <2 completed exams
- **Fix:** Complete at least 2 exams to see trends

### Chart.js Not Loading
- **Cause:** CDN blocked or offline
- **Fix:** Check browser console; consider self-hosting Chart.js

### Trends Empty Despite Exams
- **Cause:** Exams not completed (answers not submitted)
- **Fix:** Submit exam answers to complete

### Wrong Exam Order
- **Cause:** Timezone issues with completed_at
- **Fix:** Database stores UTC; display uses sequential numbers

---

**Phase 3 completed: November 9, 2026**  
**All requirements from new_feature.txt Section 3 fulfilled ✅**
