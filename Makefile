# VisionaryX 2.0. Needs GNU make and a POSIX shell: macOS, Linux, or Git Bash / WSL on Windows.
.PHONY: help install dev run-backend run-frontend test lint clean

help:
	@echo "make install       Install backend (Python 3.12) and frontend dependencies"
	@echo "make dev           Run backend (:8000) and frontend (:5173) together; Ctrl+C stops both"
	@echo "make run-backend   Run only the FastAPI backend with reload"
	@echo "make run-frontend  Run only the Vite dev server"
	@echo "make test          Backend (pytest) and frontend (Vitest) tests"
	@echo "make lint          ruff and ESLint"
	@echo "make clean         Remove caches and build output"

install:
	$(MAKE) -C backend install
	$(MAKE) -C frontend install

dev:
	$(MAKE) -j2 run-backend run-frontend

run-backend:
	$(MAKE) -C backend dev

run-frontend:
	$(MAKE) -C frontend dev

test:
	$(MAKE) -C backend test
	$(MAKE) -C frontend test

lint:
	$(MAKE) -C backend lint
	$(MAKE) -C frontend lint

clean:
	$(MAKE) -C backend clean
	$(MAKE) -C frontend clean
