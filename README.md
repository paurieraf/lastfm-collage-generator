![](https://img.shields.io/pypi/dm/lastfmcollagegenerator?)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# lastfm-collage-generator

Python library to create Last.fm collages from user's top items. 

It supports different configurations like grid size, entity types, and time periods.

---

## Features

- Choose entity types: `album`, `artist`, `track`.
- Choose the number of rows and columns (up to 5x5).
- Choose the aggregation period: `7day`, `1month`, `3month`, `6month`, `12month`, `overall` (Default: `7day`).
- Displays dark translucent overlay banners with artist/title and playcount.

---

## Installation

### Using uv
```bash
uv add lastfmcollagegenerator
```

### Using pip
```bash
pip install lastfmcollagegenerator
```

---

## Usage / Examples

```python
from lastfmcollagegenerator.collage_generator import CollageGenerator

collage_generator = CollageGenerator(
    lastfm_api_key="YOUR_API_KEY", 
    lastfm_api_secret="YOUR_API_SECRET"
)

# 1. Standard generate method (returns a PIL Image object)
image = collage_generator.generate(
    entity="album", 
    username="username", 
    cols=5, 
    rows=5, 
    period="7day"
)
image.save("5x5_album_collage.png", "png")

# 2. Or using dedicated convenience methods
album_collage = collage_generator.generate_top_albums_collage(
    username="username", cols=5, rows=5, period="7day"
)

artist_collage = collage_generator.generate_top_artists_collage(
    username="username", cols=3, rows=3, period="overall"
)

track_collage = collage_generator.generate_top_tracks_collage(
    username="username", cols=4, rows=4, period="1month"
)
```

### Options Reference

- **Entity**: `"album"`, `"artist"`, `"track"`
- **Period**: `"7day"`, `"1month"`, `"3month"`, `"6month"`, `"12month"`, `"overall"`
- **Grid Dimensions**: `cols` (1–5), `rows` (1–5)

---

## Development & Debugging

The project uses [uv](https://docs.astral.sh/uv/) for fast, deterministic dependency and environment management.

### Prerequisites & Setup

1. **Install `uv`** (if not already installed):
   ```bash
   # macOS / Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Or using Homebrew
   brew install uv
   ```

2. **Install dependencies and create virtual environment**:
   ```bash
   uv sync
   ```

3. **Configure local environment credentials**:
   Copy `.env.example` to `.env` and fill in your Last.fm API keys and testing username:
   ```bash
   cp .env.example .env
   ```
   ```dotenv
   # .env
   LASTFM_API_KEY=your_api_key_here
   LASTFM_API_SECRET=your_api_secret_here
   LASTFM_USERNAME=your_username_here
   ```

---

### Local Debug Runner (`scripts/debug_collage.py`)

A unified debug runner is provided in `scripts/debug_collage.py` that executes directly against the local `src/` code without requiring any build or installation step.

#### 1. Offline Mock Mode (Instant / 0 Network Calls)
Generates synthetic colored album/artist/track tiles in memory. Ideal for rapidly testing Pillow layouts, font rendering, title banner mathematics, and grid geometries:
```bash
# Generate 3x3 album collage in mock mode
uv run python scripts/debug_collage.py --mock -g 3x3

# Generate 5x5 artist collage and automatically open in system viewer
uv run python scripts/debug_collage.py --mock -e artist -g 5x5 --open
```

#### 2. Live API & Web Retrieval Mode
Pulls real listening data from Last.fm and fetches artist hero imagery using credentials from your `.env`:
```bash
# Run live generation using .env credentials and username
uv run python scripts/debug_collage.py --live

# Customize entity, period, grid size, and open viewer
uv run python scripts/debug_collage.py --live -e artist -g 4x4 -p 1month --open

# Override username or period on the fly
uv run python scripts/debug_collage.py --live -u different_user -e track -p overall
```

#### CLI Options Reference

| Option | Shorthand | Description | Default |
|---|---|---|---|
| `--mock` | | Run offline mock rendering with synthetic tiles | |
| `--live` | | Run live Last.fm queries and web retrieval | |
| `--username` | `-u` | Target Last.fm username | `LASTFM_USERNAME` from `.env` |
| `--entity` | `-e` | `album`, `artist`, or `track` | `DEFAULT_ENTITY` (`album`) |
| `--grid` | `-g` | Shorthand grid dimension (e.g. `3x3`, `5x5`, `4x3`) | `DEFAULT_GRID` (`3x3`) |
| `--cols` / `--rows` | `-c` / `-r` | Custom column and row count (1 to 5) | `3` / `3` |
| `--period` | `-p` | `7day`, `1month`, `3month`, `6month`, `12month`, `overall` | `DEFAULT_PERIOD` (`7day`) |
| `--output` | `-o` | Custom PNG output file destination | `output/debug_<mode>_<entity>_<grid>.png` |
| `--open` | | Automatically open generated image in system image viewer | `False` |
| `--no-title` | | Disable tile overlay banners and playcount text | `False` |

---

### Debugging in Visual Studio Code (F5)

The repository includes pre-configured launch targets in `.vscode/launch.json`:

1. Open any file in `src/lastfmcollagegenerator/` and click next to a line number to set a **breakpoint** (red dot).
2. Go to the **Run & Debug** tab (`Ctrl+Shift+D` / `Cmd+Shift+D`) and select a launch profile:
   - `🎨 Debug: Mock Album Collage (3x3)`: Instant offline debugging with synthetic tiles.
   - `🎨 Debug: Mock Artist Collage (5x5)`: Multi-row offline mock debug.
   - `🌐 Debug: Live Album Collage (.env)`: Live Last.fm API query with `.env` credentials.
   - `🌐 Debug: Live Artist Collage (.env)`: Live Last.fm API query and web retrieval.
   - `🎵 Debug: Live Track Collage (.env)`: Live Track query with cover art fallbacks.
   - `🧪 Debug: Current Test File (Pytest)`: Step-by-step debugging of the active test file.
3. Press **F5**. The debugger will stop at your breakpoints, allowing you to step through code, inspect variables, and use the debug console.

---

### Testing with External Consumer Projects (Editable Mode)

If you need to test the library inside another local application without publishing to PyPI:
```bash
# In your consumer project's virtual environment:
uv pip install -e /path/to/lastfm-collage-generator
# or
pip install -e /path/to/lastfm-collage-generator
```
Any edits you make in `src/` will immediately be reflected in your consumer app without needing to rebuild or reinstall.

---

### Running Tests & Linters

```bash
# Run pytest test suite
uv run pytest tests/

# Run tests with code coverage report
uv run pytest --cov=src/lastfmcollagegenerator tests/

# Run linters & type analysis
uv run flake8 src/ tests/
uv run black --check src/ tests/
uv run mypy src/
```

---

## Packaging & Publishing to PyPI

The project uses `hatchling` as the build backend and `uv` for building and publishing packages.

### 1. Pre-Release Checklist

1. Update the version number in [`pyproject.toml`](file:///Users/priera/.gemini/antigravity/worktrees/lastfm-collage-generator/setup_library_debug_environment/pyproject.toml):
   ```toml
   [project]
   name = "lastfmcollagegenerator"
   version = "0.5.0"
   ```
2. Verify all tests and linters pass:
   ```bash
   uv run pytest tests/
   uv run flake8 src/ tests/
   uv run black --check src/ tests/
   uv run mypy src/
   ```

### 2. Build Distribution Artifacts

Clean previous artifacts and build new source distributions (`.tar.gz`) and binary wheels (`.whl`):
```bash
# Clean previous builds if any
rm -rf dist/

# Build package
uv build
```
This generates the package artifacts in the `dist/` folder:
- `dist/lastfmcollagegenerator-<version>.tar.gz`
- `dist/lastfmcollagegenerator-<version>-py3-none-any.whl`

### 3. Verify Local Distribution (Optional)

Test installing the built wheel in a temporary environment:
```bash
uv pip install dist/lastfmcollagegenerator-*.whl
```

### 4. Publish to PyPI

Upload the distribution packages to PyPI using a PyPI API Token:

```bash
# Option A: Interactive prompt for PyPI token
uv publish

# Option B: Pass PyPI API Token via environment variable
export UV_PUBLISH_TOKEN="pypi-AgEIcHlwaS5vcmc..."
uv publish

# Option C: Publish to TestPyPI first (for verification)
uv publish --publish-url https://test.pypi.org/legacy/
```

---

## License

[MIT](https://choosealicense.com/licenses/mit/)

---

## Authors

- [@paurieraf](https://www.github.com/paurieraf)
