import os
from typing import Any, Dict, Optional, Union, cast
from PIL import Image

from lastfmcollagegenerator.cache import ArtworkCache
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
from lastfmcollagegenerator.fallback_art import (
    FALLBACK_STYLE_GRADIENT,
    FALLBACK_STYLES,
)
from lastfmcollagegenerator.lastfm.client import LastfmClient
from lastfmcollagegenerator.network import (
    ResilientHttpFetcher,
    DEFAULT_RATE_LIMIT,
)
from lastfmcollagegenerator.presets import (
    SocialPreset,
    resolve_preset,
)
from lastfmcollagegenerator.theme import Theme, resolve_theme, parse_color


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
        show_playcount: bool = True,
        font_bold: bool = False,
        font_path: Optional[str] = None,
        preset: Optional[str] = None,
        cache_dir: Optional[str] = None,
        cache_ttl_override: Optional[int] = None,
        rate_limit: Optional[float] = None,
        fallback_style: str = FALLBACK_STYLE_GRADIENT,
        corner_radius: int = 0,
        border_width: int = 0,
        border_color: Optional[Union[str, tuple]] = None,
        spacing: int = 0,
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
            show_playcount: If False, hides the scrobble count on overlays.
                       Default True.
            font_bold: If True, uses bold typography for overlay text.
                       Default False.
            font_path: Optional path to a custom TrueType (.ttf) or OpenType
                       (.otf) font file.
            preset: Optional social media dimension preset. One of:
                    "instagram-story", "instagram-post", "twitter-header",
                    "desktop-wallpaper", "desktop-wallpaper-4k". When set,
                    it overrides cols, rows and tile_size.
            cache_dir: Optional directory for the persistent artwork cache.
                       Defaults to ~/.cache/lastfm-collage/.
            cache_ttl_override: Optional override for cache entry lifetime
                       in days (applies to all artwork kinds).
            rate_limit: Optional maximum HTTP request rate in requests per
                       second. Defaults to 5.0.
            fallback_style: Fallback tile style when artwork cannot be
                       downloaded: "gradient" (default) or "black".
            corner_radius: Rounded corner radius in pixels (default 0).
            border_width: Tile border stroke width in pixels (default 0).
            border_color: Tile border color as hex string or RGB(A) tuple.
            spacing: Inter-tile spacing margin in pixels (default 0).

        Returns:
            PIL.Image.Image: RGB composite canvas. Without a preset, the
            dimensions are (cols * tile_size, rows * tile_size) pixels.

        Raises:
            ValueError: If any parameter is invalid or out of bounds.
            TypeError: If types of parameters are invalid.
            FileNotFoundError: If font_path does not exist on disk.
        """
        resolved_preset = self._resolve_preset(preset)
        if resolved_preset is not None:
            cols = resolved_preset.cols
            rows = resolved_preset.rows

        if resolved_preset is not None:
            resolved_tile_size = resolved_preset.tile_size
        else:
            resolved_tile_size = self._resolve_tile_size(cols, rows, tile_size)

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
            show_playcount=show_playcount,
            font_bold=font_bold,
            font_path=font_path,
            preset=preset,
            cache_dir=cache_dir,
            cache_ttl_override=cache_ttl_override,
            rate_limit=rate_limit,
            fallback_style=fallback_style,
            corner_radius=corner_radius,
            border_width=border_width,
            border_color=border_color,
            spacing=spacing,
            resolved_tile_size=resolved_tile_size,
        )
        collage_builder = self._get_collage_builder(
            entity=entity,
            cols=cols,
            rows=rows,
            period=period,
            tile_size=resolved_tile_size,
            theme=resolved_theme,
            overlay_style=overlay_style,
            show_text=show_text,
            show_playcount=show_playcount,
            font_bold=font_bold,
            font_path=font_path,
            preset=resolved_preset,
            cache_dir=cache_dir,
            cache_ttl_override=cache_ttl_override,
            rate_limit=rate_limit,
            fallback_style=fallback_style,
            corner_radius=corner_radius,
            border_width=border_width,
            border_color=border_color,
            spacing=spacing,
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
        show_playcount: bool = True,
        font_bold: bool = False,
        font_path: Optional[str] = None,
        preset: Optional[str] = None,
        cache_dir: Optional[str] = None,
        cache_ttl_override: Optional[int] = None,
        rate_limit: Optional[float] = None,
        fallback_style: str = FALLBACK_STYLE_GRADIENT,
        corner_radius: int = 0,
        border_width: int = 0,
        border_color: Optional[Union[str, tuple]] = None,
        spacing: int = 0,
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
            show_playcount=show_playcount,
            font_bold=font_bold,
            font_path=font_path,
            preset=preset,
            cache_dir=cache_dir,
            cache_ttl_override=cache_ttl_override,
            rate_limit=rate_limit,
            fallback_style=fallback_style,
            corner_radius=corner_radius,
            border_width=border_width,
            border_color=border_color,
            spacing=spacing,
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
        show_playcount: bool = True,
        font_bold: bool = False,
        font_path: Optional[str] = None,
        preset: Optional[str] = None,
        cache_dir: Optional[str] = None,
        cache_ttl_override: Optional[int] = None,
        rate_limit: Optional[float] = None,
        fallback_style: str = FALLBACK_STYLE_GRADIENT,
        corner_radius: int = 0,
        border_width: int = 0,
        border_color: Optional[Union[str, tuple]] = None,
        spacing: int = 0,
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
            show_playcount=show_playcount,
            font_bold=font_bold,
            font_path=font_path,
            preset=preset,
            cache_dir=cache_dir,
            cache_ttl_override=cache_ttl_override,
            rate_limit=rate_limit,
            fallback_style=fallback_style,
            corner_radius=corner_radius,
            border_width=border_width,
            border_color=border_color,
            spacing=spacing,
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
        show_playcount: bool = True,
        font_bold: bool = False,
        font_path: Optional[str] = None,
        preset: Optional[str] = None,
        cache_dir: Optional[str] = None,
        cache_ttl_override: Optional[int] = None,
        rate_limit: Optional[float] = None,
        fallback_style: str = FALLBACK_STYLE_GRADIENT,
        corner_radius: int = 0,
        border_width: int = 0,
        border_color: Optional[Union[str, tuple]] = None,
        spacing: int = 0,
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
            show_playcount=show_playcount,
            font_bold=font_bold,
            font_path=font_path,
            preset=preset,
            cache_dir=cache_dir,
            cache_ttl_override=cache_ttl_override,
            rate_limit=rate_limit,
            fallback_style=fallback_style,
            corner_radius=corner_radius,
            border_width=border_width,
            border_color=border_color,
            spacing=spacing,
        )

    async def generate_async(
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
        show_playcount: bool = True,
        font_bold: bool = False,
        font_path: Optional[str] = None,
        preset: Optional[str] = None,
        cache_dir: Optional[str] = None,
        cache_ttl_override: Optional[int] = None,
        rate_limit: Optional[float] = None,
        fallback_style: str = FALLBACK_STYLE_GRADIENT,
        corner_radius: int = 0,
        border_width: int = 0,
        border_color: Optional[Union[str, tuple]] = None,
        spacing: int = 0,
        max_concurrency: int = 20,
    ) -> Image.Image:
        """Asynchronously generate a composite collage image."""
        resolved_preset = self._resolve_preset(preset)
        if resolved_preset is not None:
            cols = resolved_preset.cols
            rows = resolved_preset.rows

        if resolved_preset is not None:
            resolved_tile_size = resolved_preset.tile_size
        else:
            resolved_tile_size = self._resolve_tile_size(cols, rows, tile_size)

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
            show_playcount=show_playcount,
            font_bold=font_bold,
            font_path=font_path,
            preset=preset,
            cache_dir=cache_dir,
            cache_ttl_override=cache_ttl_override,
            rate_limit=rate_limit,
            fallback_style=fallback_style,
            corner_radius=corner_radius,
            border_width=border_width,
            border_color=border_color,
            spacing=spacing,
            resolved_tile_size=resolved_tile_size,
        )
        collage_builder = self._get_collage_builder(
            entity=entity,
            cols=cols,
            rows=rows,
            period=period,
            tile_size=resolved_tile_size,
            theme=resolved_theme,
            overlay_style=overlay_style,
            show_text=show_text,
            show_playcount=show_playcount,
            font_bold=font_bold,
            font_path=font_path,
            preset=resolved_preset,
            cache_dir=cache_dir,
            cache_ttl_override=cache_ttl_override,
            rate_limit=rate_limit,
            fallback_style=fallback_style,
            corner_radius=corner_radius,
            border_width=border_width,
            border_color=border_color,
            spacing=spacing,
        )
        return await collage_builder.create_async(
            username, max_concurrency=max_concurrency
        )

    async def generate_top_albums_collage_async(
        self,
        username: str,
        cols: int = 5,
        rows: int = 5,
        period: str = "overall",
        tile_size: Optional[int] = None,
        theme: Union[str, Theme, Dict[str, Any]] = THEME_DARK,
        overlay_style: str = OVERLAY_BANNER,
        show_text: bool = True,
        show_playcount: bool = True,
        font_bold: bool = False,
        font_path: Optional[str] = None,
        preset: Optional[str] = None,
        cache_dir: Optional[str] = None,
        cache_ttl_override: Optional[int] = None,
        rate_limit: Optional[float] = None,
        fallback_style: str = FALLBACK_STYLE_GRADIENT,
        corner_radius: int = 0,
        border_width: int = 0,
        border_color: Optional[Union[str, tuple]] = None,
        spacing: int = 0,
        max_concurrency: int = 20,
    ) -> Image.Image:
        """Convenience method to asynchronously generate an album collage."""
        return await self.generate_async(
            entity=ENTITY_ALBUM,
            username=username,
            cols=cols,
            rows=rows,
            period=period,
            tile_size=tile_size,
            theme=theme,
            overlay_style=overlay_style,
            show_text=show_text,
            show_playcount=show_playcount,
            font_bold=font_bold,
            font_path=font_path,
            preset=preset,
            cache_dir=cache_dir,
            cache_ttl_override=cache_ttl_override,
            rate_limit=rate_limit,
            fallback_style=fallback_style,
            corner_radius=corner_radius,
            border_width=border_width,
            border_color=border_color,
            spacing=spacing,
            max_concurrency=max_concurrency,
        )

    async def generate_top_artists_collage_async(
        self,
        username: str,
        cols: int = 5,
        rows: int = 5,
        period: str = "overall",
        tile_size: Optional[int] = None,
        theme: Union[str, Theme, Dict[str, Any]] = THEME_DARK,
        overlay_style: str = OVERLAY_BANNER,
        show_text: bool = True,
        show_playcount: bool = True,
        font_bold: bool = False,
        font_path: Optional[str] = None,
        preset: Optional[str] = None,
        cache_dir: Optional[str] = None,
        cache_ttl_override: Optional[int] = None,
        rate_limit: Optional[float] = None,
        fallback_style: str = FALLBACK_STYLE_GRADIENT,
        corner_radius: int = 0,
        border_width: int = 0,
        border_color: Optional[Union[str, tuple]] = None,
        spacing: int = 0,
        max_concurrency: int = 20,
    ) -> Image.Image:
        """Convenience method to asynchronously generate an artist collage."""
        return await self.generate_async(
            entity=ENTITY_ARTIST,
            username=username,
            cols=cols,
            rows=rows,
            period=period,
            tile_size=tile_size,
            theme=theme,
            overlay_style=overlay_style,
            show_text=show_text,
            show_playcount=show_playcount,
            font_bold=font_bold,
            font_path=font_path,
            preset=preset,
            cache_dir=cache_dir,
            cache_ttl_override=cache_ttl_override,
            rate_limit=rate_limit,
            fallback_style=fallback_style,
            corner_radius=corner_radius,
            border_width=border_width,
            border_color=border_color,
            spacing=spacing,
            max_concurrency=max_concurrency,
        )

    async def generate_top_tracks_collage_async(
        self,
        username: str,
        cols: int = 5,
        rows: int = 5,
        period: str = "overall",
        tile_size: Optional[int] = None,
        theme: Union[str, Theme, Dict[str, Any]] = THEME_DARK,
        overlay_style: str = OVERLAY_BANNER,
        show_text: bool = True,
        show_playcount: bool = True,
        font_bold: bool = False,
        font_path: Optional[str] = None,
        preset: Optional[str] = None,
        cache_dir: Optional[str] = None,
        cache_ttl_override: Optional[int] = None,
        rate_limit: Optional[float] = None,
        fallback_style: str = FALLBACK_STYLE_GRADIENT,
        corner_radius: int = 0,
        border_width: int = 0,
        border_color: Optional[Union[str, tuple]] = None,
        spacing: int = 0,
        max_concurrency: int = 20,
    ) -> Image.Image:
        """Convenience method to asynchronously generate a track collage."""
        return await self.generate_async(
            entity=ENTITY_TRACK,
            username=username,
            cols=cols,
            rows=rows,
            period=period,
            tile_size=tile_size,
            theme=theme,
            overlay_style=overlay_style,
            show_text=show_text,
            show_playcount=show_playcount,
            font_bold=font_bold,
            font_path=font_path,
            preset=preset,
            cache_dir=cache_dir,
            cache_ttl_override=cache_ttl_override,
            rate_limit=rate_limit,
            fallback_style=fallback_style,
            corner_radius=corner_radius,
            border_width=border_width,
            border_color=border_color,
            spacing=spacing,
            max_concurrency=max_concurrency,
        )

    @staticmethod
    def _resolve_preset(preset: Optional[str]) -> Optional[SocialPreset]:
        if preset is None:
            return None
        return resolve_preset(preset)

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
        show_playcount: bool = True,
        font_bold: bool = False,
        font_path: Optional[str] = None,
        preset: Optional[SocialPreset] = None,
        cache_dir: Optional[str] = None,
        cache_ttl_override: Optional[int] = None,
        rate_limit: Optional[float] = None,
        fallback_style: str = FALLBACK_STYLE_GRADIENT,
        corner_radius: int = 0,
        border_width: int = 0,
        border_color: Optional[Union[str, tuple]] = None,
        spacing: int = 0,
    ) -> BaseCollageBuilder:
        collage_builder_config = CollageBuilderConfig(
            cols=cols,
            rows=rows,
            period=period,
            tile_size=tile_size,
            theme=theme,
            overlay_style=overlay_style,
            show_text=show_text,
            show_playcount=show_playcount,
            font_bold=font_bold,
            font_path=font_path,
            corner_radius=corner_radius,
            border_width=border_width,
            border_color=border_color,
            spacing=spacing,
            fallback_style=fallback_style,
            preset_width=preset.width if preset is not None else None,
            preset_height=preset.height if preset is not None else None,
        )
        lastfm_client = LastfmClient(
            api_key=self.lastfm_config.lastfm_api_key,
            api_secret=self.lastfm_config.lastfm_api_secret,
        )
        cache = ArtworkCache(
            cache_dir=cache_dir,
            ttl_override_days=cache_ttl_override,
        )
        fetcher = ResilientHttpFetcher(
            rate_limit=rate_limit if rate_limit is not None else DEFAULT_RATE_LIMIT
        )
        return cast(
            BaseCollageBuilder,
            CollageBuilderFactory(
                entity=entity,
                config=collage_builder_config,
                lastfm_client=lastfm_client,
                cache=cache,
                fetcher=fetcher,
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
        show_playcount: bool = True,
        font_bold: bool = False,
        font_path: Optional[str] = None,
        preset: Optional[str] = None,
        cache_dir: Optional[str] = None,
        cache_ttl_override: Optional[int] = None,
        rate_limit: Optional[float] = None,
        fallback_style: str = FALLBACK_STYLE_GRADIENT,
        corner_radius: int = 0,
        border_width: int = 0,
        border_color: Optional[Union[str, tuple]] = None,
        spacing: int = 0,
        resolved_tile_size: Optional[int] = None,
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

        if type(show_playcount) is not bool:
            raise TypeError("show_playcount must be a boolean.")

        if type(font_bold) is not bool:
            raise TypeError("font_bold must be a boolean.")

        if font_path is not None:
            if not isinstance(font_path, str):
                raise TypeError("font_path must be a string or None.")
            if not os.path.isfile(font_path):
                raise FileNotFoundError(f"Custom font file not found: {font_path}")

        if preset is not None:
            if not isinstance(preset, str):
                raise TypeError("preset must be a string or None.")
            resolve_preset(preset)

        if cache_dir is not None and not isinstance(cache_dir, str):
            raise TypeError("cache_dir must be a string or None.")

        if cache_ttl_override is not None:
            if type(cache_ttl_override) is not int:
                raise TypeError("cache_ttl_override must be an integer or None.")
            if cache_ttl_override <= 0:
                raise ValueError(
                    "cache_ttl_override must be a positive number of days."
                )

        if rate_limit is not None:
            if type(rate_limit) not in (int, float):
                raise TypeError("rate_limit must be a number or None.")
            if rate_limit <= 0:
                raise ValueError(
                    "rate_limit must be a positive number of requests per second."
                )

        if not isinstance(fallback_style, str) or fallback_style not in FALLBACK_STYLES:
            raise ValueError(
                f"Invalid fallback_style: '{fallback_style}'. "
                f"Options are: {FALLBACK_STYLES}"
            )

        effective_tile = (
            resolved_tile_size
            if resolved_tile_size is not None
            else self._resolve_tile_size(cols, rows, tile_size)
        )

        for name, value in (
            ("corner_radius", corner_radius),
            ("border_width", border_width),
            ("spacing", spacing),
        ):
            if type(value) is not int:
                raise TypeError(f"{name} must be an integer.")
            if value < 0:
                raise ValueError(f"{name} must be a non-negative integer.")
            if value > effective_tile:
                raise ValueError(
                    f"Invalid {name}: {value} exceeds the tile size "
                    f"of {effective_tile} pixels."
                )

        if border_color is not None:
            parse_color(border_color)

        resolved_theme = resolve_theme(theme)
        return resolved_theme
