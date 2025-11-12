# Test Suite per Mergington High School API

Questa directory contiene una suite completa di test per l'API FastAPI del sistema di gestione delle attività scolastiche.

## Struttura dei Test

### `conftest.py`
File di configurazione pytest che contiene:
- Fixture per il client di test FastAPI
- Setup automatico per il reset dei dati delle attività prima di ogni test

### `test_app.py` - Test Principali
Test delle funzionalità principali dell'API:
- ✅ Redirect della homepage
- ✅ Recupero di tutte le attività
- ✅ Iscrizione di successo alle attività
- ✅ Gestione di attività inesistenti
- ✅ Prevenzione di iscrizioni duplicate
- ✅ Gestione della capacità massima delle attività
- ✅ Rimozione di partecipanti
- ✅ Workflow completo di iscrizione e rimozione
- ✅ Iscrizione multipla a più attività

### `test_edge_cases.py` - Test di Casi Limite
Test per verificare la robustezza dell'API:
- ✅ Email con caratteri speciali
- ✅ Nomi delle attività con caratteri speciali
- ✅ Email vuote
- ✅ Richieste malformate
- ✅ Sensibilità alle maiuscole/minuscole
- ✅ Iscrizioni simultanee
- ✅ Gestione della capacità al limite
- ✅ Rimozione e ri-aggiunta di partecipanti
- ✅ Consistenza dei dati dopo operazioni multiple

### `test_integration.py` - Test di Integrazione
Test per l'integrazione frontend-backend:
- ✅ Servizio dei file statici (HTML, JS, CSS)
- ✅ Formato delle risposta API per il frontend
- ✅ Formato delle risposte di errore
- ✅ Compatibilità con encoding URL
- ✅ Consistenza dei dati dopo operazioni frontend
- ✅ Workflow tipico del frontend

## Esecuzione dei Test

### Prerequisiti
```bash
# Installa le dipendenze
pip install -r requirements.txt
```

### Comandi Base
```bash
# Esegue tutti i test
pytest tests/

# Esegue test con output verboso
pytest tests/ -v

# Esegue test con coverage
pytest tests/ --cov=src --cov-report=term-missing

# Esegue test con report HTML della coverage
pytest tests/ --cov=src --cov-report=html
```

### Usando il Makefile
```bash
# Esegue tutti i test
make test

# Esegue test con coverage
make test-cov

# Esegue test con report HTML della coverage
make test-cov-html
```

### Test Specifici
```bash
# Esegue solo i test principali
pytest tests/test_app.py

# Esegue solo i test di casi limite
pytest tests/test_edge_cases.py

# Esegue solo i test di integrazione
pytest tests/test_integration.py

# Esegue un test specifico
pytest tests/test_app.py::test_signup_success
```

## Coverage

La suite di test attualmente raggiunge il **100% di coverage** del codice sorgente in `src/app.py`.

## Configurazione

### `pytest.ini`
La configurazione pytest include:
- Path di ricerca per i test
- Pattern per i file di test
- Opzioni di output verboso
- Filtri per i warning

### Reset Automatico dei Dati
Ogni test viene eseguito con dati puliti grazie alla fixture `reset_activities` che:
1. Ripristina lo stato iniziale delle attività prima di ogni test
2. Garantisce l'isolamento tra i test
3. Pulisce lo stato dopo ogni test

## Tipi di Test

### Test Unitari
- Testano singole funzionalità dell'API
- Verificano input/output specifici
- Controllano gestione degli errori

### Test di Integrazione
- Verificano l'interazione tra frontend e backend
- Testano il servizio dei file statici
- Controllano il formato delle risposte

### Test End-to-End
- Simulano workflow utente completi
- Verificano la consistenza dei dati
- Testano scenari d'uso reali

## Metriche di Qualità

- **30 test totali**
- **100% coverage del codice**
- **0 test falliti**
- **Tempo di esecuzione: < 1 secondo**

## Best Practices Implementate

1. **Isolamento dei Test**: Ogni test è indipendente e non influenza gli altri
2. **Fixture Riutilizzabili**: Setup comune condiviso tra i test
3. **Test Descrittivi**: Nomi dei test che descrivono chiaramente cosa testano
4. **Coverage Completo**: Ogni linea di codice è testata
5. **Test di Edge Cases**: Scenari limite e casi d'errore sono coperti
6. **Documentazione**: Test ben documentati e organizzati