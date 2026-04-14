# zZHelpers (ZzTools)

Sada jednoduchých lokálních helperů v Pythonu.

- **UI (View)**: Streamlit na `http://127.0.0.1:8501`.
- **Backend (API)**: Flask na `http://127.0.0.1:5000` (Streamlit volá nástroje přes endpointy).

## Požadavky

- Windows
- Python 3.12+

## Spuštění (jeden příkaz – API i Streamlit)

```powershell
cd "C:\_Programs\zZHelpers"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run.py
```

Nebo z rootu repa:

```powershell
.\run.ps1
```

```bat
run.cmd
```

- API: `GET http://127.0.0.1:5000/api/health` → `ok`
- UI: `http://127.0.0.1:8501/`

## Struktura repozitáře

| Cesta | Účel |
|-------|------|
| `zzhelpers/` | Sdílená logika (base64, obrázky, PFX) |
| `apps/endpoints/` | Flask endpointy (Blueprints) |
| `apps/flask_app.py` | Flask REST API (registruje endpointy) |
| `apps/view/` | View vrstva (Streamlit UI) |
| `apps/streamlit_app.py` | Streamlit entrypoint (volá view) |
| `run.py`, `run.cmd`, `run.ps1` | Spuštění API + Streamlit najednou |

## Poznámky k bezpečnosti

- Vše běží lokálně na tvém PC (localhost).
- Hesla a klíče se nikam neodesílají mimo tvoje zařízení.
