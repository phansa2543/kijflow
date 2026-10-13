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

Update `.env` with local development credentials as required.

The local environment uses separate databases for:

- application development
- automated tests

`DATABASE_URL` must point to the development database.

`TEST_DATABASE_URL` must point to a separate test database.

The test suite intentionally rejects using the same database URL for both.

### PostgreSQL

Start the local PostgreSQL development database from the project root:

```bat
docker compose up -d
```

The default development database is:

```text
kijflow
```

The automated test database is:

```text
kijflow_test
```

Create `kijflow_test` once in the local PostgreSQL instance if it does not already exist.

### Database Migration

From the `backend` directory, migrate the development database:

```bat
python -m alembic upgrade head
```

### Test Database Migration

The test database must also be migrated before running PostgreSQL-backed tests.

From the `backend` directory, temporarily set `DATABASE_URL` to the same value as `TEST_DATABASE_URL` from the root `.env` file:

```bat
set DATABASE_URL=<TEST_DATABASE_URL value from ..\.env>
python -m alembic upgrade head
set DATABASE_URL=
```

Do not use the development database URL here.

After the migration completes, `DATABASE_URL` is cleared from the current command session so normal application configuration can continue to come from `.env`.

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

The tests use `TEST_DATABASE_URL`.

Persistence tests run against PostgreSQL and use the dedicated test database.

### Frontend Setup and Run

From the `frontend` directory:

```bat
npm ci
npm run dev
```