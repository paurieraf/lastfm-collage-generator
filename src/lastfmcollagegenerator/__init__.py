"""lastfmcollagegenerator: Python library to build Last.fm collages."""

from lastfmcollagegenerator.collage_generator import CollageGenerator
from lastfmcollagegenerator.theme import Theme, THEME_PRESETS, resolve_theme

__version__ = "0.8.0"
__all__ = ["CollageGenerator", "Theme", "THEME_PRESETS", "resolve_theme", "__version__"]
