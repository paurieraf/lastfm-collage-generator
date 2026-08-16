import colorsys
import hashlib
import os
import random
from io import BytesIO
from typing import Any, Tuple

from PIL import Image, ImageDraw, ImageFont

FALLBACK_STYLE_GRADIENT = "gradient"
FALLBACK_STYLE_BLACK = "black"
FALLBACK_STYLES = (FALLBACK_STYLE_GRADIENT, FALLBACK_STYLE_BLACK)

_FONT_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "fonts", "DejaVuSansMono-Bold.ttf"
)

_PASTEL_SATURATION = 0.45
_PASTEL_VALUE = 0.88


def _derive_seed(title: str) -> int:
    digest = hashlib.sha256(title.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def _pastel_color(rng: random.Random) -> Tuple[int, int, int]:
    hue = rng.random()
    r, g, b = colorsys.hsv_to_rgb(hue, _PASTEL_SATURATION, _PASTEL_VALUE)
    return (int(r * 255), int(g * 255), int(b * 255))


def _initials(title: str) -> str:
    words = [word for word in title.split() if word]
    letters = []
    for word in words[:2]:
        for char in word:
            if char.isalnum():
                letters.append(char.upper())
                break
    if not letters:
        return "?"
    return "".join(letters)


def _load_font(size: int) -> Any:
    try:
        return ImageFont.truetype(_FONT_PATH, size)
    except OSError:
        return ImageFont.load_default()


def generate_fallback_tile(title: str, width: int = 300, height: int = 300) -> bytes:
    """Generate a deterministic gradient fallback tile for an entity title.

    Colors and initials are derived from a SHA-256 hash of the title so
    the same entity always produces byte-identical artwork.
    """
    seed = _derive_seed(title)
    rng = random.Random(seed)
    top_color = _pastel_color(rng)
    bottom_color = _pastel_color(rng)

    with Image.new("RGB", (width, height)) as img:
        draw = ImageDraw.Draw(img)
        for y in range(height):
            ratio = y / float(height)
            color = tuple(
                int(top_color[i] + (bottom_color[i] - top_color[i]) * ratio)
                for i in range(3)
            )
            draw.line([(0, y), (width, y)], fill=color)

        initials = _initials(title)
        font_size = max(8, min(width, height) // 4)
        font = _load_font(font_size)
        draw.text(
            (width // 2, height // 2),
            initials,
            fill=(255, 255, 255),
            font=font,
            anchor="mm",
        )

        with BytesIO() as buf:
            img.save(buf, format="png")
            return buf.getvalue()


def generate_blank_tile(width: int = 300, height: int = 300) -> bytes:
    """Legacy solid black fallback tile."""
    with Image.new("RGB", (width, height)) as img:
        with BytesIO() as buf:
            img.save(buf, format="png")
            return buf.getvalue()
