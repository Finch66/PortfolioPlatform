# Debugging: import CSV e problemi UI/API

## Errore "Failed to fetch"
Significa che il browser non riesce a contattare l'API (di solito CORS o API non raggiungibile).

### Passi rapidi
1) Verifica API: apri `http://localhost:8000/docs`
2) Verifica porta frontend: `http://localhost:5173`
3) Verifica endpoint import:
```powershell
curl.exe -F "file=@docs/sample-portfolio.csv" http://localhost:8000/imports/transactions
```
Se questo fallisce, il problema è backend o CSV.

### Controllo CORS
L'API permette `http://localhost:5173` via `CORS_ORIGINS`.
Se il frontend è su un'altra porta, aggiungila:
```powershell
$env:CORS_ORIGINS="http://localhost:5173"
```
Poi riavvia il backend.

## Debug frontend (browser)
1) Apri DevTools (F12)
2) Tab "Console": cerca errori CORS o network
3) Tab "Network": clicca la richiesta `/imports/transactions` e guarda status/response

## Debug backend (log)
Con Docker:
```powershell
docker compose logs -f transactions-service
```
Cerca errori di import o validazione.

## Errori CSV comuni
- Header mancante o colonne non valide
- Date non in formato `YYYY-MM-DD`
- `quantity` o `price` non numerici
- `operation_type` non è `BUY` o `SELL`

## Dove guardare nel codice
- Import CSV: `services/transaction/app/api/imports.py`
- Regole di dominio: `services/transaction/app/domain/services.py`
- Aggregazioni portfolio: `services/transaction/app/domain/portfolio.py`
