from io import BytesIO

import requests
from PIL import Image
from pylast import Album


class LastfmUtils:

    @staticmethod
    def get_album_cover(album: Album) -> bytes:
        url = album.get_cover_image()
        if not url:
            img = LastfmUtils.generate_blank_tile()
        else:
            img = requests.get(url).content
            Image.open(BytesIO(img)).seek(0)
        return img

    @staticmethod
    def generate_blank_tile() -> bytes:
        img_bytes = BytesIO()
        img = Image.new("RGB", (300, 300))
        img.save(img_bytes, format="png")
        img = img_bytes.getvalue()
        return img
