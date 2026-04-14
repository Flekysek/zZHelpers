from __future__ import annotations

from flask import Blueprint, Response, jsonify

bp = Blueprint("meta", __name__)

_HTML = """<!DOCTYPE html>
<html lang="cs">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>zZHelpers API</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 42rem; margin: 2rem auto; padding: 0 1rem; line-height: 1.5; }
    code { background: #f4f4f5; padding: 0.1em 0.35em; border-radius: 4px; }
    h1 { font-size: 1.25rem; }
    ul { padding-left: 1.25rem; }
    .hint { color: #52525b; font-size: 0.9rem; margin-top: 2rem; }
  </style>
</head>
<body>
  <h1>zZHelpers API</h1>
  <p>Backend běží. UI (Streamlit) je na <code>http://127.0.0.1:8501</code>.</p>
  <p><strong>Rychlá kontrola:</strong> <a href="/api/health"><code>GET /api/health</code></a> → mělo by vrátit <code>ok</code>.</p>
  <p><strong>Endpointy</strong> (podrobnosti v README):</p>
  <ul>
    <li><code>GET /api/health</code></li>
    <li><code>POST /api/convert/base64</code> (JSON)</li>
    <li><code>POST /api/image/reformat</code>, <code>POST /api/image/compress</code> (multipart)</li>
    <li><code>POST /api/pfx/make-self-signed</code> (JSON)</li>
    <li><code>POST /api/pfx/extract</code>, <code>POST /api/pfx/wrap</code>, <code>POST /api/wrap-pfx</code> (multipart)</li>
  </ul>
  <p>Strojově čitelný seznam: <a href="/api"><code>GET /api</code></a> (JSON).</p>
  <p class="hint">404 na kořenové adrese už neuvidíš — dřív tu žádná stránka nebyla, proto prohlížeč hlásil Not Found.</p>
</body>
</html>
"""


@bp.get("/")
def index() -> Response:
    return Response(_HTML, mimetype="text/html; charset=utf-8", headers={"Cache-Control": "no-store"})


@bp.get("/api")
def api_index():
    return jsonify(
        {
            "service": "zZHelpers",
            "ui": "http://127.0.0.1:8501",
            "endpoints": [
                {"method": "GET", "path": "/api/health", "note": "plain text ok"},
                {"method": "GET", "path": "/", "note": "this HTML page"},
                {"method": "GET", "path": "/api", "note": "this JSON"},
                {"method": "POST", "path": "/api/convert/base64"},
                {"method": "POST", "path": "/api/image/reformat"},
                {"method": "POST", "path": "/api/image/compress"},
                {"method": "POST", "path": "/api/pfx/make-self-signed"},
                {"method": "POST", "path": "/api/pfx/extract"},
                {"method": "POST", "path": "/api/pfx/wrap"},
                {"method": "POST", "path": "/api/wrap-pfx", "note": "alias of /api/pfx/wrap"},
            ],
        }
    )
