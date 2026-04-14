from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass
from typing import Iterable, List, Optional

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12

from .io import safe_filename


@dataclass(frozen=True)
class WrapPfxResult:
    filename: str
    pfx_bytes: bytes


@dataclass(frozen=True)
class ExtractPfxResult:
    cert_pem: str
    key_pem: str | None
    chain_pem: str | None


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
    friendly = safe_filename(friendly, default="certifikat")

    pfx_bytes = pkcs12.serialize_key_and_certificates(
        name=friendly.encode("utf-8"),
        key=private_key,
        cert=leaf_cert,
        cas=chain_certs or None,
        encryption_algorithm=serialization.BestAvailableEncryption(pfx_password.encode("utf-8")),
    )

    return WrapPfxResult(filename=f"{friendly}.pfx", pfx_bytes=pfx_bytes)


def extract_pfx(*, pfx_bytes: bytes, pfx_password: str | None) -> ExtractPfxResult:
    if not pfx_bytes:
        raise ValueError("Chybí .pfx soubor.")

    password = pfx_password.encode("utf-8") if pfx_password else None

    try:
        key, cert, cas = pkcs12.load_key_and_certificates(pfx_bytes, password)
    except Exception:
        raise ValueError("Špatné heslo nebo poškozený soubor.") from None

    if cert is None:
        raise ValueError("V souboru nebyl nalezen žádný certifikát.")

    cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")

    key_pem = None
    if key is not None:
        key_pem = key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.TraditionalOpenSSL,
            serialization.NoEncryption(),
        ).decode("utf-8")

    chain_pem = None
    if cas:
        chain_pem = "\n".join(
            ca.public_bytes(serialization.Encoding.PEM).decode("utf-8").strip()
            for ca in cas
            if ca is not None
        ).strip() or None

    return ExtractPfxResult(cert_pem=cert_pem, key_pem=key_pem, chain_pem=chain_pem)


def make_self_signed_pfx(
    *,
    common_name: str,
    organization: str = "",
    organizational_unit: str = "",
    locality: str = "",
    state: str = "",
    country: str = "",
    rsa_bits: int = 2048,
    days_valid: int = 365,
    pfx_password: str,
    pfx_password2: str,
) -> WrapPfxResult:
    cn = (common_name or "").strip()
    if not cn:
        raise ValueError("Common Name (CN) je povinný.")
    if not pfx_password:
        raise ValueError("Heslo PFX je povinné.")
    if pfx_password != pfx_password2:
        raise ValueError("Hesla PFX se neshodují.")
    if rsa_bits not in (2048, 4096):
        raise ValueError("Délka RSA klíče musí být 2048 nebo 4096.")
    if days_valid < 1 or days_valid > 9999:
        raise ValueError("Platnost musí být v rozsahu 1–9999 dnů.")

    attrs: list[x509.NameAttribute] = [x509.NameAttribute(x509.NameOID.COMMON_NAME, cn)]
    if organization.strip():
        attrs.append(x509.NameAttribute(x509.NameOID.ORGANIZATION_NAME, organization.strip()))
    if organizational_unit.strip():
        attrs.append(
            x509.NameAttribute(x509.NameOID.ORGANIZATIONAL_UNIT_NAME, organizational_unit.strip())
        )
    if locality.strip():
        attrs.append(x509.NameAttribute(x509.NameOID.LOCALITY_NAME, locality.strip()))
    if state.strip():
        attrs.append(x509.NameAttribute(x509.NameOID.STATE_OR_PROVINCE_NAME, state.strip()))
    if country.strip():
        c = country.strip().upper()
        if len(c) != 2:
            raise ValueError("Country (C) musí mít přesně 2 znaky (např. CZ).")
        attrs.append(x509.NameAttribute(x509.NameOID.COUNTRY_NAME, c))

    subject = issuer = x509.Name(attrs)

    key = rsa.generate_private_key(public_exponent=65537, key_size=rsa_bits)

    now = dt.datetime.now(dt.timezone.utc)
    cert_builder = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - dt.timedelta(minutes=1))
        .not_valid_after(now + dt.timedelta(days=days_valid))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=True,
                key_encipherment=True,
                data_encipherment=True,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.SERVER_AUTH, x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH]),
            critical=False,
        )
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(key.public_key()), critical=False)
    )

    cert = cert_builder.sign(private_key=key, algorithm=hashes.SHA256())

    friendly = safe_filename(cn, default="certifikat")
    pfx_bytes = pkcs12.serialize_key_and_certificates(
        name=friendly.encode("utf-8"),
        key=key,
        cert=cert,
        cas=None,
        encryption_algorithm=serialization.BestAvailableEncryption(pfx_password.encode("utf-8")),
    )

    return WrapPfxResult(filename=f"{friendly}.pfx", pfx_bytes=pfx_bytes)

