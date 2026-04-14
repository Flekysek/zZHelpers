$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

if (!(Test-Path ".venv\\Scripts\\python.exe")) {
  Write-Host "Creating venv..."
  python -m venv .venv
}

Write-Host "Installing requirements..."
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

Write-Host "Starting API + Streamlit..."
.\.venv\Scripts\python.exe run.py
