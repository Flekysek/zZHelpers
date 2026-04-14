from __future__ import annotations

from flask import Flask

from apps.endpoints import build_api_blueprint

app = Flask(__name__, static_folder=None)
app.register_blueprint(build_api_blueprint())


def main() -> None:
    app.run(host="127.0.0.1", port=5000, debug=False)


if __name__ == "__main__":
    main()

