from __future__ import annotations

import base64
import binascii
import re
from dataclasses import dataclass


_DATA_URL_RE = re.compile(r"^\s*data:(?P<mime>[^;]+);base64,(?P<data>.*)\s*$", re.DOTALL)


@dataclass(frozen=True)
class Base64DecodeResult:
    data: bytes
    detected_mime: str | None


def decode_base64_text(text: str) -> Base64DecodeResult:
    """
    Accepts raw base64 OR a full data URL: data:<mime>;base64,<payload>.
    Returns bytes and optional detected mime from data URL.
    """
    if text is None:
        raise ValueError("Chybí vstupní text.")

    s = text.strip()
    if not s:
        raise ValueError("Chybí base64 řetězec.")

    detected_mime = None
    m = _DATA_URL_RE.match(s)
    if m:
        detected_mime = m.group("mime").strip() or None
        s = m.group("data").strip()

    # tolerate whitespace/newlines
    s = re.sub(r"\s+", "", s)

    try:
        data = base64.b64decode(s, validate=True)
    except (binascii.Error, ValueError):
        raise ValueError("Neplatný base64 řetězec.") from None

    if not data:
        raise ValueError("Base64 se dekódovalo na prázdná data.")

    return Base64DecodeResult(data=data, detected_mime=detected_mime)

