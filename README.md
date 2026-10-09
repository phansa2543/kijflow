# Kijflow

Business Management SaaS for SMEs.

## Local Development

### Requirements

- Python 3.13
- Node.js 24
- Docker Desktop
- Git

### Backend Setup

From the project root:

```bat
cd backend
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
```

### Environment Configuration

From the project root, copy the example environment file:

```bat
copy .env.example .env
```

### PostgreSQL

Start the local PostgreSQL development database from the project root:

```bat
docker compose up -d
```

### Database Migration

From the `backend` directory:

```bat
python -m alembic upgrade head
```

### Run Backend

From the `backend` directory:

```bat
uvicorn app.main:app
```

### Run Backend Tests

From the `backend` directory:

```bat
python -m pytest
```

### Frontend Setup and Run

From the `frontend` directory:

```bat
npm ci
npm run dev
```