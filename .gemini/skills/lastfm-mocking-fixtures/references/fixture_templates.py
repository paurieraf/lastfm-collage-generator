"""Pytest Fixture Templates & Mock Builders for lastfm-collage-generator.

Provides synthetic image generation, pylast entity mocking, and HTML retrieval
response simulators for offline, zero-network automated testing.
"""

import io
from typing import Any, List, Optional, Tuple, Union
from unittest.mock import MagicMock
from PIL import Image, ImageDraw


class SyntheticImageFactory:
    """Factory for creating in-memory synthetic PIL images and raw image bytes."""

    @staticmethod
    def create_image_bytes(
        width: int = 300,
        height: int = 300,
        color: Union[str, Tuple[int, int, int]] = "blue",
        format: str = "PNG",
        text_label: Optional[str] = None,
    ) -> bytes:
        """Generates raw image bytes in-memory for testing."""
        img = Image.new("RGB", (width, height), color=color)
        if text_label:
            draw = ImageDraw.Draw(img)
            draw.text((10, 10), text_label, fill=(255, 255, 255))
        with io.BytesIO() as buf:
            img.save(buf, format=format)
            return buf.getvalue()

    @staticmethod
    def create_pil_image(
        width: int = 300,
        height: int = 300,
        color: Union[str, Tuple[int, int, int]] = "red",
    ) -> Image.Image:
        """Generates a PIL Image instance."""
        return Image.new("RGB", (width, height), color=color)


class MockPylastEntityFactory:
    """Generates mock pylast entities (User, TopItem, Album, Artist, Track)."""

    @staticmethod
    def create_mock_album(
        artist: str = "Radiohead",
        title: str = "OK Computer",
        cover_url: str = "https://mock.cdn/ok_computer.png",
    ) -> MagicMock:
        """Creates a mock pylast.Album."""
        mock_album = MagicMock()
        mock_album.artist = artist
        mock_album.title = title
        mock_album.get_cover_image.return_value = cover_url
        mock_album.__repr__ = lambda s: f"<pylast.Album '{artist}' - '{title}'>"
        return mock_album

    @staticmethod
    def create_mock_artist(
        name: str = "David Bowie",
    ) -> MagicMock:
        """Creates a mock pylast.Artist."""
        mock_artist = MagicMock()
        mock_artist.name = name
        mock_artist.__repr__ = lambda s: f"<pylast.Artist '{name}'>"
        return mock_artist

    @staticmethod
    def create_mock_track(
        artist: str = "Daft Punk",
        title: str = "Harder, Better, Faster, Stronger",
        cover_url: str = "https://mock.cdn/discovery.png",
    ) -> MagicMock:
        """Creates a mock pylast.Track."""
        mock_track = MagicMock()
        mock_track.artist = artist
        mock_track.title = title
        mock_track.get_cover_image.return_value = cover_url
        mock_track.__repr__ = lambda s: f"<pylast.Track '{artist}' - '{title}'>"
        return mock_track

    @classmethod
    def create_mock_top_item(
        cls,
        item: Union[MagicMock, Any] = None,
        weight: int = 100,
        entity_type: str = "album",
        index: int = 1,
    ) -> MagicMock:
        """Creates a mock pylast.TopItem containing an entity."""
        if item is None:
            if entity_type == "artist":
                item = cls.create_mock_artist(name=f"Artist {index}")
            elif entity_type == "track":
                item = cls.create_mock_track(artist=f"Artist {index}", title=f"Track {index}")
            else:
                item = cls.create_mock_album(artist=f"Artist {index}", title=f"Album {index}")

        top_item = MagicMock()
        top_item.item = item
        top_item.weight = weight
        return top_item

    @classmethod
    def create_mock_top_items_list(
        cls,
        count: int = 9,
        entity_type: str = "album",
    ) -> List[MagicMock]:
        """Creates a list of mock TopItem objects sorted descending by weight."""
        items = []
        for i in range(1, count + 1):
            weight = 1000 - (i * 50)
            items.append(
                cls.create_mock_top_item(
                    weight=weight,
                    entity_type=entity_type,
                    index=i,
                )
            )
        return items


class MockHtmlResponses:
    """Simulated HTML responses for Last.fm artist web retrieval."""

    SUCCESS_HTML = """
    <!DOCTYPE html>
    <html lang="en">
    <head><title>Artist on Last.fm</title></head>
    <body>
      <div class="header-new-background-image" content="https://lastfm.freetls.fastly.net/i/u/avatar170s/mock_artist.png"></div>
    </body>
    </html>
    """

    MISSING_IMAGE_HTML = """
    <!DOCTYPE html>
    <html lang="en">
    <head><title>Artist on Last.fm</title></head>
    <body>
      <div class="header-new-background-image"></div>
    </body>
    </html>
    """

    NO_HEADER_HTML = """
    <!DOCTYPE html>
    <html lang="en">
    <head><title>Artist on Last.fm</title></head>
    <body>
      <div class="artist-content">No background header present</div>
    </body>
    </html>
    """


class MockLastfmClient:
    """Drop-in mock for lastfmcollagegenerator.lastfm.client.LastfmClient."""

    def __init__(self, api_key: str = "mock_key", api_secret: str = "mock_secret") -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.mock_user = MagicMock()

    def get_user(self, username: str) -> MagicMock:
        return self.mock_user

    def get_top_albums(self, user: MagicMock, limit: int, period: str) -> List[MagicMock]:
        return MockPylastEntityFactory.create_mock_top_items_list(count=limit, entity_type="album")

    def get_top_artists(self, user: MagicMock, limit: int, period: str) -> List[MagicMock]:
        return MockPylastEntityFactory.create_mock_top_items_list(count=limit, entity_type="artist")

    def get_top_tracks(self, user: MagicMock, limit: int, period: str) -> List[MagicMock]:
        return MockPylastEntityFactory.create_mock_top_items_list(count=limit, entity_type="track")


# Standard Pytest Fixtures (Can be imported into tests/conftest.py)

try:
    import pytest

    @pytest.fixture
    def synthetic_png_bytes() -> bytes:
        """Provides a 300x300 blue PNG byte stream."""
        return SyntheticImageFactory.create_image_bytes(300, 300, color=(30, 144, 255))

    @pytest.fixture
    def mock_lastfm_client() -> MockLastfmClient:
        """Provides a fully mocked LastfmClient instance."""
        return MockLastfmClient()

    @pytest.fixture
    def mock_album_top_items() -> List[MagicMock]:
        """Provides 9 mock album top items."""
        return MockPylastEntityFactory.create_mock_top_items_list(9, "album")

    @pytest.fixture
    def mock_artist_top_items() -> List[MagicMock]:
        """Provides 9 mock artist top items."""
        return MockPylastEntityFactory.create_mock_top_items_list(9, "artist")

    @pytest.fixture
    def mock_track_top_items() -> List[MagicMock]:
        """Provides 9 mock track top items."""
        return MockPylastEntityFactory.create_mock_top_items_list(9, "track")

except ImportError:
    pass
