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

### Registration Counter Cleanup (Manual)

The registration-counter cleanup runner is separate from the Registration request path. After applying database migrations, run it from the `backend` directory with the intended `DATABASE_URL` configured:

```bat
python -m app.auth.infrastructure.registration_counter_cleanup_runner
```

**This performs real deletions, not a dry run.** Check that `DATABASE_URL` targets the intended database before running.

Provisional cleanup contract: expired counters are eligible for deletion **24 hours after their rate-limit window ends**; cleanup uses PostgreSQL time and `FOR UPDATE SKIP LOCKED`. The runner deletes at most **500 rows per batch** and stops after **20 batches** (10,000 rows per invocation). Uncaught failures propagate and return a non-zero process exit code. If the 20-batch ceiling is reached, the runner displays `Additional cleanup may be required`, but may still exit with status zero **while a backlog remains**.

**B2 Cleanup Implementation QA: CLOSED.** No production scheduler is configured. A provisional **hourly external scheduler** and verification of job execution, failure reporting, backlog/retention monitoring and database permissions are deferred to the **Pre-External-Use Gate** under AQ-014. They are not required for internal M3 Login API work.

**Login counter cleanup:** M3 Step 6 adds separate cleanup logic for `auth_login_attempt_counters`, with PostgreSQL time, `FOR UPDATE SKIP LOCKED`, 24-hour retention after window expiry, and a maximum of 500 rows/batch × 20 batches. It is not the Registration cleanup runner above; **no dedicated Login cleanup runner or scheduled operational job is established in the current pushed baseline**. The execution mechanism, failure detection and backlog monitoring remain deferred to the Pre-External-Use Gate (AQ-014). Step 6 Login Abuse Protection is **CLOSED — Independent QA PASS / Founder Approved** (accepted implementation commit `b7aac2e`; closure documented at `53c0e78`). This closure does not imply final M3 acceptance.

### Optional Live HIBP Integration Test

The HIBP live integration test contacts the real HIBP Pwned Passwords Range API.

It is opt-in and must not run automatically during normal CI or standard backend regression tests.

The test uses a public, known-compromised test password. Never use real user passwords or production credentials in integration tests.

From the `backend` directory, first verify that the test is skipped by default:

```bat
python -m pytest tests/test_hibp_live.py -v
```

Expected result: `1 skipped`.

To explicitly run the live integration test on Windows CMD:

```bat
set RUN_LIVE_HIBP=1
python -m pytest tests/test_hibp_live.py -v
set RUN_LIVE_HIBP=
```

Expected result when HIBP is available: `1 passed`.

The environment variable is cleared after the test to avoid unintended external API requests.

To run the normal backend regression suite:

```bat
python -m pytest -q
```

The live HIBP test should remain skipped unless explicitly enabled.

A real HIBP service failure must not be treated as an automatic failure of Kijflow's deterministic mocked tests.

Live integration verification is required before formal Password Blocklist acceptance and should be repeated before external-user release.

### Frontend Setup and Run

From the `frontend` directory:

```bat
npm ci
npm run dev
```