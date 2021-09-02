from dataclasses import dataclass
from io import BytesIO
from typing import List, Tuple

from PIL import Image, ImageDraw
from pylast import User, TopItem

from lastfmcollagegenerator.lastfm.client import LastfmClient
from lastfmcollagegenerator.lastfm.utils import LastfmUtils


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
    VALID_PERIODS = ("7day", "1month", "3month", "6month", "12month", "overall",)
    MAX_COLS = 5
    MAX_ROWS = 5

    def __init__(self, lastfm_api_key: str, lastfm_api_secret: str):
        self.lastfm_client = LastfmClient(lastfm_api_key, lastfm_api_secret)

    def generate_top_albums_collage(self, username: str, cols: int, rows: int, period: str) -> Image:
        user = self.lastfm_client.get_user(username)
        tiles = self._get_tiles_from_top_albums(user, limit=cols * rows, period=period)
        return self._create_image(tiles, cols, rows)

    def _get_tiles_from_top_albums(self, user: User, limit: int, period: str) -> List:
        top_albums = self.lastfm_client.get_top_albums(user, limit, period)
        covers = self._create_tiles_from_top_albums(top_albums)
        return covers

    def _create_image(self, tiles: List[CollageTile], cols, rows):
        """
        300px is the height and the width of the covers
        TODO: Maybe is a good idea to always resize the images to 300x300 to ensure the smaller ones fit the tile
        """

        width = 300
        height = 300
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

    @staticmethod
    def _create_tiles_from_top_albums(top_albums: List[TopItem]) -> List[CollageTile]:
        tiles: List[CollageTile] = []
        for top_item in top_albums:
            tile = CollageTile(
                data=LastfmUtils.get_album_cover(top_item.item),
                playcount=top_item.weight,
                title=f"{top_item.item.artist} - {top_item.item.title}"
            )
            tiles.append(tile)
        return tiles

    @staticmethod
    def _insert_tile_title(image: Image, title: str, cursor: Tuple[int, int]):
        draw = ImageDraw.Draw(image, "RGBA")
        x = cursor[0]
        y = cursor[1]
        y_0 = y + 235
        y_1 = y * 2 + 300
        if y_1 == 0:
            y_1 += 600
        draw.rectangle([(x, y_0), (x + 300, y_1)], (0, 0, 0, 123))
        draw.text((x + 8, y + 240), title, (255, 255, 255))
