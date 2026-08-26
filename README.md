# JobFlow API

Async backend service for managing vacancies, job applications and interview pipelines.

The project demonstrates a production-oriented Python backend with asynchronous database access, background jobs, Redis caching, external API integrations, business rules, automated tests and continuous integration.

## Features

* Vacancy CRUD
* Vacancy search and filtering
* Pagination
* Salary validation
* Job application pipeline
* Controlled application status transitions
* Redis caching
* Background processing with ARQ
* Background job status tracking
* Async external HTTP integrations
* Structured request logging
* Request ID tracking
* Global error handling
* PostgreSQL persistence
* Alembic migrations
* Async integration tests
* GitHub Actions CI

## Tech Stack

### Backend

* Python
* FastAPI
* AsyncIO
* Pydantic

### Database

* PostgreSQL
* SQLAlchemy AsyncSession
* asyncpg
* Alembic

### Infrastructure

* Redis
* ARQ

### HTTP & Integrations

* httpx

### Testing

* Pytest
* pytest-asyncio
* httpx AsyncClient

### CI

* GitHub Actions

## Architecture

The application uses layered architecture:

```text
HTTP Request
     ↓
FastAPI Router
     ↓
Service Layer
     ↓
Repository Layer
     ↓
SQLAlchemy AsyncSession
     ↓
PostgreSQL
```

Additional infrastructure:

```text
                 ┌───────────────┐
                 │   FastAPI     │
                 └───────┬───────┘
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
        PostgreSQL                Redis
              │                     │
              │                     ▼
              │                  ARQ Queue
              │                     │
              │                     ▼
              │                 ARQ Worker
              │
              ▼
        Persistent Data
```

## Project Structure

```text
app/
├── main.py
├── config.py
├── database.py
├── cache.py
├── queue.py
├── worker.py
├── tasks.py
├── exceptions.py
├── logging_config.py
│
├── models/
│   ├── vacancy.py
│   └── application.py
│
├── schemas/
│   ├── vacancy.py
│   ├── application.py
│   └── job.py
│
├── repositories/
│   ├── vacancies.py
│   └── applications.py
│
├── services/
│   ├── vacancies.py
│   └── applications.py
│
├── routers/
│   ├── vacancies.py
│   └── applications.py
│
├── integrations/
│   └── company_lookup.py
│
└── middleware/
    ├── logging.py
    └── request_id.py

migrations/
tests/
.github/workflows/
```

## Vacancies

Example vacancy:

```json
{
  "title": "Python Backend Developer",
  "company": "Example Tech",
  "url": "https://example.com",
  "salary_from": 2000,
  "salary_to": 3000,
  "currency": "EUR",
  "location": "Remote",
  "work_format": "remote",
  "description": "FastAPI, PostgreSQL and Redis"
}
```

Available operations:

```text
POST   /vacancies
GET    /vacancies
GET    /vacancies/{id}
PATCH  /vacancies/{id}
DELETE /vacancies/{id}
```

## Vacancy Search

Vacancies support search, filtering and pagination.

Examples:

```text
GET /vacancies?search=python
GET /vacancies?company=example
GET /vacancies?location=stockholm
GET /vacancies?work_format=remote
GET /vacancies?salary_from=2000
GET /vacancies?limit=20&offset=0
```

Example response:

```json
{
  "items": [],
  "total": 0,
  "limit": 20,
  "offset": 0
}
```

## Application Pipeline

Job applications use a controlled status workflow:

```text
NEW
 │
 ▼
APPLIED
 │
 ▼
HR_SCREEN
 │
 ▼
TECH_INTERVIEW
 │
 ├──────────────► OFFER
 │
 ▼
FINAL_INTERVIEW
 │
 ├──────────────► OFFER
 │
 └──────────────► REJECTED
```

Applications may also be rejected during intermediate stages.

Terminal statuses:

```text
OFFER
REJECTED
```

Invalid transitions return:

```text
409 Conflict
```

For example:

```text
NEW → OFFER
```

is not allowed.

## Redis Caching

Vacancy listings are cached in Redis.

Repeated requests with the same filters can be served from cache instead of querying PostgreSQL again.

Example cache key:

```text
vacancies:search=python:company=None:location=None:work_format=remote:salary_from=None:limit=20:offset=0
```

The cache is invalidated when a vacancy is:

* created
* updated
* deleted

## Background Jobs

The project uses ARQ with Redis for background processing.

Start the worker:

```bash
arq app.worker.WorkerSettings
```

Queue a vacancy analysis:

```text
POST /vacancies/{id}/analyze
```

Example response:

```json
{
  "job_id": "example-job-id",
  "status": "queued"
}
```

Job processing happens outside the HTTP request.

## Background Job Status

Job status can be requested using:

```text
GET /vacancies/jobs/{job_id}
```

Possible states include:

```text
queued
in_progress
complete
```

Example completed job:

```json
{
  "job_id": "example-job-id",
  "status": "complete",
  "result": {
    "vacancy_id": 1,
    "status": "processed"
  }
}
```

## External HTTP Integration

The project uses `httpx.AsyncClient` for asynchronous HTTP requests.

The integration layer handles:

* HTTP timeouts
* redirects
* HTTP errors
* unavailable external services

External service failures are converted into appropriate API responses instead of exposing internal tracebacks.

## Logging

Requests are logged with:

* HTTP method
* path
* response status
* execution time
* request ID

Example:

```text
GET /health | status=200 | 1.24ms | request_id=3b29d2d7...
```

Every response includes:

```text
X-Request-ID
```

Clients can also provide their own request ID.

## Local Setup

Clone the repository:

```bash
git clone https://github.com/TrippleT25/jobflow-api.git
cd jobflow-api
```

Create virtual environment:

```bash
python -m venv .venv
```

Activate on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Environment Variables

Create `.env`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/jobflow
REDIS_URL=redis://localhost:6379/0
```

Do not commit `.env`.

## Database

Create PostgreSQL database:

```sql
CREATE DATABASE jobflow;
```

Apply migrations:

```bash
alembic upgrade head
```

## Run API

```bash
python -m uvicorn app.main:app --reload
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

## Run Worker

Redis must be running before starting the worker.

```bash
arq app.worker.WorkerSettings
```

The API and worker are separate processes.

## Tests

Create:

```sql
CREATE DATABASE jobflow_test;
```

Create `.env.test`:

```env
TEST_DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/jobflow_test
```

Run:

```bash
pytest -v
```

Tests cover:

* health endpoint
* vacancy CRUD
* salary validation
* vacancy search
* filtering
* pagination
* application creation
* allowed status transitions
* forbidden status transitions
* full application pipeline
* terminal statuses

Redis is mocked where external infrastructure is not required for the test.

## Continuous Integration

GitHub Actions automatically runs tests on:

```text
push
pull_request
```

The CI environment provides:

* PostgreSQL
* Redis
* Python environment
* automated pytest execution

## Development Principles

This project focuses on:

* asynchronous Python
* clear layer separation
* business logic outside routers
* isolated database access
* external service error handling
* caching
* background processing
* automated testing
* maintainable API design

## Development Status

The project is under active development.

Planned improvements:

* authentication
* per-user vacancy ownership
* application statistics
* rate limiting
* improved cache strategy
* additional background tasks
* test coverage reporting
* deployment
