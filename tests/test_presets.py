from unittest.mock import MagicMock

import pytest

from lastfmcollagegenerator.collage import (
    BaseCollageBuilder,
    CollageBuilderConfig,
    CollageTile,
)
from lastfmcollagegenerator.collage_generator import CollageGenerator
from lastfmcollagegenerator.presets import (
    PRESET_DESKTOP_WALLPAPER,
    PRESET_DESKTOP_WALLPAPER_4K,
    PRESET_INSTAGRAM_POST,
    PRESET_INSTAGRAM_STORY,
    PRESET_TWITTER_HEADER,
    SOCIAL_PRESETS,
    resolve_preset,
)
from tests.conftest import SyntheticImageFactory


@pytest.mark.parametrize(
    "preset_name,width,height",
    [
        (PRESET_INSTAGRAM_STORY, 1080, 1920),
        (PRESET_INSTAGRAM_POST, 1080, 1080),
        (PRESET_TWITTER_HEADER, 1500, 500),
        (PRESET_DESKTOP_WALLPAPER, 1920, 1080),
        (PRESET_DESKTOP_WALLPAPER_4K, 3840, 2160),
    ],
)
def test_preset_canvas_dimensions(preset_name, width, height):
    preset = SOCIAL_PRESETS[preset_name]
    config = CollageBuilderConfig(
        cols=preset.cols,
        rows=preset.rows,
        period="overall",
        tile_size=preset.tile_size,
        preset_width=preset.width,
        preset_height=preset.height,
        show_text=False,
    )
    builder = BaseCollageBuilder(config, MagicMock())
    tile_bytes = SyntheticImageFactory.create_image_bytes(
        preset.tile_size, preset.tile_size, color=(255, 0, 0)
    )
    tiles = [
        CollageTile(data=tile_bytes, playcount=100 - i, title=f"T{i}")
        for i in range(preset.cols * preset.rows)
    ]
    img = builder._create_image(tiles, cols=preset.cols, rows=preset.rows)
    assert img.size == (width, height)


def test_unknown_preset_raises_value_error():
    generator = CollageGenerator("k", "s")
    with pytest.raises(ValueError, match="Unknown preset"):
        generator.generate(
            entity="album",
            username="user",
            cols=3,
            rows=3,
            preset="tiktok",
        )


def test_resolve_preset_unknown_name():
    with pytest.raises(ValueError, match="Unknown preset"):
        resolve_preset("myspace")


def test_backdrop_fills_letterbox_with_blurred_artwork():
    preset = SOCIAL_PRESETS[PRESET_INSTAGRAM_STORY]
    config = CollageBuilderConfig(
        cols=preset.cols,
        rows=preset.rows,
        period="overall",
        tile_size=preset.tile_size,
        preset_width=preset.width,
        preset_height=preset.height,
        show_text=False,
    )
    builder = BaseCollageBuilder(config, MagicMock())
    red_tile = SyntheticImageFactory.create_image_bytes(
        preset.tile_size, preset.tile_size, color=(255, 0, 0)
    )
    tiles = [
        CollageTile(data=red_tile, playcount=100 - i, title=f"T{i}")
        for i in range(preset.cols * preset.rows)
    ]
    img = builder._create_image(tiles, cols=preset.cols, rows=preset.rows)

    bottom_strip_y = preset.height - 10
    pixel = img.getpixel((preset.width // 2, bottom_strip_y))
    assert pixel != (0, 0, 0)
    assert 30 <= pixel[0] <= 200
    assert pixel[1] < 60


def test_square_grid_skips_backdrop():
    preset = SOCIAL_PRESETS[PRESET_INSTAGRAM_POST]
    config = CollageBuilderConfig(
        cols=preset.cols,
        rows=preset.rows,
        period="overall",
        tile_size=preset.tile_size,
        preset_width=preset.width,
        preset_height=preset.height,
        show_text=False,
    )
    builder = BaseCollageBuilder(config, MagicMock())
    red_tile = SyntheticImageFactory.create_image_bytes(
        preset.tile_size, preset.tile_size, color=(255, 0, 0)
    )
    tiles = [
        CollageTile(data=red_tile, playcount=100 - i, title=f"T{i}")
        for i in range(preset.cols * preset.rows)
    ]
    img = builder._create_image(tiles, cols=preset.cols, rows=preset.rows)
    assert img.size == (1080, 1080)
    assert img.getpixel((5, 5)) == (255, 0, 0)


def test_preset_validation_in_facade():
    generator = CollageGenerator("k", "s")
    assert generator._resolve_preset("instagram-post") is not None
    assert generator._resolve_preset(None) is None
    with pytest.raises(ValueError):
        generator._resolve_preset("nope")
