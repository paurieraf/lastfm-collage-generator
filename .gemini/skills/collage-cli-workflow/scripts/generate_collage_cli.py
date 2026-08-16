#!/usr/bin/env python3
"""Collage CLI Generator for lastfm-collage-generator.

Generates Last.fm collages with support for live API credentials or offline mock mode.
"""

import argparse
import io
import os
import sys
from typing import List, Optional, Tuple

# Add src to sys.path
project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
)
src_path = os.path.join(project_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Default constants
ENTITIES = ("album", "artist", "track")
PERIODS = ("7day", "1month", "3month", "6month", "12month", "overall")
TILE_WIDTH = 300
TILE_HEIGHT = 300


class MockTile:
    """Mock tile container for standalone offline rendering."""

    def __init__(self, data: bytes, playcount: int, title: str) -> None:
        self.data = data
        self.playcount = playcount
        self.title = title


def generate_mock_tiles(
    count: int,
    entity: str,
    tile_width: int = 300,
    tile_height: int = 300,
) -> List[MockTile]:
    """Generates synthetic colored MockTile objects for offline mock rendering."""
    from PIL import Image, ImageDraw

    palette = [
        ("#E63946", "Crimson"),
        ("#457B9D", "Steel Blue"),
        ("#2A9D8F", "Persian Green"),
        ("#E76F51", "Burnt Sienna"),
        ("#F4A261", "Sandy Brown"),
        ("#6A4C93", "Royal Purple"),
        ("#1D3557", "Prussian Blue"),
        ("#8338EC", "Violet"),
        ("#3A86FF", "Azure"),
        ("#FB5607", "Orange"),
        ("#FFBE0B", "Amber"),
        ("#06D6A0", "Mint"),
        ("#118AB2", "Cerulean"),
        ("#073B4C", "Midnight"),
        ("#D90429", "Ruby"),
    ]

    tiles = []
    for i in range(count):
        bg_color, color_name = palette[i % len(palette)]
        img = Image.new("RGB", (tile_width, tile_height), color=bg_color)
        draw = ImageDraw.Draw(img)

        # Draw decorative mock geometry
        draw.rectangle(((20, 20), (tile_width - 20, tile_height - 20)), outline="#FFFFFF", width=3)
        draw.ellipse(((80, 80), (tile_width - 80, tile_height - 80)), outline="#FFFFFF", width=2)

        with io.BytesIO() as buf:
            img.save(buf, format="PNG")
            img_data = buf.getvalue()

        playcount = 500 - (i * 15)
        if entity == "artist":
            title = f"Mock Artist #{i + 1} ({color_name})"
        elif entity == "track":
            title = f"Artist #{i + 1} - Hit Song #{i + 1}"
        else:
            title = f"Artist #{i + 1} - Iconic Album #{i + 1}"

        tiles.append(MockTile(data=img_data, playcount=playcount, title=title))
    return tiles


def wrap_text_for_font(font, text: str, max_width: int = 275) -> str:
    """Wraps text so lines do not exceed max_width in pixels."""
    processed_chars = []
    processed_text = ""
    text_lines = []
    for c in text:
        processed_chars.append(c)
        processed_text = "".join(processed_chars)
        try:
            font_w = font.getlength(processed_text)
        except AttributeError:
            font_w = len(processed_text) * 9
        if font_w >= max_width:
            text_lines.append(processed_text)
            processed_chars = []
            processed_text = ""
    text_lines.append(processed_text)
    return "\n".join(text_lines)


def render_standalone_mock_collage(
    tiles: List[MockTile],
    cols: int,
    rows: int,
    show_playcount: bool = True,
) -> "Image.Image":
    """Renders a composite collage from tiles using Pillow and bundled TrueType fonts."""
    from PIL import Image, ImageDraw, ImageFont

    collage_width = cols * TILE_WIDTH
    collage_height = rows * TILE_HEIGHT
    new_image = Image.new("RGB", (collage_width, collage_height), color="black")

    # Resolve bundled font
    font_path = os.path.join(project_root, "src", "lastfmcollagegenerator", "fonts", "DejaVuSansMono.ttf")
    try:
        font = ImageFont.truetype(font_path, size=15)
    except (OSError, IOError):
        font = ImageFont.load_default()

    cursor = (0, 0)
    for tile in tiles:
        with io.BytesIO(tile.data) as stream:
            with Image.open(stream) as tile_img:
                new_image.paste(tile_img, cursor)

        # Title overlay
        if show_playcount:
            title = f"{tile.title}. ({tile.playcount})"
        else:
            title = f"{tile.title}"

        draw = ImageDraw.Draw(new_image, "RGBA")
        x, y = cursor
        y_0 = y + (TILE_HEIGHT - 65)
        y_1 = y + TILE_HEIGHT
        draw.rectangle(((x, y_0), (x + TILE_WIDTH, y_1)), (0, 0, 0, 123))

        wrapped_title = wrap_text_for_font(font, title, 275)
        draw.text((x + 8, y + 240), wrapped_title, fill=(255, 255, 255), font=font)

        # Move cursor
        next_y = cursor[1]
        next_x = cursor[0] + TILE_WIDTH
        if cursor[0] >= (collage_width - TILE_WIDTH):
            next_y = cursor[1] + TILE_HEIGHT
            next_x = 0
        cursor = (next_x, next_y)

    return new_image


def run_mock_generation(
    entity: str,
    username: str,
    cols: int,
    rows: int,
    period: str,
    show_playcount: bool = True,
) -> "Image.Image":
    """Renders a collage using synthetic mock data offline."""
    # Attempt to use package builder if available, else use standalone mock renderer
    try:
        from unittest.mock import MagicMock
        from lastfmcollagegenerator.collage import (
            CollageBuilderConfig,
            CollageBuilderFactory,
            CollageTile,
        )
        from lastfmcollagegenerator.lastfm.client import LastfmClient

        config = CollageBuilderConfig(
            cols=cols,
            rows=rows,
            period=period,
            show_playcount=show_playcount,
        )
        mock_client = MagicMock(spec=LastfmClient)
        builder = CollageBuilderFactory(entity=entity, config=config, lastfm_client=mock_client)
        mock_tiles = generate_mock_tiles(cols * rows, entity, builder.TILE_WIDTH, builder.TILE_HEIGHT)
        collage_tiles = [CollageTile(data=t.data, playcount=t.playcount, title=t.title) for t in mock_tiles]
        return builder._create_image(collage_tiles, cols, rows)
    except Exception:
        mock_tiles = generate_mock_tiles(cols * rows, entity, TILE_WIDTH, TILE_HEIGHT)
        return render_standalone_mock_collage(mock_tiles, cols, rows, show_playcount)


def run_live_generation(
    entity: str,
    username: str,
    cols: int,
    rows: int,
    period: str,
    api_key: str,
    api_secret: str,
) -> "Image.Image":
    """Renders a live collage by calling the CollageGenerator facade."""
    from lastfmcollagegenerator.collage_generator import CollageGenerator

    generator = CollageGenerator(
        lastfm_api_key=api_key,
        lastfm_api_secret=api_secret,
    )
    return generator.generate(
        entity=entity,
        username=username,
        cols=cols,
        rows=rows,
        period=period,
    )


def parse_args() -> argparse.Namespace:
    """Configures and parses CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Generate Last.fm composite collages with real API credentials or offline mock mode."
    )
    parser.add_argument(
        "-u",
        "--username",
        type=str,
        default="testuser",
        help="Last.fm profile username (default: testuser).",
    )
    parser.add_argument(
        "-e",
        "--entity",
        type=str,
        default="album",
        choices=list(ENTITIES),
        help="Entity to collage: album, artist, or track (default: album).",
    )
    parser.add_argument(
        "-c",
        "--cols",
        type=int,
        default=3,
        help="Number of columns (1 to 5, default: 3).",
    )
    parser.add_argument(
        "-r",
        "--rows",
        type=int,
        default=3,
        help="Number of rows (1 to 5, default: 3).",
    )
    parser.add_argument(
        "-p",
        "--period",
        type=str,
        default="7day",
        choices=list(PERIODS),
        help="Time period for scrobble data (default: 7day).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="collage.png",
        help="Destination path for generated collage image (default: collage.png).",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=os.environ.get("LASTFM_API_KEY", ""),
        help="Last.fm API Key (default: reads from LASTFM_API_KEY env).",
    )
    parser.add_argument(
        "--api-secret",
        type=str,
        default=os.environ.get("LASTFM_API_SECRET", ""),
        help="Last.fm API Secret (default: reads from LASTFM_API_SECRET env).",
    )
    parser.add_argument(
        "-m",
        "--mock",
        action="store_true",
        help="Run offline mock generation without calling Last.fm API.",
    )
    parser.add_argument(
        "--no-title",
        action="store_true",
        help="Disable title overlay banners on tiles.",
    )
    return parser.parse_args()


def main() -> int:
    """Main CLI execution flow."""
    args = parse_args()

    # Boundary check
    if not (1 <= args.cols <= 5 and 1 <= args.rows <= 5):
        print(f"[!] Error: Grid dimensions {args.cols}x{args.rows} out of bounds (allowed: 1x1 to 5x5).", file=sys.stderr)
        return 1

    print("=" * 60)
    print("Last.fm Collage Generator CLI")
    print(f"User: {args.username} | Entity: {args.entity} | Grid: {args.cols}x{args.rows} | Period: {args.period}")
    print(f"Mode: {'OFFLINE MOCK' if args.mock else 'LIVE API'}")
    print("=" * 60)

    try:
        if args.mock:
            print("[+] Generating synthetic offline collage...")
            image = run_mock_generation(
                entity=args.entity,
                username=args.username,
                cols=args.cols,
                rows=args.rows,
                period=args.period,
                show_playcount=not args.no_title,
            )
        else:
            if not args.api_key or not args.api_secret:
                print(
                    "[!] Error: Last.fm API Key and Secret are required for live mode.\n"
                    "    Provide them via --api-key / --api-secret or set LASTFM_API_KEY / LASTFM_API_SECRET env vars.\n"
                    "    Alternatively, pass --mock to generate an offline sample collage.",
                    file=sys.stderr,
                )
                return 1

            print("[+] Contacting Last.fm API and downloading assets...")
            image = run_live_generation(
                entity=args.entity,
                username=args.username,
                cols=args.cols,
                rows=args.rows,
                period=args.period,
                api_key=args.api_key,
                api_secret=args.api_secret,
            )

        # Save output
        output_path = os.path.abspath(args.output)
        out_dir = os.path.dirname(output_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        image.save(output_path)

        file_size_kb = os.path.getsize(output_path) / 1024
        print(f"[✓] Collage successfully saved to: {output_path}")
        print(f"[✓] Dimensions: {image.width}x{image.height} px | Size: {file_size_kb:.1f} KB | Mode: {image.mode}")
        return 0

    except Exception as exc:
        print(f"[!] Error generating collage: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
