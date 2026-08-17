from unittest.mock import patch, MagicMock
import pytest
from PIL import Image

from lastfmcollagegenerator.collage_generator import CollageGenerator
from lastfmcollagegenerator.constants import ENTITY_ALBUM, ENTITY_ARTIST, ENTITY_TRACK
from lastfmcollagegenerator.fallback_art import FALLBACK_STYLE_BLACK


@pytest.fixture
def mock_builder():
    mock = MagicMock()
    mock.create.return_value = Image.new("RGB", (900, 900), color="blue")
    return mock


@patch("lastfmcollagegenerator.collage_generator.ResilientHttpFetcher")
@patch("lastfmcollagegenerator.collage_generator.ArtworkCache")
@patch("lastfmcollagegenerator.collage_generator.CollageBuilderFactory")
@patch("lastfmcollagegenerator.collage_generator.LastfmClient")
def test_generate_top_albums_collage(
    mock_client_cls, mock_factory_cls, mock_cache_cls, mock_fetcher_cls, mock_builder
):
    mock_factory_cls.return_value = mock_builder
    generator = CollageGenerator("mock_key", "mock_secret")

    result = generator.generate_top_albums_collage(
        username="testuser",
        cols=3,
        rows=3,
        period="7day",
    )

    assert isinstance(result, Image.Image)
    assert result.size == (900, 900)
    mock_factory_cls.assert_called_once()
    call_kwargs = mock_factory_cls.call_args.kwargs
    assert call_kwargs["entity"] == ENTITY_ALBUM
    assert call_kwargs["config"].cols == 3
    assert call_kwargs["config"].rows == 3
    assert call_kwargs["config"].period == "7day"
    mock_builder.create.assert_called_once_with("testuser")


@patch("lastfmcollagegenerator.collage_generator.ResilientHttpFetcher")
@patch("lastfmcollagegenerator.collage_generator.ArtworkCache")
@patch("lastfmcollagegenerator.collage_generator.CollageBuilderFactory")
@patch("lastfmcollagegenerator.collage_generator.LastfmClient")
def test_generate_top_artists_collage(
    mock_client_cls, mock_factory_cls, mock_cache_cls, mock_fetcher_cls, mock_builder
):
    mock_factory_cls.return_value = mock_builder
    generator = CollageGenerator("mock_key", "mock_secret")

    result = generator.generate_top_artists_collage(
        username="testuser",
        cols=2,
        rows=2,
        period="1month",
    )

    assert isinstance(result, Image.Image)
    call_kwargs = mock_factory_cls.call_args.kwargs
    assert call_kwargs["entity"] == ENTITY_ARTIST
    assert call_kwargs["config"].cols == 2
    assert call_kwargs["config"].rows == 2
    assert call_kwargs["config"].period == "1month"
    mock_builder.create.assert_called_once_with("testuser")


@patch("lastfmcollagegenerator.collage_generator.ResilientHttpFetcher")
@patch("lastfmcollagegenerator.collage_generator.ArtworkCache")
@patch("lastfmcollagegenerator.collage_generator.CollageBuilderFactory")
@patch("lastfmcollagegenerator.collage_generator.LastfmClient")
def test_generate_top_tracks_collage(
    mock_client_cls, mock_factory_cls, mock_cache_cls, mock_fetcher_cls, mock_builder
):
    mock_factory_cls.return_value = mock_builder
    generator = CollageGenerator("mock_key", "mock_secret")

    result = generator.generate_top_tracks_collage(
        username="testuser",
        cols=4,
        rows=4,
        period="overall",
    )

    assert isinstance(result, Image.Image)
    call_kwargs = mock_factory_cls.call_args.kwargs
    assert call_kwargs["entity"] == ENTITY_TRACK
    assert call_kwargs["config"].cols == 4
    assert call_kwargs["config"].rows == 4
    assert call_kwargs["config"].period == "overall"
    assert call_kwargs["config"].tile_size == 300
    mock_builder.create.assert_called_once_with("testuser")


@patch("lastfmcollagegenerator.collage_generator.ResilientHttpFetcher")
@patch("lastfmcollagegenerator.collage_generator.ArtworkCache")
@patch("lastfmcollagegenerator.collage_generator.CollageBuilderFactory")
@patch("lastfmcollagegenerator.collage_generator.LastfmClient")
def test_generate_with_custom_tile_size_and_high_density(
    mock_client_cls, mock_factory_cls, mock_cache_cls, mock_fetcher_cls, mock_builder
):
    mock_factory_cls.return_value = mock_builder
    generator = CollageGenerator("mock_key", "mock_secret")

    # High density 10x10 auto downscaled to 150px
    generator.generate_top_albums_collage(
        username="testuser",
        cols=10,
        rows=10,
        period="overall",
    )
    call_kwargs_10x10 = mock_factory_cls.call_args.kwargs
    assert call_kwargs_10x10["config"].tile_size == 150

    # Explicit tile_size override (250px)
    generator.generate(
        entity=ENTITY_ALBUM,
        username="testuser",
        cols=8,
        rows=8,
        period="overall",
        tile_size=250,
    )
    call_kwargs_custom = mock_factory_cls.call_args.kwargs
    assert call_kwargs_custom["config"].tile_size == 250


@patch("lastfmcollagegenerator.collage_generator.ResilientHttpFetcher")
@patch("lastfmcollagegenerator.collage_generator.ArtworkCache")
@patch("lastfmcollagegenerator.collage_generator.CollageBuilderFactory")
@patch("lastfmcollagegenerator.collage_generator.LastfmClient")
def test_generate_with_themes_and_overlay_styles(
    mock_client_cls, mock_factory_cls, mock_cache_cls, mock_fetcher_cls, mock_builder
):
    mock_factory_cls.return_value = mock_builder
    generator = CollageGenerator("mock_key", "mock_secret")

    generator.generate_top_albums_collage(
        username="testuser",
        cols=3,
        rows=3,
        period="7day",
        theme="light",
        overlay_style="full_tint",
        show_text=False,
    )
    call_kwargs = mock_factory_cls.call_args.kwargs
    assert call_kwargs["config"].theme.name == "light"
    assert call_kwargs["config"].overlay_style == "full_tint"
    assert call_kwargs["config"].show_text is False


@patch("lastfmcollagegenerator.collage_generator.ResilientHttpFetcher")
@patch("lastfmcollagegenerator.collage_generator.ArtworkCache")
@patch("lastfmcollagegenerator.collage_generator.CollageBuilderFactory")
@patch("lastfmcollagegenerator.collage_generator.LastfmClient")
def test_generate_with_typography_options(
    mock_client_cls, mock_factory_cls, mock_cache_cls, mock_fetcher_cls, mock_builder
):
    mock_factory_cls.return_value = mock_builder
    generator = CollageGenerator("mock_key", "mock_secret")

    generator.generate_top_artists_collage(
        username="testuser",
        cols=3,
        rows=3,
        period="overall",
        show_playcount=False,
        font_bold=True,
    )
    call_kwargs = mock_factory_cls.call_args.kwargs
    assert call_kwargs["config"].show_playcount is False
    assert call_kwargs["config"].font_bold is True


@patch("lastfmcollagegenerator.collage_generator.ResilientHttpFetcher")
@patch("lastfmcollagegenerator.collage_generator.ArtworkCache")
@patch("lastfmcollagegenerator.collage_generator.CollageBuilderFactory")
@patch("lastfmcollagegenerator.collage_generator.LastfmClient")
def test_generate_with_preset_overrides_grid(
    mock_client_cls, mock_factory_cls, mock_cache_cls, mock_fetcher_cls, mock_builder
):
    mock_factory_cls.return_value = mock_builder
    generator = CollageGenerator("mock_key", "mock_secret")

    generator.generate(
        entity=ENTITY_ALBUM,
        username="testuser",
        cols=9,
        rows=9,
        period="overall",
        preset="instagram-post",
    )
    call_kwargs = mock_factory_cls.call_args.kwargs
    config = call_kwargs["config"]
    assert config.cols == 3
    assert config.rows == 3
    assert config.tile_size == 360
    assert config.preset_width == 1080
    assert config.preset_height == 1080


@patch("lastfmcollagegenerator.collage_generator.ResilientHttpFetcher")
@patch("lastfmcollagegenerator.collage_generator.ArtworkCache")
@patch("lastfmcollagegenerator.collage_generator.CollageBuilderFactory")
@patch("lastfmcollagegenerator.collage_generator.LastfmClient")
def test_generate_with_geometry_and_fallback_params(
    mock_client_cls, mock_factory_cls, mock_cache_cls, mock_fetcher_cls, mock_builder
):
    mock_factory_cls.return_value = mock_builder
    generator = CollageGenerator("mock_key", "mock_secret")

    generator.generate(
        entity=ENTITY_ALBUM,
        username="testuser",
        cols=3,
        rows=3,
        period="overall",
        fallback_style=FALLBACK_STYLE_BLACK,
        corner_radius=12,
        border_width=3,
        border_color="#FF0000",
        spacing=8,
        cache_dir="/tmp/collage-cache",
        cache_ttl_override=15,
        rate_limit=10,
    )
    call_kwargs = mock_factory_cls.call_args.kwargs
    config = call_kwargs["config"]
    assert config.fallback_style == FALLBACK_STYLE_BLACK
    assert config.corner_radius == 12
    assert config.border_width == 3
    assert config.border_color == "#FF0000"
    assert config.spacing == 8

    mock_cache_cls.assert_called_once_with(
        cache_dir="/tmp/collage-cache",
        ttl_override_days=15,
    )
    mock_fetcher_cls.assert_called_once()
    assert mock_fetcher_cls.call_args.kwargs["rate_limit"] == 10


def test_package_exports_and_version():
    import lastfmcollagegenerator

    assert hasattr(lastfmcollagegenerator, "CollageGenerator")
    assert hasattr(lastfmcollagegenerator, "Theme")
    assert hasattr(lastfmcollagegenerator, "THEME_PRESETS")
    assert hasattr(lastfmcollagegenerator, "resolve_theme")
    assert hasattr(lastfmcollagegenerator, "ImageFilter")
    assert hasattr(lastfmcollagegenerator, "VisualEffectPipeline")
    assert hasattr(lastfmcollagegenerator, "DuotoneFilter")
    assert hasattr(lastfmcollagegenerator, "ColorExtractor")
    assert hasattr(lastfmcollagegenerator, "export_image")
    assert hasattr(lastfmcollagegenerator, "infer_format")
    assert hasattr(lastfmcollagegenerator, "SUPPORTED_EXPORT_FORMATS")
    assert hasattr(lastfmcollagegenerator, "__version__")
    assert lastfmcollagegenerator.__version__ == "1.3.0"
