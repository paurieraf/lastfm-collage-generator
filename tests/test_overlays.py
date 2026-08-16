import pytest
from PIL import Image

from lastfmcollagegenerator.collage import (
    AlbumCollageBuilder,
    CollageBuilderConfig,
    CollageTile,
)
from lastfmcollagegenerator.constants import (
    OVERLAY_BANNER,
    OVERLAY_FULL_TINT,
    OVERLAY_GRADIENT,
    OVERLAY_PILL,
    OVERLAY_CLEAN,
    THEME_DARK,
    THEME_LIGHT,
    THEME_GLASSMORPHIC,
    THEME_SUNSET,
    THEME_NEON,
)
from lastfmcollagegenerator.theme import Theme, THEME_PRESETS
from tests.conftest import SyntheticImageFactory


@pytest.fixture
def sample_tiles():
    tile_data = SyntheticImageFactory.create_image_bytes(
        300, 300, color=(100, 150, 200)
    )
    return [
        CollageTile(
            data=tile_data,
            playcount=500,
            title="Artist Name - Album Title (2026)",
        ),
        CollageTile(
            data=tile_data,
            playcount=400,
            title="Second Artist - Second Album",
        ),
        CollageTile(
            data=tile_data,
            playcount=300,
            title="Third Artist - Third Album",
        ),
        CollageTile(
            data=tile_data,
            playcount=200,
            title="Fourth Artist - Fourth Album",
        ),
    ]


@pytest.mark.parametrize(
    "overlay_style",
    [
        OVERLAY_BANNER,
        OVERLAY_FULL_TINT,
        OVERLAY_GRADIENT,
        OVERLAY_PILL,
    ],
)
def test_overlay_styles_render_successfully(
    mock_lastfm_client, sample_tiles, overlay_style
):
    config = CollageBuilderConfig(
        cols=2,
        rows=2,
        period="overall",
        tile_size=300,
        overlay_style=overlay_style,
        show_text=True,
    )
    builder = AlbumCollageBuilder(config, mock_lastfm_client)
    img = builder._create_image(sample_tiles, cols=2, rows=2)

    assert isinstance(img, Image.Image)
    assert img.size == (600, 600)
    assert img.mode == "RGB"


@pytest.mark.parametrize(
    "theme_name",
    [
        THEME_DARK,
        THEME_LIGHT,
        THEME_GLASSMORPHIC,
        THEME_SUNSET,
        THEME_NEON,
    ],
)
def test_themes_render_successfully(mock_lastfm_client, sample_tiles, theme_name):
    config = CollageBuilderConfig(
        cols=2,
        rows=2,
        period="overall",
        tile_size=300,
        theme=THEME_PRESETS[theme_name],
        overlay_style=OVERLAY_BANNER,
        show_text=True,
    )
    builder = AlbumCollageBuilder(config, mock_lastfm_client)
    img = builder._create_image(sample_tiles, cols=2, rows=2)

    assert isinstance(img, Image.Image)
    assert img.size == (600, 600)


def test_clean_mode_and_show_text_false(mock_lastfm_client, sample_tiles):
    # overlay_style clean
    config_clean = CollageBuilderConfig(
        cols=2,
        rows=2,
        period="overall",
        tile_size=300,
        overlay_style=OVERLAY_CLEAN,
    )
    builder_clean = AlbumCollageBuilder(config_clean, mock_lastfm_client)
    img_clean = builder_clean._create_image(sample_tiles, cols=2, rows=2)

    # show_text False
    config_no_text = CollageBuilderConfig(
        cols=2,
        rows=2,
        period="overall",
        tile_size=300,
        show_text=False,
    )
    builder_no_text = AlbumCollageBuilder(config_no_text, mock_lastfm_client)
    img_no_text = builder_no_text._create_image(sample_tiles, cols=2, rows=2)

    assert img_clean.size == (600, 600)
    assert img_no_text.size == (600, 600)

    # Check that bottom pixel is identical to top pixel (no overlay banner applied)
    p_top = img_clean.getpixel((50, 50))
    p_bottom = img_clean.getpixel((50, 270))
    assert p_top == p_bottom


def test_custom_theme_object(mock_lastfm_client, sample_tiles):
    custom_theme = Theme(
        name="custom_purple",
        overlay_bg=(80, 0, 120, 160),
        text_color=(255, 255, 0),
        accent_color=(200, 100, 255, 200),
    )
    config = CollageBuilderConfig(
        cols=2,
        rows=2,
        period="overall",
        tile_size=300,
        theme=custom_theme,
        overlay_style=OVERLAY_FULL_TINT,
    )
    builder = AlbumCollageBuilder(config, mock_lastfm_client)
    img = builder._create_image(sample_tiles, cols=2, rows=2)

    assert img.size == (600, 600)
