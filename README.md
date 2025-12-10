# Generic FastAPI Template

A simple FastAPI project template with user authentication using JWT RS256.

**This is an example project** - use it as a starting point for your own APIs.

---

## What's Inside

- **User registration & login** with JWT tokens (RS256 asymmetric encryption)
- **PostgreSQL** database with SQLAlchemy ORM
- **Alembic** for database migrations
- **Password hashing** with bcrypt
- **Pydantic v2** for data validation

---

## User Model

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key (auto-generated) |
| `email` | String | Unique, used for login |
| `hashed_password` | String | bcrypt hash (never stored in plain text) |
| `is_active` | Boolean | Account status |
| `created_at` | DateTime | Registration timestamp (UTC) |

---

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Create new user |
| POST | `/auth/login` | Get JWT token |
| GET | `/api/v1/health` | Health check |

---

## Quick Start

1. Clone the repo
2. Create a `.env` file (see `.env.example`)
3. Run PostgreSQL (Docker recommended)
4. Install dependencies: `pip install -r requirements.txt`
5. Run migrations: `alembic upgrade head`
6. Start server: `uvicorn app.main:app --reload`

---

## AI Disclosure

Documentation and code comments in this project were written with the assistance of AI (GitHub Copilot). The actual code logic and architecture were developed by the author.

---

## License

Do whatever you want with it.
