from io import BytesIO

import requests
from PIL import Image
from pylast import Album


class LastfmUtils:

    @staticmethod
    def get_album_cover(album: Album) -> bytes:
        url = album.get_cover_image()
        img = requests.get(url).content
        Image.open(BytesIO(img)).seek(0)
        return img
