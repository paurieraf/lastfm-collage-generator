from typing import cast

from PIL import Image

from lastfmcollagegenerator.collage import (
    BaseCollageBuilder,
    CollageBuilderConfig,
    CollageBuilderFactory,
    LastfmConfig,
)
from lastfmcollagegenerator.constants import (
    ENTITIES,
    ENTITY_ALBUM,
    ENTITY_ARTIST,
    ENTITY_TRACK,
    PERIODS,
)
from lastfmcollagegenerator.lastfm.client import LastfmClient


class CollageGenerator:
    """
    Generates a NxN collage with the covers of a Last.fm
    user tops of a given period.
    """

    MAX_COLS = 5
    MAX_ROWS = 5
    MIN_COLS = 1
    MIN_ROWS = 1
    DEFAULT_PERIOD = "7day"

    def __init__(self, lastfm_api_key: str, lastfm_api_secret: str) -> None:
        self.lastfm_config = LastfmConfig(
            lastfm_api_key=lastfm_api_key, lastfm_api_secret=lastfm_api_secret
        )

    def generate(
        self, entity: str, username: str, cols: int, rows: int, period: str
    ) -> Image.Image:
        """
        Generate a composite collage image from a Last.fm user's top items.

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
        """
        self._validate_parameters(entity, cols, rows, period)
        collage_builder = self._get_collage_builder(entity, cols, rows, period)
        return collage_builder.create(username)

    # ------------------------------------------------------------------
    # Convenience Methods
    # ------------------------------------------------------------------

    def generate_top_albums_collage(
        self, username: str, cols: int, rows: int, period: str = DEFAULT_PERIOD
    ) -> Image.Image:
        """
        Generate a collage from the user's top albums.

        Args:
            username: Valid Last.fm username.
            cols: Number of columns (1–5).
            rows: Number of rows (1–5).
            period: Aggregation period (default: "7day").

        Returns:
            PIL.Image.Image: Composite album art collage.
        """
        return self.generate(
            entity=ENTITY_ALBUM,
            username=username,
            cols=cols,
            rows=rows,
            period=period,
        )

    def generate_top_artists_collage(
        self, username: str, cols: int, rows: int, period: str = DEFAULT_PERIOD
    ) -> Image.Image:
        """
        Generate a collage from the user's top artists.

        Artist imagery is retrieved from Last.fm artist pages because the
        Last.fm API no longer provides artist images directly.

        Args:
            username: Valid Last.fm username.
            cols: Number of columns (1–5).
            rows: Number of rows (1–5).
            period: Aggregation period (default: "7day").

        Returns:
            PIL.Image.Image: Composite artist hero image collage.
        """
        return self.generate(
            entity=ENTITY_ARTIST,
            username=username,
            cols=cols,
            rows=rows,
            period=period,
        )

    def generate_top_tracks_collage(
        self, username: str, cols: int, rows: int, period: str = DEFAULT_PERIOD
    ) -> Image.Image:
        """
        Generate a collage from the user's top tracks.

        Artwork is resolved from each track's associated album cover.
        Tracks without resolvable artwork fall back to solid black tiles.

        Args:
            username: Valid Last.fm username.
            cols: Number of columns (1–5).
            rows: Number of rows (1–5).
            period: Aggregation period (default: "7day").

        Returns:
            PIL.Image.Image: Composite track album-art collage.
        """
        return self.generate(
            entity=ENTITY_TRACK,
            username=username,
            cols=cols,
            rows=rows,
            period=period,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

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
        self, entity: str, cols: int, rows: int, period: str
    ) -> None:
        if entity not in ENTITIES:
            raise ValueError(f"Invalid entity: {entity}. Valid: {ENTITIES}")
        if not (self.MIN_COLS <= cols <= self.MAX_COLS):
            raise ValueError(
                f"Invalid number of columns: {cols}. "
                f"Must be between {self.MIN_COLS} and {self.MAX_COLS}."
            )
        if not (self.MIN_ROWS <= rows <= self.MAX_ROWS):
            raise ValueError(
                f"Invalid number of rows: {rows}. "
                f"Must be between {self.MIN_ROWS} and {self.MAX_ROWS}."
            )
        if period not in PERIODS:
            raise ValueError(f"Invalid period: {period}. Valid: {PERIODS}")
