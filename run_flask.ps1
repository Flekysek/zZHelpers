$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

if (!(Test-Path ".venv\\Scripts\\python.exe")) {
  Write-Host "Creating venv..."
  python -m venv .venv
}

Write-Host "Installing requirements..."
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

Write-Host "Starting Flask on http://127.0.0.1:5000 ..."
.\.venv\Scripts\python.exe apps\\flask_app.py

