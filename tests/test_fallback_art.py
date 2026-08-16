from io import BytesIO

from PIL import Image

from lastfmcollagegenerator.fallback_art import (
    FALLBACK_STYLE_BLACK,
    FALLBACK_STYLE_GRADIENT,
    FALLBACK_STYLES,
    generate_blank_tile,
    generate_fallback_tile,
)


def test_gradient_tile_is_deterministic():
    first = generate_fallback_tile("Radiohead - OK Computer")
    second = generate_fallback_tile("Radiohead - OK Computer")
    assert first == second


def test_gradient_tiles_differ_per_title():
    a = generate_fallback_tile("Album A")
    b = generate_fallback_tile("Album B")
    assert a != b


def test_gradient_tile_dimensions_and_mode():
    data = generate_fallback_tile("Some Title", 120, 90)
    with Image.open(BytesIO(data)) as img:
        assert img.size == (120, 90)
        assert img.mode == "RGB"


def test_gradient_tile_is_not_black():
    data = generate_fallback_tile("Some Title")
    with Image.open(BytesIO(data)) as img:
        assert img.getpixel((0, 0)) != (0, 0, 0)
        assert img.getpixel((150, 150)) != (0, 0, 0)


def test_legacy_black_tile():
    data = generate_blank_tile()
    with Image.open(BytesIO(data)) as img:
        assert img.size == (300, 300)
        assert img.mode == "RGB"
        assert img.getpixel((0, 0)) == (0, 0, 0)


def test_fallback_styles_constant():
    assert FALLBACK_STYLE_GRADIENT == "gradient"
    assert FALLBACK_STYLE_BLACK == "black"
    assert FALLBACK_STYLES == (FALLBACK_STYLE_GRADIENT, FALLBACK_STYLE_BLACK)


def test_empty_title_does_not_crash():
    data = generate_fallback_tile("")
    assert isinstance(data, bytes)
    with Image.open(BytesIO(data)) as img:
        assert img.size == (300, 300)
