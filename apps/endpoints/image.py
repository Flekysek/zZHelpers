from __future__ import annotations

from flask import Blueprint, Response, request

from zzhelpers.image_tools import compress_or_resize, reformat
from zzhelpers.io import safe_filename

bp = Blueprint("image", __name__)


def _get_upload_bytes(field: str) -> tuple[bytes, str]:
    f = request.files.get(field)
    if not f or not f.readable():
        raise ValueError(f"Chybí soubor: {field}")
    data = f.read()
    if not data:
        raise ValueError(f"Soubor je prázdný: {field}")
    return data, (f.filename or "")


@bp.post("/api/image/reformat")
def image_reformat() -> Response:
    try:
        img_bytes, orig_name = _get_upload_bytes("file")
        out = (request.form.get("out") or "png").strip().upper()
        if out not in ("PNG", "JPEG"):
            raise ValueError("Neplatný formát výstupu. Povolené: PNG/JPEG.")

        jpeg_quality = int((request.form.get("jpeg_quality") or "92").strip())
        filename_base = safe_filename(
            (request.form.get("filename_base") or orig_name.rsplit(".", 1)[0] or "image").strip(),
            default="image",
        )

        res = reformat(
            image_bytes=img_bytes,
            out_format=out,  # type: ignore[arg-type]
            jpeg_quality=jpeg_quality,
            filename_base=filename_base,
        )

        return Response(
            res.data,
            mimetype=res.mime,
            headers={
                "Content-Disposition": f'attachment; filename="{res.filename}"',
                "Cache-Control": "no-store",
            },
        )
    except ValueError as e:
        return Response(str(e) or "Neplatné vstupy.", status=400, mimetype="text/plain; charset=utf-8")
    except Exception:
        return Response("Neočekávaná chyba při převodu obrázku.", status=500, mimetype="text/plain; charset=utf-8")


@bp.post("/api/image/compress")
def image_compress() -> Response:
    try:
        img_bytes, orig_name = _get_upload_bytes("file")
        out = (request.form.get("out") or "JPEG").strip().upper()
        if out not in ("PNG", "JPEG"):
            raise ValueError("Neplatný formát výstupu. Povolené: PNG/JPEG.")

        scale_percent = int((request.form.get("scale_percent") or "100").strip())
        jpeg_quality = int((request.form.get("jpeg_quality") or "85").strip())
        filename_base = safe_filename(
            (request.form.get("filename_base") or orig_name.rsplit(".", 1)[0] or "image").strip(),
            default="image",
        )

        res = compress_or_resize(
            image_bytes=img_bytes,
            out_format=out,  # type: ignore[arg-type]
            scale_percent=scale_percent,
            jpeg_quality=jpeg_quality,
            filename_base=filename_base,
        )

        return Response(
            res.data,
            mimetype=res.mime,
            headers={
                "Content-Disposition": f'attachment; filename="{res.filename}"',
                "Cache-Control": "no-store",
            },
        )
    except ValueError as e:
        return Response(str(e) or "Neplatné vstupy.", status=400, mimetype="text/plain; charset=utf-8")
    except Exception:
        return Response("Neočekávaná chyba při kompresi obrázku.", status=500, mimetype="text/plain; charset=utf-8")

