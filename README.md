# MediChat — Medical Q&A Chatbot

Domain-restricted medical chatbot powered by FastAPI + Claude + PostgreSQL.

---

## Backend Structure

```
backend/
├── app/
│   ├── api/routes/
│   │   ├── auth.py          # POST /api/auth/signup, /login, GET /me
│   │   └── chat.py          # POST /api/chat, GET /history/:id, DELETE /:id
│   ├── core/
│   │   ├── config.py        # Settings (reads .env)
│   │   ├── deps.py          # get_current_user FastAPI dependency
│   │   └── security.py      # bcrypt + JWT helpers
│   ├── db/
│   │   └── database.py      # SQLAlchemy engine + get_db()
│   ├── models/              # User, Session, Message ORM models
│   ├── schemas/             # Pydantic request/response schemas
│   ├── services/
│   │   ├── classifier.py    # Domain classifier (keyword guard)
│   │   └── claude.py        # Anthropic Claude API wrapper
│   └── main.py              # FastAPI app, CORS, rate limiting
├── migrations/              # Alembic migration files
├── Dockerfile
├── alembic.ini
└── requirements.txt
```

---

## Quick Start (Docker)

```bash
# 1. Copy env file and fill in your API key
cp backend/.env.example backend/.env
# Edit backend/.env — set ANTHROPIC_API_KEY and JWT_SECRET

# 2. Start everything
docker compose up --build

# API available at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

## Local Development (without Docker)

```bash
cd backend

# Create a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Copy and configure env vars
cp .env.example .env
# Edit .env with your DATABASE_URL, ANTHROPIC_API_KEY, JWT_SECRET

# Run DB migrations
alembic upgrade head

# Start the dev server
uvicorn app.main:app --reload --port 8000
```

---

## API Reference

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/signup` | No | Register new user |
| POST | `/api/auth/login` | No | Login, get JWT |
| GET | `/api/auth/me` | Yes | Current user profile |
| POST | `/api/chat` | Yes | Send message, get reply |
| GET | `/api/chat/sessions` | Yes | List all sessions |
| GET | `/api/chat/history/{id}` | Yes | Get session messages |
| DELETE | `/api/chat/{id}` | Yes | Delete session |
| GET | `/health` | No | Health check |

All protected endpoints require `Authorization: Bearer <token>` header.

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `JWT_SECRET` | Secret key for signing JWTs |
| `JWT_EXPIRE_MINUTES` | Token expiry (default: 10080 = 7 days) |
| `ANTHROPIC_API_KEY` | Your Claude API key |
| `CLAUDE_MODEL` | Model to use (default: claude-3-5-sonnet-20241022) |
| `ALLOWED_ORIGINS` | Comma-separated CORS origins |
