<div align="center">

# 🎵 lastfm-collage-generator

**Production-grade Python library for generating high-resolution visual composite image collages from Last.fm scrobble histories.**

[![PyPI version](https://img.shields.io/pypi/v/lastfmcollagegenerator?color=blue&logo=pypi)](https://pypi.org/project/lastfmcollagegenerator/)
[![Python Versions](https://img.shields.io/pypi/pyversions/lastfmcollagegenerator?logo=python)](https://pypi.org/project/lastfmcollagegenerator/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](https://img.shields.io/badge/mypy-checked-blue.svg)](http://mypy-lang.org/)
[![Downloads](https://img.shields.io/pypi/dm/lastfmcollagegenerator?color=orange)](https://pypi.org/project/lastfmcollagegenerator/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/paurieraf/lastfm-collage-generator/pulls)

[Key Features](#-key-features) • [Grid Geometry](#-grid-dimensions--geometry-reference) • [Architecture](#-system-architecture--design-patterns) • [Installation](#-installation) • [Quickstart](#-quickstart) • [API Reference](#-python-api-reference) • [Developer Workflows](#-developer--debugging-workflows) • [Testing & QA](#-testing--quality-assurance) • [Caching & Social Presets](#-caching-social-presets--tile-geometry) • [GitHub Actions](#-github-actions-automation) • [Roadmap](#-multi-phase-feature-roadmap) • [Defect Catalog](#-known-bugs--defect-catalog) • [Contributing](#-contributing)

</div>

---

## ✨ Key Features

- **Multi-Entity Composite Grids**:
  - 💿 **Top Albums (`album`)**: Queries user scrobble history via the Last.fm Audioscrobbler REST API (`pylast`), downloads album cover artwork, and composites them into an aligned matrix.
  - 🎤 **Top Artists (`artist`)**: Fetches top artists via the API and fetches high-resolution artist hero imagery directly from `https://www.last.fm/music/<artist>` (bypassing the historical deprecation of artist images in the Last.fm API), thumbnails images to 300x300px, and composites the grid.
  - 🎵 **Top Tracks (`track`)**: Queries top tracks, resolves associated album artwork or applies solid black fallbacks, and renders the composite.
- **Configurable Grid Geometry**: Generates rectangular or square grids from `1x1` up to `5x5` (e.g. `3x3` standard 9-tile grid, `5x5` 25-tile poster, or asymmetric `3x5`). Standard tile resolution is `300 x 300` pixels.
- **Comprehensive Time Horizons**: Full support for all Last.fm aggregation periods: `7day` (Weekly), `1month` (Monthly), `3month` (Quarterly), `6month` (Semi-Annual), `12month` (Yearly), and `overall` (All-Time).
- **Translucent Monospace Typography Banners**: Renders a dark translucent banner overlay (`RGBA(0, 0, 0, 123)`) on the bottom 65px of each tile displaying entity name, artist, and scrobble playcount in bundled TrueType monospace font (`DejaVuSansMono.ttf`).
- **Concurrent Image Acquisition**: Utilizes Python's `concurrent.futures.ThreadPoolExecutor` for parallel, non-blocking downloads of artwork assets across worker threads.
- **Resilient Fallback Handling**: Gracefully handles missing artwork, HTTP 404s, or network timeouts by rendering solid black `300x300` blank tiles without failing the entire collage generation process.
- **Zero External System Dependencies**: TrueType fonts are bundled directly in the distribution package and loaded dynamically relative to module path.
- **Modern Tooling & Developer Experience**: Built with [uv](https://docs.astral.sh/uv/) and `hatchling`, featuring offline synthetic mock debugging runners, VS Code F5 launch profiles, and 100% offline pytest fixtures.

---

## 📐 Grid Dimensions & Geometry Reference

The library supports arbitrary square and rectangular grids from **$1 \times 1$ up to $20 \times 20$** (up to 400 tiles), with **dynamic resolution auto-scaling** and configurable tile sizes:

| Grid Size | Total Tiles | Default Tile Resolution | Canvas Dimensions | Aspect Ratio | Megapixels | Typical Use Case |
|---|---|---|---|---|---|---|
| **`1x1`** | 1 tile | 300 x 300 px | **300 x 300 px** | 1:1 Square | 0.09 MP | Single item avatar / badge |
| **`3x3`** | 9 tiles | 300 x 300 px | **900 x 900 px** | 1:1 Square | 0.81 MP | Standard social media card (#LastFmFriday, Instagram) |
| **`5x5`** | 25 tiles | 300 x 300 px | **1500 x 1500 px** | 1:1 Square | 2.25 MP | Classic weekly / monthly listening card |
| **`8x8`** | 64 tiles | 150 x 150 px *(Auto)* | **1200 x 1200 px** | 1:1 Square | 1.44 MP | Detailed monthly recap poster |
| **`10x10`** | 100 tiles | 150 x 150 px *(Auto)* | **1500 x 1500 px** | 1:1 Square | 2.25 MP | High-density 100-album annual overview |
| **`20x20`** | 400 tiles | 100 x 100 px *(Auto)* | **2000 x 2000 px** | 1:1 Square | 4.00 MP | Comprehensive mega-recap poster |
| **`3x10`** | 30 tiles | 150 x 150 px *(Auto)* | **450 x 1500 px** | 3:10 Portrait | 0.68 MP | Mobile sidebar / Story banner |
| **`12x6`** | 72 tiles | 100 x 100 px *(Auto)* | **1200 x 600 px** | 2:1 Landscape | 0.72 MP | Ultra-wide desktop banner |

### Dynamic Resolution Auto-Scaling Tiers

To keep memory footprint safe and execution fast without sacrificing visual detail:
- **Standard Density ($\le 5 \times 5$)**: Defaults to **300x300 px** per tile.
- **Medium Density ($6 \times 6$ to $10 \times 10$)**: Automatically scales to **150x150 px** per tile.
- **High Density ($> 10 \times 10$, up to $20 \times 20$)**: Automatically scales to **100x100 px** per tile.
- **Custom Resolution**: Explicitly supply `tile_size` (between 50 and 600 px) to override automatic scaling.

### Proportional Tile Layout Anatomy

Overlay typography and dark translucent banners automatically scale proportionally with tile size:

```
(x, y) ┌──────────────────────────────────────────────────────────────┐
       │                                                              │
       │                   Tile Cover Artwork                         │
       │                 (Downloaded or Retrieved)                      │
       │                   (S x S px, e.g. 300px)                     │
       │                                                              │
y+h_0  ├──────────────────────────────────────────────────────────────┤ ◄── Banner Top: y + (S - h_banner)
       │ Translucent Dark Banner: RGBA(0, 0, 0, 123)                  │
y+y_t  │ Monospace Typography: DejaVuSansMono.ttf (Proportional Font) │ ◄── Text Origin: x + pad_x, y_0 + pad_y
       │ "Artist Name - Album / Track Title. (42 scrobbles)"          │
(x+S,  │                                                              │
  y+S) └──────────────────────────────────────────────────────────────┘ ◄── Tile Bottom (y + S)
```

---

## 🏗️ System Architecture & Design Patterns

The library strictly implements a 4-layer object-oriented design: **Facade → Factory → Builder → Client Adapter**.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Client / Consumer Application                      │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 1. Facade Layer: CollageGenerator (src/collage_generator.py)           │
│    - Encapsulates LastfmConfig (API key and API secret)                 │
│    - Validates grid bounds (1 <= cols/rows <= 5), entity, and period    │
│    - Dispatches generation request to CollageBuilderFactory             │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 2. Factory Layer: CollageBuilderFactory (src/collage.py)                │
│    - Inspects entity string ("album", "artist", "track")                │
│    - Instantiates and returns the corresponding concrete Builder        │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        │                            │                            │
        ▼                            ▼                            ▼
┌───────────────────────┐  ┌───────────────────────┐  ┌───────────────────────┐
│  AlbumCollageBuilder  │  │  ArtistCollageBuilder │  │  TrackCollageBuilder  │
│  - Queries pylast     │  │  - Queries pylast     │  │  - Queries pylast     │
│  - Downloads cover art│  │  - Fetches Last.fm DOM│  │  - Resolves album art │
└───────────┬───────────┘  └───────────┬───────────┘  └───────────┬───────────┘
            │                          │                          │
            └──────────────────────────┼──────────────────────────┘
                                       │ Inherits
                                       ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 3. Builder Layer: BaseCollageBuilder (src/collage.py)                   │
│    - Template Method create(username):                                  │
│      1. _get_tiles_from_top_items() -> Parallel ThreadPoolExecutor      │
│      2. _create_image() -> Pillow RGB canvas allocation & tile pasting  │
│      3. _insert_tile_title() -> Translucent RGBA banner overlay         │
│    - Font loading (DejaVuSansMono.ttf) & text wrapping                  │
│    - Solid black (300x300) fallback tile generator                      │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 4. Client Adapter Layer: LastfmClient (src/lastfm/client.py)            │
│    - Wraps pylast.LastFMNetwork, isolating API network credentials      │
│    - Exposes get_user(), get_top_albums(), get_top_artists(),           │
│      and get_top_tracks()                                               │
└─────────────────────────────────────────────────────────────────────────┘
```

### Module Responsibilities Matrix

| Module | Component | Pattern / Architectural Role | Key Responsibilities |
|---|---|---|---|
| `collage_generator.py` | `CollageGenerator` | **Facade** | Public API entrypoint; credential management; input parameter boundary validation. |
| `collage.py` | `CollageBuilderFactory` | **Factory** | Dispatches concrete builder instances based on `entity` string key. |
| `collage.py` | `BaseCollageBuilder` | **Base Builder / Template Method** | Canvas lifecycle; concurrent worker pool; coordinate math; text wrapping; banner overlays. |
| `collage.py` | `AlbumCollageBuilder` | **Concrete Builder** | Fetches top albums via `pylast`; downloads cover images from Last.fm CDN. |
| `collage.py` | `ArtistCollageBuilder` | **Concrete Builder** | Fetches `last.fm/music/<artist>` DOM for `.header-new-background-image`; thumbnails to 300x300px. |
| `collage.py` | `TrackCollageBuilder` | **Concrete Builder** | Fetches top tracks; inherits album cover extraction and fallback mechanics. |
| `lastfm/client.py` | `LastfmClient` | **Client Adapter** | Wraps `pylast.LastFMNetwork` calls; isolates third-party API types from core builders. |
| `constants.py` | `ENTITIES`, `PERIODS` | **Domain Constants** | Defines supported entity tuples and Last.fm aggregation horizons. |
| `exceptions.py` | `ArtistNotFound`, etc. | **Exception Hierarchy** | Custom domain errors for missing artists or unresolvable artwork. |

---

## 📦 Installation

### Using `uv` (Recommended)

```bash
uv add lastfmcollagegenerator
```

### Using `pip`

```bash
pip install lastfmcollagegenerator
```

### Using `pipx` (Standalone execution)

```bash
pipx install lastfmcollagegenerator
```

### Runtime Requirements

- **Python**: `>= 3.8` (Fully tested and verified on Python 3.8, 3.9, 3.10, 3.11, and 3.12).
- **Core Dependencies**: `Pillow >= 10.4.0`, `pylast >= 5.3.0`, `requests >= 2.32.3`, `beautifulsoup4 >= 4.12.3`, `html5lib >= 1.1`.
- **Last.fm API Account**: Free API Key & Secret obtained from the [Last.fm API Account Creation Page](https://www.last.fm/api/account/create).

---

## 🚀 Quickstart

Create and save a high-resolution 3x3 album collage in just a few lines of Python:

```python
from lastfmcollagegenerator.collage_generator import CollageGenerator

# 1. Initialize the generator with your Last.fm API credentials
generator = CollageGenerator(
    lastfm_api_key="YOUR_LASTFM_API_KEY",
    lastfm_api_secret="YOUR_LASTFM_API_SECRET"
)

# 2. Generate a 3x3 album collage for the past 7 days (returns a PIL.Image object)
image = generator.generate(
    entity="album",
    username="your_lastfm_username",
    cols=3,
    rows=3,
    period="7day",
)

# 3. Save the resulting composite image to disk
image.save("my_weekly_collage.png", format="PNG")
print(f"Collage saved successfully! Canvas size: {image.width}x{image.height}px")

# 4. Or generate directly using dedicated convenience methods
album_collage = generator.generate_top_albums_collage(
    username="your_lastfm_username", cols=5, rows=5, period="7day"
)
artist_collage = generator.generate_top_artists_collage(
    username="your_lastfm_username", cols=3, rows=3, period="overall"
)
track_collage = generator.generate_top_tracks_collage(
    username="your_lastfm_username", cols=4, rows=4, period="1month"
)
```

---

## 📖 Python API Reference

### `CollageGenerator`
`lastfmcollagegenerator.collage_generator.CollageGenerator`

The primary public entrypoint and facade for configuring and executing collage creation.

#### Constructor

```python
CollageGenerator(lastfm_api_key: str, lastfm_api_secret: str)
```

**Parameters**:
- **`lastfm_api_key`** (`str`): Valid Last.fm Audioscrobbler REST API key.
- **`lastfm_api_secret`** (`str`): Valid Last.fm API secret.

---

#### Method: `generate()`

```python
def generate(
    self,
    entity: str,
    username: str,
    cols: int,
    rows: int,
    period: str = "overall",
    tile_size: Optional[int] = None,
    theme: Union[str, Theme, Dict[str, Any]] = "dark",
    overlay_style: str = "banner",
    show_text: bool = True,
    font_path: Optional[str] = None
) -> PIL.Image.Image
```

Generates a composite image collage for the specified entity and time horizon.

**Parameter Matrix**:

| Parameter | Type | Allowed Values | Default | Description |
|---|---|---|---|---|
| **`entity`** | `str` | `"album"`, `"artist"`, `"track"` | *Required* | Type of Last.fm listening entity to composite. |
| **`username`** | `str` | Any valid Last.fm username string | *Required* | The target Last.fm user account. |
| **`cols`** | `int` | `1 <= cols <= 20` | *Required* | Number of horizontal grid columns. |
| **`rows`** | `int` | `1 <= rows <= 20` | *Required* | Number of vertical grid rows (max 400 total tiles). |
| **`period`** | `str` | `"7day"`, `"1month"`, `"3month"`, `"6month"`, `"12month"`, `"overall"` | `"overall"` | Scrobble aggregation time window. |
| **`tile_size`** | `Optional[int]` | `50 <= tile_size <= 600` | `None` *(Auto)* | Explicit tile dimension in px. If `None`, dynamically auto-scaled. |
| **`theme`** | `Union[str, Theme, dict]` | `"dark"`, `"light"`, `"glassmorphic"`, `"sunset"`, `"neon"`, or custom `Theme` | `"dark"` | Visual color scheme for overlay banners and typography. |
| **`overlay_style`** | `str` | `"banner"`, `"full_tint"`, `"gradient"`, `"pill"`, `"clean"` | `"banner"` | Overlay visual presentation layout mode. |
| **`show_text`** | `bool` | `True`, `False` | `True` | Whether to render title and playcount overlays. |
| **`font_path`** | `Optional[str]` | Filesystem path to `.ttf`/`.otf` | `None` | Custom font file path override. |

**Returns**:
- `PIL.Image.Image`: An allocated Pillow 24-bit RGB raster canvas with dimensions `(cols * tile_size, rows * tile_size)` pixels.

**Exceptions Raised**:
- `ValueError`: If `entity` is not in `ENTITIES`, `period` is not in `PERIODS`, `cols`/`rows` are outside `1..20`, total tiles exceed 400, `tile_size` is outside `50..600`, or `theme`/`overlay_style` are invalid.
- `TypeError`: If `cols`, `rows`, or `tile_size` are not integers, or parameter types are invalid.
- `FileNotFoundError`: If custom `font_path` does not exist on disk.
- `pylast.WSError`: If Last.fm API authentication fails or the requested username does not exist.
- `pylast.NetworkError`: If network connection to Last.fm API endpoints cannot be established.

---

#### Convenience Methods

For intuitive syntax, `CollageGenerator` provides dedicated helper methods:

```python
# Generate Top Albums Collage (3x3, last 7 days)
album_collage = generator.generate_top_albums_collage(
    username="rj",
    cols=3,
    rows=3,
    period="7day"
)

# Generate High-Density Top Artists Collage (10x10, monthly, auto 150px tiles)
artist_collage = generator.generate_top_artists_collage(
    username="rj",
    cols=10,
    rows=10,
    period="1month"
)

# Generate Custom High-Res Top Tracks Collage (4x3, overall history, explicit 300px tiles)
track_collage = generator.generate_top_tracks_collage(
    username="rj",
    cols=4,
    rows=3,
    period="overall",
    tile_size=300
)
```

---

### Safe Image Export with `export_image()`

The library provides a built-in `export_image()` utility (also available as `CollageGenerator.export_image()`) that safely handles format inference, quality settings, directory creation, and automatic RGBA-to-RGB background flattening for JPEG:

```python
from lastfmcollagegenerator import export_image, CollageGenerator

generator = CollageGenerator("YOUR_API_KEY", "YOUR_API_SECRET")
image = generator.generate(entity="album", username="user", cols=3, rows=3, period="7day")

# 1. Automatic format inference & directory creation
export_image(image, "output/weekly_recap.png")

# 2. Modern WebP export with optimized quality (default quality=85)
export_image(image, "output/weekly_recap.webp")

# 3. Safe JPEG export (automatically flattens alpha channel onto black background to prevent crashes)
export_image(image, "output/weekly_recap.jpg", quality=90)
```

---

### Working with Returned `PIL.Image` Objects

The returned object is a standard Pillow `PIL.Image.Image` instance, offering full flexibility for saving, converting, streaming, or displaying:

```python
import io
from lastfmcollagegenerator.collage_generator import CollageGenerator

generator = CollageGenerator("YOUR_API_KEY", "YOUR_API_SECRET")
image = generator.generate(entity="album", username="user", cols=3, rows=3, period="7day")

# 1. Save as Lossless PNG
image.save("collage.png", format="PNG")

# 2. Save as Optimized JPEG with custom compression quality
image.convert("RGB").save("collage.jpg", format="JPEG", quality=90, optimize=True)

# 3. Save as Modern WebP (reduces size by 60-80% relative to PNG)
image.save("collage.webp", format="WEBP", quality=85)

# 4. Extract In-Memory Binary Buffer (for FastAPI / Flask / Discord Bot responses)
buffer = io.BytesIO()
image.save(buffer, format="PNG")
buffer.seek(0)
raw_bytes = buffer.getvalue()

# 5. Generate a Thumbnail / Downscaled Version
thumbnail = image.copy()
thumbnail.thumbnail((450, 450))
thumbnail.save("collage_thumbnail.png")

# 6. Display inline within Jupyter / IPython Notebooks
display(image)
```

---

### Error Handling & Exception Management

```python
from lastfmcollagegenerator.collage_generator import CollageGenerator
from lastfmcollagegenerator.exceptions import ArtistNotFound, ArtistImageNotFound
import pylast

generator = CollageGenerator(
    lastfm_api_key="your_api_key",
    lastfm_api_secret="your_api_secret"
)

try:
    image = generator.generate(
        entity="album",
        username="some_lastfm_user",
        cols=3,
        rows=3,
        period="7day"
    )
    image.save("collage.png")
except ValueError as e:
    print(f"Validation error (invalid parameters): {e}")
except pylast.WSError as e:
    print(f"Last.fm API Service error: {e}")
except pylast.NetworkError as e:
    print(f"Network connectivity error: {e}")
except (ArtistNotFound, ArtistImageNotFound) as e:
    print(f"Artist retrieval warning: {e}")
except Exception as e:
    print(f"Unexpected error during collage generation: {e}")
```

---

## 🛠️ Developer & Debugging Workflows

The repository includes a comprehensive zero-build development runner (`scripts/debug_collage.py`) and preconfigured debug profiles.

### 1. Offline Mock Mode (0 Network Calls / Instant Rendering)

Generates synthetic in-memory colored tiles with geometric artwork to test Pillow canvas allocation, font rendering, coordinate math, and text wrapping instantly without API keys or an internet connection:

```bash
# Generate 3x3 mock album collage
uv run python scripts/debug_collage.py --mock -g 3x3

# Generate 5x5 mock artist collage and automatically open in system viewer
uv run python scripts/debug_collage.py --mock -e artist -g 5x5 --open

# Generate asymmetric 3x5 track collage without playcount banners
uv run python scripts/debug_collage.py --mock -e track -c 3 -r 5 --no-title -o output/mock_track.png
```

### 2. Live Last.fm Mode with `.env` Configuration

Configure credentials once in a `.env` file:

```bash
cp .env.example .env
```

```dotenv
# .env
LASTFM_API_KEY=your_api_key_here
LASTFM_API_SECRET=your_api_secret_here
LASTFM_USERNAME=your_username_here
```

Execute live queries:

```bash
# Run live generation using .env credentials and username
uv run python scripts/debug_collage.py --live

# Customize entity, period, grid size, and open viewer
uv run python scripts/debug_collage.py --live -e artist -g 4x4 -p 1month --open

# Override username or period on the fly
uv run python scripts/debug_collage.py --live -u different_user -e track -p overall
```

### 3. Debug Runner CLI Options Reference

| Flag | Short | Type | Default | Description |
|---|---|---|---|---|
| `--mock` | | `flag` | `False` | Run offline with synthetic colored tiles (0 network calls). |
| `--live` | | `flag` | `False` | Run live Last.fm API queries and web retrieval. |
| `--username` | `-u` | `str` | `.env` / `testuser` | Target Last.fm username. |
| `--entity` | `-e` | `str` | `album` | Musical entity: `album`, `artist`, `track`. |
| `--grid` | `-g` | `str` | `3x3` | Shorthand grid dimension (e.g. `3x3`, `5x5`, `4x3`, `3x5`). |
| `--cols` / `--rows` | `-c` / `-r` | `int` | `3` / `3` | Explicit column and row counts (`1` to `5`). |
| `--period` | `-p` | `str` | `7day` | Aggregation period (`7day`, `1month`, `3month`, `6month`, `12month`, `overall`). |
| `--output` | `-o` | `str` | `output/...` | Custom destination PNG filepath. |
| `--open` | | `flag` | `False` | Automatically open result in default operating system image viewer. |
| `--no-title` | | `flag` | `False` | Disable title and playcount overlay banners. |
| `--api-key` | | `str` | `.env` / `""` | Last.fm API Key override. |
| `--api-secret` | | `str` | `.env` / `""` | Last.fm API Secret override. |

### 4. VS Code F5 Breakpoint Debugging

The repository includes preconfigured `.vscode/launch.json` debug profiles:
- `🎨 Debug: Mock Album Collage (3x3)`: Step through Pillow rendering offline.
- `🎨 Debug: Mock Artist Collage (5x5)`: Step through 5x5 multi-row rendering.
- `🌐 Debug: Live Album Collage (.env)`: Step through live Last.fm API calls.
- `🌐 Debug: Live Artist Collage (.env)`: Step through web retrieval pipeline.
- `🎵 Debug: Live Track Collage (.env)`: Step through track cover fallbacks.
- `🧪 Debug: Current Test File (Pytest)`: Step through active test cases.

### 5. Local Editable Installation for Consumer Applications

If you are developing a consuming application (e.g. a Discord bot or web service) alongside this library:

```bash
# In your consumer application's virtual environment:
uv pip install -e /path/to/lastfm-collage-generator
# or
pip install -e /path/to/lastfm-collage-generator
```

Any edits made inside `src/` are immediately active in the consumer application without reinstalling.

---

## 🧪 Testing & Quality Assurance

The project enforces a **zero live network calls** policy for automated tests. All tests execute 100% offline using synthetic in-memory fixtures.

### Running the Pytest Suite

```bash
# Run all unit and integration tests
uv run pytest tests/ -v

# Run with line and branch coverage report
uv run pytest --cov=lastfmcollagegenerator --cov-report=term-missing tests/

# Enforce minimum 90% coverage quality gate
uv run pytest --cov=lastfmcollagegenerator --cov-fail-under=90 tests/
```

### Static Analysis & Linters

```bash
# Lint code syntax and PEP 8 compliance
uv run flake8 src/ tests/

# Verify Black code formatting
uv run black --check src/ tests/

# Run static type checking
uv run mypy src/
```

### Unified QA Runner Skill

Execute the entire QA pipeline with a single command:

```bash
uv run python .gemini/skills/poetry-test-runner/scripts/run_tests.py --all
```

---

## 📦 Packaging & Publishing to PyPI

The package is built and published using `uv` with the `hatchling` build backend.

### 1. Build Distribution Artifacts

Always ensure only clean, current release artifacts exist in `dist/` prior to building:

```bash
# Clean previous build artifacts
rm -rf dist/

# Build source distribution (.tar.gz) and binary wheel (.whl)
uv build
```

### 2. Configure PyPI Authentication

`uv publish` authenticates automatically using the `UV_PUBLISH_TOKEN` environment variable or standard `~/.pypirc` / `~/.netrc` config:

- **Shell profile (`~/.zshrc`)**:
  ```bash
  export UV_PUBLISH_TOKEN="pypi-AgEI..."
  ```
- **Project `.env`**:
  ```dotenv
  UV_PUBLISH_TOKEN=pypi-AgEI...
  ```
- **Global `~/.pypirc`**:
  ```ini
  [distutils]
  index-servers = pypi

  [pypi]
  username = __token__
  password = pypi-AgEI...
  ```

### 3. Publish to PyPI

```bash
# Publish built release to PyPI
uv publish
```

---

## 🗃️ Caching, Social Presets & Tile Geometry

### Multi-Tier Artwork Caching

Artwork is cached across two tiers: an in-memory LRU store (256 entries) and a persistent SQLite cache at `~/.cache/lastfm-collage/artwork.db`. Album/track covers expire after 30 days, retrieved artist hero images after 7 days. On every cache hit, no HTTP request is issued.

```python
generator.generate(
    entity="album",
    username="your_username",
    cols=5,
    rows=5,
    cache_dir="/custom/cache/dir",  # Default: ~/.cache/lastfm-collage/
    cache_ttl_override=14,          # Override TTL (days) for all artwork kinds
    rate_limit=10,                  # HTTP requests per second (default 5.0)
)
```

All HTTP acquisition flows through a resilience middleware: a token-bucket rate limiter, exponential backoff with full jitter on transient errors, and a per-host circuit breaker. Unavailable artwork falls back to a deterministic algorithmic gradient tile (SHA-256-derived pastel gradient + initials) instead of a black square; pass `fallback_style="black"` for the legacy solid tile.

### Social Media Dimension Presets

One-click output sizing for common platforms. When a preset is set it overrides `cols`, `rows` and `tile_size`, and letterboxed regions are filled with an acrylic backdrop (Gaussian-blurred, darkened rendition of your #1 artwork):

```python
generator.generate(
    entity="album",
    username="your_username",
    cols=5,
    rows=5,
    preset="instagram-story",
)
```

| Preset | Dimensions | Grid |
|---|---|---|
| `instagram-story` | 1080 × 1920 (9:16) | 3×5 @ 360px |
| `instagram-post` | 1080 × 1080 (1:1) | 3×3 @ 360px |
| `twitter-header` | 1500 × 500 (3:1) | 5×1 @ 300px |
| `desktop-wallpaper` | 1920 × 1080 (16:9) | 6×3 @ 320px |
| `desktop-wallpaper-4k` | 3840 × 2160 (16:9) | 6×3 @ 600px |

### Tile Geometry

Rounded corners, border strokes and inter-tile spacing are available with defaults preserving the classic edge-to-edge look:

```python
generator.generate(
    entity="album",
    username="your_username",
    cols=3,
    rows=3,
    corner_radius=12,
    border_width=3,
    border_color="#FF5A5F",
    spacing=8,
)
```

---

## 🤖 GitHub Actions Automation

The repository ships a reusable composite action (`action.yml`) that generates a collage inside a workflow and writes it into the repository — ideal for keeping a GitHub profile README fresh with weekly listening recaps.

**Inputs:** `username` (required), `entity`, `cols`, `rows`, `period`, `output-path`, `mock`, `api-key`, `api-secret`.

```yaml
name: Weekly Last.fm Recap
on:
  schedule:
    - cron: "0 9 * * 1"
  workflow_dispatch:

permissions:
  contents: write

jobs:
  recap:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Generate weekly collage
        uses: paurieraf/lastfm-collage-generator@v0.8.0
        with:
          username: ${{ secrets.LASTFM_USERNAME }}
          entity: album
          cols: "5"
          rows: "5"
          period: 7day
          output-path: weekly-recap.png
          api-key: ${{ secrets.LASTFM_API_KEY }}
          api-secret: ${{ secrets.LASTFM_API_SECRET }}
      - name: Commit updated collage
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add weekly-recap.png
          git commit -m "chore: update weekly Last.fm recap" || echo "No changes"
          git push
```

See [`.github/workflows/weekly-recap.yml.example`](.github/workflows/weekly-recap.yml.example) for a ready-to-copy workflow. Set `mock: "true"` to validate workflows without Last.fm credentials.

---

## 🔤 Font Handling & Asset Packaging
The library bundles official TrueType fonts directly inside the distribution package at `src/lastfmcollagegenerator/fonts/`:
- **`DejaVuSansMono.ttf`** (340 KB): Default monospace font for tile title and playcount rendering.
- **`DejaVuSansMono-Bold.ttf`** (332 KB): Bold monospace font variant.

Fonts are loaded dynamically relative to the package directory (`os.path.dirname(__file__)`), ensuring zero dependencies on host system fonts across macOS, Linux, and containerized Docker environments. Assets are declared in `MANIFEST.in` via `recursive-include src/lastfmcollagegenerator/fonts *.ttf`.

---

## 🗺️ Multi-Phase Feature Roadmap

Our development roadmap is organized across 4 strategic pillars and versioned milestones:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       STRATEGIC ROADMAP PILLARS                             │
├───────────────────────┬─────────────────────────┬───────────────────────────┤
│ 1. Visual Styling     │ 2. Performance, Caching │ 3. Advanced Layouts       │ 4. Ecosystem &
│    & Custom Themes    │    & Resilience         │    & Modern Formats       │    CLI Integrations
└───────────────────────┴─────────────────────────┴───────────────────────────┘
```

### 🎨 Pillar 1: Visual Styling & Custom Themes

- **Phase 1 (v0.5.0 — Immediate Stability)**:
  - [x] Correct multi-row overlay geometry bug (`y_1 = y + self.TILE_HEIGHT`).
  - [x] Implement `generate_top_albums_collage()`, `generate_top_artists_collage()`, `generate_top_tracks_collage()` convenience methods on `CollageGenerator`.
  - [x] Implement strict lower boundary validation (`1 <= cols <= 5`, `1 <= rows <= 5`).
  - [x] Author comprehensive 100% offline pytest suite (>90% coverage).
- **Phase 2 (v0.6.0 — Visual Personalization)**:
  - [x] **Dynamic Theme Engine**: Pre-packaged themes (`Dark`, `Light`, `Glassmorphic`, `Sunset`, `Neon`, and custom user hex palettes/Theme objects).
  - [x] **Typography & Auto-Scaling Engine**: Word-boundary line breaking via `textwrap`, dynamic font downscaling for long titles, and custom `.ttf`/`.otf` font path support.
  - [x] **Tile Geometry & Rounded Corners**: Rounded squircle corner masking (`radius=12`), configurable border stroke widths and colors, and inter-tile spacing margins.
  - [x] **Versatile Overlay Styles**: `Banner` (lower third), `Full Tint` (centered text), `Gradient Fade`, `Minimalist Badge / Pill` (rank + playcount chip), and `Clean Mode` (`show_text=False` for pure artwork grids).

### ⚡ Pillar 2: Performance, Caching & Retrieval Resilience

- **Phase 2 (v0.6.0 — Fallbacks & Determinism)**:
  - [x] **Dynamic Fallback Artwork Engine**: Algorithmic two-color pastel gradients and initials typography derived from SHA-256 entity hashes to replace solid black tiles.
  - [x] **Deterministic Secondary Sorting**: Secondary sort key `(int(playcount), title)` to ensure byte-for-byte identical collages on tied scrobble counts.
- **Phase 3 (v0.7.0 — Caching & Network Resilience)**:
  - [x] **Multi-Tier Caching Subsystem**: Tier-1 in-memory LRU cache (`maxsize=256`) + Tier-2 SQLite persistent disk cache (`~/.cache/lastfm-collage/`) with 30-day TTL for album covers and 7-day TTL for retrieved artist hero images.
  - [x] **Network Resilience Middleware**: Token-bucket rate limiter (5 req/sec), exponential backoff with full jitter for transient HTTP errors, and circuit breaker for web retrieval fallbacks.
- **Phase 4 (v1.0.0 — Asynchronous Architecture)**:
  - [x] **Native AsyncIO Pipeline**: Non-blocking concurrent asset acquisition via `httpx` (`async def generate_async()`) with async semaphore concurrency throttling.

### 📐 Pillar 3: Advanced Layouts & Modern Formats

- **Phase 2 (v0.6.0 — High-Density Grids)**:
  - [x] **Arbitrary $N \times M$ Matrix Grids**: Expand grid size beyond `5x5` (up to `20x20`, max 400 tiles) with dynamic resolution auto-scaling (300px $\to$ 150px $\to$ 100px), configurable explicit tile sizes, and proportional typography.
- **Phase 3 (v0.7.0 — Social Presets & Backdrop Decorators)**:
  - [x] **Social Media Dimension Presets**: One-click generation for Instagram Story (`9:16` $1080\times1920$), Instagram Post (`1:1` $1080\times1080$), Twitter Header (`3:1` $1500\times500$), and Desktop Wallpaper (`16:9` $1920\times1080$ / 4K).
  - [x] **Acrylic Backdrop Blur**: Automatically fill non-square letterboxing with an acrylic Gaussian-blurred backdrop derived from the user's #1 top artwork.
- **Phase 4 (v1.0.0 — Modern Formats & Asymmetric Grids)**:
  - [ ] **Modern Export Formats**: Direct export to WebP (lossy/lossless), SVG vector containers with crisp `<text>` nodes, and 300 DPI print-ready PDF posters.
  - [ ] **Asymmetrical Layout Strategies**: `Hero Grid` (#1 item in $2\times2$ block, surrounded by $1\times1$ and $0.5\times0.5$ tiles), `Bento Box` editorial grids, and `Honeycomb Hexagon` tessellations.
- **Phase 5 (v1.1.0 — Motion Recaps)**:
  - [ ] **Animated Transitions**: Generate animated GIF / MP4 listening recaps smoothly crossfading across time horizons (`7day` $\to$ `1month` $\to$ `3month` $\to$ `12month`).

### 🌐 Pillar 4: Ecosystem & CLI Integrations

- **Phase 2 (v0.6.0 — Standalone CLI)**:
  - [ ] **Rich CLI Tool (`lastfm-collage`)**: Global console script with rich terminal UI, colorized progress bars, download speed metrics, and ASCII art terminal previews.
- **Phase 3 (v0.8.0 — GitHub Actions Automation)**:
  - [x] **GitHub Profile README Action (`action.yml`)**: Automated scheduled workflow updating developer GitHub Profile READMEs with weekly listening recaps on cron.
- **Phase 5 (v1.1.0 - v1.2.0 — Web Services & Chatbots)**:
  - [ ] **FastAPI Microservice Wrapper**: Containerized REST API with OpenAPI docs and binary image streaming endpoints (`GET /api/v1/collage`).
  - [ ] **Discord, Telegram & Slack Bot Connectors**: Slash commands (`/collage`), user account binding, and direct embed image attachments.

---

## 🐛 Known Bugs & Defect Catalog

The following known defects in legacy versions (`<= 0.4.13`) have been diagnosed with root causes and remediation:

| Defect ID | Component | Severity | Description & Root Cause | Resolution Status |
|---|---|---|---|---|
| **BUG-01** | `collage.py:126-130` | **Critical** | **Multi-Row Overlay Coordinate Drift**: `y_1 = y * 2 + TILE_WIDTH` causes exponential coordinate inflation on rows 1..4 (Row 1 banner height is 365px, completely covering Row 2). | Fixed in v0.5.0 (`y_1 = y + self.TILE_HEIGHT`). |
| **BUG-02** | `collage_generator.py` | **High** | **Documentation & API Signature Drift**: `generate_top_albums_collage()`, `generate_top_artists_collage()`, and `generate_top_tracks_collage()` advertised in documentation but missing in code. | Added in v0.5.0 facade. |
| **BUG-03** | `collage_generator.py:69` | **Medium** | **Incomplete Boundary Validation**: `_validate_parameters` checks `cols > 5` but allows `cols <= 0` or `rows <= 0`, causing zero-dimension canvas crashes inside PIL. | Enforced `1 <= cols <= 5` and `1 <= rows <= 5`. |
| **BUG-04** | `collage.py:234, 251, 308` | **Medium** | **Retrieval Fragility & Missing Timeouts**: `requests.get()` lacks custom `User-Agent`, request timeouts, and catches only limited exceptions, crashing worker threads on CDN 502/503. | Wrapped with `DEFAULT_HEADERS`, `timeout=(3.05, 10.0)`, and blank tile fallbacks. |
| **BUG-05** | `collage.py:191` | **Low** | **Non-Deterministic Tile Ordering on Tied Plays**: `as_completed` arrival jitter combined with single-key sort produces non-deterministic tile order on identical playcounts. | Secondary sort key added: `(int(playcount), title)`. |

---

## 🤝 Contributing

We welcome contributions from the community! To contribute:

1. **Fork the Repository** and clone your fork locally.
2. **Initialize the Virtual Environment with `uv`**:
   ```bash
   uv sync
   ```
3. **Create a Feature Branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Author Tests**: Ensure all new functionality is accompanied by 100% offline unit tests in `tests/` using synthetic in-memory fixtures.
5. **Execute the QA Suite**:
   ```bash
   uv run flake8 src/ tests/
   uv run black --check src/ tests/
   uv run mypy src/
   uv run pytest tests/ -v
   ```
6. **Submit a Pull Request** with a detailed explanation of your changes and test verification evidence.

### Pull Request Quality Checklist

- [ ] All new methods have complete Python 3.8-compatible type annotations.
- [ ] No live network requests are made during test execution.
- [ ] All `PIL.Image` and `io.BytesIO` streams are cleanly closed or managed via context managers.
- [ ] HTTP requests specify explicit timeouts and custom `User-Agent` headers.
- [ ] Pytest suite passes cleanly with zero warnings or failures.

---

## 📄 License

This project is open-source software licensed under the [MIT License](LICENSE).

---

## 👤 Authors & Acknowledgments

- **Lead Author & Maintainer**: [@paurieraf](https://github.com/paurieraf) (Pau Riera)
- **Built With & Powered By**:
  - [pylast](https://github.com/pylast/pylast) — Python Last.fm REST API v2.0 Client.
  - [Pillow (PIL Fork)](https://python-pillow.org/) — Python Imaging Library for raster 2D graphics.
  - [Beautiful Soup 4](https://www.crummy.com/software/BeautifulSoup/) & [html5lib](https://github.com/html5lib/html5lib-python) — Resilient HTML DOM retrieval.
  - [uv](https://github.com/astral-sh/uv) — Fast Python package and dependency manager by Astral.
  - Monospace typography provided by the open-source **DejaVu Fonts Project**.
