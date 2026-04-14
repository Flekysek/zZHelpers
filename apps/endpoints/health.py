from __future__ import annotations

from flask import Blueprint, Response

bp = Blueprint("health", __name__)


@bp.get("/api/health")
def health() -> Response:
    return Response("ok", mimetype="text/plain; charset=utf-8", headers={"Cache-Control": "no-store"})

