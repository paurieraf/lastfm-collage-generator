import concurrent.futures
import logging
import os
import urllib.parse
from dataclasses import dataclass
from io import BytesIO
from typing import List, Tuple, Union

import bs4
import requests
from pylast import User, TopItem, Album, Artist, Track
from PIL import Image, ImageDraw, ImageFont

import lastfmcollagegenerator
from lastfmcollagegenerator.constants import ENTITY_ARTIST, ENTITY_ALBUM, \
    ENTITY_TRACK
from lastfmcollagegenerator.exceptions import ArtistNotFound
from lastfmcollagegenerator.lastfm.client import LastfmClient

logger = logging.getLogger(__name__)

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


@dataclass
class CollageTile:
    data: bytes
    playcount: int
    title: str


@dataclass
class CollageConfig:
    width: int
    height: int


class BaseCollageBuilder:
    ENTITY = None
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
    ):
        self.config = config
        self.lastfm_client = lastfm_client
        self._path = os.path.dirname(
            lastfmcollagegenerator.collage.__file__
        )

    def create(self, username: str) -> Image:
        user = self.lastfm_client.get_user(username)
        tiles = self._get_tiles_from_top_items(
            user=user,
            limit=self.config.cols * self.config.rows,
            period=self.config.period
        )
        return self._create_image(tiles, self.config.cols, self.config.rows)

    def _create_image(
            self,
            tiles: List[CollageTile],
            cols: int,
            rows: int
    ) -> Image:
        """
        300px is the height and the width of the covers
        """
        width = self.TILE_WIDTH
        height = self.TILE_HEIGHT
        collage_width = cols * width
        collage_height = rows * height

        # create blank image of the full size
        new_image = Image.new("RGB", (collage_width, collage_height))
        cursor = (0, 0)
        for tile in tiles:
            new_image.paste(Image.open(BytesIO(tile.data)), cursor)
            title = f"{tile.title}"
            if self.config.show_playcount:
                title += f". ({tile.playcount})"
            self._insert_tile_title(
                image=new_image,
                title=title,
                cursor=cursor
            )

            # move cursor to next tile
            y = cursor[1]
            x = cursor[0] + width
            if cursor[0] >= (collage_width - width):
                y = cursor[1] + height
                x = 0
            cursor = (x, y)
        return new_image

    def _insert_tile_title(
            self,
            image: Image,
            title: str,
            cursor: Tuple[int, int]
    ):
        draw = ImageDraw.Draw(image, "RGBA")
        x = cursor[0]
        y = cursor[1]
        y_0 = y + 235
        y_1 = y * 2 + self.TILE_WIDTH
        if y_1 == 0:
            y_1 += self.TILE_WIDTH * 2
        draw.rectangle(((x, y_0), (x + self.TILE_WIDTH, y_1)), (0, 0, 0, 123))

        font_path = self.FONT_BOLD_PATH if self.FONT_BOLD else self.FONT_REGULAR_PATH
        font = ImageFont.truetype(
            f"{self._path}"
            f"/{font_path}",
            self.FONT_SIZE
        )

        title = self._insert_newline_characters_to_text(font, title)
        draw.text((x + 8, y + 240), title, fill=(255, 255, 255), font=font)

    @staticmethod
    def _insert_newline_characters_to_text(font: ImageFont, text: str) -> str:
        processed_chars = []
        processed_text = ""
        text_lines = []
        for c in text:
            processed_chars.append(c)
            processed_text = "".join(processed_chars)
            font_w = font.getlength(processed_text)
            if font_w >= 275:
                text_lines.append(processed_text)
                processed_chars = []
                processed_text = ""
        text_lines.append(processed_text)  # Add residual characters
        title = "\n".join(text_lines)
        return title

    @classmethod
    def _generate_blank_tile(cls) -> bytes:
        img_bytes = BytesIO()
        img = Image.new("RGB", (cls.TILE_WIDTH, cls.TILE_HEIGHT))
        img.save(img_bytes, format="png")
        img = img_bytes.getvalue()
        return img

    def _get_tiles_from_top_items(
            self,
            user: User,
            limit: int,
            period: str
    ) -> List[CollageTile]:
        raise NotImplementedError

    @classmethod
    def _create_tiles_from_top_items(
            cls,
            top_items: List[TopItem],
    ) -> List[CollageTile]:
        tiles: List[CollageTile] = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for top_item in top_items:
                future = executor.submit(
                    cls._create_tile_from_top_item,
                    top_item,
                )
                futures.append(future)
            for future in concurrent.futures.as_completed(futures):
                tiles.append(future.result())
        tiles.sort(key=lambda x: int(x.playcount), reverse=True)
        return tiles

    @classmethod
    def _create_tile_from_top_item(
            cls,
            top_item: TopItem,
    ) -> CollageTile:
        raise NotImplementedError


class ArtistCollageBuilder(BaseCollageBuilder):
    ENTITY = ENTITY_ARTIST

    def _get_tiles_from_top_items(
            self,
            user: User,
            limit: int,
            period: str
    ) -> List[CollageTile]:
        top_artists = self.lastfm_client.get_top_artists(user, limit, period)
        return self._create_tiles_from_top_items(top_artists)

    @classmethod
    def _create_tile_from_top_item(
            cls,
            top_item: TopItem,
    ) -> CollageTile:
        data = cls._get_artist_image(top_item.item)
        title = top_item.item.name
        return CollageTile(
            data=data,
            playcount=top_item.weight,
            title=title
        )

    @classmethod
    def _get_artist_image(cls, artist: Artist) -> bytes:
        """
        Last.fm API does not provide artist images.
        So we scrape it from the website.
        """
        try:
            resp = requests.get("https://www.last.fm/music/{artist}".format(
                artist=urllib.parse.quote_plus(artist.name)
            ))
            if resp.status_code == 404:
                raise ArtistNotFound
            soup = bs4.BeautifulSoup(resp.content, 'html5lib')

            url = None
            if soup.find(class_="header-new-background-image"):
                url = str(
                    soup.find(
                        class_="header-new-background-image"
                    ).get("content")
                )
            if not url:
                raise ArtistNotFound

            response = requests.get(url).content
            img = Image.open(BytesIO(response))
            img.seek(0)
            img.thumbnail((cls.TILE_WIDTH, cls.TILE_HEIGHT))
            img_bytes = BytesIO()
            img.save(img_bytes, format="png")
            img = img_bytes.getvalue()
            return img
        except ArtistNotFound as e:
            logger.exception(e)
            return cls._generate_blank_tile()


    def __repr__(self):
        return f"<ArtistCollage [" \
               f"{self.config.cols}x{self.config.rows}, " \
               f"{self.config.period}" \
               f"]>"


class AlbumCollageBuilder(BaseCollageBuilder):
    ENTITY = ENTITY_ALBUM

    def _get_tiles_from_top_items(
            self,
            user: User,
            limit: int,
            period: str
    ) -> List[CollageTile]:
        top_albums = self.lastfm_client.get_top_albums(user, limit, period)
        return self._create_tiles_from_top_items(top_albums)

    @classmethod
    def _create_tile_from_top_item(
            cls,
            top_item: TopItem,

    ) -> CollageTile:
        data = cls._get_album_cover(top_item.item)
        title = f"{top_item.item.artist} - {top_item.item.title}"
        return CollageTile(
            data=data,
            playcount=top_item.weight,
            title=title
        )

    @classmethod
    def _get_album_cover(
            cls,
            item: Union[Album, Track]
    ) -> bytes:
        try:
            url = item.get_cover_image()
        except IndexError:
            url = None
        if not url:
            img = cls._generate_blank_tile()
        else:
            img = requests.get(url).content
            Image.open(BytesIO(img)).seek(0)
        return img

    def __repr__(self):
        return f"<AlbumCollage [" \
               f"{self.config.cols}x{self.config.rows}, " \
               f"{self.config.period}" \
               f"]>"


class TrackCollageBuilder(AlbumCollageBuilder):
    ENTITY = ENTITY_TRACK

    def _get_tiles_from_top_items(
            self,
            user: User,
            limit: int,
            period: str
    ) -> List[CollageTile]:
        top_tracks = self.lastfm_client.get_top_tracks(user, limit, period)
        return self._create_tiles_from_top_items(top_tracks)

    def __repr__(self):
        return f"<TrackCollage [" \
               f"{self.config.cols}x{self.config.rows}, " \
               f"{self.config.period}" \
               f"]>"


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
            lastfm_client: LastfmClient
    ):
        collage_builder = cls.entity_collage_builders.get(entity)
        if not collage_builder:
            raise ValueError(f"Invalid entity: {entity}")
        return collage_builder(config, lastfm_client)
