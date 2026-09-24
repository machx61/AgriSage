"""Image helpers."""

import io

from PIL import Image, ImageOps


def make_jpeg(image_bytes: bytes, max_side: int, quality: int = 80) -> bytes:
    """Return a resized RGB JPEG. Handles PNG transparency and phone rotation."""
    with Image.open(io.BytesIO(image_bytes)) as source:
        image = ImageOps.exif_transpose(source).convert("RGB")
    image.thumbnail((max_side, max_side))
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=quality)
    return buffer.getvalue()
