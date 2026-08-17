#!/usr/bin/env python3
"""Generates authentic visual preview assets for README.md."""

import os
import sys
from unittest.mock import MagicMock

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_PATH = os.path.join(PROJECT_ROOT, "src")
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from scripts.debug_collage import generate_synthetic_tiles
from lastfmcollagegenerator.collage import (
    CollageBuilderConfig,
    CollageBuilderFactory,
    CollageTile,
)
from lastfmcollagegenerator.lastfm.client import LastfmClient
from lastfmcollagegenerator.theme import resolve_theme, Theme
from lastfmcollagegenerator.effects import DuotoneFilter
from lastfmcollagegenerator.presets import resolve_preset
from lastfmcollagegenerator.export import export_image


def generate_mock_image(
    entity: str = "album",
    cols: int = 3,
    rows: int = 3,
    tile_size: int = 300,
    theme: str = "dark",
    overlay_style: str = "banner",
    show_text: bool = True,
    corner_radius: int = 0,
    border_width: int = 0,
    border_color = None,
    spacing: int = 0,
    filters = None,
    preset: str = None,
):
    resolved_preset = resolve_preset(preset) if preset else None
    if resolved_preset:
        cols = resolved_preset.cols
        rows = resolved_preset.rows
        tile_size = resolved_preset.tile_size
        preset_width = resolved_preset.width
        preset_height = resolved_preset.height
    else:
        preset_width = None
        preset_height = None

    if isinstance(theme, Theme):
        resolved_theme = theme
    else:
        resolved_theme = resolve_theme(theme)

    config = CollageBuilderConfig(
        cols=cols,
        rows=rows,
        period="7day",
        show_playcount=True,
        tile_size=tile_size,
        theme=resolved_theme,
        overlay_style=overlay_style,
        show_text=show_text,
        corner_radius=corner_radius,
        border_width=border_width,
        border_color=border_color,
        spacing=spacing,
        preset_width=preset_width,
        preset_height=preset_height,
        filters=[filters] if isinstance(filters, DuotoneFilter) else filters,
    )

    mock_client = MagicMock(spec=LastfmClient)
    builder = CollageBuilderFactory(entity=entity, config=config, lastfm_client=mock_client)
    
    mock_tiles = generate_synthetic_tiles(cols * rows, entity, tile_size, tile_size)
    collage_tiles = [
        CollageTile(data=t.data, playcount=t.playcount, title=t.title)
        for t in mock_tiles
    ]
    return builder._create_image(collage_tiles, cols, rows)


def main():
    assets_dir = os.path.join(PROJECT_ROOT, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    print("Generating README preview assets...")

    # 1. Main Header Preview (3x3 Standard Album Grid)
    img_preview = generate_mock_image(entity="album", cols=3, rows=3, tile_size=300)
    img_preview.save(os.path.join(assets_dir, "collage_preview.png"))
    print("✓ assets/collage_preview.png")

    # 2. Artists Collage (4x4)
    img_artists = generate_mock_image(entity="artist", cols=4, rows=4, tile_size=200)
    img_artists.save(os.path.join(assets_dir, "example_artists.png"))
    print("✓ assets/example_artists.png")

    # 3. Instagram Story Preset (3x5 with blurred backdrop)
    img_story = generate_mock_image(entity="album", preset="instagram-story")
    img_story.save(os.path.join(assets_dir, "example_story.png"))
    print("✓ assets/example_story.png")

    # 4. Geometry (Rounded corners, spacing, custom border)
    img_geom = generate_mock_image(
        entity="album",
        cols=3,
        rows=3,
        tile_size=300,
        corner_radius=18,
        spacing=12,
        border_width=3,
        border_color="#FF5A5F",
    )
    img_geom.save(os.path.join(assets_dir, "example_geometry.png"))
    print("✓ assets/example_geometry.png")

    # 5. Themes: Sunset + Pill
    img_sunset = generate_mock_image(
        entity="album",
        cols=3,
        rows=3,
        tile_size=300,
        theme="sunset",
        overlay_style="pill",
    )
    img_sunset.save(os.path.join(assets_dir, "example_sunset_pill.png"))
    print("✓ assets/example_sunset_pill.png")

    # 6. Themes: Neon + Full Tint
    img_neon = generate_mock_image(
        entity="artist",
        cols=3,
        rows=3,
        tile_size=300,
        theme="neon",
        overlay_style="full_tint",
    )
    img_neon.save(os.path.join(assets_dir, "example_neon_tint.png"))
    print("✓ assets/example_neon_tint.png")

    # 7. Clean Mode (Cover art only)
    img_clean = generate_mock_image(
        entity="album",
        cols=4,
        rows=4,
        tile_size=200,
        show_text=False,
    )
    img_clean.save(os.path.join(assets_dir, "example_clean.png"))
    print("✓ assets/example_clean.png")

    # 8. Custom Theme (Forest)
    forest_theme = Theme(
        name="forest",
        overlay_bg=(20, 50, 30, 190),
        text_color=(235, 255, 235),
        accent_color=(100, 200, 120, 220),
    )
    img_custom = generate_mock_image(
        entity="album",
        cols=3,
        rows=3,
        tile_size=300,
        theme=forest_theme,
        overlay_style="banner",
    )
    img_custom.save(os.path.join(assets_dir, "example_custom_theme.png"))
    print("✓ assets/example_custom_theme.png")

    # 9. Duotone Filter
    duotone = DuotoneFilter(black_color="#0F0C29", white_color="#FF007F")
    img_duotone = generate_mock_image(
        entity="album",
        cols=3,
        rows=3,
        tile_size=300,
        filters=duotone,
    )
    img_duotone.save(os.path.join(assets_dir, "example_duotone.png"))
    print("✓ assets/example_duotone.png")

    print("\nAll README assets generated successfully!")


if __name__ == "__main__":
    main()
