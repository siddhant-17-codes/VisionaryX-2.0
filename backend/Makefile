# Backend targets. Run from backend/ with a Python 3.12 environment active.
# Settings are read from backend/.env (copy .env.example first).
.PHONY: install dev run test lint lock clean

PYTHON ?= python

install:
	$(PYTHON) -m pip install -r requirements-dev.txt

dev:
	$(PYTHON) -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

run:
	$(PYTHON) -m uvicorn main:app --host 127.0.0.1 --port 8000

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff check --config pyproject.toml ../scripts

# After editing requirements.in: regenerate the fully pinned requirements.txt.
lock:
	uv pip compile requirements.in --universal --python-version 3.12 -o requirements.txt

clean:
	rm -rf .pytest_cache .ruff_cache
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
