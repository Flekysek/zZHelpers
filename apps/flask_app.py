from __future__ import annotations

import sys
from pathlib import Path

# Spuštění přes `python apps/flask_app.py` přidá do sys.path jen `apps/` — bez tohoto nejde importovat balíček `apps`.
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from flask import Flask

from apps.endpoints import build_api_blueprint

app = Flask(__name__, static_folder=None)
app.register_blueprint(build_api_blueprint())


def main() -> None:
    app.run(host="127.0.0.1", port=5000, debug=False)


if __name__ == "__main__":
    main()

