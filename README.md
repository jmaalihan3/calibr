# Academic Assessment System - Prototype 1

A web-based academic assessment application built with FastAPI backend and vanilla JavaScript frontend.

## Features

- **User Authentication:** Secure registration and login with Argon2id password hashing
- **Session Management:** Persistent sessions with HttpOnly cookies and CSRF protection
- **Random Exam Generation:** Customizable number of questions (1-5)
- **Confidence Tracking:** Rate your confidence (0-100%) for each answer
- **Calibration Metrics:** Brier Score and Bias Score to measure prediction accuracy
- **Anonymous Mode:** Take exams without authentication (optional)
- **Dark Theme UI:** Reduced eye strain with modern interface
- **Persistent Storage:** SQLite (local) or PostgreSQL (production)

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

### 2. Configure Environment (Optional)

For local development, the app works with auto-generated secrets. For production:

```bash
# Copy example environment file
cp .env.example .env

# Generate secure secrets
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32)); print('CSRF_SECRET=' + secrets.token_urlsafe(32))"

# Add secrets to .env file
```

**Environment Variables:**
- `SECRET_KEY` - Session signing secret (auto-generated in dev)
- `CSRF_SECRET` - CSRF token secret (auto-generated in dev)
- `SESSION_TIMEOUT_DAYS` - Session validity period (default: 7 days)
- `RATE_LIMIT_LOGIN` - Login attempts per minute (default: 5)
- `RATE_LIMIT_REGISTER` - Registration attempts per minute (default: 3)
- `ENVIRONMENT` - `development` or `production`

### 3. Run Tests

```bash
pytest tests/ -v
```

All 66 tests should pass:
- 28 original tests (database, services, API)
- 38 new authentication tests (auth utilities, auth API)

**Test Coverage:**
- ✅ Password hashing and verification
- ✅ Session token generation and validation
- ✅ CSRF protection
- ✅ Rate limiting
- ✅ User registration and login
- ✅ Cross-user data isolation
- ✅ Exam flow (anonymous and authenticated)

### 4. Start the Server

```bash
uvicorn app.main:app --reload --port 8000
```

The server will:
- Initialize the SQLite database
- Create users, sessions, questions, exams, and exam_answers tables
- Populate 10 sample questions
- Start on http://localhost:8000

### 5. Access the Application

Open your browser to:
- **Frontend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Health Check**: http://localhost:8000/api/health

## API Endpoints

### Authentication

#### POST /api/auth/register
Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Password Requirements:**
- At least 8 characters
- One uppercase letter
- One lowercase letter
- One digit
- One special character

**Response:** 201 Created
```json
{
  "message": "Registration successful",
  "detail": "Please log in with your credentials"
}
```

#### POST /api/auth/login
Authenticate and create session.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response:** 200 OK (sets session cookie)
```json
{
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "created_at": "2026-11-09T17:30:00",
    "email_verified": false
  },
  "csrf_token": "session_id:timestamp:signature",
  "message": "Login successful"
}
```

#### POST /api/auth/logout
Logout and revoke session (requires CSRF token header).

**Headers:**
```
X-CSRF-Token: <csrf_token_from_login>
```

**Response:** 200 OK
```json
{
  "message": "Logout successful"
}
```

#### GET /api/auth/me
Get current user profile (requires authentication).

**Response:** 200 OK
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "created_at": "2026-11-09T17:30:00",
  "email_verified": false
}
```

#### GET /api/auth/csrf-token
Get CSRF token for authenticated requests.

**Response:** 200 OK
```json
{
  "csrf_token": "session_id:timestamp:signature"
}
```

### Exams

#### POST /api/exams/start
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

1. ~~**No authentication**~~ ✅ **IMPLEMENTED** - Users can now register and login
2. **No persistence on refresh** - Exam progress lost if page refreshed (in-progress exams)
3. **No security** - Correct answers visible in browser DevTools (by design for immediate feedback)
4. **Single-instance rate limiting** - Rate limits reset on server restart
5. **No exam history** - Users can't see past exams yet (Phase 2)

### Phase 1 Complete ✅
- ✅ User registration and authentication
- ✅ Secure password hashing (Argon2id)
- ✅ Session management with HttpOnly cookies
- ✅ CSRF protection
- ✅ Rate limiting (basic implementation)
- ✅ Database schema with users and sessions

### Phase 2 Complete ✅
- ✅ User-linked exam history
- ✅ View past exam results
- ✅ Aggregate statistics (accuracy, confidence, Brier score)
- ✅ Exam history pagination
- ✅ Anonymous mode still supported

### Coming in Phase 3
- Historical trend tracking
- Topic-based performance breakdown
- Calibration visualization
- Comparative statistics

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
