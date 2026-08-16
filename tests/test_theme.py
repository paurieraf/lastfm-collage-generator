import pytest
from lastfmcollagegenerator.theme import (
    Theme,
    THEME_PRESETS,
    resolve_theme,
    _parse_color,
)
from lastfmcollagegenerator.constants import (
    THEME_DARK,
    THEME_LIGHT,
    THEME_GLASSMORPHIC,
    THEME_SUNSET,
    THEME_NEON,
)


def test_theme_presets_defined():
    for name in [
        THEME_DARK,
        THEME_LIGHT,
        THEME_GLASSMORPHIC,
        THEME_SUNSET,
        THEME_NEON,
    ]:
        assert name in THEME_PRESETS
        preset = THEME_PRESETS[name]
        assert isinstance(preset, Theme)
        assert len(preset.overlay_bg) == 4
        assert len(preset.text_color) == 3


def test_resolve_theme_from_string():
    theme = resolve_theme("dark")
    assert theme == THEME_PRESETS[THEME_DARK]

    theme_light = resolve_theme("LIGHT")
    assert theme_light == THEME_PRESETS[THEME_LIGHT]


def test_resolve_theme_from_instance():
    custom = Theme(
        name="custom",
        overlay_bg=(10, 20, 30, 100),
        text_color=(200, 210, 220),
    )
    assert resolve_theme(custom) is custom


def test_resolve_theme_from_dict():
    theme_dict = {
        "name": "my_theme",
        "overlay_bg": "#11223380",
        "text_color": "#ffffff",
        "accent_color": (255, 200, 100, 150),
    }
    theme = resolve_theme(theme_dict)
    assert theme.name == "my_theme"
    assert theme.overlay_bg == (0x11, 0x22, 0x33, 0x80)
    assert theme.text_color == (255, 255, 255)
    assert theme.accent_color == (255, 200, 100, 150)


def test_resolve_theme_unknown_preset():
    with pytest.raises(ValueError, match="Unknown theme preset"):
        resolve_theme("non_existent_preset")


def test_resolve_theme_invalid_type():
    with pytest.raises(TypeError, match="Theme must be a preset string"):
        resolve_theme(123)


def test_parse_color_helpers():
    assert _parse_color("#aabbcc", default_alpha=200) == (
        0xAA,
        0xBB,
        0xCC,
        200,
    )
    assert _parse_color("#aabbccdd") == (0xAA, 0xBB, 0xCC, 0xDD)
    assert _parse_color((1, 2, 3), default_alpha=50) == (1, 2, 3, 50)
    assert _parse_color((1, 2, 3, 4)) == (1, 2, 3, 4)

    with pytest.raises(ValueError, match="Invalid hex color string"):
        _parse_color("#12345")

    with pytest.raises(ValueError, match="Color tuple must have 3 or 4"):
        _parse_color((1, 2))

    with pytest.raises(TypeError, match="Unsupported color type"):
        _parse_color(object())
