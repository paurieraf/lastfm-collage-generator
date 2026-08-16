# Survey Report: Features, Interfaces, API Client, Rendering Pipeline, and Test Suite

**Author**: Explorer Survey 2  
**Date**: 2026-08-16  
**Target Repository**: `lastfm-collage-generator` (v0.4.13)  
**Location**: `/Users/priera/.gemini/antigravity/worktrees/lastfm-collage-generator/initialize_antigravity_architecture_analysis`

---

## 1. Observation

Direct observations from source files, metadata, and configuration in the workspace:

### 1.1 Project Structure and Build Metadata
- **`pyproject.toml`** (lines 1–33):
  ```toml
  [tool.poetry]
  name = "lastfmcollagegenerator"
  version = "0.4.13 "
  description = "Python library to build Last.fm collages"
  authors = ["Pau Riera <pau.riera.forteza@gmail.com>"]
  readme = "README.md"
  keywords = ["lastfm", "music", "collage", "album", "cover", "artist", "musicbucket", "musicbucket.net"]
  repository = "https://github.com/paurieraf/lastfm-collage-generator"
  homepage = "https://github.com/paurieraf/lastfm-collage-generator"
  classifiers = [
      "Programming Language :: Python :: 3",
      "License :: OSI Approved :: MIT License",
      "Operating System :: OS Independent"
  ]
  packages = [
      { include = "lastfmcollagegenerator", from = "src" }
  ]

  [tool.poetry.urls]
  "Bug Tracker" = "https://github.com/paurieraf/lastfm-collage-generator/issues"

  [tool.poetry.dependencies]
  python = "^3.8"
  requests = "==2.32.3"
  pylast = "==5.3.0"
  Pillow = "==10.4.0"
  beautifulsoup4 = "==4.12.3"
  html5lib = "1.1"

  [build-system]
  requires = ["poetry-core"]
  build-backend = "poetry.core.masonry.api"
  ```
- **`MANIFEST.in`** (line 1):
  ```
  recursive-include src/lastfmcollagegenerator/fonts *.ttf
  ```
- **Font Assets**:
  - `src/lastfmcollagegenerator/fonts/DejaVuSansMono.ttf` (340,712 bytes)
  - `src/lastfmcollagegenerator/fonts/DejaVuSansMono-Bold.ttf` (334,168 bytes)

### 1.2 Public Interface & Entry Points
- **CLI/UI Status**:
  - No `[tool.poetry.scripts]` or entry points defined in `pyproject.toml`.
  - No `__main__.py` or CLI script file in `src/lastfmcollagegenerator/` or root.
  - No UI (GUI/Web) components in repository.
  - The project functions solely as a Python library.
- **Top-Level Class**: `lastfmcollagegenerator.collage_generator.CollageGenerator`
  - `__init__(self, lastfm_api_key: str, lastfm_api_secret: str)` (`collage_generator.py:17-21`)
  - `generate(self, entity: str, username: str, cols: int, rows: int, period: str) -> PIL.Image.Image` (`collage_generator.py:23-33`)
  - `MAX_COLS = 5`, `MAX_ROWS = 5` (`collage_generator.py:14-15`)
- **Documentation Discrepancy (Doc Drift)**:
  - `README.md` (lines 48–49) states:
    ```python
    # Or just call the method directly
    image = collage_generator.generate_top_albums_collage(username="username", cols=5, rows=5, period="7day")
    image.save("5x5 album collage.png", "png")
    ```
  - In `collage_generator.py`, `generate_top_albums_collage` is **not defined**; only `generate()` exists. Calling `generate_top_albums_collage()` raises an `AttributeError`.

### 1.3 Constants and Parameter Domain
- **`constants.py`** (lines 1–20):
  ```python
  from pylast import PERIOD_7DAYS, PERIOD_1MONTH, PERIOD_3MONTHS, PERIOD_6MONTHS, \
      PERIOD_12MONTHS, PERIOD_OVERALL

  ENTITY_ALBUM = "album"
  ENTITY_ARTIST = "artist"
  ENTITY_TRACK = "track"
  ENTITIES = (
      ENTITY_ALBUM,
      ENTITY_ARTIST,
      ENTITY_TRACK
  )
  PERIODS = (
      PERIOD_7DAYS,
      PERIOD_1MONTH,
      PERIOD_3MONTHS,
      PERIOD_6MONTHS,
      PERIOD_12MONTHS,
      PERIOD_OVERALL
  )
  ```
  - `ENTITIES`: `("album", "artist", "track")`
  - `PERIODS`: `("7day", "1month", "3month", "6month", "12month", "overall")`

### 1.4 Parameter Validation
- **`collage_generator.py:57-78`**:
  ```python
  def _validate_parameters(
          self,
          entity: str,
          cols: int,
          rows: int,
          period: str
  ):
      if entity not in ENTITIES:
          raise ValueError(
              f"Invalid entity: {entity}. "
              f"Options are: {ENTITIES}"
          )
      if cols > self.MAX_COLS or rows > self.MAX_ROWS:
          raise ValueError(
              f"Invalid number of columns or rows: {cols}x{rows}: "
              f"Max values are: {self.MAX_ROWS}x{self.MAX_COLS}"
          )
      if period not in PERIODS:
          raise ValueError(
              f"Invalid period: {period}. "
              f"Options are: {PERIODS}"
          )
  ```
  - Missing validation: `cols` and `rows` are not checked for non-positive or negative values (`cols <= 0` or `rows <= 0`).

### 1.5 Last.fm API Client Integration
- **`lastfm/client.py:7-44`**:
  - Initializes `pylast.LastFMNetwork(api_key=api_key, api_secret=api_secret)`.
  - `get_user(username: str) -> pylast.User`: `self.network.get_user(username)`
  - `get_top_albums(user: User, limit: int, period: str) -> List[TopItem]`: `user.get_top_albums(period=period, limit=limit)`
  - `get_top_artists(user: User, limit: int, period: str) -> List[TopItem]`: `user.get_top_artists(period=period, limit=limit)`
  - `get_top_tracks(user: User, limit: int, period: str) -> List[TopItem]`: `user.get_top_tracks(period=period, limit=limit)`
  - Comment in file: `"TODO: It will be necessary to do a custom request because pylast doesn't support page param in this query"`.
  - No retries, timeout configuration, or error transformation implemented.

### 1.6 Collage Builders & Factory
- **`collage.py:23-48` Data Models**:
  - `LastfmConfig(lastfm_api_key: str, lastfm_api_secret: str)`
  - `CollageBuilderConfig(cols: int, rows: int, period: str, show_playcount: bool = True)`
  - `CollageTile(data: bytes, playcount: int, title: str)`
  - `CollageConfig(width: int, height: int)`
- **`collage.py:338-355` Factory**:
  - `CollageBuilderFactory`: maps `ENTITY_ARTIST` to `ArtistCollageBuilder`, `ENTITY_ALBUM` to `AlbumCollageBuilder`, `ENTITY_TRACK` to `TrackCollageBuilder`.

### 1.7 Image Fetching and Web Scraping Mechanism
- **Album / Track Covers** (`collage.py:297-311`):
  - Calls `item.get_cover_image()` from `pylast`.
  - If `IndexError` or `not url`: generates blank tile `_generate_blank_tile()` (black 300x300 PNG).
  - If URL present: `requests.get(url).content`.
  - No explicit resizing or HTTP error catching for album covers.
- **Artist Images** (`collage.py:228-261`):
  - Last.fm API does not provide artist images, so scraping is used.
  - Queries `https://www.last.fm/music/{urllib.parse.quote_plus(artist.name)}`.
  - If status == 404: raises `ArtistNotFound`.
  - Parses HTML using `bs4.BeautifulSoup(resp.content, 'html5lib')`.
  - Selects `soup.find(class_="header-new-background-image").get("content")`.
  - If missing: raises `ArtistImageNotFound`.
  - Fetches image URL via `requests.get(url).content`.
  - Scales image to 300x300 via `img.thumbnail((cls.TILE_WIDTH, cls.TILE_HEIGHT))` and converts to PNG bytes.
  - Catches `(ArtistNotFound, ArtistImageNotFound)` and falls back to blank tile.
- **Concurrency** (`collage.py:176-193`):
  - Uses `concurrent.futures.ThreadPoolExecutor()`.
  - Submits worker per `TopItem`.
  - Collects with `concurrent.futures.as_completed(futures)`.
  - Sorts tiles: `tiles.sort(key=lambda x: int(x.playcount), reverse=True)`.

### 1.8 Image Layout & Text Rendering Pipeline
- **Tile Configuration**:
  - `TILE_WIDTH = 300`, `TILE_HEIGHT = 300`, `FONT_SIZE = 15`, `FONT_BOLD = False`.
  - Canvas creation: `new_image = Image.new("RGB", (cols * 300, rows * 300))`.
- **Text & Overlay Algorithm** (`collage.py:117-141`):
  ```python
  def _insert_tile_title(
          self,
          image: Image,
          title: str,
          cursor: Tuple[int, int]
  ):
      draw = ImageDraw.Draw(image, "RGBA")
      x = cursor[0]
      y = cursor[1]
      y_0 = y + 235
      y_1 = y * 2 + self.TILE_WIDTH
      if y_1 == 0:
          y_1 += self.TILE_WIDTH * 2
      draw.rectangle(((x, y_0), (x + self.TILE_WIDTH, y_1)), (0, 0, 0, 123))

      font_path = self.FONT_BOLD_PATH if self.FONT_BOLD else self.FONT_REGULAR_PATH
      font = ImageFont.truetype(
          f"{self._path}"
          f"/{font_path}",
          self.FONT_SIZE
      )

      title = self._insert_newline_characters_to_text(font, title)
      draw.text((x + 8, y + 240), title, fill=(255, 255, 255), font=font)
  ```
- **Text Wrapping Algorithm** (`collage.py:142-158`):
  - Checks character by character: if `font.getlength(processed_text) >= 275`: breaks line.
  - Word boundaries are not respected (characters wrap mid-word).

### 1.9 Test Suites and CI/CD Status
- **`tests/` Directory**:
  - Only contains `tests/__init__.py` (0 bytes).
  - No test files exist (`test_*.py` or `*_test.py`).
  - No fixtures, mock data, or test runners.
  - Zero test coverage (0%).
- **CI/CD**:
  - No `.github/` directory or GitHub Actions workflows.
  - No Tox/Nox/pre-commit configuration.

---

## 2. Logic Chain

1. **Interface Classification**:
   - Observations 1.1 and 1.2 show no CLI script hooks in `pyproject.toml` and no CLI scripts in `src/`.
   - Therefore, `lastfm-collage-generator` is strictly an importable Python library, with `CollageGenerator` as its primary API.

2. **Documentation & API Mismatch**:
   - Observation 1.2 shows `README.md` line 48 demonstrating `generate_top_albums_collage()`.
   - Observation 1.2 and `collage_generator.py` show only `generate()` is implemented.
   - Therefore, any user following the `README.md` code snippet for direct method invocation will experience an immediate `AttributeError`.

3. **Rendering & Overlay Coordinate Defect**:
   - In `collage.py:126-127`, `y_0 = y + 235` and `y_1 = y * 2 + self.TILE_WIDTH`.
   - When rendering row 0 (`y = 0`): `y_0 = 235`, `y_1 = 300`. Height is 65px (within the 0..300 tile).
   - When rendering row 1 (`y = 300`): `y_0 = 535`, `y_1 = 300 * 2 + 300 = 900`. The tile spans `300..600`, but the overlay rectangle spans `535..900`, bleeding over into subsequent rows (rows 2 and beyond).
   - When rendering row 2 (`y = 600`): `y_0 = 835`, `y_1 = 600 * 2 + 300 = 1500`.
   - Therefore, the formula is defective for any multi-row grid (`rows > 1`). The correct formula for bounding the banner within the tile is `y_1 = y + self.TILE_HEIGHT` (or `y + 300`).

4. **Web Scraping Fragility**:
   - Observation 1.7 shows `ArtistCollageBuilder._get_artist_image` relies on scraping `https://www.last.fm/music/<artist>` and locating the class `.header-new-background-image`.
   - Last.fm does not provide artist images via API. Scraping lacks custom User-Agent headers, session reuse, timeout limits, and fallback strategies if Last.fm updates DOM structure, returns Cloudflare challenges, or rate-limits/blocks requests.

5. **Concurrency and Determinism**:
   - Observation 1.7 shows concurrent image fetching via `ThreadPoolExecutor` and `as_completed()`, followed by `tiles.sort(key=lambda x: int(x.playcount), reverse=True)`.
   - Because `as_completed` finishes in arbitrary network completion order, items with identical play counts will sort stably according to arrival order, producing non-deterministic tile placement across repeated runs for ties.

6. **Missing Tests and Verification Void**:
   - Observation 1.9 confirms no test files exist in `tests/` and no CI pipelines exist.
   - Therefore, any future modifications or refactoring lack regression verification unless a test suite with mocks (for Last.fm API and web scraping) is introduced.

---

## 3. Caveats

1. **Network Live Verification**: The survey was conducted via static code analysis without executing live Last.fm API calls, as external network credentials and live API keys were not configured in the workspace environment.
2. **Font Dependencies**: Bundled TrueType font files (`DejaVuSansMono.ttf` and `DejaVuSansMono-Bold.ttf`) were confirmed present in `src/lastfmcollagegenerator/fonts/` and registered in `MANIFEST.in`.
3. **Pylast Compatibility**: The project is pinned to `pylast == 5.3.0` and `Pillow == 10.4.0` in `pyproject.toml`.

---

## 4. Conclusion & Comprehensive Feature Inventory

### 4.1 Feature Inventory Table

| Feature / Aspect | Implementation / Component | Supported Values / Behavior | Limitations / Notes |
|---|---|---|---|
| **Public API** | `CollageGenerator` (`collage_generator.py`) | `generate(entity, username, cols, rows, period)` | Returns `PIL.Image.Image`. `generate_top_albums_collage` in README is non-existent. |
| **CLI / UI** | None | N/A | Pure Python library; no CLI entry points or GUI/Web apps. |
| **Supported Entities** | `constants.ENTITIES` | `"album"`, `"artist"`, `"track"` | Case-sensitive string check. |
| **Supported Periods** | `constants.PERIODS` | `"7day"`, `"1month"`, `"3month"`, `"6month"`, `"12month"`, `"overall"` | Maps to `pylast.PERIOD_*` constants. |
| **Grid Dimensions** | `cols`, `rows` parameters | Max: `5x5` (`MAX_COLS=5`, `MAX_ROWS=5`) | Minimum limit (`> 0`) is not validated in `_validate_parameters`. |
| **Tile Dimensions** | `BaseCollageBuilder` | Fixed `300x300` px | Hardcoded across all builders. |
| **Overlay Title** | `_insert_tile_title` (`collage.py`) | White text on semi-transparent black banner `(0,0,0,123)` | Formatted as `Title. (playcount)`. Coordinate formula bug affects multi-row collages. |
| **Typography** | Bundled TrueType fonts (`fonts/`) | DejaVu Sans Mono (Regular / Bold, 15px) | Loaded relative to module path; character-based line wrapping at 275px. |
| **Album Cover Pipeline** | `AlbumCollageBuilder` (`collage.py`) | `item.get_cover_image()` -> `requests.get()` | Falls back to blank tile on `IndexError` or null URL. No explicit image resizing. |
| **Track Cover Pipeline** | `TrackCollageBuilder` (`collage.py`) | Inherits from `AlbumCollageBuilder` | Uses track's album cover via `pylast.Track.get_cover_image()`. |
| **Artist Image Pipeline** | `ArtistCollageBuilder` (`collage.py`) | Web scrape `last.fm/music/<artist>` via `BeautifulSoup` & `html5lib` | Extracts `.header-new-background-image`, thumbnails to 300x300. Falls back to blank tile on 404/not found. |
| **Concurrency** | `_create_tiles_from_top_items` | `concurrent.futures.ThreadPoolExecutor` | Fetches tile images concurrently; sorts results descending by play count. |
| **Blank Tile Generator** | `_generate_blank_tile` | Black `300x300` RGB PNG bytes | Used when image lookup fails or cover is absent. |
| **Playcount Display** | `CollageBuilderConfig.show_playcount` | Boolean (`True` by default) | Configured in dataclass, but not exposed as parameter in `CollageGenerator.generate()`. |
| **Test Suite** | `tests/` | None (`tests/__init__.py` only) | 0% test coverage; no unit, integration, or mock tests. |
| **Build & Packaging** | Poetry (`pyproject.toml`) | `poetry build`, `poetry.core.masonry.api` | Python `^3.8` compatibility. Locked dependencies in `poetry.lock`. |

### 4.2 Detailed Error States

1. **Parameter Validation Errors**:
   - `ValueError: Invalid entity: <val>. Options are: ('album', 'artist', 'track')`
   - `ValueError: Invalid number of columns or rows: <cols>x<rows>: Max values are: 5x5`
   - `ValueError: Invalid period: <val>. Options are: ('7day', '1month', '3month', '6month', '12month', 'overall')`
   - Unhandled: `cols <= 0` or `rows <= 0` causes unhandled PIL canvas errors.

2. **Upstream API & Network Exceptions**:
   - `pylast.WSError`: Raised on invalid Last.fm API keys, bad method signatures, or invalid usernames. Not caught by library.
   - `pylast.NetworkError` / `requests.exceptions.RequestException`: Raised on connection timeout/DNS failure during API calls or image fetching.

3. **Scraping Exceptions**:
   - `ArtistNotFound` (`exceptions.py:1-3`): Raised when Last.fm artist page returns HTTP 404. Handled -> returns blank tile.
   - `ArtistImageNotFound` (`exceptions.py:5-7`): Raised when `.header-new-background-image` DOM element is missing. Handled -> returns blank tile.

---

## 5. Verification Method

To independently verify all observations and conclusions:

1. **Verify Interface & Doc Drift**:
   - Inspect `src/lastfmcollagegenerator/collage_generator.py` and `README.md:48`.
   - Run Python command to check available methods on `CollageGenerator`:
     ```bash
     python3 -c "from lastfmcollagegenerator.collage_generator import CollageGenerator; print(dir(CollageGenerator))"
     ```
   - Confirm `generate_top_albums_collage` is missing from `dir(CollageGenerator)`.

2. **Verify Mathematical Overlay Defect**:
   - Inspect `src/lastfmcollagegenerator/collage.py:126-127`.
   - Calculate `y_1` for `y = 300`: `300 * 2 + 300 = 900` (extends 300px beyond row 1's bottom boundary of 600px).

3. **Verify Absence of Tests**:
   - Inspect `tests/` directory:
     ```bash
     ls -la tests/
     ```
   - Confirm only `__init__.py` is present.

4. **Verify Build System & Packaging**:
   - Inspect `pyproject.toml` and `MANIFEST.in`.
   - Run poetry build check (if poetry is installed):
     ```bash
     poetry check
     ```
