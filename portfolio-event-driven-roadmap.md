# Event-Driven Portfolio Platform – Roadmap a Obiettivi

Roadmap personale per lo studio e lo sviluppo di una piattaforma backend
event-driven per la gestione di un portafoglio finanziario.

Obiettivo: imparare architetture moderne (microservizi, Kafka, event sourcing)
costruendo un progetto reale, usabile e presentabile anche in ambito aziendale.

---

## 🟢 OBIETTIVO 0 – Setup & Baseline Tecnica

### Scopo
Preparare un ambiente di sviluppo professionale e riproducibile.

### Deliverable
- Repository Git inizializzata
- Ambiente Python funzionante
- Docker operativo

### Checklist
- [ ] Repository Git creato
- [ ] Python >= 3.11 installato
- [ ] Docker installato e funzionante
- [ ] Docker Compose funzionante
- [ ] VS Code configurato
- [ ] README.md iniziale

### Competenze acquisite
- Tooling professionale
- Setup ambiente come in azienda

---

## 🟢 OBIETTIVO 1 – Transactions Service (Backend Core)

### Scopo
Costruire un backend solido per registrare operazioni finanziarie.

### Funzionalità
- Inserimento operazioni BUY / SELL
- Validazioni di dominio
- Persistenza su database

### API Minime
- POST /transactions
- GET /transactions
- DELETE /transactions/{id}

### Modello Dati
- asset_id
- quantity
- price
- currency
- trade_date
- operation_type

### Checklist
- [ ] FastAPI
- [ ] Modelli Pydantic
- [ ] PostgreSQL
- [ ] SQLAlchemy
- [ ] Validazioni corrette
- [ ] Error handling coerente
- [ ] OpenAPI / Swagger
- [ ] Test minimi

### Output
- Servizio backend standalone e funzionante

### Competenze acquisite
- API design
- Backend Python production-like

---

## 🟢 OBIETTIVO 2 – Dockerizzazione Completa

### Scopo
Rendere il servizio eseguibile come in produzione.

### Checklist
- [ ] Dockerfile per API
- [ ] docker-compose.yml
- [ ] Container PostgreSQL
- [ ] Configurazione via variabili ambiente
- [ ] Logging leggibile

### Criterio di successo
```bash
docker-compose up
