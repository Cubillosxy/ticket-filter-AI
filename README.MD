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
- Testing flag to force fallback: `?simulate_ai_failure=true`
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
