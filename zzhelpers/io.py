from __future__ import annotations

import re


def safe_filename(name: str, *, default: str = "output", max_len: int = 80) -> str:
    name = (name or "").strip()
    name = re.sub(r'[<>:"/\\\\|?*\\x00-\\x1F]+', "_", name)
    name = re.sub(r"\s+", "_", name)
    return (name[:max_len] or default)


def fmt_bytes(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n/1024:.1f} KB"
    return f"{n/(1024*1024):.2f} MB"

