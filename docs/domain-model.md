# Domain Model – Event-Driven Portfolio Platform

Questo documento descrive il modello di dominio della piattaforma di gestione
del portafoglio finanziario.  
Il dominio è definito prima del codice ed è la base per tutte le scelte
architetturali (API, eventi, microservizi, storage).

Il sistema è progettato per un utilizzo reale personale, ma con standard
professionali e scalabili.

---

## 1. Scopo del Sistema (WHY)

Il sistema serve a:

- registrare operazioni finanziarie effettuate dall’utente
- ricostruire lo stato del portafoglio nel tempo
- calcolare metriche di performance e allocazione
- supportare un’architettura event-driven

Il sistema NON serve a:

- fare trading automatico
- fornire prezzi real-time
- sostituire un broker
- gestire fiscalità o dichiarazioni

Lo scope è intenzionalmente limitato per mantenere il dominio chiaro e robusto.

---

## 2. Profilo del Portafoglio Target

Il modello è costruito per riflettere un portafoglio reale composto da:

- ~80% ETF
- ~12% azioni singole
- ~5% obbligazioni
- ~3% crypto

Il dominio deve quindi supportare asset eterogenei, con caratteristiche
diverse ma unificati sotto concetti comuni.

---

## 3. Concetti di Dominio Principali

### 3.1 Asset

Un Asset rappresenta uno strumento finanziario investibile.

Esempi:
- ETF (identificato da ISIN)
- Azione singola (ticker)
- Obbligazione
- Crypto asset

Attributi concettuali:
- asset_id (identificatore interno)
- asset_type (ETF, STOCK, BOND, CRYPTO)
- symbol (ISIN, ticker o codice simbolico)
- name
- base_currency

Un Asset è considerato relativamente stabile nel tempo.

---

### 3.2 Transaction

Una Transaction rappresenta un’operazione effettuata dall’utente.

Tipi supportati:
- BUY
- SELL

Attributi concettuali:
- transaction_id
- asset_id
- operation_type (BUY / SELL)
- quantity
- price
- currency
- trade_date
- fees (opzionali)

Una Transaction è un fatto storico:
- una volta registrata, non viene modificata
- eventuali correzioni avvengono tramite nuove transazioni/eventi

---

### 3.3 Portfolio

Il Portfolio NON è un’entità persistita direttamente.

È definito come:

> Lo stato derivato dell’insieme delle transazioni nel tempo.

Concetti associati:
- holdings per asset
- quantità totale per asset
- prezzo medio di carico
- esposizione per valuta

Il Portfolio viene sempre ricostruito a partire dagli eventi.

---

## 4. Invarianti di Dominio

Le invarianti sono regole che devono essere sempre rispettate.

Esempi:
- non è possibile vendere più quantità di quanta detenuta
- una transazione deve avere una data valida
- la quantità deve essere diversa da zero
- la valuta deve essere supportata
- un asset deve esistere prima di poter essere scambiato

Le invarianti:
- non sono responsabilità del database
- non sono responsabilità del controller HTTP
- appartengono al dominio

---

## 5. Eventi di Dominio

Il sistema è progettato per essere event-driven.

Eventi principali:

- TransactionCreated
- TransactionDeleted
- TransactionCorrected (futuro)

Caratteristiche degli eventi:
- immutabili
- timestamped
- rappresentano qualcosa che è successo nel passato
- sono la fonte di verità per il portfolio

Gli eventi sono il linguaggio con cui i servizi comunicano.

---

## 6. Aggregati e Confini di Responsabilità

Aggregato principale:
- Transaction

Il Portfolio NON è un aggregato, ma una proiezione.

Responsabilità:
- il servizio di transazioni emette eventi
- il portfolio service consuma eventi
- i servizi di analytics lavorano su dati derivati

Questo approccio abilita naturalmente CQRS ed event sourcing.

---

## 7. Cosa NON viene modellato (Scelte Consapevoli)

Esplicitamente escluso in questa fase:

- dividendi
- tassazione
- split azionari
- multi-portfolio
- prezzi real-time
- ribilanciamenti automatici

Questi elementi:
- aumentano significativamente la complessità
- possono essere aggiunti in futuro tramite nuovi eventi
- non sono necessari per validare l’architettura

---

## 8. Evoluzione Futura (Non Vincolante)

Possibili estensioni future:
- eventi di dividendo
- supporto multi-valuta avanzato
- snapshot di portfolio
- simulazioni e backtesting

Il dominio è progettato per evolvere senza rompere le basi.

---

## 9. Obiettivo Architetturale

Questo dominio è progettato per:

- supportare microservizi
- abilitare event sourcing
- essere facilmente osservabile
- essere spiegabile a stakeholder tecnici e non

La chiarezza del dominio ha priorità sulla quantità di funzionalità.
