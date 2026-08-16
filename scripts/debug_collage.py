#!/usr/bin/env python3
"""Unified Debug & Development Runner for lastfm-collage-generator.

Provides zero-build, instant execution and debugging for both:
1. Offline Mock Mode (--mock): 0 network calls, instant synthetic visual rendering.
2. Live API Mode (--live): Real Last.fm queries and web retrieval using .env.
"""

import argparse
import io
import os
import platform
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Tuple, Union

# Ensure src/ is on sys.path for instant, zero-build execution against local source
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_PATH = os.path.join(PROJECT_ROOT, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from lastfmcollagegenerator.constants import (  # noqa: E402
    ENTITIES,
    PERIODS,
    THEMES,
    THEME_DARK,
    OVERLAY_STYLES,
    OVERLAY_BANNER,
)
from lastfmcollagegenerator.theme import Theme, resolve_theme  # noqa: E402


def load_dotenv(env_path: Optional[str] = None) -> Dict[str, str]:
    """Lightweight zero-dependency .env parser.

    Reads key-value pairs from a .env file and sets them in os.environ
    if they are not already defined.
    """
    if env_path is None:
        env_path = os.path.join(PROJECT_ROOT, ".env")

    env_vars: Dict[str, str] = {}
    if not os.path.isfile(env_path):
        return env_vars

    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip()
                # Strip wrapping single or double quotes
                if (val.startswith('"') and val.endswith('"')) or (
                    val.startswith("'") and val.endswith("'")
                ):
                    val = val[1:-1]
                env_vars[key] = val
                if key not in os.environ:
                    os.environ[key] = val
    except Exception as e:
        print(f"[!] Warning: Could not parse .env file: {e}", file=sys.stderr)

    return env_vars


class SyntheticTile:
    """Mock container for synthetic in-memory image tiles."""

    def __init__(self, data: bytes, playcount: int, title: str) -> None:
        self.data = data
        self.playcount = playcount
        self.title = title


def generate_synthetic_tiles(
    count: int, entity: str, tile_width: int = 300, tile_height: int = 300
) -> List[SyntheticTile]:
    """Generates synthetic colored image tiles for fast offline mock rendering."""
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
        ("#588157", "Fern"),
        ("#3D5A80", "Navy"),
        ("#9B5DE5", "Lavender"),
        ("#F15BB5", "Magenta"),
        ("#00BBF9", "Capri"),
        ("#00F5D4", "Aquamarine"),
        ("#E07A5F", "Terracotta"),
        ("#3D405B", "Charcoal"),
        ("#81B29A", "Eton"),
        ("#F2CC8F", "Camel"),
    ]

    tiles: List[SyntheticTile] = []
    for i in range(count):
        bg_color, color_name = palette[i % len(palette)]
        img = Image.new("RGB", (tile_width, tile_height), color=bg_color)
        draw = ImageDraw.Draw(img)

        # Draw decorative geometry proportionally
        margin = max(2, int(tile_width * 0.05))
        draw.rectangle(
            ((margin, margin), (tile_width - margin, tile_height - margin)),
            outline="#FFFFFF",
            width=max(1, int(tile_width * 0.01)),
        )
        inset = max(6, int(tile_width * 0.23))
        draw.ellipse(
            ((inset, inset), (tile_width - inset, tile_height - inset)),
            outline="#FFFFFF",
            width=max(1, int(tile_width * 0.007)),
        )

        with io.BytesIO() as buf:
            img.save(buf, format="PNG")
            img_bytes = buf.getvalue()

        playcount = 1000 - (i * 37)
        if entity == "artist":
            title = f"Artist #{i + 1} ({color_name})"
        elif entity == "track":
            title = f"Artist #{i + 1} - Track #{i + 1}"
        else:
            title = f"Artist #{i + 1} - Album #{i + 1}"

        tiles.append(SyntheticTile(data=img_bytes, playcount=playcount, title=title))
    return tiles


def run_mock_generation(
    entity: str,
    username: str,
    cols: int,
    rows: int,
    period: str,
    show_playcount: bool = True,
    tile_size: Optional[int] = None,
    theme: Union[str, Theme, Dict[str, Any]] = THEME_DARK,
    overlay_style: str = OVERLAY_BANNER,
    show_text: bool = True,
    font_path: Optional[str] = None,
):
    """Renders a collage using local library builder code with synthetic tiles."""
    from unittest.mock import MagicMock
    from lastfmcollagegenerator.collage import (
        CollageBuilderConfig,
        CollageBuilderFactory,
        CollageTile,
    )
    from lastfmcollagegenerator.lastfm.client import LastfmClient

    if tile_size is None:
        max_dim = max(cols, rows)
        if max_dim <= 5:
            resolved_tile_size = 300
        elif max_dim <= 10:
            resolved_tile_size = 150
        else:
            resolved_tile_size = 100
    else:
        resolved_tile_size = tile_size

    resolved_theme = resolve_theme(theme)

    config = CollageBuilderConfig(
        cols=cols,
        rows=rows,
        period=period,
        show_playcount=show_playcount,
        tile_size=resolved_tile_size,
        theme=resolved_theme,
        overlay_style=overlay_style,
        show_text=show_text,
        font_path=font_path,
    )
    mock_client = MagicMock(spec=LastfmClient)
    builder = CollageBuilderFactory(
        entity=entity, config=config, lastfm_client=mock_client
    )
    mock_tiles = generate_synthetic_tiles(
        cols * rows, entity, resolved_tile_size, resolved_tile_size
    )
    collage_tiles = [
        CollageTile(data=t.data, playcount=t.playcount, title=t.title)
        for t in mock_tiles
    ]
    return builder._create_image(collage_tiles, cols, rows)


def run_live_generation(
    entity: str,
    username: str,
    cols: int,
    rows: int,
    period: str,
    api_key: str,
    api_secret: str,
    show_playcount: bool = True,
    tile_size: Optional[int] = None,
    theme: Union[str, Theme, Dict[str, Any]] = THEME_DARK,
    overlay_style: str = OVERLAY_BANNER,
    show_text: bool = True,
    font_path: Optional[str] = None,
):
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
        tile_size=tile_size,
        theme=theme,
        overlay_style=overlay_style,
        show_text=show_text,
        font_path=font_path,
    )


def open_file_in_system_viewer(filepath: str) -> None:
    """Opens a generated file using the operating system's default viewer."""
    try:
        system = platform.system()
        if system == "Darwin":
            subprocess.run(["open", filepath], check=False)
        elif system == "Windows":
            os.startfile(filepath)  # type: ignore[attr-defined]
        else:
            subprocess.run(["xdg-open", filepath], check=False)
    except Exception as e:
        print(f"[!] Could not open viewer: {e}")


def parse_grid_dimension(grid_str: str) -> Tuple[int, int]:
    """Parses grid dimensions like '3x3', '5x5', '3x5' into (cols, rows)."""
    parts = grid_str.lower().split("x")
    if len(parts) != 2:
        raise ValueError(
            f"Invalid grid format '{grid_str}'. Expected format like '3x3' or '4x5'."
        )
    return int(parts[0]), int(parts[1])


def parse_arguments() -> argparse.Namespace:
    """Configures CLI argument parser with environment defaults."""
    env = load_dotenv()

    default_user = env.get("LASTFM_USERNAME", "testuser")
    default_entity = env.get("DEFAULT_ENTITY", "album")
    default_period = env.get("DEFAULT_PERIOD", "7day")
    default_grid = env.get("DEFAULT_GRID", "3x3")
    default_api_key = env.get("LASTFM_API_KEY", "")
    default_api_secret = env.get("LASTFM_API_SECRET", "")

    # Parse default grid if valid
    default_cols, default_rows = 3, 3
    try:
        default_cols, default_rows = parse_grid_dimension(default_grid)
    except Exception:
        pass

    parser = argparse.ArgumentParser(
        description="Unified Debug & Development Runner for lastfm-collage-generator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Mode selection
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--mock",
        action="store_true",
        help="Run offline mock rendering (0 network calls, instant synthetic image)",
    )
    mode_group.add_argument(
        "--live",
        action="store_true",
        help="Run live Last.fm API querying and web retrieval using .env credentials",
    )

    # Collage parameters
    parser.add_argument(
        "-u",
        "--username",
        type=str,
        default=default_user,
        help="Target Last.fm username",
    )
    parser.add_argument(
        "-e",
        "--entity",
        type=str,
        default=default_entity,
        choices=list(ENTITIES),
        help="Entity to collage (album, artist, track)",
    )
    parser.add_argument(
        "-c",
        "--cols",
        type=int,
        default=default_cols,
        help="Grid columns (1 to 20)",
    )
    parser.add_argument(
        "-r",
        "--rows",
        type=int,
        default=default_rows,
        help="Grid rows (1 to 20)",
    )
    parser.add_argument(
        "-g",
        "--grid",
        type=str,
        default=None,
        help="Shorthand grid dimension (e.g. 3x3, 5x5, 10x10) overrides -c and -r",
    )
    parser.add_argument(
        "--tile-size",
        type=int,
        default=None,
        help="Explicit tile size in px (50-600). Defaults to dynamic auto-scaling.",
    )
    parser.add_argument(
        "-p",
        "--period",
        type=str,
        default=default_period,
        choices=list(PERIODS),
        help="Scrobble aggregation period",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Custom destination filepath (default: output/debug_<entity>_<grid>.png)",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Automatically open the generated image in the system viewer",
    )
    parser.add_argument(
        "--theme",
        type=str,
        default=THEME_DARK,
        choices=list(THEMES),
        help="Visual theme preset (dark, light, glassmorphic, sunset, neon)",
    )
    parser.add_argument(
        "--overlay-style",
        type=str,
        default=OVERLAY_BANNER,
        choices=list(OVERLAY_STYLES),
        help="Overlay presentation mode (banner, full_tint, gradient, pill, clean)",
    )
    parser.add_argument(
        "--no-text",
        action="store_true",
        help="Disable all text and overlay rendering (Clean Mode)",
    )
    parser.add_argument(
        "--no-title",
        action="store_true",
        help="Disable title and playcount overlay banners (alias for --no-text)",
    )
    parser.add_argument(
        "--font-path",
        type=str,
        default=None,
        help="Custom .ttf or .otf font file path",
    )

    # API credentials overrides
    parser.add_argument(
        "--api-key",
        type=str,
        default=default_api_key,
        help="Last.fm API Key override",
    )
    parser.add_argument(
        "--api-secret",
        type=str,
        default=default_api_secret,
        help="Last.fm API Secret override",
    )

    return parser.parse_args()


def main() -> int:
    """Main CLI execution flow."""
    args = parse_arguments()

    if args.grid:
        try:
            args.cols, args.rows = parse_grid_dimension(args.grid)
        except ValueError as e:
            print(f"[!] Error: {e}", file=sys.stderr)
            return 1

    # Validate grid bounds
    if not (
        1 <= args.cols <= 20 and 1 <= args.rows <= 20 and args.cols * args.rows <= 400
    ):
        print(
            f"[!] Error: Grid dimensions {args.cols}x{args.rows} "
            f"({args.cols * args.rows} tiles) out of bounds "
            f"(allowed: 1x1 to 20x20, max 400 tiles).",
            file=sys.stderr,
        )
        return 1

    # Determine mode: default to live if credentials exist and --mock not requested
    is_mock = args.mock
    if not args.mock and not args.live:
        if args.api_key and args.api_secret:
            is_mock = False
        else:
            is_mock = True

    # Compute default output path if not specified
    output_path = args.output
    if not output_path:
        out_dir = os.path.join(PROJECT_ROOT, "output")
        mode_prefix = "mock" if is_mock else "live"
        filename = (
            f"debug_{mode_prefix}_{args.entity}_{args.cols}x{args.rows}_"
            f"{args.theme}_{args.overlay_style}.png"
        )
        output_path = os.path.join(out_dir, filename)

    show_text = not (args.no_text or args.no_title)

    mode_label = (
        "OFFLINE MOCK (Synthetic Tiles)" if is_mock else "LIVE API (Last.fm & Retrieval)"
    )
    print("=" * 65)
    print(" 🎵 Last.fm Collage Generator - Debug Runner")
    print("=" * 65)
    print(f" • Mode          : {mode_label}")
    print(f" • Username      : {args.username}")
    print(f" • Entity        : {args.entity.upper()}")
    print(
        f" • Grid Size     : {args.cols} cols x {args.rows} rows "
        f"({args.cols * args.rows} total tiles)"
    )
    print(f" • Period        : {args.period}")
    print(f" • Tile Size     : {args.tile_size if args.tile_size else 'Auto Dynamic'}")
    print(f" • Theme         : {args.theme}")
    print(f" • Overlay Style : {args.overlay_style}")
    print(f" • Show Text     : {'Yes' if show_text else 'No'}")
    print(f" • Output Dest   : {output_path}")
    print("-" * 65)

    start_time = time.perf_counter()

    try:
        if is_mock:
            print("[+] Rendering synthetic mock collage...")
            image = run_mock_generation(
                entity=args.entity,
                username=args.username,
                cols=args.cols,
                rows=args.rows,
                period=args.period,
                show_playcount=True,
                tile_size=args.tile_size,
                theme=args.theme,
                overlay_style=args.overlay_style,
                show_text=show_text,
                font_path=args.font_path,
            )
        else:
            if not args.api_key or not args.api_secret:
                print(
                    "[!] Error: API Key and Secret are required for live mode.\n"
                    "    Provide them in .env or pass --api-key and --api-secret.\n"
                    "    Alternatively, pass --mock to run in offline mock mode.",
                    file=sys.stderr,
                )
                return 1

            print(
                f"[+] Querying Last.fm API for '{args.username}' "
                f"({args.entity} / {args.period})..."
            )
            image = run_live_generation(
                entity=args.entity,
                username=args.username,
                cols=args.cols,
                rows=args.rows,
                period=args.period,
                api_key=args.api_key,
                api_secret=args.api_secret,
                show_playcount=True,
                tile_size=args.tile_size,
                theme=args.theme,
                overlay_style=args.overlay_style,
                show_text=show_text,
                font_path=args.font_path,
            )

        elapsed = time.perf_counter() - start_time

        # Ensure output directory exists
        abs_output_path = os.path.abspath(output_path)
        os.makedirs(os.path.dirname(abs_output_path), exist_ok=True)
        image.save(abs_output_path)

        file_size_kb = os.path.getsize(abs_output_path) / 1024
        print("-" * 65)
        print(f"[✓] SUCCESS! Collage generated in {elapsed:.2f} seconds")
        print(f"[✓] Dimensions : {image.width}x{image.height} px")
        print(f"[✓] File Size  : {file_size_kb:.1f} KB")
        print(f"[✓] Saved to   : {abs_output_path}")
        print("=" * 65)

        if args.open:
            print("[+] Opening generated collage in system image viewer...")
            open_file_in_system_viewer(abs_output_path)

        return 0

    except Exception as exc:
        elapsed = time.perf_counter() - start_time
        print(f"\n[!] Error occurred after {elapsed:.2f}s: {exc}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
