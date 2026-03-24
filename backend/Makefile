.PHONY: install run dev clean logs

install:
	pip install -r requirements.txt

run:
	uvicorn main:app --host 127.0.0.1 --port 8000

dev:
	uvicorn main:app --host 127.0.0.1 --port 8000 --reload

clean:
	rmdir /s /q storage\chats 2>nul & mkdir storage\chats
	rmdir /s /q storage\documents 2>nul & mkdir storage\documents
	rmdir /s /q faiss_index 2>nul & mkdir faiss_index
	rmdir /s /q logs 2>nul & mkdir logs
	@echo Storage and logs cleared.

logs:
	type logs\visionaryx_*.log 2>nul || echo No logs found.