from unittest.mock import MagicMock
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
