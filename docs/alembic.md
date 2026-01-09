# Alembic: perche serve e come usarlo

## Cos e Alembic
Alembic e lo strumento di migrazione del database usato da SQLAlchemy/SQLModel.
Serve per applicare modifiche allo schema del database (nuove colonne, indici, vincoli)
in modo versionato e ripetibile.

## Perche ti serve qui
Quando aggiungiamo campi al modello `Transaction` (es. `asset_name`, `asset_type`),
il database deve essere aggiornato. Alembic applica queste modifiche senza dover
ricreare manualmente le tabelle e senza perdere dati.

## Cosa fa un comando `alembic upgrade head`
- Legge le migrazioni in `services/transaction/migrations/versions/`
- Applica in ordine le modifiche non ancora presenti nel database
- Porta lo schema alla versione piu recente ("head")

## Come usarlo in questo progetto
Modo consigliato (automatico):
```powershell
.\scripts\migrate.ps1
```
Lo script imposta `DATABASE_URL` sul Postgres locale del compose se non e gia presente.

Se vuoi eseguirlo a mano:
```powershell
$env:DATABASE_URL="postgresql://postgres:postgres@localhost:5432/transactions"
cd services/transaction
alembic upgrade head
```

## Nota su SQLite
Se `DATABASE_URL` non e impostata, Alembic puo usare SQLite di default.
SQLite non supporta alcune modifiche (es. creare vincoli con ALTER TABLE),
per questo hai visto l errore. Usare il Postgres del compose risolve.
