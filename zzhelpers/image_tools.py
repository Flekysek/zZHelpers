from __future__ import annotations

import io
from dataclasses import dataclass
from typing import Literal

from PIL import Image, ImageOps


ImageFormat = Literal["PNG", "JPEG"]


@dataclass(frozen=True)
class ImageTransformResult:
    filename: str
    mime: str
    data: bytes
    width: int
    height: int


def _open_image(data: bytes) -> Image.Image:
    if not data:
        raise ValueError("Chybí obrázek.")
    try:
        img = Image.open(io.BytesIO(data))
        img = ImageOps.exif_transpose(img)
        return img
    except Exception:
        raise ValueError("Neplatný obrázek (nelze načíst).") from None


def compress_or_resize(
    *,
    image_bytes: bytes,
    out_format: ImageFormat,
    scale_percent: int = 100,
    jpeg_quality: int = 85,
    filename_base: str = "image",
) -> ImageTransformResult:
    img = _open_image(image_bytes)

    scale_percent = int(scale_percent)
    if scale_percent < 5 or scale_percent > 100:
        raise ValueError("Zmenšení rozlišení musí být v rozsahu 5–100 %.")

    w, h = img.size
    new_w = max(1, round(w * scale_percent / 100))
    new_h = max(1, round(h * scale_percent / 100))

    if (new_w, new_h) != (w, h):
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    buf = io.BytesIO()
    if out_format == "PNG":
        img.save(buf, format="PNG", optimize=True)
        ext = "png"
        mime = "image/png"
    else:
        jpeg_quality = int(jpeg_quality)
        if jpeg_quality < 1 or jpeg_quality > 100:
            raise ValueError("Kvalita JPG musí být v rozsahu 1–100 %.")

        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        img.save(buf, format="JPEG", quality=jpeg_quality, optimize=True, progressive=True)
        ext = "jpg"
        mime = "image/jpeg"

    data = buf.getvalue()
    return ImageTransformResult(
        filename=f"{filename_base}_out.{ext}",
        mime=mime,
        data=data,
        width=new_w,
        height=new_h,
    )


def reformat(
    *,
    image_bytes: bytes,
    out_format: ImageFormat,
    jpeg_quality: int = 92,
    filename_base: str = "image",
) -> ImageTransformResult:
    # Reformat = no resize by default; just re-encode.
    return compress_or_resize(
        image_bytes=image_bytes,
        out_format=out_format,
        scale_percent=100,
        jpeg_quality=jpeg_quality,
        filename_base=filename_base,
    )

