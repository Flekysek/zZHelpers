# ZzTools Helper – lokální PFX wrapper

Tahle složka obsahuje lokální (localhost) nástroje pro zabalení existujícího certifikátu a privátního klíče do `.pfx`.

## Požadavky
- Windows
- Python 3.12+

Pokud nemáš Python:

```powershell
winget install --id Python.Python.3.12 --source winget --accept-package-agreements --accept-source-agreements
```

Poznámka: někdy je potřeba restartovat PowerShell/IDE, aby se projevil PATH.

## Instalace (jednorázově)

```powershell
cd "c:\Users\dominik.skubla\Documents\LogSeqNotes\MedicalcNotes\assets\Scripts\Helper\server"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Spuštění – Flask (HTML UI)

```powershell
cd "c:\Users\dominik.skubla\Documents\LogSeqNotes\MedicalcNotes\assets\Scripts\Helper\server"
.\.venv\Scripts\python.exe app.py
```

Otevři: `http://127.0.0.1:5000/`

## Spuštění – Streamlit

```powershell
cd "c:\Users\dominik.skubla\Documents\LogSeqNotes\MedicalcNotes\assets\Scripts\Helper\server"
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true --browser.gatherUsageStats false
```

Otevři: `http://127.0.0.1:8501/`

## Řešení problémů
- **Port 8501 is not available**: běží ti už jiný Streamlit/Python proces. Najdi PID a ukonči:

```powershell
netstat -ano | findstr :8501
Stop-Process -Id <PID> -Force
```

