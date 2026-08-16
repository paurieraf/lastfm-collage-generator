import os
from PIL import ImageFont
from lastfmcollagegenerator.typography import (
    wrap_text_to_width,
    get_auto_scaled_font,
)


def _get_default_font():
    font_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "src",
        "lastfmcollagegenerator",
        "fonts",
        "DejaVuSansMono.ttf",
    )
    return os.path.abspath(font_path)


def test_wrap_text_empty():
    font_path = _get_default_font()
    font = ImageFont.truetype(font_path, 15)
    assert wrap_text_to_width(font, "", 200) == ""
    assert wrap_text_to_width(font, "   ", 200) == "   "


def test_wrap_text_word_boundary():
    font_path = _get_default_font()
    font = ImageFont.truetype(font_path, 15)
    text = "The Quick Brown Fox Jumps Over The Lazy Dog"
    wrapped = wrap_text_to_width(font, text, max_width=150)
    lines = wrapped.split("\n")
    assert len(lines) > 1
    # Check that words are not awkwardly cut
    for line in lines:
        assert font.getlength(line) <= 150


def test_wrap_text_long_token_character_split():
    font_path = _get_default_font()
    font = ImageFont.truetype(font_path, 15)
    text = "SupercalifragilisticexpialidociousIsVeryLongWord"
    wrapped = wrap_text_to_width(font, text, max_width=100)
    lines = wrapped.split("\n")
    assert len(lines) > 1
    for line in lines:
        assert font.getlength(line) <= 100


def test_wrap_text_max_lines():
    font_path = _get_default_font()
    font = ImageFont.truetype(font_path, 15)
    text = "Line one line two line three line four line five line six"
    wrapped = wrap_text_to_width(font, text, max_width=100, max_lines=2)
    lines = wrapped.split("\n")
    assert len(lines) <= 2
    assert lines[-1].endswith("...")


def test_get_auto_scaled_font_downscaling():
    font_path = _get_default_font()
    long_text = (
        "Extremely Long Artist Name - Super Extended Deluxe Edition "
        "Album Title With Bonus Tracks (2026 Remaster)"
    )
    font, wrapped = get_auto_scaled_font(
        font_path=font_path,
        base_font_size=16,
        text=long_text,
        max_width=200,
        max_height=50,
        min_font_size=8,
    )
    assert font.size <= 16
    assert isinstance(wrapped, str)
    assert len(wrapped) > 0


def test_get_auto_scaled_font_invalid_path_fallback():
    font, wrapped = get_auto_scaled_font(
        font_path="/invalid/non_existent_font.ttf",
        base_font_size=15,
        text="Sample Text",
        max_width=200,
        max_height=50,
    )
    assert font is not None
    assert "Sample Text" in wrapped
