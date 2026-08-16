from unittest.mock import MagicMock

import pytest

from lastfmcollagegenerator.collage import (
    BaseCollageBuilder,
    CollageBuilderConfig,
    CollageTile,
)
from tests.conftest import SyntheticImageFactory


def test_canvas_dimensions():
    config = CollageBuilderConfig(cols=3, rows=2, period="overall")
    builder = BaseCollageBuilder(config, lastfm_client=MagicMock())

    red_tile_bytes = SyntheticImageFactory.create_image_bytes(
        300, 300, color=(255, 0, 0)
    )
    tiles = [
        CollageTile(data=red_tile_bytes, playcount=10, title=f"Tile {i}")
        for i in range(6)
    ]

    img = builder._create_image(tiles, cols=3, rows=2)
    assert img.size == (900, 600)
    assert img.mode == "RGB"


def test_multi_row_title_overlay_geometry():
    """Verify that title overlays are bounded in [y+235, y+300] per row."""
    config = CollageBuilderConfig(cols=2, rows=3, period="overall", show_playcount=True)
    builder = BaseCollageBuilder(config, lastfm_client=MagicMock())

    # Create solid bright red tiles (255, 0, 0)
    red_tile_bytes = SyntheticImageFactory.create_image_bytes(
        300, 300, color=(255, 0, 0)
    )
    tiles = [
        CollageTile(data=red_tile_bytes, playcount=100 - i, title=f"Album {i}")
        for i in range(6)
    ]

    img = builder._create_image(tiles, cols=2, rows=3)
    assert img.size == (600, 900)

    # Row 0 (y: 0 to 299)
    # Tile upper area (y=100) must be pure red (255, 0, 0)
    assert img.getpixel((50, 100)) == (255, 0, 0)
    # Banner area (y=250) must be shaded (darkened due to alpha overlay)
    pixel_r0_banner = img.getpixel((50, 250))
    assert pixel_r0_banner != (255, 0, 0)
    assert pixel_r0_banner[0] < 255  # Red component darkened

    # Row 1 (y: 300 to 599)
    # Upper tile area (y=350, row 1) must be pure red (255, 0, 0) - NOT covered
    assert img.getpixel((50, 350)) == (255, 0, 0)
    # Row 1 banner area (y=550) must be shaded
    pixel_r1_banner = img.getpixel((50, 550))
    assert pixel_r1_banner != (255, 0, 0)
    assert pixel_r1_banner[0] < 255

    # Row 2 (y: 600 to 899)
    # Upper tile area (y=650, row 2) must be pure red (255, 0, 0)
    # In defective version, row 1 banner extended to y=900, covering Row 2.
    assert img.getpixel((50, 650)) == (255, 0, 0)
    # Row 2 banner area (y=850) must be shaded
    pixel_r2_banner = img.getpixel((50, 850))
    assert pixel_r2_banner != (255, 0, 0)
    assert pixel_r2_banner[0] < 255


def test_scaled_tile_geometry_150px():
    """Verify that multi-row title overlays scale proportionally with 150px tiles."""
    config = CollageBuilderConfig(
        cols=2, rows=2, period="overall", show_playcount=True, tile_size=150
    )
    builder = BaseCollageBuilder(config, lastfm_client=MagicMock())

    # Create 300x300 source tiles (downscaled to 150x150 during canvas creation)
    red_tile_bytes = SyntheticImageFactory.create_image_bytes(
        300, 300, color=(255, 0, 0)
    )
    tiles = [
        CollageTile(data=red_tile_bytes, playcount=50, title=f"Item {i}")
        for i in range(4)
    ]

    img = builder._create_image(tiles, cols=2, rows=2)
    assert img.size == (300, 300)

    # Row 0: top area (y=50) is pure red
    assert img.getpixel((30, 50)) == (255, 0, 0)
    # Row 0: banner area (y=135) is shaded
    assert img.getpixel((30, 135))[0] < 255

    # Row 1: top area (y=150 + 40 = 190) is pure red (not overwritten)
    assert img.getpixel((30, 190)) == (255, 0, 0)
    # Row 1: banner area (y=150 + 135 = 285) is shaded
    assert img.getpixel((30, 285))[0] < 255


def test_high_density_canvas_allocation():
    """Verify high-density matrix canvas dimensions with auto and custom tile sizes."""
    config_10x10 = CollageBuilderConfig(
        cols=10, rows=10, period="overall", tile_size=150
    )
    builder_10x10 = BaseCollageBuilder(config_10x10, lastfm_client=MagicMock())
    tile_bytes = SyntheticImageFactory.create_image_bytes(150, 150)
    tiles_100 = [
        CollageTile(data=tile_bytes, playcount=1, title=f"T{i}") for i in range(100)
    ]
    img_10x10 = builder_10x10._create_image(tiles_100, cols=10, rows=10)
    assert img_10x10.size == (1500, 1500)

    config_20x20 = CollageBuilderConfig(
        cols=20, rows=20, period="overall", tile_size=100
    )
    builder_20x20 = BaseCollageBuilder(config_20x20, lastfm_client=MagicMock())
    tile_bytes_100 = SyntheticImageFactory.create_image_bytes(100, 100)
    tiles_400 = [
        CollageTile(data=tile_bytes_100, playcount=1, title=f"T{i}") for i in range(400)
    ]
    img_20x20 = builder_20x20._create_image(tiles_400, cols=20, rows=20)
    assert img_20x20.size == (2000, 2000)


def test_rounded_corners_mask_canvas_background():
    config = CollageBuilderConfig(
        cols=1, rows=1, period="overall", corner_radius=12, show_text=False
    )
    builder = BaseCollageBuilder(config, lastfm_client=MagicMock())
    tile_bytes = SyntheticImageFactory.create_image_bytes(300, 300, color=(255, 0, 0))
    img = builder._create_image(
        [CollageTile(data=tile_bytes, playcount=1, title="T")], cols=1, rows=1
    )
    assert img.size == (300, 300)
    assert img.getpixel((150, 150)) == (255, 0, 0)
    assert img.getpixel((0, 0)) != (255, 0, 0)


def test_border_stroke_rendering():
    config = CollageBuilderConfig(
        cols=1,
        rows=1,
        period="overall",
        border_width=6,
        border_color=(0, 255, 0),
        show_text=False,
    )
    builder = BaseCollageBuilder(config, lastfm_client=MagicMock())
    tile_bytes = SyntheticImageFactory.create_image_bytes(300, 300, color=(255, 0, 0))
    img = builder._create_image(
        [CollageTile(data=tile_bytes, playcount=1, title="T")], cols=1, rows=1
    )
    assert img.getpixel((150, 150)) == (255, 0, 0)
    assert img.getpixel((150, 2)) == (0, 255, 0)
    assert img.getpixel((2, 150)) == (0, 255, 0)


def test_inter_tile_spacing_canvas_growth():
    config = CollageBuilderConfig(
        cols=2, rows=2, period="overall", spacing=8, show_text=False
    )
    builder = BaseCollageBuilder(config, lastfm_client=MagicMock())
    tile_bytes = SyntheticImageFactory.create_image_bytes(300, 300, color=(255, 0, 0))
    tiles = [
        CollageTile(data=tile_bytes, playcount=10 - i, title=f"T{i}") for i in range(4)
    ]
    img = builder._create_image(tiles, cols=2, rows=2)
    assert img.size == (2 * 300 + 3 * 8, 2 * 300 + 3 * 8)
    assert img.getpixel((4, 4)) != (255, 0, 0)


def test_default_geometry_is_byte_identical_to_legacy():
    legacy_bytes = SyntheticImageFactory.create_image_bytes(300, 300, color=(255, 0, 0))
    tiles = [
        CollageTile(data=legacy_bytes, playcount=100 - i, title=f"Album {i}")
        for i in range(4)
    ]
    plain = BaseCollageBuilder(
        CollageBuilderConfig(cols=2, rows=2, period="overall"), MagicMock()
    )
    legacy = plain._create_image_legacy(tiles, cols=2, rows=2)
    img = plain._create_image(tiles, cols=2, rows=2)
    assert img.tobytes() == legacy.tobytes()


def test_invalid_geometry_parameters_raise():
    from lastfmcollagegenerator.collage_generator import CollageGenerator

    generator = CollageGenerator("k", "s")
    with pytest.raises(ValueError, match="corner_radius"):
        generator._validate_parameters(
            entity="album",
            username="user",
            cols=3,
            rows=3,
            period="overall",
            corner_radius=-1,
        )
    with pytest.raises(ValueError, match="border_width"):
        generator._validate_parameters(
            entity="album",
            username="user",
            cols=3,
            rows=3,
            period="overall",
            border_width=-2,
        )
    with pytest.raises(ValueError, match="spacing"):
        generator._validate_parameters(
            entity="album",
            username="user",
            cols=3,
            rows=3,
            period="overall",
            spacing=301,
        )
    with pytest.raises(ValueError, match="corner_radius"):
        generator._validate_parameters(
            entity="album",
            username="user",
            cols=3,
            rows=3,
            period="overall",
            corner_radius=301,
        )
