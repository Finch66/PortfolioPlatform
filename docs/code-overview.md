# Panoramica del codice

Questa mappa spiega cosa contiene ogni file principale e come si collega al flusso del servizio transazioni.

## Radice repository
- `.gitignore`: esclusioni per cache Python, virtualenv, build, IDE, ecc.
- `requirements.txt`: dipendenze principali (fastapi, uvicorn, sqlmodel, psycopg2-binary, python-dotenv).
- `portfolio-event-driven-roadmap.md`: note di roadmap (alto livello, non codice).
- `docs/domain-model.md`: descrive concetti di dominio (Asset, Transaction, Portfolio, eventi) e vincoli.

## Servizio transazioni (`services/transaction`)
- `pyproject.toml`: metadati PEP 621 del pacchetto (`transactions-service`), Python >=3.11, e dipendenze runtime.

### App FastAPI (`services/transaction/app`)
- `main.py`: crea `FastAPI` con titolo, monta il router delle transazioni e, all avvio, crea le tabelle SQLModel sul database configurato.
- `api/transactions.py`: definisce il router `/transactions`. POST crea una transazione usando `TransactionService` e mappa errori dominio in HTTP 400. GET restituisce la lista di tutte le transazioni.
- `core/config.py`: definisce `Settings` (Pydantic) e legge la variabile d ambiente `DATABASE_URL`, necessaria per connettersi al DB.
- `core/database.py`: costruisce l `engine` SQLModel/SQLAlchemy usando `DATABASE_URL` e fornisce `get_session()` come dependency FastAPI per aprire una sessione per richiesta.

### Dominio (`services/transaction/app/domain`)
- `models.py`: modelli di dominio con persistenza SQLModel. `OperationType` enum BUY/SELL; `Transaction` con campi id (UUID), asset_id, tipo operazione, quantity, price, currency, trade_date.
- `services.py`: logica di dominio per creare transazioni. Valida regole base (quantit� > 0, data non futura, currency a 3 lettere) e, per le SELL, calcola la quantit� disponibile aggregando BUY/SELL dello stesso asset; se non basta, solleva `DomainException`. Se tutto ok, persiste la transazione (add/commit/refresh).

## Flusso applicativo
1. Richieste HTTP arrivano a FastAPI (`main.py`).
2. Il router `/transactions` (`api/transactions.py`) gestisce POST/GET, ottenendo una sessione DB da `get_session`.
3. `TransactionService` (`domain/services.py`) applica invarianti e salva su DB usando i modelli SQLModel (`domain/models.py`).
4. All avvio, `SQLModel.metadata.create_all(engine)` (in `main.py`) crea le tabelle in base ai modelli, usando la connessione definita in `core/database.py` con la `DATABASE_URL` letta in `core/config.py`.

## Portfolio e import
- `services/transaction/app/api/imports.py`: endpoint `POST /imports/transactions` per caricare CSV.
- `services/transaction/app/api/portfolio.py`: endpoint `GET /portfolio` + metriche/allocazioni.
- `services/transaction/app/domain/portfolio.py`: aggregazioni e calcoli per holdings, metriche e distribuzioni.
