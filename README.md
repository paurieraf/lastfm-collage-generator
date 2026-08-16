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

[Key Features](#-key-features) • [Grid Geometry](#-grid-dimensions--geometry-reference) • [Architecture](#-system-architecture--design-patterns) • [Installation](#-installation) • [Quickstart](#-quickstart) • [API Reference](#-python-api-reference) • [Developer Workflows](#-developer--debugging-workflows) • [Testing & QA](#-testing--quality-assurance) • [Roadmap](#-multi-phase-feature-roadmap) • [Defect Catalog](#-known-bugs--defect-catalog) • [Contributing](#-contributing)

</div>

---

## ✨ Key Features

- **Multi-Entity Composite Grids**:
  - 💿 **Top Albums (`album`)**: Queries user scrobble history via the Last.fm Audioscrobbler REST API (`pylast`), downloads album cover artwork, and composites them into an aligned matrix.
  - 🎤 **Top Artists (`artist`)**: Fetches top artists via the API and scrapes high-resolution artist hero imagery directly from `https://www.last.fm/music/<artist>` (bypassing the historical deprecation of artist images in the Last.fm API), thumbnails images to 300x300px, and composites the grid.
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

Every collage is dynamically assembled from individual `300 x 300` pixel raster tiles:

| Grid Size | Total Tiles | Dimensions (Width x Height) | Aspect Ratio | Megapixels | Typical Use Case |
|---|---|---|---|---|---|
| **`1x1`** | 1 tile | **300 x 300 px** | 1:1 Square | 0.09 MP | Single item avatar / badge |
| **`2x2`** | 4 tiles | **600 x 600 px** | 1:1 Square | 0.36 MP | Compact widget / blog embed |
| **`3x3`** | 9 tiles | **900 x 900 px** | 1:1 Square | 0.81 MP | Standard social media card (#LastFmFriday, Instagram) |
| **`4x4`** | 16 tiles | **1200 x 1200 px** | 1:1 Square | 1.44 MP | Monthly scrobble recap poster |
| **`5x5`** | 25 tiles | **1500 x 1500 px** | 1:1 Square | 2.25 MP | High-density yearly / all-time overview |
| **`3x4`** | 12 tiles | **900 x 1200 px** | 3:4 Portrait | 1.08 MP | Mobile wallpaper / Instagram Story |
| **`4x3`** | 12 tiles | **1200 x 900 px** | 4:3 Landscape | 1.08 MP | Tablet wallpaper / forum signature |
| **`5x3`** | 15 tiles | **1500 x 900 px** | 5:3 Landscape | 1.35 MP | Desktop banner / Twitter header |

### Tile Layout Anatomy (300 x 300 px)

Each tile within the collage follows exact pixel geometry:

```
(x, y) ┌──────────────────────────────────────────────────────────────┐
       │                                                              │
       │                                                              │
       │                   Tile Cover Artwork                         │
       │                 (Downloaded or Scraped)                      │
       │                     (300 x 300 px)                           │
       │                                                              │
       │                                                              │
y+235  ├──────────────────────────────────────────────────────────────┤ ◄── Banner Top (y + 235)
       │ Translucent Dark Banner: RGBA(0, 0, 0, 123) (Height: 65px)  │
y+240  │ Monospace Typography: DejaVuSansMono.ttf (15px regular/bold) │ ◄── Text Origin (x + 8, y + 240)
       │ "Artist Name - Album / Track Title. (42 scrobbles)"          │
(x+300,│                                                              │
 y+300)└──────────────────────────────────────────────────────────────┘ ◄── Tile Bottom (y + 300)
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
│  - Downloads cover art│  │  - Scrapes Last.fm DOM│  │  - Resolves album art │
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
| `collage.py` | `ArtistCollageBuilder` | **Concrete Builder** | Scrapes `last.fm/music/<artist>` DOM for `.header-new-background-image`; thumbnails to 300x300px. |
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
    period: str
) -> PIL.Image.Image
```

Generates a composite image collage for the specified entity and time horizon.

**Parameter Matrix**:

| Parameter | Type | Allowed Values | Default | Description |
|---|---|---|---|---|
| **`entity`** | `str` | `"album"`, `"artist"`, `"track"` | *Required* | Type of Last.fm listening entity to composite. |
| **`username`** | `str` | Any valid Last.fm username string | *Required* | The target Last.fm user account. |
| **`cols`** | `int` | `1 <= cols <= 5` | *Required* | Number of horizontal grid columns. |
| **`rows`** | `int` | `1 <= rows <= 5` | *Required* | Number of vertical grid rows. |
| **`period`** | `str` | `"7day"`, `"1month"`, `"3month"`, `"6month"`, `"12month"`, `"overall"` | *Required* | Scrobble aggregation time window. |

**Returns**:
- `PIL.Image.Image`: An allocated Pillow 24-bit RGB raster canvas with dimensions `(cols * 300, rows * 300)` pixels.

**Exceptions Raised**:
- `ValueError`: If `entity` is not in `ENTITIES`, `period` is not in `PERIODS`, or `cols`/`rows` are outside `1..5`.
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

# Generate Top Artists Collage (5x5, monthly)
artist_collage = generator.generate_top_artists_collage(
    username="rj",
    cols=5,
    rows=5,
    period="1month"
)

# Generate Top Tracks Collage (4x3, overall history)
track_collage = generator.generate_top_tracks_collage(
    username="rj",
    cols=4,
    rows=3,
    period="overall"
)
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
    print(f"Artist scraping warning: {e}")
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
| `--live` | | `flag` | `False` | Run live Last.fm API queries and web scraping. |
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
- `🌐 Debug: Live Artist Collage (.env)`: Step through web scraping pipeline.
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
  - [ ] **Dynamic Theme Engine**: Pre-packaged themes (`Dark`, `Light`, `Glassmorphic` with localized Gaussian blur, `Gradient Overlays`, and custom user hex palettes).
  - [ ] **Typography & Auto-Scaling Engine**: Word-boundary line breaking via `textwrap`, dynamic font downscaling for long titles, and custom `.ttf`/`.otf` font path support.
  - [ ] **Tile Geometry & Rounded Corners**: Rounded squircle corner masking (`radius=12`), configurable border stroke widths and colors, and inter-tile spacing margins.
  - [ ] **Versatile Overlay Styles**: `Banner` (lower third), `Full Tint` (centered text), `Gradient Fade`, `Minimalist Badge / Pill` (rank + playcount chip), and `Clean Mode` (`show_text=False` for pure artwork grids).

### ⚡ Pillar 2: Performance, Caching & Scraping Resilience

- **Phase 2 (v0.6.0 — Fallbacks & Determinism)**:
  - [ ] **Dynamic Fallback Artwork Engine**: Algorithmic two-color pastel gradients and initials typography derived from SHA-256 entity hashes to replace solid black tiles.
  - [ ] **Deterministic Secondary Sorting**: Secondary sort key `(int(playcount), title)` to ensure byte-for-byte identical collages on tied scrobble counts.
- **Phase 3 (v0.7.0 — Caching & Network Resilience)**:
  - [ ] **Multi-Tier Caching Subsystem**: Tier-1 in-memory LRU cache (`maxsize=256`) + Tier-2 SQLite persistent disk cache (`~/.cache/lastfm-collage/`) with 30-day TTL for album covers and 7-day TTL for scraped artist hero images.
  - [ ] **Network Resilience Middleware**: Token-bucket rate limiter (5 req/sec), exponential backoff with full jitter for transient HTTP errors, and circuit breaker for web scraping fallbacks.
- **Phase 4 (v1.0.0 — Asynchronous Architecture)**:
  - [ ] **Native AsyncIO Pipeline**: Non-blocking concurrent asset acquisition via `httpx` (`async def generate_async()`) with async semaphore concurrency throttling.

### 📐 Pillar 3: Advanced Layouts & Modern Formats

- **Phase 2 (v0.6.0 — High-Density Grids)**:
  - [ ] **Arbitrary $N \times M$ Matrix Grids**: Expand grid size beyond `5x5` (e.g. `10x10` 100-album grids) with dynamic tile resolution downscaling (300px $\to$ 150px $\to$ 100px) and memory-safe allocation.
- **Phase 3 (v0.7.0 — Social Presets & Backdrop Decorators)**:
  - [ ] **Social Media Dimension Presets**: One-click generation for Instagram Story (`9:16` $1080\times1920$), Instagram Post (`1:1` $1080\times1080$), Twitter Header (`3:1` $1500\times500$), and Desktop Wallpaper (`16:9` $1920\times1080$ / 4K).
  - [ ] **Acrylic Backdrop Blur**: Automatically fill non-square letterboxing with an acrylic Gaussian-blurred backdrop derived from the user's #1 top artwork.
- **Phase 4 (v1.0.0 — Modern Formats & Asymmetric Grids)**:
  - [ ] **Modern Export Formats**: Direct export to WebP (lossy/lossless), SVG vector containers with crisp `<text>` nodes, and 300 DPI print-ready PDF posters.
  - [ ] **Asymmetrical Layout Strategies**: `Hero Grid` (#1 item in $2\times2$ block, surrounded by $1\times1$ and $0.5\times0.5$ tiles), `Bento Box` editorial grids, and `Honeycomb Hexagon` tessellations.
- **Phase 5 (v1.1.0 — Motion Recaps)**:
  - [ ] **Animated Transitions**: Generate animated GIF / MP4 listening recaps smoothly crossfading across time horizons (`7day` $\to$ `1month` $\to$ `3month` $\to$ `12month`).

### 🌐 Pillar 4: Ecosystem & CLI Integrations

- **Phase 2 (v0.6.0 — Standalone CLI)**:
  - [ ] **Rich CLI Tool (`lastfm-collage`)**: Global console script with rich terminal UI, colorized progress bars, download speed metrics, and ASCII art terminal previews.
- **Phase 3 (v0.8.0 — GitHub Actions Automation)**:
  - [ ] **GitHub Profile README Action (`action.yml`)**: Automated scheduled workflow updating developer GitHub Profile READMEs with weekly listening recaps on cron.
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
| **BUG-04** | `collage.py:234, 251, 308` | **Medium** | **Scraping Fragility & Missing Timeouts**: `requests.get()` lacks custom `User-Agent`, request timeouts, and catches only limited exceptions, crashing worker threads on CDN 502/503. | Wrapped with `DEFAULT_HEADERS`, `timeout=(3.05, 10.0)`, and blank tile fallbacks. |
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
  - [Beautiful Soup 4](https://www.crummy.com/software/BeautifulSoup/) & [html5lib](https://github.com/html5lib/html5lib-python) — Resilient HTML DOM scraping.
  - [uv](https://github.com/astral-sh/uv) — Fast Python package and dependency manager by Astral.
  - Monospace typography provided by the open-source **DejaVu Fonts Project**.
