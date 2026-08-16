from typing import cast
from PIL import Image

from lastfmcollagegenerator.collage import (
    CollageBuilderFactory,
    LastfmConfig,
    CollageBuilderConfig,
    BaseCollageBuilder,
)
from lastfmcollagegenerator.constants import (
    ENTITIES,
    PERIODS,
    ENTITY_ALBUM,
    ENTITY_ARTIST,
    ENTITY_TRACK,
)
from lastfmcollagegenerator.lastfm.client import LastfmClient


class CollageGenerator:
    """Generates a NxN collage with the covers of a Last.fm

    user tops of a given period.
    """

    MAX_COLS = 5
    MAX_ROWS = 5

    def __init__(self, lastfm_api_key: str, lastfm_api_secret: str) -> None:
        self.lastfm_config = LastfmConfig(
            lastfm_api_key=lastfm_api_key,
            lastfm_api_secret=lastfm_api_secret,
        )

    def generate(
        self,
        entity: str,
        username: str,
        cols: int,
        rows: int,
        period: str = "overall",
    ) -> Image.Image:
        """Generate a composite collage image from a Last.fm user's top items.

        Args:
            entity: Entity type. One of: "album", "artist", "track".
            username: Valid Last.fm username.
            cols: Number of columns (1–5).
            rows: Number of rows (1–5).
            period: Aggregation period. One of: "7day", "1month", "3month",
                    "6month", "12month", "overall".

        Returns:
            PIL.Image.Image: RGB composite canvas with dimensions
            (cols * 300, rows * 300) pixels.

        Raises:
            ValueError: If any parameter is invalid or out of bounds.
            TypeError: If cols or rows are not integers.
        """
        self._validate_parameters(
            entity=entity,
            username=username,
            cols=cols,
            rows=rows,
            period=period,
        )
        collage_builder = self._get_collage_builder(entity, cols, rows, period)
        return collage_builder.create(username)

    def generate_top_albums_collage(
        self,
        username: str,
        cols: int = 5,
        rows: int = 5,
        period: str = "overall",
    ) -> Image.Image:
        """Convenience method to generate an album collage."""
        return self.generate(
            entity=ENTITY_ALBUM,
            username=username,
            cols=cols,
            rows=rows,
            period=period,
        )

    def generate_top_artists_collage(
        self,
        username: str,
        cols: int = 5,
        rows: int = 5,
        period: str = "overall",
    ) -> Image.Image:
        """Convenience method to generate an artist collage."""
        return self.generate(
            entity=ENTITY_ARTIST,
            username=username,
            cols=cols,
            rows=rows,
            period=period,
        )

    def generate_top_tracks_collage(
        self,
        username: str,
        cols: int = 5,
        rows: int = 5,
        period: str = "overall",
    ) -> Image.Image:
        """Convenience method to generate a track collage."""
        return self.generate(
            entity=ENTITY_TRACK,
            username=username,
            cols=cols,
            rows=rows,
            period=period,
        )

    def _get_collage_builder(
        self, entity: str, cols: int, rows: int, period: str
    ) -> BaseCollageBuilder:
        collage_builder_config = CollageBuilderConfig(
            cols=cols,
            rows=rows,
            period=period,
        )
        lastfm_client = LastfmClient(
            api_key=self.lastfm_config.lastfm_api_key,
            api_secret=self.lastfm_config.lastfm_api_secret,
        )
        return cast(
            BaseCollageBuilder,
            CollageBuilderFactory(
                entity=entity,
                config=collage_builder_config,
                lastfm_client=lastfm_client,
            ),
        )

    def _validate_parameters(
        self,
        entity: str,
        username: str,
        cols: int,
        rows: int,
        period: str,
    ) -> None:
        if not isinstance(username, str) or not username.strip():
            raise ValueError("A valid non-empty username string is required.")

        if type(cols) is not int or type(rows) is not int:
            raise TypeError("Columns and rows must be integers.")

        if cols < 1 or cols > self.MAX_COLS or rows < 1 or rows > self.MAX_ROWS:
            raise ValueError(
                f"Invalid number of columns or rows: {cols}x{rows}. "
                f"Allowed bounds are 1 to {self.MAX_COLS} columns "
                f"and 1 to {self.MAX_ROWS} rows."
            )

        if entity not in ENTITIES:
            raise ValueError(f"Invalid entity: {entity}. Options are: {ENTITIES}")

        if period not in PERIODS:
            raise ValueError(f"Invalid period: {period}. Options are: {PERIODS}")
