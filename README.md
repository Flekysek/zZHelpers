# zZHelpers (ZzTools)

Sada jednoduchých lokálních helperů v Pythonu.

- **UI (View)**: Streamlit na `http://127.0.0.1:8501`.
- **Backend (API)**: Flask na `http://127.0.0.1:5000` (Streamlit volá nástroje přes endpointy).

## Požadavky

- Windows nebo macOS / Linux
- Python 3.12+

## Spuštění (jeden příkaz – API i Streamlit)

### macOS / Linux (zsh, bash)

`run.cmd` a `run.ps1` jsou určené pro **Windows**. Na Macu použij jednu z možností:

```bash
cd /cesta/k/zZHelpers
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python run.py
```

Nebo po jednorázovém `chmod +x run.sh run.py`:

```bash
./run.sh
# nebo
./run.py
```

Na Unixu musí mít skript **právo spuštění** (`chmod +x`), jinak `./run.py` skončí na `permission denied`. Bez `chmod` vždy funguje `python3 run.py`.

### Windows (PowerShell / CMD)

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
| `run.py`, `run.sh`, `run.cmd`, `run.ps1` | Spuštění API + Streamlit (`run.sh` / přímé `python` = Mac/Linux; `.cmd`/`.ps1` = Windows) |

## Poznámky k bezpečnosti

- Vše běží lokálně na tvém PC (localhost).
- Hesla a klíče se nikam neodesílají mimo tvoje zařízení.
