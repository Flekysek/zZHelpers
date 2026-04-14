from __future__ import annotations

from dataclasses import asdict

from flask import Flask, Response, jsonify, request

from zzhelpers.base64_tools import decode_base64_text
from zzhelpers.image_tools import compress_or_resize, reformat
from zzhelpers.io import safe_filename
from zzhelpers.pfx_tools import extract_pfx, make_self_signed_pfx, wrap_to_pfx


app = Flask(__name__, static_folder=None)


@app.get("/api/health")
def health() -> Response:
    return Response("ok", mimetype="text/plain; charset=utf-8", headers={"Cache-Control": "no-store"})


@app.post("/api/wrap-pfx")
def api_wrap_pfx() -> Response:
    try:
        cert_f = request.files.get("cert")
        key_f = request.files.get("key")
        chain_f = request.files.get("chain")

        if not cert_f or not cert_f.readable():
            raise ValueError("Chybí soubor: cert")
        if not key_f or not key_f.readable():
            raise ValueError("Chybí soubor: key")

        cert_bytes = cert_f.read()
        key_bytes = key_f.read()
        chain_bytes = chain_f.read() if chain_f else b""

        pfx_password = (request.form.get("pfxPassword") or "").strip()
        pfx_password2 = (request.form.get("pfxPassword2") or "").strip()
        key_password = (request.form.get("keyPassword") or "").strip() or None
        friendly_name = (request.form.get("friendlyName") or "").strip() or None

        res = wrap_to_pfx(
            cert_bytes=cert_bytes,
            key_bytes=key_bytes,
            chain_bytes=chain_bytes,
            pfx_password=pfx_password,
            pfx_password2=pfx_password2,
            key_password=key_password,
            friendly_name=friendly_name,
        )

        return Response(
            res.pfx_bytes,
            mimetype="application/x-pkcs12",
            headers={
                "Content-Disposition": f'attachment; filename="{res.filename}"',
                "Cache-Control": "no-store",
            },
        )
    except ValueError as e:
        return Response(str(e) or "Neplatné vstupy.", status=400, mimetype="text/plain; charset=utf-8")
    except TypeError:
        return Response(
            "Špatné heslo ke klíči nebo neplatný formát privátního klíče.",
            status=400,
            mimetype="text/plain; charset=utf-8",
        )
    except Exception:
        return Response(
            "Neočekávaná chyba při balení. Zkontroluj vstupy (cert/key/chain) a hesla.",
            status=500,
            mimetype="text/plain; charset=utf-8",
        )


@app.post("/api/pfx/wrap")
def api_pfx_wrap() -> Response:
    # Alias endpoint with consistent naming. Keep /api/wrap-pfx for compatibility.
    return api_wrap_pfx()


@app.post("/api/convert/base64")
def api_convert_base64() -> Response:
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


def _get_upload_bytes(field: str) -> tuple[bytes, str]:
    f = request.files.get(field)
    if not f or not f.readable():
        raise ValueError(f"Chybí soubor: {field}")
    data = f.read()
    if not data:
        raise ValueError(f"Soubor je prázdný: {field}")
    return data, (f.filename or "")


@app.post("/api/image/reformat")
def api_image_reformat() -> Response:
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


@app.post("/api/image/compress")
def api_image_compress() -> Response:
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


@app.post("/api/pfx/make-self-signed")
def api_pfx_make_self_signed() -> Response:
    try:
        payload = request.get_json(silent=True) or {}
        if not isinstance(payload, dict):
            raise ValueError("Neplatné JSON tělo požadavku.")

        res = make_self_signed_pfx(
            common_name=str(payload.get("common_name") or ""),
            organization=str(payload.get("organization") or ""),
            organizational_unit=str(payload.get("organizational_unit") or ""),
            locality=str(payload.get("locality") or ""),
            state=str(payload.get("state") or ""),
            country=str(payload.get("country") or ""),
            rsa_bits=int(payload.get("rsa_bits") or 2048),
            days_valid=int(payload.get("days_valid") or 365),
            pfx_password=str(payload.get("pfx_password") or ""),
            pfx_password2=str(payload.get("pfx_password2") or ""),
        )

        return Response(
            res.pfx_bytes,
            mimetype="application/x-pkcs12",
            headers={
                "Content-Disposition": f'attachment; filename="{res.filename}"',
                "Cache-Control": "no-store",
            },
        )
    except ValueError as e:
        return Response(str(e) or "Neplatné vstupy.", status=400, mimetype="text/plain; charset=utf-8")
    except Exception:
        return Response("Neočekávaná chyba při generování PFX.", status=500, mimetype="text/plain; charset=utf-8")


@app.post("/api/pfx/extract")
def api_pfx_extract() -> Response:
    try:
        pfx_bytes, _ = _get_upload_bytes("file")
        pfx_password = (request.form.get("pass") or "").strip() or None
        res = extract_pfx(pfx_bytes=pfx_bytes, pfx_password=pfx_password)
        return jsonify(asdict(res))
    except ValueError as e:
        return Response(str(e) or "Neplatné vstupy.", status=400, mimetype="text/plain; charset=utf-8")
    except Exception:
        return Response("Neočekávaná chyba při rozbalování PFX.", status=500, mimetype="text/plain; charset=utf-8")


def main() -> None:
    app.run(host="127.0.0.1", port=5000, debug=False)


if __name__ == "__main__":
    main()

