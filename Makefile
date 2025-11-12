# Makefile per il progetto Mergington High School API

# Variabili
PYTHON = .venv/bin/python
PIP = .venv/bin/pip

# Setup dell'ambiente di sviluppo
setup:
	python3 -m venv .venv
	$(PIP) install -r requirements.txt

# Installa le dipendenze
install:
	$(PIP) install -r requirements.txt

# Esegue tutti i test
test:
	$(PYTHON) -m pytest tests/ -v

# Esegue i test con coverage
test-cov:
	$(PYTHON) -m pytest tests/ --cov=src --cov-report=term-missing

# Esegue i test con report HTML della coverage
test-cov-html:
	$(PYTHON) -m pytest tests/ --cov=src --cov-report=html
	@echo "Coverage report generato in htmlcov/index.html"

# Avvia il server di sviluppo
dev:
	$(PYTHON) -m uvicorn src.app:app --reload --host 0.0.0.0 --port 8000

# Avvia il server di produzione
run:
	$(PYTHON) -m uvicorn src.app:app --host 0.0.0.0 --port 8000

# Pulizia dei file temporanei
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name ".coverage" -delete

# Mostra l'aiuto
help:
	@echo "Comandi disponibili:"
	@echo "  setup     - Crea l'ambiente virtuale e installa le dipendenze"
	@echo "  install   - Installa le dipendenze"
	@echo "  test      - Esegue tutti i test"
	@echo "  test-cov  - Esegue i test con coverage"
	@echo "  test-cov-html - Esegue i test con report HTML della coverage"
	@echo "  dev       - Avvia il server di sviluppo con reload automatico"
	@echo "  run       - Avvia il server di produzione"
	@echo "  clean     - Pulisce i file temporanei"
	@echo "  help      - Mostra questo messaggio di aiuto"

.PHONY: setup install test test-cov test-cov-html dev run clean help