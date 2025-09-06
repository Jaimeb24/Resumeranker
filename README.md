# ResumeRanker

A React + Flask application for matching resumes against job postings using AI-powered analysis.

## Features

- User authentication (signup, login, password reset)
- Resume upload and management (PDF/DOC/DOCX support)
- Job posting parsing from URLs
- AI-powered resume-job matching with suggestions
- Real-time progress updates via WebSockets

## Quick Start

### Backend Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment:
```bash
cp .env.example .env
# Edit .env with your actual values
```

4. Start the Flask server:
```bash
python src/app.py
```

The backend will run on http://localhost:3001

### Frontend Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The frontend will run on http://localhost:5173

## Environment Variables

Copy `.env.example` to `.env` and fill in the values:

- `SECRET_KEY`: Flask secret key
- `JWT_SECRET`: JWT signing secret
- `DATABASE_URL`: Database connection string (defaults to SQLite)
- `OPENAI_API_KEY`: OpenAI API key for AI matching
- `OPENAI_MODEL`: OpenAI model to use (default: gpt-4o-mini)
- `ENABLE_PLAYWRIGHT`: Enable Playwright for advanced scraping (default: false)
- `CORS_ORIGINS`: Allowed CORS origins (comma-separated)

## API Endpoints

### Authentication
- `POST /api/auth/signup` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/request-password-reset` - Request password reset
- `POST /api/auth/reset-password` - Reset password

### Resumes
- `POST /api/resumes` - Upload resume (multipart/form-data)
- `GET /api/resumes` - List user's resumes
- `DELETE /api/resumes/<id>` - Delete resume

### Jobs
- `POST /api/jobs/parse` - Parse job posting from URL

### Matching
- `POST /api/match` - Match resume against job posting

## Testing

### Backend Tests
```bash
pytest
```

### Frontend Tests
```bash
npm test
```

## Smoke Tests

### 1. Signup and Login
```bash
# Signup
curl -X POST http://localhost:3001/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# Login
curl -X POST http://localhost:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

### 2. Upload Resume
```bash
curl -X POST http://localhost:3001/api/resumes \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@resume.pdf"
```

### 3. Parse Job URL
```bash
curl -X POST http://localhost:3001/api/jobs/parse \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/job-posting"}'
```

### 4. Match Resume vs Job
```bash
curl -X POST http://localhost:3001/api/match \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"resumeId": 1, "jobPostingId": 1}'
```
