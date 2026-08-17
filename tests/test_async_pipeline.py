from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from PIL import Image
import httpx

from lastfmcollagegenerator.collage import (
    BaseCollageBuilder,
    AlbumCollageBuilder,
    ArtistCollageBuilder,
    TrackCollageBuilder,
    CollageBuilderConfig,
)
from lastfmcollagegenerator.collage_generator import CollageGenerator
from lastfmcollagegenerator.constants import ENTITY_ALBUM
from lastfmcollagegenerator.lastfm.client import LastfmClient
from tests.conftest import (
    MockPylastEntityFactory,
    MockHtmlResponses,
)


@pytest.mark.asyncio
async def test_lastfm_client_async_methods():
    client = LastfmClient("mock_key", "mock_secret")
    with patch.object(client.network, "get_user") as mock_get_user:
        mock_user = MagicMock()
        mock_get_user.return_value = mock_user
        mock_user.get_top_albums.return_value = ["mock_album"]
        mock_user.get_top_artists.return_value = ["mock_artist"]
        mock_user.get_top_tracks.return_value = ["mock_track"]

        user = await client.get_user_async("testuser")
        assert user == mock_user

        albums = await client.get_top_albums_async(user, limit=5, period="7day")
        assert albums == ["mock_album"]
        mock_user.get_top_albums.assert_called_once_with(period="7day", limit=5)

        artists = await client.get_top_artists_async(user, limit=5, period="7day")
        assert artists == ["mock_artist"]
        mock_user.get_top_artists.assert_called_once_with(period="7day", limit=5)

        tracks = await client.get_top_tracks_async(user, limit=5, period="7day")
        assert tracks == ["mock_track"]
        mock_user.get_top_tracks.assert_called_once_with(period="7day", limit=5)


@pytest.mark.asyncio
async def test_base_collage_builder_abstract_async_methods():
    config = CollageBuilderConfig(cols=1, rows=1, period="overall")
    builder = BaseCollageBuilder(config, MagicMock())
    with pytest.raises(NotImplementedError):
        await builder._get_tiles_from_top_items_async(MagicMock(), 1, "overall")
    with pytest.raises(NotImplementedError):
        await builder._create_tile_from_top_item_async(
            MagicMock(), MagicMock(), MagicMock()
        )


@pytest.mark.asyncio
async def test_album_collage_builder_create_async(synthetic_png_bytes):
    config = CollageBuilderConfig(cols=2, rows=2, period="overall")
    mock_client = MagicMock()
    mock_user = MagicMock()
    mock_client.get_user_async = AsyncMock(return_value=mock_user)
    mock_items = MockPylastEntityFactory.create_mock_top_items_list(4, "album")
    mock_client.get_top_albums_async = AsyncMock(return_value=mock_items)

    builder = AlbumCollageBuilder(config, mock_client)

    # Mock httpx.AsyncClient.get to return synthetic image
    async def mock_async_get(url, **kwargs):
        response = MagicMock()
        response.status_code = 200
        response.content = synthetic_png_bytes
        response.raise_for_status = MagicMock()
        return response

    with patch("httpx.AsyncClient.get", side_effect=mock_async_get):
        image = await builder.create_async("testuser")
        assert isinstance(image, Image.Image)
        assert image.size == (600, 600)


@pytest.mark.asyncio
async def test_album_collage_builder_async_fallbacks():
    config = CollageBuilderConfig(cols=1, rows=1, period="overall")
    mock_client = MagicMock()
    builder = AlbumCollageBuilder(config, mock_client)

    # Test item without cover image
    item_no_cover = MockPylastEntityFactory.create_mock_album(cover_url=None)
    item_no_cover.get_cover_image.return_value = None
    mock_http_client = AsyncMock()

    data = await builder._get_album_cover_async(
        mock_http_client, item_no_cover, "No Cover"
    )
    assert isinstance(data, bytes)

    # Test HTTP error on download
    item_error = MockPylastEntityFactory.create_mock_album(
        cover_url="https://fail.cdn/img.png"
    )
    mock_http_client.get = AsyncMock(side_effect=httpx.HTTPError("Connection failed"))
    data_err = await builder._get_album_cover_async(
        mock_http_client, item_error, "Err Cover"
    )
    assert isinstance(data_err, bytes)


@pytest.mark.asyncio
async def test_artist_collage_builder_create_async(synthetic_png_bytes):
    config = CollageBuilderConfig(cols=2, rows=2, period="overall")
    mock_client = MagicMock()
    mock_user = MagicMock()
    mock_client.get_user_async = AsyncMock(return_value=mock_user)
    mock_items = MockPylastEntityFactory.create_mock_top_items_list(4, "artist")
    mock_client.get_top_artists_async = AsyncMock(return_value=mock_items)

    builder = ArtistCollageBuilder(config, mock_client)

    async def mock_async_get(url, **kwargs):
        response = MagicMock()
        response.status_code = 200
        if "last.fm/music" in url:
            response.content = MockHtmlResponses.SUCCESS_HTML.encode("utf-8")
        else:
            response.content = synthetic_png_bytes
        response.raise_for_status = MagicMock()
        return response

    with patch("httpx.AsyncClient.get", side_effect=mock_async_get):
        image = await builder.create_async("testuser")
        assert isinstance(image, Image.Image)
        assert image.size == (600, 600)


@pytest.mark.asyncio
async def test_artist_collage_builder_async_fallbacks():
    config = CollageBuilderConfig(cols=1, rows=1, period="overall")
    mock_client = MagicMock()
    builder = ArtistCollageBuilder(config, mock_client)
    artist = MockPylastEntityFactory.create_mock_artist("Ghost Artist")

    # 404 response
    mock_http_client = AsyncMock()
    resp_404 = MagicMock()
    resp_404.status_code = 404
    mock_http_client.get.return_value = resp_404

    data = await builder._get_artist_image_async(mock_http_client, artist, "Ghost")
    assert isinstance(data, bytes)

    # Missing image in html
    resp_missing = MagicMock()
    resp_missing.status_code = 200
    resp_missing.content = MockHtmlResponses.MISSING_IMAGE_HTML.encode("utf-8")
    resp_missing.raise_for_status = MagicMock()
    mock_http_client.get.return_value = resp_missing

    data_missing = await builder._get_artist_image_async(
        mock_http_client, artist, "Ghost"
    )
    assert isinstance(data_missing, bytes)


@pytest.mark.asyncio
async def test_track_collage_builder_create_async(synthetic_png_bytes):
    config = CollageBuilderConfig(cols=1, rows=1, period="overall")
    mock_client = MagicMock()
    mock_user = MagicMock()
    mock_client.get_user_async = AsyncMock(return_value=mock_user)
    mock_items = MockPylastEntityFactory.create_mock_top_items_list(1, "track")
    mock_client.get_top_tracks_async = AsyncMock(return_value=mock_items)

    builder = TrackCollageBuilder(config, mock_client)

    async def mock_async_get(url, **kwargs):
        response = MagicMock()
        response.status_code = 200
        response.content = synthetic_png_bytes
        response.raise_for_status = MagicMock()
        return response

    with patch("httpx.AsyncClient.get", side_effect=mock_async_get):
        image = await builder.create_async("testuser")
        assert isinstance(image, Image.Image)
        assert image.size == (300, 300)


@pytest.mark.asyncio
async def test_async_cache_integration(synthetic_png_bytes):
    config = CollageBuilderConfig(cols=1, rows=1, period="overall")
    mock_client = MagicMock()
    mock_cache = MagicMock()
    mock_cache.get.return_value = synthetic_png_bytes

    builder = AlbumCollageBuilder(config, mock_client, cache=mock_cache)
    mock_http_client = AsyncMock()

    data = await builder._download_bytes_async(
        mock_http_client, "https://cached.url/img.png", "album"
    )
    assert data == synthetic_png_bytes
    mock_cache.get.assert_called_once_with("https://cached.url/img.png", "album")
    mock_http_client.get.assert_not_called()


@pytest.mark.asyncio
async def test_facade_generate_async_methods():
    generator = CollageGenerator("mock_key", "mock_secret")
    mock_image = Image.new("RGB", (900, 900), color="green")

    with patch.object(
        BaseCollageBuilder, "create_async", new_callable=AsyncMock
    ) as mock_create_async:
        mock_create_async.return_value = mock_image

        res1 = await generator.generate_async(
            entity=ENTITY_ALBUM,
            username="testuser",
            cols=3,
            rows=3,
        )
        assert isinstance(res1, Image.Image)
        assert res1 == mock_image

        res_album = await generator.generate_top_albums_collage_async(
            username="testuser", cols=3, rows=3
        )
        assert isinstance(res_album, Image.Image)

        res_artist = await generator.generate_top_artists_collage_async(
            username="testuser", cols=3, rows=3
        )
        assert isinstance(res_artist, Image.Image)

        res_track = await generator.generate_top_tracks_collage_async(
            username="testuser", cols=3, rows=3
        )
        assert isinstance(res_track, Image.Image)
