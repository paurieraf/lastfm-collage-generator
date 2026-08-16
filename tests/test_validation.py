import pytest
from lastfmcollagegenerator.collage_generator import CollageGenerator


@pytest.fixture
def generator():
    return CollageGenerator("dummy_api_key", "dummy_api_secret")


def test_validation_valid_inputs(generator):
    # Should not raise exception
    generator._validate_parameters(
        entity="album",
        username="valid_user",
        cols=3,
        rows=3,
        period="7day",
    )
    generator._validate_parameters(
        entity="album",
        username="valid_user",
        cols=20,
        rows=20,
        period="overall",
        tile_size=100,
    )


@pytest.mark.parametrize(
    "cols,rows",
    [
        (0, 3),
        (-1, 3),
        (3, 0),
        (3, -2),
        (21, 3),
        (3, 21),
        (25, 25),
    ],
)
def test_validation_invalid_dimensions(generator, cols, rows):
    with pytest.raises(ValueError, match="Invalid number of columns or rows"):
        generator._validate_parameters(
            entity="album",
            username="valid_user",
            cols=cols,
            rows=rows,
            period="overall",
        )


def test_validation_max_tiles_exceeded(generator):
    generator.MAX_TILES = 50
    with pytest.raises(ValueError, match="exceeds maximum capacity"):
        generator._validate_parameters(
            entity="album",
            username="valid_user",
            cols=10,
            rows=10,
            period="overall",
        )


@pytest.mark.parametrize(
    "cols,rows",
    [
        ("3", 3),
        (3, "3"),
        (2.5, 3),
        (3, 2.5),
        (True, 3),
        (3, False),
        (None, 3),
    ],
)
def test_validation_invalid_dimension_types(generator, cols, rows):
    with pytest.raises(TypeError, match="Columns and rows must be integers"):
        generator._validate_parameters(
            entity="album",
            username="valid_user",
            cols=cols,
            rows=rows,
            period="overall",
        )


@pytest.mark.parametrize(
    "tile_size",
    [
        49,
        0,
        -10,
        601,
        1000,
    ],
)
def test_validation_invalid_tile_size(generator, tile_size):
    with pytest.raises(ValueError, match="Invalid tile_size"):
        generator._validate_parameters(
            entity="album",
            username="valid_user",
            cols=3,
            rows=3,
            period="overall",
            tile_size=tile_size,
        )


@pytest.mark.parametrize(
    "tile_size",
    [
        "300",
        150.5,
        [100],
    ],
)
def test_validation_invalid_tile_size_type(generator, tile_size):
    with pytest.raises(TypeError, match="tile_size must be an integer"):
        generator._validate_parameters(
            entity="album",
            username="valid_user",
            cols=3,
            rows=3,
            period="overall",
            tile_size=tile_size,
        )


def test_resolve_tile_size(generator):
    assert generator._resolve_tile_size(3, 3) == 300
    assert generator._resolve_tile_size(5, 5) == 300
    assert generator._resolve_tile_size(6, 6) == 150
    assert generator._resolve_tile_size(10, 10) == 150
    assert generator._resolve_tile_size(3, 10) == 150
    assert generator._resolve_tile_size(11, 11) == 100
    assert generator._resolve_tile_size(20, 20) == 100
    assert generator._resolve_tile_size(5, 5, tile_size=200) == 200


@pytest.mark.parametrize(
    "username",
    [
        "",
        "   ",
        None,
        123,
    ],
)
def test_validation_invalid_username(generator, username):
    with pytest.raises(
        ValueError, match="A valid non-empty username string is required"
    ):
        generator._validate_parameters(
            entity="album",
            username=username,
            cols=3,
            rows=3,
            period="overall",
        )


def test_validation_invalid_entity(generator):
    with pytest.raises(ValueError, match="Invalid entity: playlist"):
        generator._validate_parameters(
            entity="playlist",
            username="valid_user",
            cols=3,
            rows=3,
            period="overall",
        )


def test_validation_invalid_period(generator):
    with pytest.raises(ValueError, match="Invalid period: yesterday"):
        generator._validate_parameters(
            entity="album",
            username="valid_user",
            cols=3,
            rows=3,
            period="yesterday",
        )


def test_validation_invalid_overlay_style(generator):
    with pytest.raises(ValueError, match="Invalid overlay_style: 'invalid_style'"):
        generator._validate_parameters(
            entity="album",
            username="valid_user",
            cols=3,
            rows=3,
            period="overall",
            overlay_style="invalid_style",
        )


def test_validation_invalid_show_text_type(generator):
    with pytest.raises(TypeError, match="show_text must be a boolean"):
        generator._validate_parameters(
            entity="album",
            username="valid_user",
            cols=3,
            rows=3,
            period="overall",
            show_text="true",
        )


def test_validation_invalid_font_path(generator):
    with pytest.raises(TypeError, match="font_path must be a string or None"):
        generator._validate_parameters(
            entity="album",
            username="valid_user",
            cols=3,
            rows=3,
            period="overall",
            font_path=123,
        )

    with pytest.raises(FileNotFoundError, match="Custom font file not found"):
        generator._validate_parameters(
            entity="album",
            username="valid_user",
            cols=3,
            rows=3,
            period="overall",
            font_path="/non/existent/path/font.ttf",
        )


def test_validation_invalid_theme_preset(generator):
    with pytest.raises(ValueError, match="Unknown theme preset"):
        generator._validate_parameters(
            entity="album",
            username="valid_user",
            cols=3,
            rows=3,
            period="overall",
            theme="invalid_theme_preset",
        )


def test_validation_invalid_fallback_style(generator):
    with pytest.raises(ValueError, match="Invalid fallback_style"):
        generator._validate_parameters(
            entity="album",
            username="valid_user",
            cols=3,
            rows=3,
            period="overall",
            fallback_style="rainbow",
        )


def test_validation_invalid_cache_ttl_override(generator):
    with pytest.raises(ValueError, match="cache_ttl_override"):
        generator._validate_parameters(
            entity="album",
            username="valid_user",
            cols=3,
            rows=3,
            period="overall",
            cache_ttl_override=0,
        )
    with pytest.raises(TypeError, match="cache_ttl_override"):
        generator._validate_parameters(
            entity="album",
            username="valid_user",
            cols=3,
            rows=3,
            period="overall",
            cache_ttl_override="30",
        )


def test_validation_invalid_cache_dir_type(generator):
    with pytest.raises(TypeError, match="cache_dir"):
        generator._validate_parameters(
            entity="album",
            username="valid_user",
            cols=3,
            rows=3,
            period="overall",
            cache_dir=123,
        )


def test_validation_invalid_rate_limit(generator):
    with pytest.raises(ValueError, match="rate_limit"):
        generator._validate_parameters(
            entity="album",
            username="valid_user",
            cols=3,
            rows=3,
            period="overall",
            rate_limit=0,
        )
    with pytest.raises(TypeError, match="rate_limit"):
        generator._validate_parameters(
            entity="album",
            username="valid_user",
            cols=3,
            rows=3,
            period="overall",
            rate_limit="fast",
        )


def test_validation_invalid_preset_type(generator):
    with pytest.raises(TypeError, match="preset"):
        generator._validate_parameters(
            entity="album",
            username="valid_user",
            cols=3,
            rows=3,
            period="overall",
            preset=123,
        )


def test_validation_invalid_border_color(generator):
    with pytest.raises(TypeError):
        generator._validate_parameters(
            entity="album",
            username="valid_user",
            cols=3,
            rows=3,
            period="overall",
            border_color=42,
        )


def test_validation_geometry_type_checks(generator):
    with pytest.raises(TypeError, match="corner_radius"):
        generator._validate_parameters(
            entity="album",
            username="valid_user",
            cols=3,
            rows=3,
            period="overall",
            corner_radius=1.5,
        )
    with pytest.raises(TypeError, match="spacing"):
        generator._validate_parameters(
            entity="album",
            username="valid_user",
            cols=3,
            rows=3,
            period="overall",
            spacing="8",
        )
