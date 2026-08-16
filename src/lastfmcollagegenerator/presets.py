from dataclasses import dataclass
from typing import Dict

PRESET_INSTAGRAM_STORY = "instagram-story"
PRESET_INSTAGRAM_POST = "instagram-post"
PRESET_TWITTER_HEADER = "twitter-header"
PRESET_DESKTOP_WALLPAPER = "desktop-wallpaper"
PRESET_DESKTOP_WALLPAPER_4K = "desktop-wallpaper-4k"


@dataclass
class SocialPreset:
    name: str
    width: int
    height: int
    cols: int
    rows: int
    tile_size: int


SOCIAL_PRESETS: Dict[str, SocialPreset] = {
    PRESET_INSTAGRAM_STORY: SocialPreset(
        name=PRESET_INSTAGRAM_STORY,
        width=1080,
        height=1920,
        cols=3,
        rows=5,
        tile_size=360,
    ),
    PRESET_INSTAGRAM_POST: SocialPreset(
        name=PRESET_INSTAGRAM_POST,
        width=1080,
        height=1080,
        cols=3,
        rows=3,
        tile_size=360,
    ),
    PRESET_TWITTER_HEADER: SocialPreset(
        name=PRESET_TWITTER_HEADER,
        width=1500,
        height=500,
        cols=5,
        rows=1,
        tile_size=300,
    ),
    PRESET_DESKTOP_WALLPAPER: SocialPreset(
        name=PRESET_DESKTOP_WALLPAPER,
        width=1920,
        height=1080,
        cols=6,
        rows=3,
        tile_size=320,
    ),
    PRESET_DESKTOP_WALLPAPER_4K: SocialPreset(
        name=PRESET_DESKTOP_WALLPAPER_4K,
        width=3840,
        height=2160,
        cols=6,
        rows=3,
        tile_size=600,
    ),
}

PRESET_NAMES = tuple(SOCIAL_PRESETS.keys())


def resolve_preset(preset: str) -> SocialPreset:
    normalized = preset.lower().strip()
    if normalized not in SOCIAL_PRESETS:
        raise ValueError(
            "Unknown preset: '{0}'. Options are: {1}".format(preset, PRESET_NAMES)
        )
    return SOCIAL_PRESETS[normalized]
