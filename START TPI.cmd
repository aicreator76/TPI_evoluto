@echo off
cd /d "E:\TPI_evoluto"
"E:\TPI_evoluto\.venv\Scripts\python.exe" -m uvicorn app.main:app --app-dir "E:\TPI_evoluto" --host 127.0.0.1 --port 8000
