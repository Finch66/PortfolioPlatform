# Backend Engineer: Punti Caldi e Mental Model

Questa mini-guida riassume cosa tenere a mente mentre lavori sul progetto e come ragiona un backend engineer.

## Mental model
- Parti dal dominio: quali invarianti devono sempre essere vere? (es. non vendere oltre il posseduto).
- Confina le responsabilità: API -> validazione/mapping, dominio -> regole di business, persistenza -> DB/transaction.
- Ogni cambiamento deve essere testabile e osservabile (log/metriche) e deployabile con un click (docker/compose).
- Preferisci flussi idempotenti e sicuri rispetto a patch veloci: pensa a cosa succede se il client ritenta o il DB fallisce a metà.

## Checklist rapida per una feature
- Input/Output chiari: modelli Pydantic per request/response, niente leaking di dettagli interni.
- Regole di business centralizzate: service/domain layer unico che applica invarianti.
- Persistenza: sessione DB gestita, transazioni aperte/chiuse correttamente, commit dopo le regole.
- Errori: classi di eccezione mappate a HTTP 4xx/5xx coerenti; messaggi utili ma sicuri.
- Test: unit per invarianti, integrazione per API + DB happy/unhappy path.
- Observability: log strutturati (livelli info/warn/error) con request_id; metriche dove serve.

## Error handling e logging
- Usa eccezioni di dominio per errori attesi (400), eccezioni generiche portano a 500.
- Logga solo ciò che serve a debuggare (no dati sensibili), includi contesto (request_id, method, path, status, asset_id se utile).
- Mantieni un handler globale per formattare gli errori in modo consistente e un middleware che assegna un request_id.

## Dati e DB
- Schema esplicito (SQLModel/Alembic). Migrazioni per ogni cambio di schema.
- Concorrenza: ragiona su race condition (es. doppia SELL simultanea). Usa transazioni e lock se necessario.
- Indici dove servono (asset_id + trade_date). Pianifica query e carichi.

## API e contratti
- Versiona gli endpoint quando cambi il contratto (es. /v1/transactions).
- Documenta con OpenAPI (già esposto da FastAPI). Mantieni esempi di payload.
- Valida dati vicino al bordo (API) e nel dominio (invarianti).

## Event-driven
- Emetti eventi dopo il commit DB; definisci il payload e la semantica (es. TransactionCreated).
- Idempotenza: eventi con id e sequence, consumer idempotenti.
- Ordine e consegna: valuta code (Kafka/Rabbit) e politiche di retry/DLQ.

## Dev & Ops
- Config via env (DATABASE_URL, log level). Nessun secret hardcoded.
- Container pronti: Dockerfile minimo, compose per orchestrare (Postgres + servizio).
- Strumenti locali: make/script per up/down/test/format, linting prima del push.
- CI/CD: test e build container automatici (da pianificare).
- Migrazioni: usa Alembic per versionare lo schema; ogni change di tabella va in una migration con upgrade/downgrade. In ambienti reali evita create_all e applica alembic upgrade head.
  - Applica le migrazioni al DB che userai (dev/prod). In compose: docker compose exec transactions-service alembic upgrade head.
  - Quando creare una migration: dopo aver cambiato i modelli SQLModel -> alembic revision --autogenerate -m "desc", poi alembic upgrade head.

## Come pensare ai "casi rognosi"
- Input malevoli o incompleti: che succede? restituisci errori chiari.
- Riprovi e duplicati: se il client ritenta una POST, viene creata una doppia transazione? usa idempotency key o controlli.
- Failure a metà: commit parziale? assicurati che o tutto passa o tutto roll back (transazioni DB).
- Evoluzione schema: come migri i dati senza downtime? prepara migrazioni forward/rollback.

## Tracce di studio pratiche
- Implementa/leggi il service di dominio, poi scrivi test che rompono le invarianti.
- Aggiungi un endpoint DELETE e copri 200/404/400 con test.
- Integra Alembic e crea la prima migrazione per la tabella transactions.
- Aggiungi logging strutturato e osserva i log durante i test/API calls.
