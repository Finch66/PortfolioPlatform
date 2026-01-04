# Quickstart - Transactions Service

## Prerequisiti
- Docker Desktop installato e attivo.
- Porta 8000 libera (API) e 5432 libera (Postgres host).

## Avvio con Docker Compose
```bash
docker compose up --build
```
- Postgres ha un healthcheck (`pg_isready`); l'API parte solo quando il DB è pronto.
- Per fermare: `docker compose down` (usa `-v` per rimuovere il volume dati).
- Logging: middleware HTTP logga in JSON con request_id, metodo, path, status e durata in ms.

## Variabili d'ambiente
- L'API legge `DATABASE_URL`; nel compose è valorizzata da `.env.example/transactions.env` con:
  `postgresql://postgres:postgres@postgres:5432/transactions`

## Smoke test
1) Apri Swagger UI: http://localhost:8000/docs  
   - `POST /transactions` → inserisci:
   ```json
   {"asset_id":"ETF123","operation_type":"BUY","quantity":10,"price":100,"currency":"USD","trade_date":"2024-01-10"}
   ```
   - `GET /transactions` → dovresti vedere l'elemento inserito.
2) Da terminale (PowerShell):
```powershell
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/transactions" -ContentType "application/json" -Body '{"asset_id":"ETF123","operation_type":"BUY","quantity":10,"price":100,"currency":"USD","trade_date":"2024-01-10"}'
Invoke-RestMethod -Method Get -Uri "http://localhost:8000/transactions"
```

## Sviluppo locale senza container
- Avvia Postgres locale e esporta `DATABASE_URL=postgresql://postgres:postgres@localhost:5432/transactions`.
- Da `services/transaction`: `uvicorn app.main:app --reload`
- Swagger su http://localhost:8000/docs

## Test (Pytest)
- Installa dipendenze dev dalla root: `pip install -r requirements-dev.txt` (attiva il virtualenv se lo usi).
- Da `services/transaction`: `pytest`
  - Coprono invarianti di dominio (quantity > 0, data futura, sell oltre il posseduto) e API POST/GET.
  - Usano SQLite in-memory con override di `get_session`, quindi non richiedono Postgres.

## Script PowerShell (shortcut)
- `.\scripts\up.ps1` (aggiungi `-Build` per forzare la build)
- `.\scripts\down.ps1`
- `.\scripts\logs.ps1`
- `.\scripts\test.ps1` (ricorda di attivare la venv prima)
- `.\scripts\migrate.ps1` (applica le migrazioni Alembic al Postgres del compose esposto su localhost; richiede venv attiva con alembic)

## Migrazioni (Alembic)
- Installazione dipendenze dev già include `alembic`.
- Nota: `pyproject.toml` del servizio usa setuptools con `include = ["app*"]` (necessario dopo aver aggiunto `migrations`), quindi installa in editable dalla root con `pip install -r requirements-dev.txt`.
- Comando base (da `services/transaction`): `alembic upgrade head` (usa `DATABASE_URL` corrente).
- Generare nuova migrazione: `alembic revision --autogenerate -m "desc"` dopo aver modificato i modelli SQLModel.
- Gli script sono in `services/transaction/migrations/`.

## Idempotenza & API
- Le POST supportano header `Idempotency-Key`: se ripeti la stessa chiave, ritorna la transazione già creata.
- GET /transactions supporta paginazione con `skip` e `limit`.
- Currencies ammesse: USD, EUR, GBP (validazione di dominio).
