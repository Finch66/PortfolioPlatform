# Stato progetto e note backend

## Stato attuale (dal codice)
- Servizio transactions FastAPI con endpoint POST/GET in `services/transaction/app/api/transactions.py`, modelli di input/output Pydantic separati (`app/api/schemas.py`) e logica dominio in `app/domain/services.py`.
- Modello di dominio `Transaction` e enum `OperationType` in `services/transaction/app/domain/models.py`.
- Regole di dominio: quantity > 0, data non futura, currency a 3 lettere, blocco vendite oltre il posseduto, con `DomainException` mappata a HTTP 400.
- Config DB e sessione SQLModel in `services/transaction/app/core/config.py` e `services/transaction/app/core/database.py` con variabile `DATABASE_URL`.
- Dockerfile per il servizio presente; `docker-compose.yml` corretto con `context: ./services/transaction`, env file `.env.example/transactions.env`, healthcheck Postgres e `depends_on: service_healthy`.
- Documentazione di dominio e panoramica codice in `docs/domain-model.md`, `docs/code-overview.md` e quickstart in `docs/quickstart.md`.

## Passaggi gia' fatti (dedotti dal codice)
1. Definito il modello di dominio e le invarianti (docs/domain-model.md).
2. Creato servizio FastAPI con router /transactions e lifespan che crea le tabelle SQLModel all'avvio (app/main.py).
3. Implementata logica di dominio per creare transazioni con validazioni e controllo disponibilita' per le SELL (app/domain/services.py).
4. Configurato accesso DB via SQLModel/psycopg2 e dependency injection `get_session` (app/core/database.py).
5. Preparato packaging Python (pyproject) e Dockerfile per containerizzare il servizio (services/transaction/Dockerfile).
6. Corretto docker-compose con build path giusto, env file, healthcheck e dipendenza da Postgres pronto.
7. Aggiunti test Pytest (API + invarianti) in `services/transaction/tests/test_transactions_api.py`; 4 test passano con SQLite in-memory e override della sessione.

## Cose da completare/subito utili
- Aggiungere README/quickstart e script make/poetry per setup locale (quickstart gia' presente, resta README e comandi helper).
- Migliorare error handling/logging strutturato (in parte presente con handler globale 400/500).
- Gestire DELETE /transactions/{id}.
- Valutare emissione eventi (TransactionCreated) dopo il commit per la pipeline event-driven.

## Mini guida per studiare il backend
- Flusso base: `app/main.py` crea FastAPI (lifespan) e crea le tabelle SQLModel all'avvio, include il router.
- API: `app/api/transactions.py` espone POST/GET; POST usa `TransactionCreate` (Pydantic) e mappa su modello SQLModel; output con `TransactionRead`. Errori di dominio tornano 400 con payload `{code,message}`.
- Dominio: `app/domain/services.py` incapsula invarianti; `_validate_sell_quantity` ricalcola la quantita' netta per asset aggregando BUY/SELL e blocca vendite oltre il posseduto.
- Persistenza: `app/core/database.py` istanzia l'engine SQLModel con `DATABASE_URL` e fornisce `get_session` come dependency FastAPI che apre/chiude la sessione per richiesta.
- Modello dati: `app/domain/models.py` definisce tabella `Transaction` con UUID primario, asset_id, operation_type, quantity, price, currency, trade_date. Enum `OperationType` limita a BUY/SELL.
- Esecuzione locale: esporta `DATABASE_URL=postgresql://postgres:postgres@localhost:5432/transactions`, attiva Postgres, poi da `services/transaction` lancia `uvicorn app.main:app --reload`. In container usa compose con env file e healthcheck.
- Spunti di approfondimento: event sourcing e publish di eventi dopo il commit; gestione concorrenza/transazioni DB; aggiungere idempotenza; test di integrazione con DB; pipeline di migrazioni (Alembic) se lo schema evolve.
