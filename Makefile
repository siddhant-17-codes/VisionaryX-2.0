.PHONY: install run-backend run-frontend dev clean help

install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

run-backend:
	cd backend && uvicorn main:app --host 127.0.0.1 --port 8000 --reload

run-frontend:
	cd frontend && npm run dev

dev:
	@echo Starting VisionaryX 2.0 backend and frontend...
	@start /B cmd /C "cd backend && uvicorn main:app --host 127.0.0.1 --port 8000 --reload > ../logs/backend.log 2>&1"
	@timeout /t 3 /nobreak > nul
	@start /B cmd /C "cd frontend && npm run dev > ../logs/frontend.log 2>&1"
	@echo Backend running on http://127.0.0.1:8000
	@echo Frontend running on http://localhost:5173
	@echo Logs: logs/backend.log and logs/frontend.log
	@echo Press Ctrl+C in each window to stop.

clean:
	cd backend && $(MAKE) clean
	cd frontend && $(MAKE) clean

help:
	@echo VisionaryX 2.0 available commands:
	@echo   make install          Install all dependencies
	@echo   make run-backend      Start FastAPI backend on port 8000
	@echo   make run-frontend     Start React frontend on port 5173
	@echo   make dev              Start both backend and frontend together
	@echo   make clean            Clear storage, logs, build artifacts
