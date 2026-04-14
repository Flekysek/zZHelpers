@echo off
setlocal

cd /d %~dp0

if not exist ".venv\Scripts\python.exe" (
  echo Creating venv...
  py -m venv .venv
)

echo Installing requirements...
".venv\Scripts\python.exe" -m pip install -r requirements.txt

echo Starting Flask on http://127.0.0.1:5000 ...
".venv\Scripts\python.exe" apps\flask_app.py

