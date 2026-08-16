#!/usr/bin/env python3
"""GitHub Action entrypoint for lastfm-collage-generator.

Generates a Last.fm collage in live mode (using LASTFM_API_KEY /
LASTFM_API_SECRET environment variables) or in offline mock mode,
writing the result to the configured output path.
"""

import argparse
import io
import os
import sys
from typing import List
from unittest.mock import MagicMock

from PIL import Image, ImageDraw

from lastfmcollagegenerator.collage import (
    CollageBuilderConfig,
    CollageBuilderFactory,
    CollageTile,
)
from lastfmcollagegenerator.collage_generator import CollageGenerator
from lastfmcollagegenerator.lastfm.client import LastfmClient

ENTITIES = ("album", "artist", "track")
PERIODS = ("7day", "1month", "3month", "6month", "12month", "overall")


def generate_mock_tiles(count: int, entity: str, tile_size: int) -> List[CollageTile]:
    """Generate synthetic colored tiles for offline mock rendering."""
    palette = [
        "#E63946",
        "#457B9D",
        "#2A9D8F",
        "#E76F51",
        "#F4A261",
        "#6A4C93",
        "#1D3557",
        "#8338EC",
        "#3A86FF",
        "#FB5607",
        "#FFBE0B",
        "#06D6A0",
        "#118AB2",
        "#073B4C",
        "#D90429",
    ]
    tiles = []
    for i in range(count):
        color = palette[i % len(palette)]
        img = Image.new("RGB", (tile_size, tile_size), color=color)
        draw = ImageDraw.Draw(img)
        draw.rectangle(
            ((20, 20), (tile_size - 20, tile_size - 20)),
            outline="#FFFFFF",
            width=3,
        )
        with io.BytesIO() as buf:
            img.save(buf, format="PNG")
            img_data = buf.getvalue()
        title = "Mock Item #{0}".format(i + 1)
        tiles.append(CollageTile(data=img_data, playcount=500 - (i * 15), title=title))
    return tiles


def run_mock_generation(entity: str, cols: int, rows: int, period: str) -> Image.Image:
    config = CollageBuilderConfig(cols=cols, rows=rows, period=period)
    mock_client = MagicMock(spec=LastfmClient)
    builder = CollageBuilderFactory(
        entity=entity, config=config, lastfm_client=mock_client
    )
    tiles = generate_mock_tiles(cols * rows, entity, builder.tile_width)
    return builder._create_image(tiles, cols, rows)


def run_live_generation(
    entity: str,
    username: str,
    cols: int,
    rows: int,
    period: str,
    api_key: str,
    api_secret: str,
) -> Image.Image:
    generator = CollageGenerator(lastfm_api_key=api_key, lastfm_api_secret=api_secret)
    return generator.generate(
        entity=entity,
        username=username,
        cols=cols,
        rows=rows,
        period=period,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a Last.fm collage for GitHub Actions workflows."
    )
    parser.add_argument("--username", type=str, required=True)
    parser.add_argument("--entity", type=str, default="album", choices=list(ENTITIES))
    parser.add_argument("--cols", type=int, default=5)
    parser.add_argument("--rows", type=int, default=5)
    parser.add_argument("--period", type=str, default="7day", choices=list(PERIODS))
    parser.add_argument(
        "--output-path", type=str, default="collage.png", dest="output_path"
    )
    parser.add_argument(
        "--mock", action="store_true", help="Generate an offline mock collage."
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not (1 <= args.cols <= 20 and 1 <= args.rows <= 20):
        print(
            "[!] Error: grid dimensions out of bounds (1x1 to 20x20).",
            file=sys.stderr,
        )
        return 1

    try:
        if args.mock:
            image = run_mock_generation(
                entity=args.entity,
                cols=args.cols,
                rows=args.rows,
                period=args.period,
            )
        else:
            api_key = os.environ.get("LASTFM_API_KEY", "")
            api_secret = os.environ.get("LASTFM_API_SECRET", "")
            if not api_key or not api_secret:
                print(
                    "[!] Error: LASTFM_API_KEY and LASTFM_API_SECRET are required "
                    "for live mode. Pass --mock for an offline collage.",
                    file=sys.stderr,
                )
                return 1
            image = run_live_generation(
                entity=args.entity,
                username=args.username,
                cols=args.cols,
                rows=args.rows,
                period=args.period,
                api_key=api_key,
                api_secret=api_secret,
            )

        output_path = os.path.abspath(args.output_path)
        out_dir = os.path.dirname(output_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        image.save(output_path)
        print(
            "[+] Collage saved to {0} ({1}x{2})".format(
                output_path, image.width, image.height
            )
        )
        return 0
    except Exception as exc:
        print("[!] Error generating collage: {0}".format(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
