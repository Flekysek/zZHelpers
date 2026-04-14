$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

if (!(Test-Path ".venv\\Scripts\\python.exe")) {
  Write-Host "Creating venv..."
  python -m venv .venv
}

Write-Host "Installing requirements..."
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

Write-Host "Starting Streamlit on http://127.0.0.1:8501 ..."
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true --browser.gatherUsageStats false

