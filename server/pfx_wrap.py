from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional

from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12


@dataclass(frozen=True)
class WrapPfxResult:
    filename: str
    pfx_bytes: bytes


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
    return name[:80] or "certifikat"


def wrap_to_pfx(
    *,
    cert_bytes: bytes,
    key_bytes: bytes,
    chain_bytes: bytes = b"",
    pfx_password: str,
    pfx_password2: str,
    key_password: Optional[str] = None,
    friendly_name: Optional[str] = None,
) -> WrapPfxResult:
    if not cert_bytes:
        raise ValueError("Chybí certifikát.")
    if not key_bytes:
        raise ValueError("Chybí privátní klíč.")
    if not pfx_password:
        raise ValueError("Heslo PFX je povinné.")
    if pfx_password != pfx_password2:
        raise ValueError("Hesla PFX se neshodují.")

    leaf_cert = _load_leaf_certificate(cert_bytes)
    private_key = _load_private_key(key_bytes, key_password)
    chain_certs = _load_chain_certificates(chain_bytes) if chain_bytes else []

    friendly = friendly_name or _friendly_name_from_cert(leaf_cert)
    friendly = _safe_filename(friendly)

    pfx_bytes = pkcs12.serialize_key_and_certificates(
        name=friendly.encode("utf-8"),
        key=private_key,
        cert=leaf_cert,
        cas=chain_certs or None,
        encryption_algorithm=serialization.BestAvailableEncryption(pfx_password.encode("utf-8")),
    )

    return WrapPfxResult(filename=f"{friendly}.pfx", pfx_bytes=pfx_bytes)

