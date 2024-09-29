class ArtistNotFound(Exception):
    def __init__(self, msg="Artist not found", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)