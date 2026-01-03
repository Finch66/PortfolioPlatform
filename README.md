# Event-Driven Portfolio Platform (Transactions Service)

Backend di esempio per gestire transazioni BUY/SELL con FastAPI + SQLModel. Questa repo contiene il servizio transazioni, docker-compose per Postgres e la documentazione di dominio/roadmap.

## Prerequisiti
- Python >= 3.11 (per sviluppo locale)
- Docker Desktop (per eseguire API + Postgres via compose)

## Setup rapido
```bash
# dalla root del repo
python -m venv .venv
.\.venv\Scripts\Activate.ps1      # PowerShell su Windows
pip install -r requirements-dev.txt
```

## Avvio con Docker Compose
```bash
docker compose up --build
```
- Postgres ha healthcheck; l'API parte quando il DB è pronto.
- Variabili: `DATABASE_URL` già impostata in `.env.example/transactions.env`.
- Swagger UI: http://localhost:8000/docs

## Avvio locale senza container
```bash
set DATABASE_URL=postgresql://postgres:postgres@localhost:5432/transactions  # adatta se necessario
cd services/transaction
uvicorn app.main:app --reload
```

## Test
```bash
cd services/transaction
pytest
```
- Coprono invarianti (quantity>0, date future, sell oltre posseduto) e API POST/GET. Usano SQLite in-memory, non serve Postgres.

## Documentazione utile
- Roadmap: `portfolio-event-driven-roadmap.md`
- Stato e note backend: `docs/stato-progetto-e-note-backend.md`
- Panoramica codice: `docs/code-overview.md`
- Modello di dominio: `docs/domain-model.md`
- Quickstart dettagliato: `docs/quickstart.md`
- Playbook backend: `docs/backend-engineer-playbook.md`
