import os
from typing import Any, Dict, Optional, Union, cast
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
    OVERLAY_BANNER,
    OVERLAY_STYLES,
    THEME_DARK,
)
from lastfmcollagegenerator.lastfm.client import LastfmClient
from lastfmcollagegenerator.theme import Theme, resolve_theme


class CollageGenerator:
    """Generates a NxN collage with the covers of a Last.fm

    user tops of a given period.
    """

    MAX_COLS = 20
    MAX_ROWS = 20
    MAX_TILES = 400
    MIN_TILE_SIZE = 50
    MAX_TILE_SIZE = 600

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
        tile_size: Optional[int] = None,
        theme: Union[str, Theme, Dict[str, Any]] = THEME_DARK,
        overlay_style: str = OVERLAY_BANNER,
        show_text: bool = True,
        font_path: Optional[str] = None,
    ) -> Image.Image:
        """Generate a composite collage image from a Last.fm user's top items.

        Args:
            entity: Entity type. One of: "album", "artist", "track".
            username: Valid Last.fm username.
            cols: Number of columns (1–20).
            rows: Number of rows (1–20).
            period: Aggregation period. One of: "7day", "1month", "3month",
                    "6month", "12month", "overall".
            tile_size: Optional explicit tile width and height in pixels (50–600).
                       If None, automatically computed based on grid density.
            theme: Theme preset string ("dark", "light", "glassmorphic",
                   "sunset", "neon"), Theme instance, or dictionary configuration.
                   Default is "dark".
            overlay_style: Overlay rendering mode ("banner", "full_tint",
                           "gradient", "pill", "clean"). Default is "banner".
            show_text: If False, disables all text and overlay backgrounds.
                       Default True.
            font_path: Optional path to a custom TrueType (.ttf) or OpenType
                       (.otf) font file.

        Returns:
            PIL.Image.Image: RGB composite canvas with dimensions
            (cols * tile_size, rows * tile_size) pixels.

        Raises:
            ValueError: If any parameter is invalid or out of bounds.
            TypeError: If types of parameters are invalid.
            FileNotFoundError: If font_path does not exist on disk.
        """
        resolved_theme = self._validate_parameters(
            entity=entity,
            username=username,
            cols=cols,
            rows=rows,
            period=period,
            tile_size=tile_size,
            theme=theme,
            overlay_style=overlay_style,
            show_text=show_text,
            font_path=font_path,
        )
        resolved_tile_size = self._resolve_tile_size(cols, rows, tile_size)
        collage_builder = self._get_collage_builder(
            entity=entity,
            cols=cols,
            rows=rows,
            period=period,
            tile_size=resolved_tile_size,
            theme=resolved_theme,
            overlay_style=overlay_style,
            show_text=show_text,
            font_path=font_path,
        )
        return collage_builder.create(username)

    def generate_top_albums_collage(
        self,
        username: str,
        cols: int = 5,
        rows: int = 5,
        period: str = "overall",
        tile_size: Optional[int] = None,
        theme: Union[str, Theme, Dict[str, Any]] = THEME_DARK,
        overlay_style: str = OVERLAY_BANNER,
        show_text: bool = True,
        font_path: Optional[str] = None,
    ) -> Image.Image:
        """Convenience method to generate an album collage."""
        return self.generate(
            entity=ENTITY_ALBUM,
            username=username,
            cols=cols,
            rows=rows,
            period=period,
            tile_size=tile_size,
            theme=theme,
            overlay_style=overlay_style,
            show_text=show_text,
            font_path=font_path,
        )

    def generate_top_artists_collage(
        self,
        username: str,
        cols: int = 5,
        rows: int = 5,
        period: str = "overall",
        tile_size: Optional[int] = None,
        theme: Union[str, Theme, Dict[str, Any]] = THEME_DARK,
        overlay_style: str = OVERLAY_BANNER,
        show_text: bool = True,
        font_path: Optional[str] = None,
    ) -> Image.Image:
        """Convenience method to generate an artist collage."""
        return self.generate(
            entity=ENTITY_ARTIST,
            username=username,
            cols=cols,
            rows=rows,
            period=period,
            tile_size=tile_size,
            theme=theme,
            overlay_style=overlay_style,
            show_text=show_text,
            font_path=font_path,
        )

    def generate_top_tracks_collage(
        self,
        username: str,
        cols: int = 5,
        rows: int = 5,
        period: str = "overall",
        tile_size: Optional[int] = None,
        theme: Union[str, Theme, Dict[str, Any]] = THEME_DARK,
        overlay_style: str = OVERLAY_BANNER,
        show_text: bool = True,
        font_path: Optional[str] = None,
    ) -> Image.Image:
        """Convenience method to generate a track collage."""
        return self.generate(
            entity=ENTITY_TRACK,
            username=username,
            cols=cols,
            rows=rows,
            period=period,
            tile_size=tile_size,
            theme=theme,
            overlay_style=overlay_style,
            show_text=show_text,
            font_path=font_path,
        )

    def _resolve_tile_size(
        self, cols: int, rows: int, tile_size: Optional[int] = None
    ) -> int:
        if tile_size is not None:
            return tile_size
        max_dim = max(cols, rows)
        if max_dim <= 5:
            return 300
        elif max_dim <= 10:
            return 150
        else:
            return 100

    def _get_collage_builder(
        self,
        entity: str,
        cols: int,
        rows: int,
        period: str,
        tile_size: int = 300,
        theme: Optional[Theme] = None,
        overlay_style: str = OVERLAY_BANNER,
        show_text: bool = True,
        font_path: Optional[str] = None,
    ) -> BaseCollageBuilder:
        collage_builder_config = CollageBuilderConfig(
            cols=cols,
            rows=rows,
            period=period,
            tile_size=tile_size,
            theme=theme,
            overlay_style=overlay_style,
            show_text=show_text,
            font_path=font_path,
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
        tile_size: Optional[int] = None,
        theme: Union[str, Theme, Dict[str, Any]] = THEME_DARK,
        overlay_style: str = OVERLAY_BANNER,
        show_text: bool = True,
        font_path: Optional[str] = None,
    ) -> Theme:
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

        if (cols * rows) > self.MAX_TILES:
            raise ValueError(
                f"Total tile count ({cols * rows}) exceeds maximum "
                f"capacity of {self.MAX_TILES}."
            )

        if tile_size is not None:
            if type(tile_size) is not int:
                raise TypeError("tile_size must be an integer.")
            if tile_size < self.MIN_TILE_SIZE or tile_size > self.MAX_TILE_SIZE:
                raise ValueError(
                    f"Invalid tile_size: {tile_size}. Allowed bounds are "
                    f"{self.MIN_TILE_SIZE} to {self.MAX_TILE_SIZE} pixels."
                )

        if entity not in ENTITIES:
            raise ValueError(f"Invalid entity: {entity}. Options are: {ENTITIES}")

        if period not in PERIODS:
            raise ValueError(f"Invalid period: {period}. Options are: {PERIODS}")

        if not isinstance(overlay_style, str) or overlay_style not in OVERLAY_STYLES:
            raise ValueError(
                f"Invalid overlay_style: '{overlay_style}'. "
                f"Options are: {OVERLAY_STYLES}"
            )

        if type(show_text) is not bool:
            raise TypeError("show_text must be a boolean.")

        if font_path is not None:
            if not isinstance(font_path, str):
                raise TypeError("font_path must be a string or None.")
            if not os.path.isfile(font_path):
                raise FileNotFoundError(f"Custom font file not found: {font_path}")

        resolved_theme = resolve_theme(theme)
        return resolved_theme
