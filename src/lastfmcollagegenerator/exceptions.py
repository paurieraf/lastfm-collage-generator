class LastfmCollageGeneratorError(Exception):
    """Base exception for lastfm-collage-generator."""

    def __init__(
        self, msg="An error occurred in lastfm-collage-generator", *args, **kwargs
    ):
        super().__init__(msg, *args, **kwargs)


class ArtistNotFound(LastfmCollageGeneratorError):
    def __init__(self, msg="Artist not found", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class ArtistImageNotFound(LastfmCollageGeneratorError):
    def __init__(self, msg="Artist image not found", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)
