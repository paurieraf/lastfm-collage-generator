from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple, Union

from lastfmcollagegenerator.constants import (
    THEME_DARK,
    THEME_LIGHT,
    THEME_GLASSMORPHIC,
    THEME_SUNSET,
    THEME_NEON,
)


@dataclass
class Theme:
    name: str
    overlay_bg: Tuple[int, int, int, int]
    text_color: Tuple[int, int, int]
    accent_color: Optional[Tuple[int, int, int, int]] = None
    font_path: Optional[str] = None


THEME_PRESETS: Dict[str, Theme] = {
    THEME_DARK: Theme(
        name=THEME_DARK,
        overlay_bg=(0, 0, 0, 123),
        text_color=(255, 255, 255),
        accent_color=(255, 255, 255, 40),
    ),
    THEME_LIGHT: Theme(
        name=THEME_LIGHT,
        overlay_bg=(255, 255, 255, 185),
        text_color=(20, 20, 20),
        accent_color=(0, 0, 0, 30),
    ),
    THEME_GLASSMORPHIC: Theme(
        name=THEME_GLASSMORPHIC,
        overlay_bg=(255, 255, 255, 45),
        text_color=(255, 255, 255),
        accent_color=(255, 255, 255, 140),
    ),
    THEME_SUNSET: Theme(
        name=THEME_SUNSET,
        overlay_bg=(45, 15, 60, 160),
        text_color=(255, 240, 220),
        accent_color=(255, 120, 80, 200),
    ),
    THEME_NEON: Theme(
        name=THEME_NEON,
        overlay_bg=(10, 10, 25, 200),
        text_color=(0, 255, 200),
        accent_color=(0, 240, 255, 220),
    ),
}


def _parse_color(color: Any, default_alpha: int = 255) -> Tuple[int, ...]:
    if isinstance(color, str):
        c = color.lstrip("#")
        if len(c) == 6:
            r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
            return (r, g, b, default_alpha)
        elif len(c) == 8:
            r, g, b, a = (
                int(c[0:2], 16),
                int(c[2:4], 16),
                int(c[4:6], 16),
                int(c[6:8], 16),
            )
            return (r, g, b, a)
        raise ValueError(f"Invalid hex color string: {color}")
    elif isinstance(color, (list, tuple)):
        if len(color) == 3:
            return (int(color[0]), int(color[1]), int(color[2]), default_alpha)
        elif len(color) == 4:
            return (
                int(color[0]),
                int(color[1]),
                int(color[2]),
                int(color[3]),
            )
        raise ValueError(f"Color tuple must have 3 or 4 elements: {color}")
    raise TypeError(f"Unsupported color type: {type(color)}")


def parse_color(color: Any, default_alpha: int = 255) -> Tuple[int, ...]:
    """Public entrypoint for validating and normalizing color values."""
    return _parse_color(color, default_alpha)


def resolve_theme(theme: Union[str, Theme, Dict[str, Any]]) -> Theme:
    """Resolve a theme parameter into a validated Theme instance."""
    if isinstance(theme, Theme):
        return theme

    if isinstance(theme, str):
        normalized = theme.lower().strip()
        if normalized in THEME_PRESETS:
            return THEME_PRESETS[normalized]
        raise ValueError(
            f"Unknown theme preset: '{theme}'. "
            f"Available presets: {list(THEME_PRESETS.keys())}"
        )

    if isinstance(theme, dict):
        name = str(theme.get("name", "custom"))
        raw_bg = theme.get("overlay_bg", (0, 0, 0, 123))
        raw_text = theme.get("text_color", (255, 255, 255))
        raw_accent = theme.get("accent_color")
        font_path = theme.get("font_path")

        parsed_bg = _parse_color(raw_bg, default_alpha=123)
        parsed_text = _parse_color(raw_text, default_alpha=255)[:3]
        parsed_accent = (
            _parse_color(raw_accent, default_alpha=255)
            if raw_accent is not None
            else None
        )

        return Theme(
            name=name,
            overlay_bg=(
                int(parsed_bg[0]),
                int(parsed_bg[1]),
                int(parsed_bg[2]),
                int(parsed_bg[3]),
            ),
            text_color=(
                int(parsed_text[0]),
                int(parsed_text[1]),
                int(parsed_text[2]),
            ),
            accent_color=(
                (
                    int(parsed_accent[0]),
                    int(parsed_accent[1]),
                    int(parsed_accent[2]),
                    int(parsed_accent[3]),
                )
                if parsed_accent is not None
                else None
            ),
            font_path=font_path,
        )

    raise TypeError(
        f"Theme must be a preset string, Theme instance, or dictionary, "
        f"got {type(theme).__name__}."
    )
