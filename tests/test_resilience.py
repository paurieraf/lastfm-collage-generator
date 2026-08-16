from unittest.mock import patch, MagicMock
from io import BytesIO
import requests
from PIL import Image

from lastfmcollagegenerator.collage import (
    AlbumCollageBuilder,
    ArtistCollageBuilder,
    DEFAULT_HEADERS,
    DEFAULT_TIMEOUT,
)
from lastfmcollagegenerator.exceptions import (
    LastfmCollageGeneratorError,
    ArtistNotFound,
    ArtistImageNotFound,
)
from tests.conftest import (
    SyntheticImageFactory,
    MockPylastEntityFactory,
    MockHtmlScraperResponses,
)


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
    data = AlbumCollageBuilder._get_album_cover(mock_album)
    assert isinstance(data, bytes)
    with Image.open(BytesIO(data)) as img:
        assert img.size == (300, 300)
        assert img.getpixel((0, 0)) == (0, 0, 0)


def test_album_cover_fallback_on_exception_getting_url():
    mock_album = MagicMock()
    mock_album.get_cover_image.side_effect = IndexError("No cover image index")
    data = AlbumCollageBuilder._get_album_cover(mock_album)
    assert isinstance(data, bytes)
    with Image.open(BytesIO(data)) as img:
        assert img.size == (300, 300)
        assert img.getpixel((0, 0)) == (0, 0, 0)


@patch("lastfmcollagegenerator.collage.requests.get")
def test_album_cover_fallback_on_network_error(mock_get):
    mock_get.side_effect = requests.ConnectionError("CDN connection dropped")
    mock_album = MockPylastEntityFactory.create_mock_album(
        cover_url="https://mock.cdn/art.png"
    )

    data = AlbumCollageBuilder._get_album_cover(mock_album)
    assert isinstance(data, bytes)
    with Image.open(BytesIO(data)) as img:
        assert img.size == (300, 300)
        assert img.getpixel((0, 0)) == (0, 0, 0)

    mock_get.assert_called_once_with(
        "https://mock.cdn/art.png",
        headers=DEFAULT_HEADERS,
        timeout=DEFAULT_TIMEOUT,
    )


@patch("lastfmcollagegenerator.collage.requests.get")
def test_album_cover_success(mock_get):
    raw_img = SyntheticImageFactory.create_image_bytes(300, 300, color=(100, 150, 200))
    mock_resp = MagicMock()
    mock_resp.content = raw_img
    mock_get.return_value = mock_resp

    mock_album = MockPylastEntityFactory.create_mock_album(
        cover_url="https://mock.cdn/art.png"
    )
    data = AlbumCollageBuilder._get_album_cover(mock_album)
    assert data == raw_img


@patch("lastfmcollagegenerator.collage.requests.get")
def test_artist_image_fallback_on_404(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_get.return_value = mock_resp

    mock_artist = MockPylastEntityFactory.create_mock_artist("Nonexistent Artist")
    data = ArtistCollageBuilder._get_artist_image(mock_artist)
    assert isinstance(data, bytes)
    with Image.open(BytesIO(data)) as img:
        assert img.size == (300, 300)
        assert img.getpixel((0, 0)) == (0, 0, 0)


@patch("lastfmcollagegenerator.collage.requests.get")
def test_artist_image_fallback_on_missing_html_header(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.content = MockHtmlScraperResponses.NO_HEADER_HTML.encode("utf-8")
    mock_get.return_value = mock_resp

    mock_artist = MockPylastEntityFactory.create_mock_artist("Artist No Header")
    data = ArtistCollageBuilder._get_artist_image(mock_artist)
    assert isinstance(data, bytes)
    with Image.open(BytesIO(data)) as img:
        assert img.size == (300, 300)
        assert img.getpixel((0, 0)) == (0, 0, 0)


@patch("lastfmcollagegenerator.collage.requests.get")
def test_artist_image_success(mock_get):
    raw_img = SyntheticImageFactory.create_image_bytes(600, 600, color=(50, 100, 150))

    def side_effect(url, headers=None, timeout=None):
        resp = MagicMock()
        if "last.fm/music" in url:
            resp.status_code = 200
            resp.content = MockHtmlScraperResponses.SUCCESS_HTML.encode("utf-8")
        else:
            resp.status_code = 200
            resp.content = raw_img
        return resp

    mock_get.side_effect = side_effect

    mock_artist = MockPylastEntityFactory.create_mock_artist("David Bowie")
    data = ArtistCollageBuilder._get_artist_image(mock_artist)
    assert isinstance(data, bytes)
    with Image.open(BytesIO(data)) as img:
        assert img.size == (300, 300)
