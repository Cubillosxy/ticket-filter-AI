# Ticket Classifier (FastAPI) — MVP

A minimal, production-minded MVP to classify support tickets into 4 categories:
- Billing
- Technical Issue
- Account / Access
- Other

The service is resilient by design:
- Fast deterministic rules first
- Optional OpenAI classification
- Local fallback classifier when AI is unavailable
- Every request/response is audited to a local SQLite database for later analysis/training

## Features (MVP)
- `POST /v1/tickets/classify` returns `{category, confidence, metadata}`
- Rule-based classification for obvious cases
- Local fallback scoring classifier for availability and cost control
- Audit persistence using SQLite (`./data/audit.db`)
- Testing flags:
  - `?force_ai=true` - skip rules and use OpenAI directly
  - `?simulate_ai_failure=true` - force fallback classifier
- Simple `GET /health`

## Project structure
```
   /
    app/
    main.py
    api/
    services/
    adapters/
    core/
    tests/
    data/
```

### Getting started


- Python 3.10+ recommended

Install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

```

### Run Locallys 

```bash
uvicorn app.main:app --reload --port 8000
```

#### Health Check

```bash
GET /health
curl -s http://localhost:8000/health

```

classify a ticket:

- using swagger ui: http://localhost:8000/docs
- using curl:  

#### Heuristic Classification (rules first)
```bash
curl -s -X POST "http://localhost:8000/v1/tickets/classify" \
  -H "Content-Type: application/json" \
  -d '{
    "id":"t_001",
    "subject":"Invoice missing for last month",
    "description":"I need a copy of my invoice, I cannot download it",
    "created_at":"2025-12-29T10:00:00Z"
  }'

```

#### AI Classification (openai)
```bash
curl -s -X POST "http://localhost:8000/v1/tickets/classify" \
  -H "Content-Type: application/json" \
  -d '{
    "id":"t_004",
    "subject":"Something weird",
    "description":"Not sure what is happening but it fails sometimes",
    "created_at":"2025-12-29T10:00:00Z"
  }'

```

#### Force AI Classification (skip rules, use OpenAI directly)
```bash
curl -s -X POST "http://localhost:8000/v1/tickets/classify?force_ai=true" \
  -H "Content-Type: application/json" \
  -d '{
    "id":"t_005",
    "subject":"Invoice missing for last month",
    "description":"I need a copy of my invoice, I cannot download it",
    "created_at":"2025-12-29T10:00:00Z"
  }'

```

> **Note:** Even though this ticket matches billing rules, `force_ai=true` will bypass rules and use OpenAI directly. Useful for testing AI prompt accuracy.

#### Fallback Classification (local)
```bash
curl -s -X POST "http://localhost:8000/v1/tickets/classify?simulate_ai_failure=true" \
  -H "Content-Type: application/json" \
  -d '{
    "id":"t_004",
    "subject":"Something weird",
    "description":"Not sure what is happening but it fails sometimes",
    "created_at":"2025-12-29T10:00:00Z"
  }'

```

### Persistence (Sqlite audit log) -> Dynamodb on prod

Each classification attempt is saved into:
- `./data/audit.db` (sqlite) on local


```bash
sqlite3 ./data/audit.db ".tables"
# see schema
sqlite3 ./data/audit.db ".schema audit_attempts"
# last 10 items
sqlite3 ./data/audit.db "
SELECT
  ticket_id,
  category,
  confidence,
  decision_path,
  fallback_reason,
  latency_total_ms,
  received_at
FROM audit_attempts
ORDER BY id DESC
LIMIT 10;
"

```
