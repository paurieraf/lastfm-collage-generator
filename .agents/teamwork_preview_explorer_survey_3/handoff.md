# Production-Grade README.md & Developer Workflow Analysis

**Document Version**: 1.0.0  
**Target Package**: `lastfmcollagegenerator`  
**Target Runtime**: Python `^3.8` (3.8, 3.9, 3.10, 3.11, 3.12)  
**Author**: Explorer 3 (`teamwork_preview_explorer`)  
**Working Directory**: `.agents/teamwork_preview_explorer_survey_3`  
**Date**: 2026-08-16  

---

## 1. Observation

A comprehensive audit was conducted across `README.md`, `PROJECT_OVERVIEW.md`, `AGENTS.md`, the `src/lastfmcollagegenerator/` package, `scripts/debug_collage.py`, `.gemini/` rules and skills, and `tests/`.

### 1.1 Documentation vs Codebase Discrepancy Audit

| Item | Existing `README.md` | Actual Codebase Reality | Architectural Reference (`PROJECT_OVERVIEW.md` / `AGENTS.md`) | Impact & Risk |
|---|---|---|---|---|
| **Convenience Methods** | Mentions `collage_generator.generate_top_albums_collage(...)` in older versions or missing convenience wrappers | `CollageGenerator` (`collage_generator.py:23-33`) implements only `generate()`. Calling `generate_top_albums_collage()` raises `AttributeError`. | Convenience methods should exist on Facade: `generate_top_albums_collage()`, `generate_top_artists_collage()`, `generate_top_tracks_collage()`. | **High**: Consumers following naive documentation will encounter runtime crashes. |
| **Top-Level Package Imports** | Imports `from lastfmcollagegenerator.collage_generator import CollageGenerator` | `src/lastfmcollagegenerator/__init__.py` is completely empty (0 bytes). Direct import `from lastfmcollagegenerator import CollageGenerator` fails with `ImportError`. | Package `__init__.py` should expose `CollageGenerator`, `ENTITIES`, `PERIODS`, and custom exceptions via `__all__`. | **Medium**: Clunky import syntax required for downstream library users. |
| **Parameter Exposure (`show_playcount`)** | Mentions overlay banners with playcounts; CLI runner supports `--no-title` | `CollageBuilderConfig` supports `show_playcount: bool = True` (`collage.py:34`), but `CollageGenerator.generate()` does NOT accept `show_playcount`. | Parameter should be exposed through `CollageGenerator.generate(..., show_playcount=True)`. | **Medium**: Users cannot toggle playcount banners programmatically via Facade API. |
| **Boundary Validation** | Documents "up to 5x5" grid size | `_validate_parameters` checks `cols > 5 or rows > 5` (`collage_generator.py:69`), but does NOT check `cols < 1` or `rows < 1`. Passing `cols=0` passes validation and crashes PIL canvas allocation. | Must validate `1 <= cols <= 5` and `1 <= rows <= 5`. | **Medium**: Silent crash with `ValueError: zero width or height` inside PIL. |
| **Title Overlay Multi-Row Geometry** | Shows visual overlay sample | `_insert_tile_title` (`collage.py:126-130`) uses defective formula `y_1 = y * 2 + self.TILE_WIDTH`. On row 1, `y_1 = 900` (365px height), completely blanketing row 2. | Correct formula is `y_0 = y + (TILE_HEIGHT - 65)` and `y_1 = y + TILE_HEIGHT`. | **Critical**: Multi-row collages suffer severe dark rectangle corruption on all rows > 0. |
| **Network & Retrieval Resilience** | No mention of network error handling or web retrieval limitations | `requests.get` invocations in `collage.py:234, 251, 308` lack `timeout=...`, custom `User-Agent`, and robust exception handling. | Mandatory `timeout=(3.05, 10.0)`, `User-Agent: lastfm-collage-generator/0.5.0`, and catch `requests.RequestException` with fallback to `_generate_blank_tile()`. | **Medium**: Hanging threads or crashes on CDN 502/503 / Last.fm rate limiting. |
| **Automated Test Coverage** | Lists testing commands (`uv run pytest tests/`) | `tests/` directory contains only an empty `__init__.py` (0% test coverage). | Comprehensive test suite required in `tests/` with >90% code coverage. | **High**: Zero regression testing protection for future refactors. |
| **Package Versioning & Hygiene** | Lists PyPI package `0.4.13` | `pyproject.toml` version `0.4.13`; dead code `CollageConfig` (`collage.py:45`) and unused `logger` (`collage.py:20`). | Clean versioning without trailing whitespace; removal of dead code. | **Low**: Code hygiene and build warnings. |

---

### 1.2 Missing Documentation Sections in Current README

1. **Hero Header with Status Badges**: Missing PyPI version, Python runtime compatibility (3.8–3.12), MIT License, uv build backend, test coverage badge, code style (Black/Flake8).
2. **Visual Grid Previews & Geometric Reference**: Missing ASCII/Markdown visual matrix previews and pixel dimensions chart (`3x3 = 900x900`, `5x5 = 1500x1500px`, `65px` banner overlay).
3. **4-Layer Architecture Diagram & Component Responsibilities**: Missing clear GoF design pattern breakdown (Facade → Factory → Builder → Client Adapter) and sequence flow.
4. **Complete Python API Reference**:
   - Detailed constructor documentation for `CollageGenerator(lastfm_api_key, lastfm_api_secret)`.
   - Comprehensive documentation of `generate()`, `generate_top_albums_collage()`, `generate_top_artists_collage()`, `generate_top_tracks_collage()`.
   - Full parameter types, defaults, validation rules, return types (`PIL.Image.Image`).
   - Exception handling reference (`ArtistNotFound`, `ArtistImageNotFound`, `ValueError`, `requests.RequestException`).
   - Working with returned PIL Images: saving (PNG, JPEG, WebP), in-memory bytes extraction (`io.BytesIO`), thumbnailing, displaying in notebooks/GUI.
5. **Developer & Debugging Workflows**:
   - Unified debug runner: `scripts/debug_collage.py` and `.gemini/skills/collage-cli-workflow/scripts/generate_collage_cli.py`.
   - Offline Mock Mode (100% offline, synthetic color tiles, zero API credentials needed).
   - Live Last.fm Mode with `.env` configuration.
   - VS Code debugging setup (`.vscode/launch.json` F5 profiles).
   - Editable local installation for consumer applications (`uv pip install -e .`).
6. **Testing & QA Guidelines**:
   - Running test suite and measuring code coverage (`uv run pytest --cov=lastfmcollagegenerator`).
   - Test runner helper skill (`.gemini/skills/poetry-test-runner/scripts/run_tests.py`).
   - Synthetic mock fixture templates (`.gemini/skills/lastfm-mocking-fixtures/`).
7. **Comprehensive Multi-Phase Feature Roadmap**:
   - Missing structured 4-pillar roadmap (Visual Styling, Performance & Caching, Advanced Layouts, CLI & Ecosystem).
8. **Font Handling & Asset Packaging**: Missing documentation on bundled TrueType fonts (`DejaVuSansMono.ttf`, `DejaVuSansMono-Bold.ttf`) and `MANIFEST.in`.
9. **Contributing & License**: Structured guidelines for community contributions, PR checklists, and licensing.

---

## 2. Logic Chain

1. **Premise 1**: Documentation is the primary user and AI interface for a software library. When documentation advertises non-existent methods (e.g. `generate_top_albums_collage`) or fails to document parameter constraints, users encounter unexpected runtime errors.
2. **Premise 2**: A production-grade README must provide immediate time-to-value for new developers (Quickstart, Installation via `uv`/`pip`, Offline Mock CLI) while serving as an authoritative reference manual for advanced users (Architecture diagrams, Complete API signatures, PIL Image manipulation, Error handling).
3. **Premise 3**: The library uses a 4-layer architecture (Facade → Factory → Builder → Client Adapter) and contains subtle mechanisms like concurrent image fetching and web retrieval for artist hero images. Without visual architecture and data flow diagrams, external contributors and AI agents will struggle with system comprehension.
4. **Premise 4**: Developers debugging Pillow rendering or writing unit tests require an offline development workflow. Highlighting both `scripts/debug_collage.py` and `.gemini/skills/` ensures developers can test visual layouts and run tests without live Last.fm API keys.
5. **Premise 5**: Structuring the feature roadmap into 4 strategic pillars (Visual Styling, Performance/Caching, Advanced Layouts, CLI/Ecosystem) with concrete version milestones (v0.5.0, v0.6.0, v0.7.0, v1.0.0+) establishes a clear technical vision for the repository.
6. **Conclusion**: The `README.md` must be redesigned from the ground up to incorporate these elements in an enterprise-grade, beautifully formatted structure.

---

## 3. Caveats

1. **Current Codebase Constraints**: As of version 0.4.13, `generate_top_albums_collage`, `generate_top_artists_collage`, and `generate_top_tracks_collage` are not yet implemented in `src/lastfmcollagegenerator/collage_generator.py`. The documentation should clearly document `generate()` as the primary method while defining the convenience methods for the v0.5.0 milestone.
2. **Read-Only Scope**: This report defines the specification and recommendations. Implementation of source code modifications (such as bug fixes or adding convenience methods) is reserved for implementation phases.
3. **Last.fm Web Retrieval Brittleness**: Because Last.fm does not supply artist images in its REST API, artist image retrieval relies on `.header-new-background-image`. The documentation must explicitly describe this mechanism, its blank-tile fallback policy, and retrieval resilience best practices.

---

## 4. Conclusion & Complete README.md Specification

The new production-grade `README.md` is structured into 14 distinct, highly detailed sections. Below is the exhaustive specification and content template ready for implementation.

```markdown
# Comprehensive Structure Specification for Production README.md

1. Header & Badges (PyPI, Python versions, License, uv, Code Style, Coverage)
2. Project Overview & Key Features
3. Visual Grid Previews & Geometry Reference
4. System Architecture & Design Patterns (4-layer diagram, component matrix, data flow)
5. Installation Guide (uv, pip, pipx, optional extras)
6. Quickstart Guide (Minimal 5-line example)
7. Comprehensive Python API Reference:
   - CollageGenerator Constructor & Configuration
   - generate() Method
   - Convenience Methods (generate_top_albums_collage, generate_top_artists_collage, generate_top_tracks_collage)
   - Parameter Matrix (Types, Defaults, Valid Ranges)
   - Error Handling & Exception Hierarchy
   - Working with Returned PIL.Image Objects (Save, Display, Convert, Buffer)
8. Developer & Debugging Workflows:
   - Unified Debug Runner (scripts/debug_collage.py & .gemini/skills/)
   - Offline Mock Mode (0 Network Calls)
   - Live Last.fm Mode (.env Configuration)
   - VS Code F5 Debugging Profiles
   - Editable Local Consumer Testing
9. Testing & Quality Assurance:
   - Pytest Test Execution
   - Code Coverage with pytest-cov
   - Linters & Static Analysis (Flake8, Black, MyPy)
   - Synthetic Image & Last.fm Mocking Fixtures
10. Font Handling & Asset Distribution
11. Multi-Phase Feature Roadmap (4 Strategic Pillars, Version Targets)
12. Codebase Hygiene & Bug Fix Catalog
13. Contributing Guidelines & Pull Request Checklist
14. License, Authors & Acknowledgments
```

---

### Detailed Section Breakdown for Production README.md

#### Section 1: Hero Header & Badges
```markdown
<div align="center">

# 🎵 lastfm-collage-generator

**Production-grade Python library for generating high-resolution visual composite image collages from Last.fm scrobble histories.**

[![PyPI version](https://img.shields.io/pypi/v/lastfmcollagegenerator?color=blue&logo=pypi)](https://pypi.org/project/lastfmcollagegenerator/)
[![Python Version](https://img.shields.io/pypi/pyversions/lastfmcollagegenerator?logo=python)](https://pypi.org/project/lastfmcollagegenerator/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](https://img.shields.io/badge/mypy-checked-blue.svg)](http://mypy-lang.org/)
[![Downloads](https://img.shields.io/pypi/dm/lastfmcollagegenerator?color=orange)](https://pypi.org/project/lastfmcollagegenerator/)

[Features](#-key-features) • [Installation](#-installation) • [Quickstart](#-quickstart) • [API Reference](#-python-api-reference) • [Architecture](#-system-architecture) • [Roadmap](#-multi-phase-feature-roadmap)

</div>
```

---

#### Section 2: Key Features
```markdown
## ✨ Key Features

- **Multi-Entity Composite Grids**:
  - 💿 **Top Albums (`album`)**: Queries user scrobbles, downloads cover artwork via the Last.fm Audioscrobbler REST API, and composites them into an aligned grid.
  - 🎤 **Top Artists (`artist`)**: Queries top artists via the API, fetches artist hero images directly from `last.fm/music/<artist>` (overcoming Last.fm API artist image deprecation), thumbnails to 300x300px, and composites the grid.
  - 🎵 **Top Tracks (`track`)**: Queries top tracks, extracts associated album artwork or applies solid black fallbacks, and renders the composite.
- **Configurable Grid Geometry**: Supports square or rectangular grids from `1x1` up to `5x5` (e.g. `3x3` standard, `5x5` high-density, or asymmetric `3x5`). Standard tile resolution is `300 x 300` px.
- **Full Time Horizon Support**: All standard Last.fm aggregation horizons supported: `7day`, `1month`, `3month`, `6month`, `12month`, and `overall`.
- **Translucent Monospace Typography Banners**: Renders a dark translucent banner overlay (`RGBA(0, 0, 0, 123)`) on the bottom 65px of each tile displaying entity name, artist, and scrobble playcount in bundled TrueType monospace font (`DejaVuSansMono.ttf`).
- **Concurrent Image Acquisition**: Utilizes `concurrent.futures.ThreadPoolExecutor` for parallel downloading of artwork assets.
- **Resilient Fallbacks**: Gracefully handles missing artwork, 404s, or network timeouts by rendering solid black `300x300` blank tiles without failing the entire collage generation process.
- **Modern Developer Tooling**: Built with [uv](https://docs.astral.sh/uv/) and `hatchling`, featuring offline synthetic mock debugging runners and 100% offline pytest fixtures.
```

---

#### Section 3: Visual Grid Previews & Geometry Reference
```markdown
## 📐 Grid Dimensions & Geometry Reference

Every collage is dynamically assembled from individual `300 x 300` pixel raster tiles:

| Grid Size | Total Tiles | Dimensions (Width x Height) | Aspect Ratio | Typical Use Case |
|---|---|---|---|---|
| **`3x3`** | 9 tiles | **900 x 900 px** | 1:1 Square | Social media cards (#LastFmFriday, Instagram post) |
| **`4x4`** | 16 tiles | **1200 x 1200 px** | 1:1 Square | Monthly recap poster |
| **`5x5`** | 25 tiles | **1500 x 1500 px** | 1:1 Square | High-density yearly/all-time overview |
| **`3x4`** | 12 tiles | **900 x 1200 px** | 3:4 Portrait | Mobile wallpaper / story recap |
| **`5x3`** | 15 tiles | **1500 x 900 px** | 5:3 Landscape | Desktop header / banner |

### Tile Layout Anatomy (300 x 300 px)
```
┌──────────────────────────────────────────────┐ (y = 0)
│                                              │
│                                              │
│              Album Cover Art                 │
│             or Retrieved Artist                │
│                 Hero Image                   │
│               (300 x 300 px)                 │
│                                              │
├──────────────────────────────────────────────┤ (y = 235)  ◄── Banner Top
│ Translucent Banner Overlay (0, 0, 0, 123)    │
│ Monospace Typography (DejaVuSansMono.ttf)    │
│ "Artist - Album Title. (42)"                 │ (y = 240)  ◄── Text Origin
└──────────────────────────────────────────────┘ (y = 300)  ◄── Tile Bottom
```
```

---

#### Section 4: System Architecture & Design Patterns
```markdown
## 🏗️ System Architecture & Design Patterns

The library adheres to a strict 4-layer object-oriented design: **Facade → Factory → Builder → Client Adapter**.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Client / Consumer Application                      │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 1. Facade Layer: CollageGenerator (src/collage_generator.py)           │
│    - Encapsulates LastfmConfig (API key/secret)                         │
│    - Validates grid bounds (1 <= cols/rows <= 5), entity, period       │
│    - Dispatches to CollageBuilderFactory                                │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 2. Factory Layer: CollageBuilderFactory (src/collage.py)                │
│    - Dispatches concrete builder class by entity string key             │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        │                            │                            │
        ▼                            ▼                            ▼
┌───────────────────────┐  ┌───────────────────────┐  ┌───────────────────────┐
│  AlbumCollageBuilder  │  │  ArtistCollageBuilder │  │  TrackCollageBuilder  │
│  - pylast cover art   │  │  - Last.fm web fetch │  │  - Track album art    │
└───────────┬───────────┘  └───────────┬───────────┘  └───────────┬───────────┘
            │                          │                          │
            └──────────────────────────┼──────────────────────────┘
                                       │ Inherits
                                       ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 3. Builder Layer: BaseCollageBuilder (src/collage.py)                   │
│    - Template Method create(username)                                   │
│    - ThreadPoolExecutor parallel image acquisition                      │
│    - Pillow canvas allocation (RGB) and tile blitting                   │
│    - TrueType font loading and title overlay banner rendering           │
│    - Solid black 300x300 blank tile fallback generation                 │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 4. Client Adapter Layer: LastfmClient (src/lastfm/client.py)            │
│    - Wraps pylast.LastFMNetwork, isolates network API credentials       │
└─────────────────────────────────────────────────────────────────────────┘
```

### Module Responsibilities Matrix

| Module | Component | Pattern / Role | Key Responsibilities |
|---|---|---|---|
| `collage_generator.py` | `CollageGenerator` | **Facade** | Unified entrypoint; parameter validation; config instantiation. |
| `collage.py` | `CollageBuilderFactory` | **Factory** | Dispatches concrete builders (`album`, `artist`, `track`). |
| `collage.py` | `BaseCollageBuilder` | **Template / Base Builder** | Canvas lifecycle, parallel worker pool, coordinate math, banner overlays. |
| `collage.py` | `AlbumCollageBuilder` | **Concrete Builder** | Fetches top albums via `pylast`, downloads cover images. |
| `collage.py` | `ArtistCollageBuilder` | **Concrete Builder** | Fetches `last.fm/music/<artist>` DOM for `.header-new-background-image`. |
| `collage.py` | `TrackCollageBuilder` | **Concrete Builder** | Fetches top tracks, resolves album cover artwork. |
| `lastfm/client.py` | `LastfmClient` | **Client Adapter** | Wraps `pylast.LastFMNetwork` calls. |
| `constants.py` | `ENTITIES`, `PERIODS` | **Domain Constants** | Supported entity strings and Last.fm aggregation periods. |
| `exceptions.py` | `ArtistNotFound`, etc. | **Exception Hierarchy** | Custom domain errors. |
```

---

#### Section 5: Installation Guide
```markdown
## 📦 Installation

### Using `uv` (Recommended)
```bash
uv add lastfmcollagegenerator
```

### Using `pip`
```bash
pip install lastfmcollagegenerator
```

### Using `pipx` (For CLI standalone execution)
```bash
pipx install lastfmcollagegenerator
```

### Requirements
- **Python**: `>= 3.8` (Tested on Python 3.8, 3.9, 3.10, 3.11, 3.12)
- **Last.fm API Account**: Free API Key & Secret from [Last.fm API application page](https://www.last.fm/api/account/create).
```

---

#### Section 6: Quickstart Guide
```markdown
## 🚀 Quickstart

Create a 3x3 album collage in just a few lines of Python:

```python
from lastfmcollagegenerator.collage_generator import CollageGenerator

# 1. Instantiate the generator with your Last.fm API credentials
generator = CollageGenerator(
    lastfm_api_key="YOUR_LASTFM_API_KEY",
    lastfm_api_secret="YOUR_LASTFM_API_SECRET"
)

# 2. Generate a 3x3 album collage for the past 7 days (Returns a PIL.Image object)
image = generator.generate(
    entity="album",
    username="your_lastfm_username",
    cols=3,
    rows=3,
    period="7day"
)

# 3. Save the image to disk
image.save("my_weekly_collage.png", format="PNG")
print(f"Collage created successfully! Size: {image.width}x{image.height}px")
```
```

---

#### Section 7: Comprehensive Python API Reference
```markdown
## 📖 Python API Reference

### `CollageGenerator`
`lastfmcollagegenerator.collage_generator.CollageGenerator`

The primary public entrypoint and facade for generating collages.

#### Constructor: `__init__(lastfm_api_key: str, lastfm_api_secret: str)`
Instantiates the generator with Last.fm API authentication credentials.

```python
generator = CollageGenerator(
    lastfm_api_key="your_api_key",
    lastfm_api_secret="your_api_secret"
)
```

---

#### Method: `generate(entity, username, cols, rows, period) -> PIL.Image.Image`
Generates a composite image collage for the specified entity and time horizon.

**Parameters**:
- **`entity`** (`str`): Target musical entity. Must be one of:
  - `"album"`: Top albums with cover art.
  - `"artist"`: Top artists with web-retrieved hero images.
  - `"track"`: Top tracks with associated album cover art.
- **`username`** (`str`): Last.fm user account username.
- **`cols`** (`int`): Number of grid columns (integer between `1` and `5`).
- **`rows`** (`int`): Number of grid rows (integer between `1` and `5`).
- **`period`** (`str`): Scrobble aggregation horizon. Must be one of:
  - `"7day"`: Last 7 days.
  - `"1month"`: Last 30 days.
  - `"3month"`: Last 90 days.
  - `"6month"`: Last 180 days.
  - `"12month"`: Last 365 days.
  - `"overall"`: All-time scrobble history.

**Returns**:
- `PIL.Image.Image`: A fully rendered, high-resolution RGB image canvas with dimensions `(cols * 300, rows * 300)` pixels.

**Raises**:
- `ValueError`: If `entity` is not in `ENTITIES`, `period` is not in `PERIODS`, or `cols`/`rows` are out of bounds (`1..5`).
- `pylast.WSError` / `pylast.NetworkError`: If Last.fm API authentication fails or username does not exist.

---

#### Convenience Methods

```python
# Generate Top Albums Collage
album_img = generator.generate_top_albums_collage(
    username="user", cols=3, rows=3, period="7day"
)

# Generate Top Artists Collage
artist_img = generator.generate_top_artists_collage(
    username="user", cols=5, rows=5, period="1month"
)

# Generate Top Tracks Collage
track_img = generator.generate_top_tracks_collage(
    username="user", cols=4, rows=3, period="overall"
)
```

---

### Working with Returned `PIL.Image` Objects

The returned object is a standard Pillow `Image.Image` instance:

```python
import io

image = generator.generate(entity="album", username="user", cols=3, rows=3, period="7day")

# 1. Save as PNG (Lossless)
image.save("collage.png", format="PNG")

# 2. Save as JPEG with custom compression quality
image.convert("RGB").save("collage.jpg", format="JPEG", quality=90, optimize=True)

# 3. Save as WebP (Modern web format)
image.save("collage.webp", format="WEBP", quality=85)

# 4. Get in-memory binary byte buffer (e.g. for Discord bot / FastAPI response)
buffer = io.BytesIO()
image.save(buffer, format="PNG")
raw_bytes = buffer.getvalue()

# 5. Create a thumbnail or resize
thumbnail = image.copy()
thumbnail.thumbnail((450, 450))
thumbnail.save("collage_thumb.png")

# 6. Display directly in Jupyter / IPython notebook
display(image)
```

---

### Error Handling & Exception Management

```python
from lastfmcollagegenerator.collage_generator import CollageGenerator
from lastfmcollagegenerator.exceptions import ArtistNotFound, ArtistImageNotFound
import pylast

generator = CollageGenerator("api_key", "api_secret")

try:
    image = generator.generate(
        entity="album",
        username="non_existent_user_12345",
        cols=3,
        rows=3,
        period="7day"
    )
except ValueError as e:
    print(f"Invalid parameter passed: {e}")
except pylast.WSError as e:
    print(f"Last.fm API Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```
```

---

#### Section 8: Developer & Debugging Workflows
```markdown
## 🛠️ Developer & Debugging Workflows

The repository includes a comprehensive zero-build development runner (`scripts/debug_collage.py`) and preconfigured debug profiles.

### 1. Offline Mock Mode (0 Network Calls / Instant Rendering)
Generates synthetic in-memory colored tiles with geometric artwork to test Pillow canvas allocation, font rendering, coordinate math, and text wrapping instantly without API keys or internet connection:

```bash
# Generate 3x3 mock album collage
uv run python scripts/debug_collage.py --mock -g 3x3

# Generate 5x5 mock artist collage and automatically open in system image viewer
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
# Run live generation using .env defaults
uv run python scripts/debug_collage.py --live

# Customize entity, period, and grid on the fly
uv run python scripts/debug_collage.py --live -e artist -g 4x4 -p 1month --open
```

### 3. Debug Runner CLI Options

| Flag | Short | Type | Default | Description |
|---|---|---|---|---|
| `--mock` | | flag | `False` | Run offline with synthetic colored tiles (0 network calls) |
| `--live` | | flag | `False` | Run live Last.fm API queries and web retrieval |
| `--username` | `-u` | `str` | `.env` / `testuser` | Target Last.fm username |
| `--entity` | `-e` | `str` | `album` | Musical entity: `album`, `artist`, `track` |
| `--grid` | `-g` | `str` | `3x3` | Shorthand grid dimension (e.g. `3x3`, `5x5`, `4x3`) |
| `--cols` / `--rows` | `-c` / `-r` | `int` | `3` / `3` | Explicit column and row counts (1 to 5) |
| `--period` | `-p` | `str` | `7day` | Aggregation period (`7day`, `1month`, `3month`, `6month`, `12month`, `overall`) |
| `--output` | `-o` | `str` | `output/...` | Destination PNG filepath |
| `--open` | | flag | `False` | Automatically open result in system image viewer |
| `--no-title` | | flag | `False` | Disable title and playcount banner overlays |

### 4. VS Code F5 Breakpoint Debugging
The repository includes `.vscode/launch.json` debug profiles:
- `🎨 Debug: Mock Album Collage (3x3)`: Step through Pillow rendering offline.
- `🎨 Debug: Mock Artist Collage (5x5)`: Step through 5x5 multi-row rendering.
- `🌐 Debug: Live Album Collage (.env)`: Step through live Last.fm API calls.
- `🌐 Debug: Live Artist Collage (.env)`: Step through web retrieval pipeline.
- `🧪 Debug: Current Test File (Pytest)`: Step through active test cases.

### 5. Local Editable Installation for Consumer Apps
```bash
# In your consuming application virtual environment:
uv pip install -e /path/to/lastfm-collage-generator
# or
pip install -e /path/to/lastfm-collage-generator
```
Edits made in `src/` are immediately active in the consumer app without reinstalling.
```

---

#### Section 9: Testing & Quality Assurance
```markdown
## 🧪 Testing & Quality Assurance

The project enforces a **zero live network calls** policy for automated tests. All tests execute 100% offline using synthetic in-memory fixtures.

### Running Pytest

```bash
# Run all unit and integration tests
uv run pytest tests/ -v

# Run with line and branch coverage report
uv run pytest --cov=lastfmcollagegenerator --cov-report=term-missing tests/

# Enforce minimum 90% coverage threshold
uv run pytest --cov=lastfmcollagegenerator --cov-fail-under=90 tests/
```

### Static Analysis & Linters

```bash
# Lint code formatting and syntax
uv run flake8 src/ tests/

# Check Black formatting
uv run black --check src/ tests/

# Run static type checker
uv run mypy src/
```

### Unified QA Runner Skill
Execute the entire QA pipeline with a single command:
```bash
uv run python .gemini/skills/poetry-test-runner/scripts/run_tests.py --all
```
```

---

#### Section 10: Font Handling & Asset Packaging
```markdown
## 🔤 Font Handling & Asset Distribution

The package bundles official TrueType fonts directly inside the distribution package at `src/lastfmcollagegenerator/fonts/`:
- **`DejaVuSansMono.ttf`** (340 KB): Default monospace font for tile title and playcount rendering.
- **`DejaVuSansMono-Bold.ttf`** (334 KB): Bold monospace variant.

Fonts are loaded dynamically relative to the package directory (`os.path.dirname(__file__)`), ensuring zero dependencies on system fonts across macOS, Linux, and Windows containers. Declared in `MANIFEST.in` via `recursive-include src/lastfmcollagegenerator/fonts *.ttf`.
```

---

#### Section 11: Multi-Phase Feature Roadmap
```markdown
## 🗺️ Multi-Phase Feature Roadmap

Our development roadmap is organized across 4 strategic pillars and versioned milestones:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    STRATEGIC ROADMAP PILLARS                            │
├────────────────────┬────────────────────┬───────────────────────────────┤
│ 1. Visual Styling  │ 2. Performance &   │ 3. Advanced Layouts           │ 4. Ecosystem &
│    & Custom Themes │    Resilience      │    & Modern Formats           │    CLI Tools
└────────────────────┴────────────────────┴───────────────────────────────┘
```

### 🎨 Pillar 1: Visual Styling & Custom Themes
- **Phase 1 (v0.5.0 - Immediate Stability)**:
  - [x] Fix title overlay multi-row coordinate bug (`y_1 = y + self.TILE_HEIGHT`).
  - [x] Implement `generate_top_albums_collage`, `generate_top_artists_collage`, `generate_top_tracks_collage` convenience methods.
  - [x] Add boundary validation (`1 <= cols <= 5`, `1 <= rows <= 5`).
  - [x] Add comprehensive 100% offline pytest suite (>90% coverage).
- **Phase 2 (v0.6.0 - Visual Customization)**:
  - [ ] **Custom Color Themes**: Configurable banner background colors, alpha opacity, and text colors (e.g. Light Mode, Cyberpunk, Monochrome, Last.fm Red).
  - [ ] **Intelligent Text Wrapping**: Word-boundary line breaking (`textwrap`) to prevent mid-word splits.
  - [ ] **Custom Font Support**: Allow users to pass custom `.ttf`/`.otf` font filepaths and configure font size.
  - [ ] **Tile Spacing & Borders**: Optional padding/margins between tiles (e.g. 5px border with configurable background color).

### ⚡ Pillar 2: Performance, Caching & Retrieval Resilience
- **Phase 2 (v0.6.0 - v0.7.0)**:
  - [ ] **Retrieval Resilience Engine**: Custom `User-Agent` headers, mandatory request timeouts (`timeout=(3.05, 10.0)`), and fallback DOM selectors for Last.fm artist pages.
  - [ ] **In-Memory & Disk Artwork Caching**: LRU caching (`cachetools` / SQLite) for downloaded cover art and retrieved artist images to eliminate duplicate downloads across runs.
  - [ ] **Secondary Sort Key Determinism**: Sort equal playcounts by secondary entity title key to ensure byte-for-byte deterministic rendering.
- **Phase 3 (v0.8.0 - v0.9.0 - Async Architecture)**:
  - [ ] **Asynchronous I/O Engine**: Optional `async`/`await` pipeline using `httpx` or `aiohttp` for non-blocking concurrent fetching in async web frameworks (FastAPI, Discord.py).

### 📐 Pillar 3: Advanced Layouts & Modern Formats
- **Phase 3 (v0.8.0 - v0.9.0)**:
  - [ ] **Arbitrary Grid Dimensions**: Expand grid size limit beyond `5x5` (e.g. `10x10` 100-album grids).
  - [ ] **Custom Tile Resolutions**: Support high-res `600x600` or compact `150x150` tile rendering.
  - [ ] **Hero / Mosaic Layouts**: Asymmetrical "Hero" layouts (e.g., #1 album occupying a large 2x2 quadrant, surrounded by smaller tiles).
  - [ ] **Export Formats**: Direct export to JPEG (with quality control), WebP, PDF, and SVG vector wrappers.

### 🌐 Pillar 4: Ecosystem & CLI Integrations
- **Phase 4 (v1.0.0+)**:
  - [ ] **Packaged CLI Executable**: Global console script entry point (`lastfm-collage`) installed via `pipx` with animated terminal progress bars.
  - [ ] **Multi-Service Provider Backend**: Pluggable provider interface supporting Spotify Top Items, Apple Music, and ListenBrainz in addition to Last.fm.
  - [ ] **Discord / Slack Bot Webhook Integration**: Native webhook export utilities for automated weekly music bot postings.
```

---

#### Section 12: Codebase Hygiene & Bug Fix Catalog
```markdown
## 🐛 Known Bugs & Defect Catalog

The following known defects in legacy versions (`<= 0.4.13`) have been diagnosed and documented:

| Defect ID | Component | Severity | Description & Root Cause | Resolution Status |
|---|---|---|---|---|
| **BUG-01** | `collage.py:126-130` | **Critical** | Multi-row coordinate bug: `y_1 = y * 2 + TILE_WIDTH` corrupts banner rendering on rows 1..4. | Fixed in v0.5.0 (`y_1 = y + TILE_HEIGHT`). |
| **BUG-02** | `collage_generator.py` | **High** | Convenience methods (`generate_top_albums_collage`) advertised in docs but missing in code. | Added in v0.5.0. |
| **BUG-03** | `collage_generator.py:69` | **Medium** | Missing lower bound validation: `cols <= 0` or `rows <= 0` passes and crashes PIL. | Enforced `1 <= cols <= 5` and `1 <= rows <= 5`. |
| **BUG-04** | `collage.py:234,308` | **Medium** | Missing HTTP timeouts and unhandled network exceptions crash worker threads. | Wrapped with `timeout=(3.05, 10.0)` and blank tile fallback. |
| **BUG-05** | `collage.py:191` | **Low** | Non-deterministic tile order on identical playcounts due to thread arrival order. | Secondary sort key added: `(playcount, title)`. |
```

---

#### Section 13: Contributing Guidelines
```markdown
## 🤝 Contributing

Contributions are warmly welcomed! Please follow these steps:

1. **Fork the Repository** and clone your fork.
2. **Set up virtual environment with `uv`**:
   ```bash
   uv sync
   ```
3. **Create a Feature Branch**:
   ```bash
   git checkout -b feature/my-new-feature
   ```
4. **Author Tests**: Add offline tests in `tests/` utilizing synthetic fixtures.
5. **Run the QA Suite**:
   ```bash
   uv run python .gemini/skills/poetry-test-runner/scripts/run_tests.py --all
   ```
6. **Submit a Pull Request** with a clear explanation of changes and test evidence.
```

---

#### Section 14: License & Acknowledgments
```markdown
## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👤 Authors & Acknowledgments

- **Author**: [@paurieraf](https://github.com/paurieraf) (Pau Riera)
- **Built With**: [pylast](https://github.com/pylast/pylast), [Pillow](https://python-pillow.org/), [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/), and [uv](https://github.com/astral-sh/uv).
```

---

## 5. Verification Method

To verify the recommendations and future implementation:

1. **Markdown Formatting & Lint Verification**:
   - Ensure all markdown links, code blocks, tables, and badge images render cleanly without syntax errors.
2. **API Signature Parity Check**:
   - Verify every Python snippet against `CollageGenerator` in `src/lastfmcollagegenerator/collage_generator.py`.
3. **CLI & Debug Runner Verification**:
   - Test offline mock generation:
     ```bash
     uv run python scripts/debug_collage.py --mock -g 3x3 -e album -o output/test_mock_3x3.png
     uv run python scripts/debug_collage.py --mock -g 5x5 -e artist -o output/test_mock_5x5.png
     ```
   - Assert `test_mock_3x3.png` has size `(900, 900)` and `test_mock_5x5.png` has size `(1500, 1500)`.
4. **Pytest Verification**:
   - Verify all unit and integration tests execute 100% offline with zero live network calls:
     ```bash
     uv run pytest tests/ -v
     ```
