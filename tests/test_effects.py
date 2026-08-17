import pytest
from unittest.mock import MagicMock, patch
from io import BytesIO
from PIL import Image

from lastfmcollagegenerator.collage import BaseCollageBuilder, CollageBuilderConfig, CollageTile
from lastfmcollagegenerator.collage_generator import CollageGenerator
from lastfmcollagegenerator.constants import THEME_ADAPTIVE, THEME_DARK
from lastfmcollagegenerator.effects import (
    ImageFilter,
    VisualEffectPipeline,
    DuotoneFilter,
    ColorExtractor,
)
from lastfmcollagegenerator.theme import Theme, resolve_theme
from tests.conftest import SyntheticImageFactory, MockPylastEntityFactory


def test_visual_effect_pipeline_empty():
    pipeline = VisualEffectPipeline()
    img = Image.new("RGB", (100, 100), (255, 0, 0))
    res = pipeline.apply(img)
    assert res.getpixel((0, 0)) == (255, 0, 0)


def test_duotone_filter_rgb():
    filter_ = DuotoneFilter(black_color=(0, 0, 100), white_color=(200, 200, 255))
    img = Image.new("RGB", (10, 10), (0, 0, 0))
    res = filter_.apply(img)
    assert res.getpixel((0, 0)) == (0, 0, 100)

    white_img = Image.new("RGB", (10, 10), (255, 255, 255))
    res_white = filter_.apply(white_img)
    assert res_white.getpixel((0, 0)) == (200, 200, 255)


def test_duotone_filter_hex_and_alpha():
    filter_ = DuotoneFilter(black_color="#000000", white_color="#ffffff")
    img = Image.new("RGBA", (10, 10), (128, 128, 128, 150))
    res = filter_.apply(img)
    assert res.mode == "RGBA"
    assert res.getpixel((0, 0))[3] == 150


def test_pipeline_chaining():
    pipeline = VisualEffectPipeline()
    f1 = DuotoneFilter(black_color=(10, 10, 10), white_color=(200, 200, 200))
    f2 = DuotoneFilter(black_color=(0, 0, 0), white_color=(100, 100, 100))
    pipeline.add_filter(f1).add_filter(f2)
    assert len(pipeline.filters) == 2


def test_color_extractor_dominant_and_palette():
    img = Image.new("RGB", (50, 50), (200, 50, 50))
    dom = ColorExtractor.extract_dominant_color(img)
    assert abs(dom[0] - 200) < 15
    assert abs(dom[1] - 50) < 15

    palette = ColorExtractor.extract_palette(img, count=3)
    assert len(palette) >= 1
    assert abs(palette[0][0] - 200) < 15


def test_color_extractor_adaptive_theme_light_and_dark():
    dark_img = Image.new("RGB", (50, 50), (20, 20, 30))
    dark_theme = ColorExtractor.generate_adaptive_theme(dark_img)
    assert dark_theme.text_color == (250, 250, 250)

    light_img = Image.new("RGB", (50, 50), (240, 240, 230))
    light_theme = ColorExtractor.generate_adaptive_theme(light_img)
    assert light_theme.text_color == (15, 15, 15)


def test_resolve_theme_adaptive():
    theme = resolve_theme("adaptive")
    assert theme.name == THEME_ADAPTIVE


def test_collage_generator_with_filters_and_adaptive_theme():
    generator = CollageGenerator("test_key", "test_secret")
    red_tile = SyntheticImageFactory.create_image_bytes(300, 300, color=(255, 0, 0))
    mock_album = MockPylastEntityFactory.create_mock_album("Artist", "Adaptive Album")

    with patch("lastfmcollagegenerator.collage_generator.LastfmClient") as mock_client_cls, \
         patch("lastfmcollagegenerator.collage.requests.get") as mock_http:
        mock_client = MagicMock()
        mock_client.get_top_albums.return_value = [
            MockPylastEntityFactory.create_mock_top_item(mock_album, weight=100)
        ]
        mock_client_cls.return_value = mock_client
        mock_http.return_value.status_code = 200
        mock_http.return_value.content = red_tile

        duotone = DuotoneFilter(black_color="#101010", white_color="#00ff00")
        img = generator.generate(
            entity="album",
            username="testuser",
            cols=1,
            rows=1,
            theme="adaptive",
            filters=[duotone],
        )
        assert isinstance(img, Image.Image)
        assert img.size == (300, 300)


def test_collage_generator_invalid_filters_type():
    generator = CollageGenerator("test_key", "test_secret")
    with pytest.raises(TypeError, match="filters must be"):
        generator.generate(
            entity="album",
            username="testuser",
            cols=1,
            rows=1,
            filters=12345,  # type: ignore
        )


from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_collage_generator_async_with_filters():
    generator = CollageGenerator("test_key", "test_secret")
    blue_tile = SyntheticImageFactory.create_image_bytes(300, 300, color=(0, 0, 255))
    mock_album = MockPylastEntityFactory.create_mock_album("Artist", "Async Album")

    with patch("lastfmcollagegenerator.collage_generator.LastfmClient") as mock_client_cls, \
         patch("httpx.AsyncClient.get") as mock_get:
        mock_client = MagicMock()
        mock_client.get_user_async = AsyncMock(return_value=MagicMock())
        mock_client.get_top_albums_async = AsyncMock(return_value=[
            MockPylastEntityFactory.create_mock_top_item(mock_album, weight=100)
        ])
        mock_client_cls.return_value = mock_client
        mock_get.return_value = MagicMock(
            status_code=200,
            content=blue_tile,
            raise_for_status=MagicMock(),
        )

        duotone = DuotoneFilter(black_color="#000000", white_color="#ffffff")
        img = await generator.generate_async(
            entity="album",
            username="testuser",
            cols=1,
            rows=1,
            filters=duotone,
        )
        assert isinstance(img, Image.Image)
        assert img.size == (300, 300)
