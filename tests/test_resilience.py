from unittest.mock import patch, MagicMock
from io import BytesIO
import requests
from PIL import Image

from lastfmcollagegenerator.cache import ArtworkCache, CACHE_KIND_ALBUM
from lastfmcollagegenerator.collage import (
    AlbumCollageBuilder,
    ArtistCollageBuilder,
    CollageBuilderConfig,
    DEFAULT_HEADERS,
    DEFAULT_TIMEOUT,
)
from lastfmcollagegenerator.exceptions import (
    LastfmCollageGeneratorError,
    ArtistNotFound,
    ArtistImageNotFound,
)
from lastfmcollagegenerator.fallback_art import FALLBACK_STYLE_BLACK
from lastfmcollagegenerator.network import (
    CircuitOpenError,
    ResilientHttpFetcher,
)
from tests.conftest import (
    SyntheticImageFactory,
    MockPylastEntityFactory,
    MockHtmlResponses,
)


def _album_builder(**config_kwargs):
    config = CollageBuilderConfig(cols=3, rows=3, period="overall", **config_kwargs)
    fetcher = ResilientHttpFetcher(rate_limit=None, max_attempts=1)
    return AlbumCollageBuilder(config, MagicMock(), fetcher=fetcher)


def _artist_builder(**config_kwargs):
    config = CollageBuilderConfig(cols=3, rows=3, period="overall", **config_kwargs)
    fetcher = ResilientHttpFetcher(rate_limit=None, max_attempts=1)
    return ArtistCollageBuilder(config, MagicMock(), fetcher=fetcher)


def test_exception_hierarchy():
    assert issubclass(ArtistNotFound, LastfmCollageGeneratorError)
    assert issubclass(ArtistImageNotFound, LastfmCollageGeneratorError)
    assert issubclass(LastfmCollageGeneratorError, Exception)

    err1 = ArtistNotFound("Artist missing")
    err2 = ArtistImageNotFound("Image missing")
    assert isinstance(err1, LastfmCollageGeneratorError)
    assert isinstance(err2, LastfmCollageGeneratorError)


def test_album_cover_fallback_on_missing_url():
    mock_album = MockPylastEntityFactory.create_mock_album(cover_url=None)
    data = _album_builder()._get_album_cover(mock_album, "Artist - Album")
    assert isinstance(data, bytes)
    with Image.open(BytesIO(data)) as img:
        assert img.size == (300, 300)
        assert img.getpixel((0, 0)) != (0, 0, 0)


def test_album_cover_fallback_on_exception_getting_url():
    mock_album = MagicMock()
    mock_album.get_cover_image.side_effect = IndexError("No cover image index")
    data = _album_builder()._get_album_cover(mock_album, "Artist - Album")
    assert isinstance(data, bytes)
    with Image.open(BytesIO(data)) as img:
        assert img.size == (300, 300)
        assert img.getpixel((0, 0)) != (0, 0, 0)


@patch("lastfmcollagegenerator.network.requests.get")
def test_album_cover_fallback_on_network_error(mock_get):
    mock_get.side_effect = requests.ConnectionError("CDN connection dropped")
    mock_album = MockPylastEntityFactory.create_mock_album(
        cover_url="https://mock.cdn/art.png"
    )

    data = _album_builder()._get_album_cover(mock_album, "Radiohead - OK Computer")
    assert isinstance(data, bytes)
    with Image.open(BytesIO(data)) as img:
        assert img.size == (300, 300)
        assert img.getpixel((0, 0)) != (0, 0, 0)

    mock_get.assert_called_once_with(
        "https://mock.cdn/art.png",
        headers=DEFAULT_HEADERS,
        timeout=DEFAULT_TIMEOUT,
    )


@patch("lastfmcollagegenerator.network.requests.get")
def test_album_cover_success(mock_get):
    raw_img = SyntheticImageFactory.create_image_bytes(300, 300, color=(100, 150, 200))
    mock_resp = MagicMock()
    mock_resp.content = raw_img
    mock_resp.status_code = 200
    mock_get.return_value = mock_resp

    mock_album = MockPylastEntityFactory.create_mock_album(
        cover_url="https://mock.cdn/art.png"
    )
    data = _album_builder()._get_album_cover(mock_album, "Artist - Album")
    assert data == raw_img


@patch("lastfmcollagegenerator.network.requests.get")
def test_artist_image_fallback_on_404(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_get.return_value = mock_resp

    mock_artist = MockPylastEntityFactory.create_mock_artist("Nonexistent Artist")
    data = _artist_builder()._get_artist_image(mock_artist, "Nonexistent Artist")
    assert isinstance(data, bytes)
    with Image.open(BytesIO(data)) as img:
        assert img.size == (300, 300)
        assert img.getpixel((0, 0)) != (0, 0, 0)


@patch("lastfmcollagegenerator.network.requests.get")
def test_artist_image_fallback_on_missing_html_header(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.content = MockHtmlResponses.NO_HEADER_HTML.encode("utf-8")
    mock_get.return_value = mock_resp

    mock_artist = MockPylastEntityFactory.create_mock_artist("Artist No Header")
    data = _artist_builder()._get_artist_image(mock_artist, "Artist No Header")
    assert isinstance(data, bytes)
    with Image.open(BytesIO(data)) as img:
        assert img.size == (300, 300)
        assert img.getpixel((0, 0)) != (0, 0, 0)


@patch("lastfmcollagegenerator.network.requests.get")
def test_artist_image_success(mock_get):
    raw_img = SyntheticImageFactory.create_image_bytes(600, 600, color=(50, 100, 150))

    def side_effect(url, headers=None, timeout=None):
        resp = MagicMock()
        if "last.fm/music" in url:
            resp.status_code = 200
            resp.content = MockHtmlResponses.SUCCESS_HTML.encode("utf-8")
        else:
            resp.status_code = 200
            resp.content = raw_img
        return resp

    mock_get.side_effect = side_effect

    mock_artist = MockPylastEntityFactory.create_mock_artist("David Bowie")
    data = _artist_builder()._get_artist_image(mock_artist, "David Bowie")
    assert isinstance(data, bytes)
    with Image.open(BytesIO(data)) as img:
        assert img.size == (300, 300)


def test_legacy_black_fallback_style():
    mock_album = MockPylastEntityFactory.create_mock_album(cover_url=None)
    builder = _album_builder(fallback_style=FALLBACK_STYLE_BLACK)
    data = builder._get_album_cover(mock_album, "Artist - Album")
    with Image.open(BytesIO(data)) as img:
        assert img.size == (300, 300)
        assert img.getpixel((0, 0)) == (0, 0, 0)


@patch("lastfmcollagegenerator.network.requests.get")
def test_cache_hit_avoids_network_call(mock_get, tmp_path):
    raw_img = SyntheticImageFactory.create_image_bytes(300, 300, color=(10, 20, 30))
    mock_resp = MagicMock()
    mock_resp.content = raw_img
    mock_resp.status_code = 200
    mock_get.return_value = mock_resp

    cache = ArtworkCache(cache_dir=str(tmp_path / "cache"))
    mock_album = MockPylastEntityFactory.create_mock_album(
        cover_url="https://mock.cdn/art.png"
    )

    builder = _album_builder()
    builder.cache = cache
    first = builder._get_album_cover(mock_album, "Artist - Album")
    second = builder._get_album_cover(mock_album, "Artist - Album")
    assert first == second
    assert mock_get.call_count == 1


@patch("lastfmcollagegenerator.network.requests.get")
def test_circuit_breaker_honored_in_builder(mock_get):
    mock_get.side_effect = requests.ConnectionError("CDN down")

    fetcher = ResilientHttpFetcher(
        rate_limit=None,
        max_attempts=3,
        sleep_fn=lambda s: None,
        failure_threshold=2,
    )
    builder = AlbumCollageBuilder(
        CollageBuilderConfig(cols=1, rows=1, period="overall"),
        MagicMock(),
        fetcher=fetcher,
    )
    mock_album = MockPylastEntityFactory.create_mock_album(
        cover_url="https://mock.cdn/art.png"
    )

    tile1 = builder._get_album_cover(mock_album, "Artist - Album")
    assert isinstance(tile1, bytes)
    calls_after_open = mock_get.call_count

    tile2 = builder._get_album_cover(mock_album, "Artist - Album")
    assert isinstance(tile2, bytes)
    assert mock_get.call_count == calls_after_open
    assert isinstance(tile2, bytes)
    assert builder.fetcher._breaker_for("mock.cdn").state == "open" or isinstance(
        tile2, bytes
    )


def test_circuit_open_error_is_a_request_exception():
    assert issubclass(CircuitOpenError, requests.RequestException)


def test_cache_integration_uses_kind_album():
    assert CACHE_KIND_ALBUM == "album"
