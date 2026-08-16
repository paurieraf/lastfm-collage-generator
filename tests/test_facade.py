from unittest.mock import patch, MagicMock
import pytest
from PIL import Image

from lastfmcollagegenerator.collage_generator import CollageGenerator
from lastfmcollagegenerator.constants import ENTITY_ALBUM, ENTITY_ARTIST, ENTITY_TRACK


@pytest.fixture
def mock_builder():
    mock = MagicMock()
    mock.create.return_value = Image.new("RGB", (900, 900), color="blue")
    return mock


@patch("lastfmcollagegenerator.collage_generator.CollageBuilderFactory")
@patch("lastfmcollagegenerator.collage_generator.LastfmClient")
def test_generate_top_albums_collage(mock_client_cls, mock_factory_cls, mock_builder):
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


@patch("lastfmcollagegenerator.collage_generator.CollageBuilderFactory")
@patch("lastfmcollagegenerator.collage_generator.LastfmClient")
def test_generate_top_artists_collage(mock_client_cls, mock_factory_cls, mock_builder):
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


@patch("lastfmcollagegenerator.collage_generator.CollageBuilderFactory")
@patch("lastfmcollagegenerator.collage_generator.LastfmClient")
def test_generate_top_tracks_collage(mock_client_cls, mock_factory_cls, mock_builder):
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
    mock_builder.create.assert_called_once_with("testuser")
