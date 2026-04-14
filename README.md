# zZHelpers (ZzTools)

Sada jednoduchých lokálních helperů v Pythonu.

- **Primární UI**: Streamlit (nejjednodušší spuštění).
- **Alternativní UI**: HTML (`index.html`) přes lokální Flask server (localhost) + API pro zabalení cert+key → PFX.

## Požadavky

- Windows
- Python 3.12+

## Rychlé spuštění (Streamlit)

```powershell
cd "C:\_Programs\zZHelpers"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run apps\streamlit_app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true --browser.gatherUsageStats false
```

Potom stačí už jenom: 
```powershell
.\run_streamlit.ps1
```

Otevři `http://127.0.0.1:8501/`.

## Spuštění (HTML přes Flask)

```powershell
cd "C:\_Programs\zZHelpers"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe apps\flask_app.py
```
Potom stačí už jenom: 
```powershell
.\run_flask.ps1
```

Otevři `http://127.0.0.1:5000/`.

## Poznámky k bezpečnosti

- Vše běží lokálně na tvém PC (localhost).
- Hesla a klíče se nikam neodesílají mimo tvoje zařízení.

