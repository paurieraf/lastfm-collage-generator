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


@pytest.mark.parametrize(
    "cols,rows",
    [
        (0, 3),
        (-1, 3),
        (3, 0),
        (3, -2),
        (6, 3),
        (3, 6),
        (10, 10),
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
