"""lastfmcollagegenerator: Python library to build Last.fm collages."""

from lastfmcollagegenerator.collage_generator import CollageGenerator
from lastfmcollagegenerator.export import (
    SUPPORTED_EXPORT_FORMATS,
    export_image,
    infer_format,
)
from lastfmcollagegenerator.theme import Theme, THEME_PRESETS, resolve_theme
from lastfmcollagegenerator.effects import (
    ImageFilter,
    VisualEffectPipeline,
    DuotoneFilter,
    ColorExtractor,
)

__version__ = "1.3.0"
__all__ = [
    "CollageGenerator",
    "Theme",
    "THEME_PRESETS",
    "resolve_theme",
    "ImageFilter",
    "VisualEffectPipeline",
    "DuotoneFilter",
    "ColorExtractor",
    "export_image",
    "infer_format",
    "SUPPORTED_EXPORT_FORMATS",
    "__version__",
]
