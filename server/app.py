from __future__ import annotations

import os
import re
from typing import List, Optional, Tuple

from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
from flask import Flask, Response, abort, request, send_from_directory


APP_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

app = Flask(__name__, static_folder=None)


def _is_probably_pem(data: bytes) -> bool:
    return b"-----BEGIN " in data


def _load_leaf_certificate(cert_bytes: bytes) -> x509.Certificate:
    if _is_probably_pem(cert_bytes):
        return x509.load_pem_x509_certificate(cert_bytes)
    return x509.load_der_x509_certificate(cert_bytes)


_PEM_CERT_RE = re.compile(
    br"-----BEGIN CERTIFICATE-----\s+.*?\s+-----END CERTIFICATE-----",
    re.DOTALL,
)


def _load_chain_certificates(chain_bytes: bytes) -> List[x509.Certificate]:
    if not chain_bytes:
        return []
    if not _is_probably_pem(chain_bytes):
        raise ValueError("CA řetězec musí být v PEM formátu (BEGIN CERTIFICATE).")

    blocks = _PEM_CERT_RE.findall(chain_bytes)
    if not blocks:
        raise ValueError("CA řetězec neobsahuje žádný PEM certifikát.")

    return [x509.load_pem_x509_certificate(b) for b in blocks]


def _load_private_key(key_bytes: bytes, key_password: Optional[str]):
    password_bytes = key_password.encode("utf-8") if key_password else None

    if _is_probably_pem(key_bytes):
        return serialization.load_pem_private_key(key_bytes, password=password_bytes)

    # Záměrně nepodporujeme DER klíče bez potřeby (KEY bývá PEM).
    raise ValueError("Privátní klíč musí být v PEM formátu (BEGIN ... PRIVATE KEY).")


def _friendly_name_from_cert(cert: x509.Certificate) -> str:
    try:
        cn = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)
        if cn and cn[0].value:
            return str(cn[0].value)
    except Exception:
        pass
    return "certifikat"


def _safe_filename(name: str) -> str:
    name = (name or "").strip()
    name = re.sub(r'[<>:"/\\\\|?*\\x00-\\x1F]+', "_", name)
    name = re.sub(r"\\s+", "_", name)
    return (name[:80] or "certifikat")


def _get_form_value(key: str) -> str:
    v = request.form.get(key, "")
    if v is None:
        return ""
    return str(v)


def _get_file_bytes(field_name: str, required: bool) -> bytes:
    f = request.files.get(field_name)
    if f is None:
        if required:
            raise ValueError(f"Chybí soubor: {field_name}")
        return b""
    data = f.read()
    if required and not data:
        raise ValueError(f"Soubor je prázdný: {field_name}")
    return data


@app.get("/")
def index() -> Response:
    return send_from_directory(APP_ROOT, "index.html")


@app.get("/controller.js")
def controller_js() -> Response:
    return send_from_directory(APP_ROOT, "controller.js")


@app.get("/LogoZz.jpg")
def logo() -> Response:
    return send_from_directory(APP_ROOT, "LogoZz.jpg")


@app.post("/api/wrap-pfx")
def wrap_pfx() -> Response:
    try:
        cert_bytes = _get_file_bytes("cert", required=True)
        key_bytes = _get_file_bytes("key", required=True)
        chain_bytes = _get_file_bytes("chain", required=False)

        pfx_password = _get_form_value("pfxPassword")
        pfx_password2 = _get_form_value("pfxPassword2")
        key_password = _get_form_value("keyPassword") or None
        friendly_override = _get_form_value("friendlyName").strip() or None

        if not pfx_password:
            raise ValueError("Heslo PFX je povinné.")
        if pfx_password != pfx_password2:
            raise ValueError("Hesla PFX se neshodují.")

        leaf_cert = _load_leaf_certificate(cert_bytes)
        private_key = _load_private_key(key_bytes, key_password)
        chain_certs = _load_chain_certificates(chain_bytes) if chain_bytes else []

        friendly = friendly_override or _friendly_name_from_cert(leaf_cert)
        friendly = _safe_filename(friendly)

        pfx_bytes = pkcs12.serialize_key_and_certificates(
            name=friendly.encode("utf-8"),
            key=private_key,
            cert=leaf_cert,
            cas=chain_certs or None,
            encryption_algorithm=serialization.BestAvailableEncryption(
                pfx_password.encode("utf-8")
            ),
        )

        filename = f"{friendly}.pfx"
        return Response(
            pfx_bytes,
            mimetype="application/x-pkcs12",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Cache-Control": "no-store",
            },
        )
    except ValueError as e:
        msg = str(e) or "Neplatné vstupy."
        if "Bad decrypt" in msg or "bad decrypt" in msg:
            msg = "Špatné heslo ke klíči (nebo klíč nelze dešifrovat)."
        return Response(msg, status=400, mimetype="text/plain; charset=utf-8")
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


def main() -> None:
    app.run(host="127.0.0.1", port=5000, debug=False)


if __name__ == "__main__":
    main()
