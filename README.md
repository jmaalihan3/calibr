# Academic Assessment System - Prototype 1

A web-based academic assessment application built with FastAPI backend and vanilla JavaScript frontend.

## Features

- Random exam generation with 5 multiple-choice questions
- Single-page application with no page refreshes
- Dark theme UI for reduced eye strain
- Immediate feedback with score and correct answers
- SQLite database for persistent storage

## Tech Stack

### Backend
- **Python 3.13+**
- **FastAPI 0.104.1** - Modern async web framework
- **SQLite** - Embedded database
- **Uvicorn** - ASGI server

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Dark theme styling
- **Vanilla JavaScript** - SPA logic and API integration

## Project Structure

```
zcalib-project/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application entry point
│   ├── db.py             # Database operations
│   ├── services.py       # Business logic layer
│   └── routers/
│       ├── __init__.py
│       └── exams.py      # API endpoints
├── frontend/
│   ├── index.html        # Single-page application
│   ├── styles.css        # Dark theme styling
│   └── app.js            # Frontend logic
├── tests/
│   ├── __init__.py
│   ├── test_db.py        # Database tests
│   ├── test_services.py  # Business logic tests
│   └── test_api.py       # API integration tests
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Tests

```bash
pytest tests/ -v
```

All 28 tests should pass.

### 3. Start the Server

```bash
uvicorn app.main:app --reload --port 8000
```

The server will:
- Initialize the SQLite database
- Populate 10 sample questions
- Start on http://localhost:8000

### 4. Access the Application

Open your browser to:
- **Frontend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Health Check**: http://localhost:8000/api/health

## API Endpoints

### POST /api/exams/start
Start a new exam with random questions.

**Request:**
```json
{
  "num_questions": 5
}
```

**Response:**
```json
{
  "exam_id": 1,
  "questions": [
    {
      "id": 1,
      "question_text": "What is 2 + 2?",
      "options": ["3", "4", "5", "6"]
    }
  ]
}
```

### POST /api/exams/{exam_id}/submit
Submit answers and get results.

**Request:**
```json
{
  "answers": {
    "1": 1,
    "2": 0,
    "3": 2
  }
}
```

**Response:**
```json
{
  "score": 3,
  "total": 5,
  "percentage": 60.0,
  "results": [...]
}
```

### GET /api/exams/{exam_id}/results
Retrieve results for a completed exam.

## Development

### Running in Development Mode

The `--reload` flag enables auto-reload on code changes:

```bash
uvicorn app.main:app --reload --port 8000
```

### Database

SQLite database file: `exams.db`

To reset the database:
```bash
rm exams.db
# Restart the server to recreate
```

### Testing

Run specific test files:
```bash
pytest tests/test_db.py -v
pytest tests/test_services.py -v
pytest tests/test_api.py -v
```

Run with coverage:
```bash
pytest tests/ --cov=app --cov-report=html
```

## Architecture

### Single-Page Application (SPA)

**Frontend Flow:**
1. User clicks "Start Exam"
2. JavaScript calls `/api/exams/start`
3. Questions rendered dynamically
4. User selects answers (stored in JavaScript state)
5. User submits exam
6. JavaScript calls `/api/exams/{id}/submit`
7. Results displayed immediately

**Backend Flow:**
1. FastAPI receives request
2. Services layer processes business logic
3. Database layer performs CRUD operations
4. JSON response returned to frontend

### Design Decisions

**Decision 1: Client-Side State**
- Exam state stored in JavaScript, not server sessions
- Pro: Simpler backend, stateless API
- Con: Page refresh loses progress
- Future: Could add localStorage persistence

**Decision 2: Vanilla JavaScript**
- No framework (React, Vue, etc.)
- Pro: No build step, simpler setup
- Con: More boilerplate
- Future: Consider framework if UI complexity grows

**Decision 3: SQLite**
- In-process database
- Pro: Zero configuration
- Con: Not suitable for production/concurrent users
- Future: Migrate to PostgreSQL for deployment

## Sample Questions

The system includes 10 sample questions covering:
- General knowledge (capitals, planets, oceans)
- Basic math
- Science (chemistry, physics)
- Literature
- History

## Browser Compatibility

Tested on:
- Chrome 120+
- Firefox 120+
- Safari 17+
- Edge 120+

Requires JavaScript enabled.

## Known Limitations

1. **No authentication** - Anyone can take exams
2. **No persistence on refresh** - Exam progress lost if page refreshed
3. **No security** - Correct answers visible in browser DevTools
4. **Single-user** - SQLite not suitable for concurrent users
5. **No exam history** - Users can't see past exams

These are acceptable for a prototype. Production would need:
- User authentication and authorization
- Server-side session management
- Secure answer validation
- Production database (PostgreSQL)
- Exam history and analytics

## Future Enhancements

- User accounts and authentication
- Exam history and analytics
- Timed exams
- Question categories and difficulty levels
- Admin panel for question management
- Export results to PDF
- Mobile app using same API

## License

This is a prototype for academic purposes.

## Authors

Built as Prototype 1 for the zcalib-project academic assessment system.
