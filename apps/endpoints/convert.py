from __future__ import annotations

from flask import Blueprint, Response, request

from zzhelpers.base64_tools import decode_base64_text
from zzhelpers.io import safe_filename

bp = Blueprint("convert", __name__)


@bp.post("/api/convert/base64")
def convert_base64() -> Response:
    try:
        payload = request.get_json(silent=True) or {}
        b64 = payload.get("b64") if isinstance(payload, dict) else None
        out = (payload.get("out") if isinstance(payload, dict) else None) or "pdf"
        filename = (payload.get("filename") if isinstance(payload, dict) else None) or "zZToolExport"

        out = str(out).strip().lower()
        if out not in ("pdf", "png", "jpg", "jpeg"):
            raise ValueError("Neplatný formát výstupu. Povolené: pdf/png/jpg/jpeg.")

        res = decode_base64_text(str(b64) if b64 is not None else "")
        fname = safe_filename(str(filename), default="zZToolExport")

        mime_map = {
            "pdf": "application/pdf",
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
        }
        mime = mime_map[out]

        return Response(
            res.data,
            mimetype=mime,
            headers={
                "Content-Disposition": f'attachment; filename="{fname}.{out}"',
                "Cache-Control": "no-store",
            },
        )
    except ValueError as e:
        return Response(str(e) or "Neplatné vstupy.", status=400, mimetype="text/plain; charset=utf-8")
    except Exception:
        return Response("Neočekávaná chyba při převodu base64.", status=500, mimetype="text/plain; charset=utf-8")

