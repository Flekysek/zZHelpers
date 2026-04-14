from __future__ import annotations

from dataclasses import asdict

from flask import Blueprint, Response, jsonify, request

from zzhelpers.pfx_tools import extract_pfx, make_self_signed_pfx, wrap_to_pfx

bp = Blueprint("pfx", __name__)


def _get_upload_bytes(field: str) -> tuple[bytes, str]:
    f = request.files.get(field)
    if not f or not f.readable():
        raise ValueError(f"Chybí soubor: {field}")
    data = f.read()
    if not data:
        raise ValueError(f"Soubor je prázdný: {field}")
    return data, (f.filename or "")


@bp.post("/api/wrap-pfx")
def wrap_pfx_compat() -> Response:
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


@bp.post("/api/pfx/wrap")
def wrap_pfx() -> Response:
    # Alias endpoint with consistent naming. Keep /api/wrap-pfx for compatibility.
    return wrap_pfx_compat()


@bp.post("/api/pfx/make-self-signed")
def make_self_signed() -> Response:
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


@bp.post("/api/pfx/extract")
def extract() -> Response:
    try:
        pfx_bytes, _ = _get_upload_bytes("file")
        pfx_password = (request.form.get("pass") or "").strip() or None
        res = extract_pfx(pfx_bytes=pfx_bytes, pfx_password=pfx_password)
        return jsonify(asdict(res))
    except ValueError as e:
        return Response(str(e) or "Neplatné vstupy.", status=400, mimetype="text/plain; charset=utf-8")
    except Exception:
        return Response("Neočekávaná chyba při rozbalování PFX.", status=500, mimetype="text/plain; charset=utf-8")

