from unittest.mock import MagicMock, patch
from io import BytesIO
import pytest
from PIL import Image, ImageFont

from lastfmcollagegenerator.collage import (
    BaseCollageBuilder,
    AlbumCollageBuilder,
    ArtistCollageBuilder,
    TrackCollageBuilder,
    CollageBuilderFactory,
    CollageBuilderConfig,
    CollageTile,
)
from lastfmcollagegenerator.constants import ENTITY_ALBUM, ENTITY_ARTIST, ENTITY_TRACK
from tests.conftest import (
    SyntheticImageFactory,
    MockPylastEntityFactory,
)


def test_factory_dispatches_correct_builders():
    config = CollageBuilderConfig(cols=3, rows=3, period="overall")
    mock_client = MagicMock()

    album_builder = CollageBuilderFactory(ENTITY_ALBUM, config, mock_client)
    assert isinstance(album_builder, AlbumCollageBuilder)
    assert repr(album_builder) == "<AlbumCollage [3x3, overall]>"

    artist_builder = CollageBuilderFactory(ENTITY_ARTIST, config, mock_client)
    assert isinstance(artist_builder, ArtistCollageBuilder)
    assert repr(artist_builder) == "<ArtistCollage [3x3, overall]>"

    track_builder = CollageBuilderFactory(ENTITY_TRACK, config, mock_client)
    assert isinstance(track_builder, TrackCollageBuilder)
    assert repr(track_builder) == "<TrackCollage [3x3, overall]>"


def test_factory_invalid_entity():
    config = CollageBuilderConfig(cols=3, rows=3, period="overall")
    with pytest.raises(ValueError, match="Invalid entity: invalid_entity"):
        CollageBuilderFactory("invalid_entity", config, MagicMock())


def test_generate_blank_tile():
    blank_bytes = BaseCollageBuilder._generate_blank_tile()
    assert isinstance(blank_bytes, bytes)
    with Image.open(BytesIO(blank_bytes)) as img:
        assert img.size == (300, 300)
        assert img.mode == "RGB"
        assert img.getpixel((0, 0)) == (0, 0, 0)


def test_base_collage_builder_abstract_methods():
    config = CollageBuilderConfig(cols=1, rows=1, period="overall")
    builder = BaseCollageBuilder(config, MagicMock())
    with pytest.raises(NotImplementedError):
        builder._get_tiles_from_top_items(MagicMock(), 1, "overall")
    with pytest.raises(NotImplementedError):
        BaseCollageBuilder._create_tile_from_top_item(MagicMock())


def test_insert_newline_characters_long_title():
    config = CollageBuilderConfig(cols=1, rows=1, period="overall")
    builder = BaseCollageBuilder(config, MagicMock())
    font = ImageFont.load_default()
    long_title = "A" * 150
    formatted = builder._insert_newline_characters_to_text(font, long_title)
    assert "\n" in formatted


def test_deterministic_tile_sorting_on_tied_playcounts():
    items = [
        MockPylastEntityFactory.create_mock_top_item(
            item=MockPylastEntityFactory.create_mock_album(
                artist="Band A", title="Album B"
            ),
            weight=500,
        ),
        MockPylastEntityFactory.create_mock_top_item(
            item=MockPylastEntityFactory.create_mock_album(
                artist="Band A", title="Album Z"
            ),
            weight=500,
        ),
        MockPylastEntityFactory.create_mock_top_item(
            item=MockPylastEntityFactory.create_mock_album(
                artist="Band A", title="Album A"
            ),
            weight=500,
        ),
        MockPylastEntityFactory.create_mock_top_item(
            item=MockPylastEntityFactory.create_mock_album(
                artist="Band Top", title="Top Hits"
            ),
            weight=1000,
        ),
    ]

    sample_bytes = SyntheticImageFactory.create_image_bytes(300, 300)

    class DummyBuilder(BaseCollageBuilder):
        @classmethod
        def _create_tile_from_top_item(cls, top_item):
            return CollageTile(
                data=sample_bytes,
                playcount=top_item.weight,
                title=f"{top_item.item.artist} - {top_item.item.title}",
            )

    tiles = DummyBuilder._create_tiles_from_top_items(items)

    assert len(tiles) == 4
    assert tiles[0].playcount == 1000
    assert tiles[0].title == "Band Top - Top Hits"
    assert tiles[1].playcount == 500
    assert tiles[1].title == "Band A - Album Z"
    assert tiles[2].playcount == 500
    assert tiles[2].title == "Band A - Album B"
    assert tiles[3].playcount == 500
    assert tiles[3].title == "Band A - Album A"


def test_album_collage_builder_create(mock_lastfm_client):
    config = CollageBuilderConfig(cols=2, rows=2, period="7day", show_playcount=False)
    builder = AlbumCollageBuilder(config, mock_lastfm_client)

    sample_bytes = SyntheticImageFactory.create_image_bytes(300, 300)
    with patch.object(
        AlbumCollageBuilder, "_get_album_cover", return_value=sample_bytes
    ):
        img = builder.create("testuser")
        assert isinstance(img, Image.Image)
        assert img.size == (600, 600)


def test_artist_collage_builder_create(mock_lastfm_client):
    config = CollageBuilderConfig(cols=2, rows=1, period="1month", show_playcount=True)
    builder = ArtistCollageBuilder(config, mock_lastfm_client)

    sample_bytes = SyntheticImageFactory.create_image_bytes(300, 300)
    with patch.object(
        ArtistCollageBuilder, "_get_artist_image", return_value=sample_bytes
    ):
        img = builder.create("testuser")
        assert isinstance(img, Image.Image)
        assert img.size == (600, 300)


def test_track_collage_builder_create(mock_lastfm_client):
    config = CollageBuilderConfig(cols=1, rows=2, period="overall", show_playcount=True)
    builder = TrackCollageBuilder(config, mock_lastfm_client)

    sample_bytes = SyntheticImageFactory.create_image_bytes(300, 300)
    with patch.object(
        TrackCollageBuilder, "_get_album_cover", return_value=sample_bytes
    ):
        img = builder.create("testuser")
        assert isinstance(img, Image.Image)
        assert img.size == (300, 600)


def test_builder_resizes_non_standard_tile_images():
    config = CollageBuilderConfig(cols=1, rows=1, period="overall", tile_size=150)
    builder = BaseCollageBuilder(config, MagicMock())

    # 500x500 source image bytes
    oversized_bytes = SyntheticImageFactory.create_image_bytes(500, 500)
    tiles = [CollageTile(data=oversized_bytes, playcount=42, title="Big Image")]

    img = builder._create_image(tiles, cols=1, rows=1)
    assert img.size == (150, 150)


def test_generate_blank_tile_custom_dimensions():
    blank_bytes = BaseCollageBuilder._generate_blank_tile(120, 120)
    with Image.open(BytesIO(blank_bytes)) as img:
        assert img.size == (120, 120)
        assert img.mode == "RGB"
        assert img.getpixel((0, 0)) == (0, 0, 0)
