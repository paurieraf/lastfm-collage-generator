import os
import urllib.parse

from dataclasses import dataclass
from io import BytesIO
from typing import List, Tuple, Union

import bs4
import pylast
import requests
from PIL import Image, ImageDraw, ImageFont
from pylast import User, TopItem, Album, Artist, Track

import lastfmcollagegenerator
from lastfmcollagegenerator.lastfm.client import LastfmClient


@dataclass
class CollageTile:
    data: bytes
    playcount: int
    title: str


class CollageGenerator:
    """
    Generates a NxN collage with the covers of a Last.fm user top albums or artists of a given period
    It takes a Last.fm API key and API secret to be able to connect to the Last.fm API

    # TODO:
        - Add config parameters like displaying the title or the play count in the images
        - Add validations for the input parameters
    """
    ENTITY_ALBUM = "album"
    ENTITY_ARTIST = "artist"
    ENTITY_TRACK = "track"
    ENTITIES = (
        ENTITY_ALBUM,
        ENTITY_ARTIST,
        ENTITY_TRACK
    )
    PERIODS = (
        pylast.PERIOD_7DAYS,
        pylast.PERIOD_1MONTH,
        pylast.PERIOD_3MONTHS,
        pylast.PERIOD_6MONTHS,
        pylast.PERIOD_12MONTHS,
        pylast.PERIOD_OVERALL
    )
    MAX_COLS = 5
    MAX_ROWS = 5
    TILE_WIDTH = 300
    TILE_HEIGHT = 300
    FONT_REGULAR_PATH = "fonts/DejaVuSansMono.ttf"
    FONT_BOLD_PATH = "fonts/DejaVuSansMono-Bold.ttf"
    FONT_SIZE = 15
    FONT_BOLD = False

    def __init__(self, lastfm_api_key: str, lastfm_api_secret: str):
        self._path = os.path.dirname(lastfmcollagegenerator.collage_generator.__file__)
        self.lastfm_client = LastfmClient(lastfm_api_key, lastfm_api_secret)

    def generate(self, entity: str, username: str, cols: int, rows: int, period: str) -> Image:
        self._validate_parameters(entity, rows, cols, period)
        if entity == self.ENTITY_ALBUM:
            return self.generate_top_albums_collage(username, cols, rows, period)
        elif entity == self.ENTITY_ARTIST:
            return self.generate_top_artists_collage(username, cols, rows, period)
        elif entity == self.ENTITY_TRACK:
            return self.generate_top_tracks_collage(username, cols, rows, period)
        else:
            raise ValueError(f"Invalid entity: {entity}")

    def generate_top_albums_collage(self, username: str, cols: int, rows: int, period: str) -> Image:
        user = self.lastfm_client.get_user(username)
        tiles = self._get_tiles_from_top_albums(user, limit=cols * rows, period=period)
        return self._create_image(tiles, cols, rows)

    def generate_top_artists_collage(self, username: str, cols: int, rows: int, period: str) -> Image:
        user = self.lastfm_client.get_user(username)
        tiles = self._get_tiles_from_top_artists(user, limit=cols * rows, period=period)
        return self._create_image(tiles, cols, rows)

    def generate_top_tracks_collage(self, username: str, cols: int, rows: int, period: str) -> Image:
        user = self.lastfm_client.get_user(username)
        tiles = self._get_tiles_from_top_tracks(user, limit=cols * rows, period=period)
        return self._create_image(tiles, cols, rows)

    def _get_tiles_from_top_albums(self, user: User, limit: int, period: str) -> List:
        top_albums = self.lastfm_client.get_top_albums(user, limit, period)
        tiles = self._create_tiles_from_top_items(top_albums, entity=self.ENTITY_ALBUM)
        return tiles

    def _get_tiles_from_top_artists(self, user: User, limit: int, period: str) -> List:
        top_artists = self.lastfm_client.get_top_artists(user, limit, period)
        tiles = self._create_tiles_from_top_items(top_artists, entity=self.ENTITY_ARTIST)
        return tiles

    def _get_tiles_from_top_tracks(self, user: User, limit: int, period: str) -> List:
        top_tracks = self.lastfm_client.get_top_tracks(user, limit, period)
        tiles = self._create_tiles_from_top_items(top_tracks, entity=self.ENTITY_TRACK)
        return tiles

    def _create_image(self, tiles: List[CollageTile], cols: int, rows: int) -> Image:
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
            self._insert_tile_title(new_image, f"{tile.title}. ({tile.playcount})", cursor)

            # move cursor to next tile
            y = cursor[1]
            x = cursor[0] + width
            if cursor[0] >= (collage_width - width):
                y = cursor[1] + height
                x = 0
            cursor = (x, y)
        return new_image

    @classmethod
    def _create_tiles_from_top_items(cls, top_items: List[TopItem], entity: str) -> List[CollageTile]:
        tiles: List[CollageTile] = []
        for top_item in top_items:
            if entity == cls.ENTITY_ALBUM or entity == cls.ENTITY_TRACK:
                data = cls._get_album_cover(top_item.item)
                title = f"{top_item.item.artist} - {top_item.item.title}"
            elif entity == cls.ENTITY_ARTIST:
                data = cls._get_artist_image(top_item.item)
                title = top_item.item.name
            else:
                raise ValueError(f"Invalid entity: {entity}")

            tile = CollageTile(
                data=data,
                playcount=top_item.weight,
                title=title
            )
            tiles.append(tile)
        return tiles

    def _insert_tile_title(self, image: Image, title: str, cursor: Tuple[int, int]):
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

    @classmethod
    def _get_album_cover(cls, item: Union[Album, Track]) -> bytes:
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

    @classmethod
    def _get_artist_image(cls, artist: Artist) -> bytes:
        """
        Last.fm API does not provide artist images. So we scrape it from the website.
        """
        resp = requests.get("https://www.last.fm/music/{artist}".format(artist=urllib.parse.quote(artist.name)))
        if resp.status_code == 404:
            raise Exception("Artist not found")
        soup = bs4.BeautifulSoup(resp.content, 'html5lib')

        url = None
        if soup.find(class_="header-new-background-image"):
            url = str(soup.find(class_="header-new-background-image").get("content"))
        if not url:
            img = cls._generate_blank_tile()
        else:
            response = requests.get(url).content
            img = Image.open(BytesIO(response))
            img.seek(0)
            img.thumbnail((cls.TILE_WIDTH, cls.TILE_HEIGHT), Image.ANTIALIAS)
            img_bytes = BytesIO()
            img.save(img_bytes, format="png")
            img = img_bytes.getvalue()
        return img

    @staticmethod
    def _insert_newline_characters_to_text(font: ImageFont, text: str) -> str:
        processed_chars = []
        processed_text = ""
        text_lines = []
        for c in text:
            processed_chars.append(c)
            processed_text = "".join(processed_chars)
            temp_w, temp_h = font.getsize(processed_text)
            if temp_w >= 275:
                text_lines.append(processed_text)
                processed_chars = []
                processed_text = ""
        text_lines.append(processed_text)  # Add residual characters
        title = "\n".join(text_lines)
        return title

    @staticmethod
    def _generate_blank_tile() -> bytes:
        img_bytes = BytesIO()
        img = Image.new("RGB", (300, 300))
        img.save(img_bytes, format="png")
        img = img_bytes.getvalue()
        return img

    def _validate_parameters(self, entity: str, rows: int, cols: int, period: str):
        if entity not in self.ENTITIES:
            raise ValueError(
                f"Invalid entity: {entity}. "
                f"Options are: {self.ENTITIES}"
            )
        if cols > self.MAX_COLS or rows > self.MAX_ROWS:
            raise ValueError(
                f"Invalid number of columns or rows: {cols}x{rows}: "
                f"Max values are: {self.MAX_ROWS}x{self.MAX_COLS}"
            )
        if period not in self.PERIODS:
            raise ValueError(
                f"Invalid period: {period}. "
                f"Options are: {self.PERIODS}"
            )
