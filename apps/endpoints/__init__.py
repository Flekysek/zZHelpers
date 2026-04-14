from __future__ import annotations

from flask import Blueprint

from .convert import bp as convert_bp
from .health import bp as health_bp
from .image import bp as image_bp
from .pfx import bp as pfx_bp


def build_api_blueprint() -> Blueprint:
    """
    Single API blueprint mounting all endpoint groups under one place.
    """
    api = Blueprint("api", __name__)
    api.register_blueprint(health_bp)
    api.register_blueprint(convert_bp)
    api.register_blueprint(image_bp)
    api.register_blueprint(pfx_bp)
    return api

