import asyncio
import concurrent.futures
import functools
import os
import urllib.parse
from dataclasses import dataclass
from io import BytesIO
from typing import Any, List, Optional, Tuple, Union, cast

import bs4
import httpx
import requests
from pylast import User, TopItem, Album, Artist, Track
from PIL import Image, ImageDraw, ImageEnhance, ImageFile, ImageFilter


import lastfmcollagegenerator
from lastfmcollagegenerator.cache import (
    ArtworkCache,
    CACHE_KIND_ALBUM,
    CACHE_KIND_ARTIST,
)
from lastfmcollagegenerator.constants import (
    ENTITY_ARTIST,
    ENTITY_ALBUM,
    ENTITY_TRACK,
    OVERLAY_BANNER,
    OVERLAY_FULL_TINT,
    OVERLAY_GRADIENT,
    OVERLAY_PILL,
    OVERLAY_CLEAN,
    THEME_DARK,
)
from lastfmcollagegenerator.exceptions import (
    ArtistNotFound,
    ArtistImageNotFound,
)
from lastfmcollagegenerator.fallback_art import (
    FALLBACK_STYLE_GRADIENT,
    FALLBACK_STYLE_BLACK,
    generate_blank_tile,
    generate_fallback_tile,
)
from lastfmcollagegenerator.lastfm.client import LastfmClient
from lastfmcollagegenerator.network import ResilientHttpFetcher
from lastfmcollagegenerator.theme import (
    Theme,
    THEME_PRESETS,
    resolve_theme,
    parse_color,
)
from lastfmcollagegenerator.typography import get_auto_scaled_font, wrap_text_to_width

ImageFile.LOAD_TRUNCATED_IMAGES = True

DEFAULT_HEADERS = {
    "User-Agent": (
        "lastfm-collage-generator/1.1.0 "
        "(+https://github.com/paurieraf/lastfm-collage-generator)"
    )
}
DEFAULT_TIMEOUT = (3.05, 10.0)


@dataclass
class LastfmConfig:
    lastfm_api_key: str
    lastfm_api_secret: str


@dataclass
class CollageBuilderConfig:
    cols: int
    rows: int
    period: str
    show_playcount: bool = True
    font_bold: bool = False
    tile_size: int = 300
    theme: Optional[Theme] = None
    overlay_style: str = OVERLAY_BANNER
    show_text: bool = True
    font_path: Optional[str] = None
    corner_radius: int = 0
    border_width: int = 0
    border_color: Optional[Union[str, Tuple[int, ...]]] = None
    spacing: int = 0
    fallback_style: str = FALLBACK_STYLE_GRADIENT
    preset_width: Optional[int] = None
    preset_height: Optional[int] = None


@dataclass
class CollageTile:
    data: bytes
    playcount: int
    title: str


class BaseCollageBuilder:
    ENTITY: Optional[str] = None
    FONT_REGULAR_PATH = "fonts/DejaVuSansMono.ttf"
    FONT_BOLD_PATH = "fonts/DejaVuSansMono-Bold.ttf"
    FONT_SIZE = 15
    FONT_BOLD = False
    TILE_WIDTH = 300
    TILE_HEIGHT = 300

    def __init__(
        self,
        config: CollageBuilderConfig,
        lastfm_client: LastfmClient,
        cache: Optional[ArtworkCache] = None,
        fetcher: Optional[ResilientHttpFetcher] = None,
    ):
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        self.config = config
        self.lastfm_client = lastfm_client
        self.cache = cache
        self.fetcher = fetcher if fetcher is not None else ResilientHttpFetcher()
        self._path = os.path.dirname(lastfmcollagegenerator.collage.__file__)
        self.tile_width = getattr(self.config, "tile_size", self.TILE_WIDTH)
        self.tile_height = getattr(self.config, "tile_size", self.TILE_HEIGHT)
        raw_theme = getattr(self.config, "theme", None)
        if raw_theme is not None:
            self.theme = resolve_theme(raw_theme)
        else:
            self.theme = THEME_PRESETS[THEME_DARK]

    DEFAULT_CONCURRENCY = 20

    def create(self, username: str) -> Image.Image:
        user = self.lastfm_client.get_user(username)
        tiles = self._get_tiles_from_top_items(
            user=user,
            limit=self.config.cols * self.config.rows,
            period=self.config.period,
        )
        return self._create_image(tiles, self.config.cols, self.config.rows)

    async def create_async(
        self, username: str, max_concurrency: int = DEFAULT_CONCURRENCY
    ) -> Image.Image:
        user = await self.lastfm_client.get_user_async(username)
        tiles = await self._get_tiles_from_top_items_async(
            user=user,
            limit=self.config.cols * self.config.rows,
            period=self.config.period,
            max_concurrency=max_concurrency,
        )
        return self._create_image(tiles, self.config.cols, self.config.rows)

    def _create_image(
        self, tiles: List[CollageTile], cols: int, rows: int
    ) -> Image.Image:
        """Create composite collage canvas."""
        width = self.tile_width
        height = self.tile_height
        corner_radius = int(getattr(self.config, "corner_radius", 0) or 0)
        border_width = int(getattr(self.config, "border_width", 0) or 0)
        border_color = getattr(self.config, "border_color", None)
        spacing = int(getattr(self.config, "spacing", 0) or 0)
        preset_width = getattr(self.config, "preset_width", None)
        preset_height = getattr(self.config, "preset_height", None)

        grid_width = cols * width + (cols + 1) * spacing
        grid_height = rows * height + (rows + 1) * spacing
        canvas_width = preset_width if preset_width is not None else grid_width
        canvas_height = preset_height if preset_height is not None else grid_height

        if (
            corner_radius == 0
            and border_width == 0
            and spacing == 0
            and canvas_width == cols * width
            and canvas_height == rows * height
        ):
            return self._create_image_legacy(tiles, cols, rows)

        return self._create_image_decorated(
            tiles=tiles,
            cols=cols,
            rows=rows,
            grid_width=grid_width,
            grid_height=grid_height,
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            corner_radius=corner_radius,
            border_width=border_width,
            border_color=border_color,
            spacing=spacing,
        )

    def _create_image_legacy(
        self, tiles: List[CollageTile], cols: int, rows: int
    ) -> Image.Image:
        """Byte-identical rendering path used when no geometry options are set."""
        width = self.tile_width
        height = self.tile_height
        collage_width = cols * width
        collage_height = rows * height

        # create blank image of the full size
        new_image = Image.new("RGB", (collage_width, collage_height))
        cursor = (0, 0)
        resample_filter = Image.Resampling.LANCZOS
        show_text = getattr(self.config, "show_text", True)
        overlay_style = getattr(self.config, "overlay_style", OVERLAY_BANNER)

        for tile in tiles:
            with Image.open(BytesIO(tile.data)) as tile_img:
                if tile_img.size != (width, height):
                    resized = tile_img.resize((width, height), resample_filter)
                    new_image.paste(resized, cursor)
                    resized.close()
                else:
                    new_image.paste(tile_img, cursor)

            if show_text and overlay_style != OVERLAY_CLEAN:
                title = f"{tile.title}"
                if self.config.show_playcount:
                    title += f". ({tile.playcount})"
                self._render_overlay(image=new_image, title=title, cursor=cursor)

            # move cursor to next tile
            y = cursor[1]
            x = cursor[0] + width
            if cursor[0] >= (collage_width - width):
                y = cursor[1] + height
                x = 0
            cursor = (x, y)
        return new_image

    def _create_image_decorated(
        self,
        tiles: List[CollageTile],
        cols: int,
        rows: int,
        grid_width: int,
        grid_height: int,
        canvas_width: int,
        canvas_height: int,
        corner_radius: int,
        border_width: int,
        border_color: Optional[Union[str, Tuple[int, ...]]],
        spacing: int,
    ) -> Image.Image:
        """Rendering path with rounded corners, borders, spacing and backdrop."""
        width = self.tile_width
        height = self.tile_height
        bg = tuple(int(c) for c in self.theme.overlay_bg[:3])
        new_image = Image.new("RGB", (canvas_width, canvas_height), bg)

        letterboxed = canvas_width > grid_width or canvas_height > grid_height
        if letterboxed and tiles:
            self._render_acrylic_backdrop(
                new_image, canvas_width, canvas_height, tiles[0]
            )

        offset_x = (canvas_width - grid_width) // 2
        offset_y = (canvas_height - grid_height) // 2
        resample_filter = Image.Resampling.LANCZOS
        show_text = getattr(self.config, "show_text", True)
        overlay_style = getattr(self.config, "overlay_style", OVERLAY_BANNER)

        if border_width > 0:
            raw_border = border_color if border_color is not None else (0, 0, 0)
            border_rgb = parse_color(raw_border)[:3]
        else:
            border_rgb = None

        for i, tile in enumerate(tiles):
            col = i % cols
            row = i // cols
            x = offset_x + spacing + col * (width + spacing)
            y = offset_y + spacing + row * (height + spacing)
            cursor = (x, y)

            with Image.open(BytesIO(tile.data)) as tile_img:
                if tile_img.size != (width, height):
                    resized = tile_img.resize((width, height), resample_filter)
                    processed: Image.Image = resized
                else:
                    processed = tile_img

                if corner_radius > 0:
                    rounded = self._apply_rounded_mask(
                        processed, width, height, corner_radius
                    )
                    new_image.paste(rounded, cursor, rounded)
                    rounded.close()
                    if processed is not tile_img:
                        processed.close()
                else:
                    new_image.paste(processed, cursor)
                    if processed is not tile_img:
                        processed.close()

            if border_rgb is not None:
                draw = ImageDraw.Draw(new_image, "RGBA")
                draw.rounded_rectangle(
                    ((x, y), (x + width - 1, y + height - 1)),
                    radius=corner_radius,
                    outline=border_rgb,
                    width=border_width,
                )

            if show_text and overlay_style != OVERLAY_CLEAN:
                title = f"{tile.title}"
                if self.config.show_playcount:
                    title += f". ({tile.playcount})"
                self._render_overlay(image=new_image, title=title, cursor=cursor)
        return new_image

    @staticmethod
    def _apply_rounded_mask(
        img: Image.Image, width: int, height: int, radius: int
    ) -> Image.Image:
        mask = Image.new("L", (width, height), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle(
            (0, 0, width - 1, height - 1), radius=radius, fill=255
        )
        rgba = img.convert("RGBA")
        rgba.putalpha(mask)
        return rgba

    def _render_acrylic_backdrop(
        self,
        canvas: Image.Image,
        canvas_width: int,
        canvas_height: int,
        first_tile: CollageTile,
    ) -> None:
        try:
            with Image.open(BytesIO(first_tile.data)) as img:
                backdrop = img.convert("RGB")
                backdrop = backdrop.resize(
                    (canvas_width, canvas_height), Image.Resampling.LANCZOS
                )
                radius = max(1, min(40, min(canvas_width, canvas_height) // 50))
                backdrop = backdrop.filter(ImageFilter.GaussianBlur(radius=radius))
                backdrop = ImageEnhance.Brightness(backdrop).enhance(0.4)
                canvas.paste(backdrop, (0, 0))
                backdrop.close()
        except (OSError, requests.RequestException, Exception):
            canvas.paste((20, 20, 20), (0, 0, canvas_width, canvas_height))

    def _get_font_file(self) -> str:
        if getattr(self.config, "font_path", None):
            return cast(str, self.config.font_path)
        if self.theme.font_path:
            return self.theme.font_path
        font_bold = getattr(self.config, "font_bold", self.FONT_BOLD)
        font_path = self.FONT_BOLD_PATH if font_bold else self.FONT_REGULAR_PATH
        return os.path.join(self._path, font_path)

    def _render_overlay(
        self, image: Image.Image, title: str, cursor: Tuple[int, int]
    ) -> None:
        style = getattr(self.config, "overlay_style", OVERLAY_BANNER)
        if style == OVERLAY_FULL_TINT:
            self._render_full_tint_overlay(image, title, cursor)
        elif style == OVERLAY_GRADIENT:
            self._render_gradient_overlay(image, title, cursor)
        elif style == OVERLAY_PILL:
            self._render_pill_overlay(image, title, cursor)
        elif style == OVERLAY_CLEAN:
            pass
        else:
            self._render_banner_overlay(image, title, cursor)

    def _render_banner_overlay(
        self, image: Image.Image, title: str, cursor: Tuple[int, int]
    ) -> None:
        scale = self.tile_width / 300.0
        banner_height = max(16, int(round(65 * scale)))
        base_font_size = max(8, int(round(self.FONT_SIZE * scale)))

        draw = ImageDraw.Draw(image, "RGBA")
        x = cursor[0]
        y = cursor[1]
        y_0 = y + (self.tile_height - banner_height)
        y_1 = y + self.tile_height

        draw.rectangle(((x, y_0), (x + self.tile_width, y_1)), self.theme.overlay_bg)

        if self.theme.accent_color:
            draw.line(
                [(x, y_0), (x + self.tile_width, y_0)],
                fill=self.theme.accent_color,
                width=max(1, int(round(1 * scale))),
            )

        font_file = self._get_font_file()
        wrap_width = max(40, int(round(275 * scale)))
        font, wrapped_title = get_auto_scaled_font(
            font_file,
            base_font_size,
            title,
            max_width=wrap_width,
            max_height=banner_height - max(4, int(round(8 * scale))),
        )

        text_x = x + max(2, int(round(8 * scale)))
        text_y = y_0 + max(2, int(round(5 * scale)))
        draw.text(
            (text_x, text_y), wrapped_title, fill=self.theme.text_color, font=font
        )

    def _render_full_tint_overlay(
        self, image: Image.Image, title: str, cursor: Tuple[int, int]
    ) -> None:
        scale = self.tile_width / 300.0
        draw = ImageDraw.Draw(image, "RGBA")
        x = cursor[0]
        y = cursor[1]

        draw.rectangle(
            ((x, y), (x + self.tile_width, y + self.tile_height)), self.theme.overlay_bg
        )

        if self.theme.accent_color:
            draw.rectangle(
                ((x, y), (x + self.tile_width - 1, y + self.tile_height - 1)),
                outline=self.theme.accent_color,
                width=max(1, int(round(1 * scale))),
            )

        font_file = self._get_font_file()
        wrap_width = max(40, int(round((self.tile_width - 24) * scale)))
        base_font_size = max(9, int(round(16 * scale)))
        font, wrapped_title = get_auto_scaled_font(
            font_file,
            base_font_size,
            title,
            max_width=wrap_width,
            max_height=self.tile_height - max(10, int(round(20 * scale))),
        )

        text_x = x + max(4, int(round(12 * scale)))
        text_y = y + max(4, int(round(12 * scale)))
        draw.text(
            (text_x, text_y), wrapped_title, fill=self.theme.text_color, font=font
        )

    def _render_gradient_overlay(
        self, image: Image.Image, title: str, cursor: Tuple[int, int]
    ) -> None:
        scale = self.tile_width / 300.0
        grad_img = Image.new("RGBA", (self.tile_width, self.tile_height), (0, 0, 0, 0))
        r, g, b, max_a = self.theme.overlay_bg

        grad_draw = ImageDraw.Draw(grad_img, "RGBA")
        for i in range(self.tile_height):
            ratio = (i / float(self.tile_height)) ** 1.8
            alpha = int(max_a * ratio)
            grad_draw.line([(0, i), (self.tile_width, i)], fill=(r, g, b, alpha))

        font_file = self._get_font_file()
        wrap_width = max(40, int(round(275 * scale)))
        base_font_size = max(8, int(round(self.FONT_SIZE * scale)))
        banner_height = max(24, int(round(90 * scale)))
        font, wrapped_title = get_auto_scaled_font(
            font_file,
            base_font_size,
            title,
            max_width=wrap_width,
            max_height=banner_height,
        )

        text_x = max(2, int(round(8 * scale)))
        text_y = self.tile_height - banner_height + max(2, int(round(10 * scale)))
        grad_draw.text(
            (text_x, text_y), wrapped_title, fill=self.theme.text_color, font=font
        )

        tile_box = (
            cursor[0],
            cursor[1],
            cursor[0] + self.tile_width,
            cursor[1] + self.tile_height,
        )
        base_crop = image.crop(tile_box).convert("RGBA")
        blended = Image.alpha_composite(base_crop, grad_img).convert("RGB")
        image.paste(blended, (cursor[0], cursor[1]))
        base_crop.close()
        blended.close()
        grad_img.close()

    def _render_pill_overlay(
        self, image: Image.Image, title: str, cursor: Tuple[int, int]
    ) -> None:
        scale = self.tile_width / 300.0
        draw = ImageDraw.Draw(image, "RGBA")
        x = cursor[0]
        y = cursor[1]

        font_file = self._get_font_file()
        wrap_width = max(40, int(round((self.tile_width - 32) * scale)))
        base_font_size = max(8, int(round(13 * scale)))
        max_h = max(20, int(round(60 * scale)))
        font, wrapped_title = get_auto_scaled_font(
            font_file,
            base_font_size,
            title,
            max_width=wrap_width,
            max_height=max_h,
        )

        lines = [line for line in wrapped_title.split("\n") if line]
        line_heights = [font.size for _ in lines]
        text_w = max(font.getlength(line) for line in lines) if lines else 0
        text_h = sum(line_heights) + max(0, (len(lines) - 1) * 2)

        pad_x = max(4, int(round(8 * scale)))
        pad_y = max(3, int(round(5 * scale)))
        pill_w = min(self.tile_width - 12, int(round(text_w + 2 * pad_x)))
        pill_h = int(round(text_h + 2 * pad_y))

        pill_x0 = x + (self.tile_width - pill_w) // 2
        pill_y0 = y + self.tile_height - pill_h - max(4, int(round(8 * scale)))
        pill_x1 = pill_x0 + pill_w
        pill_y1 = pill_y0 + pill_h

        radius = max(3, int(round(6 * scale)))
        draw.rounded_rectangle(
            ((pill_x0, pill_y0), (pill_x1, pill_y1)),
            radius=radius,
            fill=self.theme.overlay_bg,
            outline=self.theme.accent_color,
            width=max(1, int(round(1 * scale))),
        )

        draw.text(
            (pill_x0 + pad_x, pill_y0 + pad_y),
            wrapped_title,
            fill=self.theme.text_color,
            font=font,
        )

    def _insert_tile_title(
        self, image: Image.Image, title: str, cursor: Tuple[int, int]
    ) -> None:
        """Backward-compatible helper for banner overlay rendering."""
        self._render_banner_overlay(image=image, title=title, cursor=cursor)

    @staticmethod
    def _insert_newline_characters_to_text(
        font: Any, text: str, max_width: int = 275
    ) -> str:
        return wrap_text_to_width(font, text, max_width=max_width)

    def _generate_blank_tile(
        self, width: int = 300, height: int = 300, title: str = ""
    ) -> bytes:
        style = getattr(self.config, "fallback_style", FALLBACK_STYLE_GRADIENT)
        if style == FALLBACK_STYLE_BLACK:
            return generate_blank_tile(width, height)
        return generate_fallback_tile(title or "", width, height)

    def _get_tiles_from_top_items(
        self, user: User, limit: int, period: str
    ) -> List[CollageTile]:
        raise NotImplementedError

    async def _get_tiles_from_top_items_async(
        self,
        user: User,
        limit: int,
        period: str,
        max_concurrency: int = DEFAULT_CONCURRENCY,
    ) -> List[CollageTile]:
        raise NotImplementedError

    def _create_tiles_from_top_items(
        self,
        top_items: List[TopItem],
    ) -> List[CollageTile]:
        tiles: List[CollageTile] = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for top_item in top_items:
                future = executor.submit(
                    self._create_tile_from_top_item,
                    top_item,
                )
                futures.append(future)
            for future in concurrent.futures.as_completed(futures):
                tiles.append(future.result())
        tiles.sort(key=lambda x: (int(x.playcount), x.title), reverse=True)
        return tiles

    async def _create_tiles_from_top_items_async(
        self,
        top_items: List[TopItem],
        max_concurrency: int = DEFAULT_CONCURRENCY,
    ) -> List[CollageTile]:
        semaphore = asyncio.Semaphore(max_concurrency)
        timeout = httpx.Timeout(10.0, connect=3.05)
        async with httpx.AsyncClient(
            headers=DEFAULT_HEADERS, timeout=timeout, follow_redirects=True
        ) as client:
            tasks = [
                self._create_tile_from_top_item_async(client, semaphore, top_item)
                for top_item in top_items
            ]
            tiles = await asyncio.gather(*tasks)
        sorted_tiles = list(tiles)
        sorted_tiles.sort(key=lambda x: (int(x.playcount), x.title), reverse=True)
        return sorted_tiles

    def _create_tile_from_top_item(
        self,
        top_item: TopItem,
    ) -> CollageTile:
        raise NotImplementedError

    async def _create_tile_from_top_item_async(
        self,
        client: httpx.AsyncClient,
        semaphore: asyncio.Semaphore,
        top_item: TopItem,
    ) -> CollageTile:
        raise NotImplementedError

    def _download_bytes(self, url: str, kind: str) -> bytes:
        data = None
        if self.cache is not None:
            data = self.cache.get(url, kind)
        if data is None:
            resp = self.fetcher.get(
                url,
                headers=DEFAULT_HEADERS,
                timeout=DEFAULT_TIMEOUT,
            )
            resp.raise_for_status()
            data = resp.content
            if self.cache is not None:
                self.cache.set(url, data, kind)
        return data

    async def _download_bytes_async(
        self, client: httpx.AsyncClient, url: str, kind: str
    ) -> bytes:
        data = None
        if self.cache is not None:
            data = self.cache.get(url, kind)
        if data is None:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.content
            if self.cache is not None:
                self.cache.set(url, data, kind)
        return data


class ArtistCollageBuilder(BaseCollageBuilder):
    ENTITY = ENTITY_ARTIST

    def _get_tiles_from_top_items(
        self, user: User, limit: int, period: str
    ) -> List[CollageTile]:
        top_artists = self.lastfm_client.get_top_artists(user, limit, period)
        return self._create_tiles_from_top_items(top_artists)

    async def _get_tiles_from_top_items_async(
        self,
        user: User,
        limit: int,
        period: str,
        max_concurrency: int = BaseCollageBuilder.DEFAULT_CONCURRENCY,
    ) -> List[CollageTile]:
        top_artists = await self.lastfm_client.get_top_artists_async(
            user, limit, period
        )
        return await self._create_tiles_from_top_items_async(
            top_artists, max_concurrency=max_concurrency
        )

    def _create_tile_from_top_item(
        self,
        top_item: TopItem,
    ) -> CollageTile:
        title = top_item.item.name
        data = self._get_artist_image(top_item.item, title)
        return CollageTile(data=data, playcount=top_item.weight, title=title)

    async def _create_tile_from_top_item_async(
        self,
        client: httpx.AsyncClient,
        semaphore: asyncio.Semaphore,
        top_item: TopItem,
    ) -> CollageTile:
        title = top_item.item.name
        async with semaphore:
            data = await self._get_artist_image_async(client, top_item.item, title)
        return CollageTile(data=data, playcount=top_item.weight, title=title)

    @functools.lru_cache(maxsize=128)
    def _get_artist_image(self, artist: Artist, title: str) -> bytes:
        """Last.fm API does not provide artist images.

        So we fetch it from the website.
        """
        try:
            artist_slug = urllib.parse.quote_plus(artist.name)
            page_url = f"https://www.last.fm/music/{artist_slug}"
            page_resp = self.fetcher.get(
                page_url,
                headers=DEFAULT_HEADERS,
                timeout=DEFAULT_TIMEOUT,
            )
            if page_resp.status_code == 404:
                raise ArtistNotFound
            page_resp.raise_for_status()
            soup = bs4.BeautifulSoup(page_resp.content, "html5lib")

            url = None
            bg_elem = soup.find(class_="header-new-background-image")
            if bg_elem:
                url = str(bg_elem.get("content"))
            if not url:
                raise ArtistImageNotFound

            data = self._download_bytes(url, CACHE_KIND_ARTIST)
            with Image.open(BytesIO(data)) as img:
                img.thumbnail((self.TILE_WIDTH, self.TILE_HEIGHT))
                with BytesIO() as img_bytes:
                    img.save(img_bytes, format="png")
                    return img_bytes.getvalue()
        except (
            ArtistNotFound,
            ArtistImageNotFound,
            requests.RequestException,
            OSError,
            Exception,
        ):
            return self._generate_blank_tile(title=title)

    async def _get_artist_image_async(
        self, client: httpx.AsyncClient, artist: Artist, title: str
    ) -> bytes:
        try:
            artist_slug = urllib.parse.quote_plus(artist.name)
            page_url = f"https://www.last.fm/music/{artist_slug}"
            page_resp = await client.get(page_url)
            if page_resp.status_code == 404:
                raise ArtistNotFound
            page_resp.raise_for_status()
            soup = bs4.BeautifulSoup(page_resp.content, "html5lib")

            url = None
            bg_elem = soup.find(class_="header-new-background-image")
            if bg_elem:
                url = str(bg_elem.get("content"))
            if not url:
                raise ArtistImageNotFound

            data = await self._download_bytes_async(client, url, CACHE_KIND_ARTIST)
            with Image.open(BytesIO(data)) as img:
                img.thumbnail((self.TILE_WIDTH, self.TILE_HEIGHT))
                with BytesIO() as img_bytes:
                    img.save(img_bytes, format="png")
                    return img_bytes.getvalue()
        except (
            ArtistNotFound,
            ArtistImageNotFound,
            httpx.HTTPError,
            requests.RequestException,
            OSError,
            Exception,
        ):
            return self._generate_blank_tile(title=title)

    def __repr__(self):
        return (
            f"<ArtistCollage ["
            f"{self.config.cols}x{self.config.rows}, "
            f"{self.config.period}"
            f"]>"
        )


class AlbumCollageBuilder(BaseCollageBuilder):
    ENTITY = ENTITY_ALBUM

    def _get_tiles_from_top_items(
        self, user: User, limit: int, period: str
    ) -> List[CollageTile]:
        top_albums = self.lastfm_client.get_top_albums(user, limit, period)
        return self._create_tiles_from_top_items(top_albums)

    async def _get_tiles_from_top_items_async(
        self,
        user: User,
        limit: int,
        period: str,
        max_concurrency: int = BaseCollageBuilder.DEFAULT_CONCURRENCY,
    ) -> List[CollageTile]:
        top_albums = await self.lastfm_client.get_top_albums_async(user, limit, period)
        return await self._create_tiles_from_top_items_async(
            top_albums, max_concurrency=max_concurrency
        )

    def _create_tile_from_top_item(
        self,
        top_item: TopItem,
    ) -> CollageTile:
        title = f"{top_item.item.artist} - {top_item.item.title}"
        data = self._get_album_cover(top_item.item, title)
        return CollageTile(data=data, playcount=top_item.weight, title=title)

    async def _create_tile_from_top_item_async(
        self,
        client: httpx.AsyncClient,
        semaphore: asyncio.Semaphore,
        top_item: TopItem,
    ) -> CollageTile:
        title = f"{top_item.item.artist} - {top_item.item.title}"
        async with semaphore:
            data = await self._get_album_cover_async(client, top_item.item, title)
        return CollageTile(data=data, playcount=top_item.weight, title=title)

    def _get_album_cover(self, item: Union[Album, Track], title: str) -> bytes:
        try:
            url = item.get_cover_image()
        except (IndexError, AttributeError, Exception):
            url = None
        if not url:
            return self._generate_blank_tile(title=title)
        try:
            data = self._download_bytes(url, CACHE_KIND_ALBUM)
            with Image.open(BytesIO(data)) as img:
                with BytesIO() as img_bytes:
                    img.save(img_bytes, format="png")
                    return img_bytes.getvalue()
        except (requests.RequestException, OSError, Exception):
            return self._generate_blank_tile(title=title)

    async def _get_album_cover_async(
        self, client: httpx.AsyncClient, item: Union[Album, Track], title: str
    ) -> bytes:
        try:
            url = item.get_cover_image()
        except (IndexError, AttributeError, Exception):
            url = None
        if not url:
            return self._generate_blank_tile(title=title)
        try:
            data = await self._download_bytes_async(client, url, CACHE_KIND_ALBUM)
            with Image.open(BytesIO(data)) as img:
                with BytesIO() as img_bytes:
                    img.save(img_bytes, format="png")
                    return img_bytes.getvalue()
        except (httpx.HTTPError, requests.RequestException, OSError, Exception):
            return self._generate_blank_tile(title=title)

    def __repr__(self):
        return (
            f"<AlbumCollage ["
            f"{self.config.cols}x{self.config.rows}, "
            f"{self.config.period}"
            f"]>"
        )


class TrackCollageBuilder(AlbumCollageBuilder):
    ENTITY = ENTITY_TRACK

    def _get_tiles_from_top_items(
        self, user: User, limit: int, period: str
    ) -> List[CollageTile]:
        top_tracks = self.lastfm_client.get_top_tracks(user, limit, period)
        return self._create_tiles_from_top_items(top_tracks)

    async def _get_tiles_from_top_items_async(
        self,
        user: User,
        limit: int,
        period: str,
        max_concurrency: int = BaseCollageBuilder.DEFAULT_CONCURRENCY,
    ) -> List[CollageTile]:
        top_tracks = await self.lastfm_client.get_top_tracks_async(user, limit, period)
        return await self._create_tiles_from_top_items_async(
            top_tracks, max_concurrency=max_concurrency
        )

    def __repr__(self):
        return (
            f"<TrackCollage ["
            f"{self.config.cols}x{self.config.rows}, "
            f"{self.config.period}"
            f"]>"
        )


class CollageBuilderFactory:
    entity_collage_builders = {
        ENTITY_ARTIST: ArtistCollageBuilder,
        ENTITY_ALBUM: AlbumCollageBuilder,
        ENTITY_TRACK: TrackCollageBuilder,
    }

    def __new__(
        cls,
        entity: str,
        config: CollageBuilderConfig,
        lastfm_client: LastfmClient,
        cache: Optional[ArtworkCache] = None,
        fetcher: Optional[ResilientHttpFetcher] = None,
    ):
        collage_builder = cls.entity_collage_builders.get(entity)
        if not collage_builder:
            raise ValueError(f"Invalid entity: {entity}")
        return collage_builder(config, lastfm_client, cache=cache, fetcher=fetcher)
