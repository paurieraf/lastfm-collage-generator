import os

from dataclasses import dataclass
from io import BytesIO
from typing import List, Tuple

import pylast
import requests
from PIL import Image, ImageDraw, ImageFont
from pylast import User, TopItem, Album

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
        self.lastfm_client = LastfmClient(lastfm_api_key, lastfm_api_secret)

    def generate_top_albums_collage(self, username: str, cols: int, rows: int, period: str) -> Image:
        user = self.lastfm_client.get_user(username)
        tiles = self._get_tiles_from_top_albums(user, limit=cols * rows, period=period)
        return self._create_image(tiles, cols, rows)

    def _get_tiles_from_top_albums(self, user: User, limit: int, period: str) -> List:
        top_albums = self.lastfm_client.get_top_albums(user, limit, period)
        tiles = self._create_tiles_from_top_albums(top_albums)
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
    def _create_tiles_from_top_albums(cls, top_albums: List[TopItem]) -> List[CollageTile]:
        tiles: List[CollageTile] = []
        for top_item in top_albums:
            tile = CollageTile(
                data=cls._get_album_cover(top_item.item),
                playcount=top_item.weight,
                title=f"{top_item.item.artist} - {top_item.item.title}"
            )
            tiles.append(tile)
        return tiles

    @classmethod
    def _insert_tile_title(cls, image: Image, title: str, cursor: Tuple[int, int]):
        draw = ImageDraw.Draw(image, "RGBA")
        x = cursor[0]
        y = cursor[1]
        y_0 = y + 235
        y_1 = y * 2 + cls.TILE_WIDTH
        if y_1 == 0:
            y_1 += cls.TILE_WIDTH * 2
        draw.rectangle(((x, y_0), (x + cls.TILE_WIDTH, y_1)), (0, 0, 0, 123))

        font_path = cls.FONT_BOLD_PATH if cls.FONT_BOLD else cls.FONT_REGULAR_PATH
        font = ImageFont.truetype(
            f"{os.path.dirname(lastfmcollagegenerator.collage_generator.__file__)}"
            f"/{font_path}",
            cls.FONT_SIZE
        )

        title = cls._insert_newline_characters_to_text(font, title)
        draw.text((x + 8, y + 240), title, fill=(255, 255, 255), font=font)

    @classmethod
    def _get_album_cover(cls, album: Album) -> bytes:
        url = album.get_cover_image()
        if not url:
            img = cls._generate_blank_tile()
        else:
            img = requests.get(url).content
            Image.open(BytesIO(img)).seek(0)
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
