# Deep Architectural and Codebase Analysis Report: `lastfm-collage-generator`

**Explorer**: `teamwork_preview_explorer_survey_1`  
**Target Package**: `lastfmcollagegenerator` (v0.4.13)  
**Target Runtime**: Python `^3.8` (compatible with 3.8, 3.9, 3.10, 3.11, 3.12)  
**Date**: 2026-08-16  

---

## 1. Observation

This section documents direct, verbatim codebase observations, exact line numbers, parameter signatures, data models, and configurations across the entire `lastfm-collage-generator` repository.

### 1.1 Source Code Inventory & Layer Mapping (`src/lastfmcollagegenerator/`)

```
src/lastfmcollagegenerator/
├── __init__.py                        # Package root (empty init)
├── collage_generator.py               # Facade Layer: CollageGenerator entrypoint
├── collage.py                         # Factory & Builder Layers: Factory, Builders, Dataclasses
├── constants.py                       # Domain Constants: ENTITIES and PERIODS tuples
├── exceptions.py                      # Exception Hierarchy: ArtistNotFound, ArtistImageNotFound
├── fonts/                             # Bundled Distribution Assets: DejaVuSansMono TrueType fonts
│   ├── DejaVuSansMono.ttf             # 340,712 bytes (Monospace regular)
│   └── DejaVuSansMono-Bold.ttf        # 331,992 bytes (Monospace bold)
└── lastfm/                            # Client Adapter Layer
    ├── __init__.py                    # Client module init
    └── client.py                      # LastfmClient wrapping pylast.LastFMNetwork
```

---

### 1.2 Deep Dive: Facade Layer (`src/lastfmcollagegenerator/collage_generator.py`)

- **Class Definition & Constants** (lines 9–15):
  ```python
  class CollageGenerator:
      MAX_COLS = 5
      MAX_ROWS = 5
  ```
- **Constructor & Credential Storage** (lines 17–21):
  ```python
  def __init__(self, lastfm_api_key: str, lastfm_api_secret: str):
      self.lastfm_config = LastfmConfig(
          lastfm_api_key=lastfm_api_key,
          lastfm_api_secret=lastfm_api_secret
      )
  ```
- **Generation Method** (lines 23–33):
  ```python
  def generate(
          self,
          entity: str,
          username: str,
          cols: int,
          rows: int,
          period: str
  ) -> Image:
      self._validate_parameters(entity, cols, rows, period)
      collage_builder = self._get_collage_builder(entity, cols, rows, period)
      return collage_builder.create(username)
  ```
- **Builder Acquisition** (lines 35–55):
  ```python
  def _get_collage_builder(
          self,
          entity: str,
          cols: int,
          rows: int,
          period: str
  ) -> BaseCollageBuilder:
      collage_builder_config = CollageBuilderConfig(
          cols=cols,
          rows=rows,
          period=period,
      )
      lastfm_client = LastfmClient(
          api_key=self.lastfm_config.lastfm_api_key,
          api_secret=self.lastfm_config.lastfm_api_secret
      )
      return CollageBuilderFactory(
          entity=entity,
          config=collage_builder_config,
          lastfm_client=lastfm_client
      )
  ```
- **Parameter Validation & Boundary Checks** (lines 57–79):
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
- **Observations on Facade Design**:
  - `_validate_parameters` checks `cols > 5 or rows > 5`, but does **not** check `cols < 1` or `rows < 1`. Passing non-positive integers (e.g. `cols=0`, `rows=-1`) passes validation and causes PIL zero-dimension allocation errors.
  - `README.md` documents calling convenience methods such as `collage_generator.generate_top_albums_collage(username="...", cols=5, rows=5, period="7day")`, but `CollageGenerator` only exposes `generate()`. Calling the documented methods raises `AttributeError`.

---

### 1.3 Deep Dive: Factory, Builder & Data Models (`src/lastfmcollagegenerator/collage.py`)

#### 1.3.1 Data Models (lines 23–48)
```python
@dataclass
class LastfmConfig:
    lastfm_api_key: str
    lastfm_api_secret: str

@dataclass
class CollageBuilderConfig:
    cols: int
    rows: int
    period: str
    show_playcount: bool = True

@dataclass
class CollageTile:
    data: bytes
    playcount: int
    title: str

@dataclass
class CollageConfig:
    width: int
    height: int
```
- `CollageConfig` (lines 45–48) is dead code: defined but never instantiated or referenced across the codebase.

#### 1.3.2 BaseCollageBuilder (lines 50–200)
- **Class Constants & Properties**:
  - `FONT_REGULAR_PATH = "fonts/DejaVuSansMono.ttf"`
  - `FONT_BOLD_PATH = "fonts/DejaVuSansMono-Bold.ttf"`
  - `FONT_SIZE = 15`
  - `FONT_BOLD = False`
  - `TILE_WIDTH = 300`
  - `TILE_HEIGHT = 300`
- **Template Method `create(username)`** (lines 71–78):
  - Fetches `user = self.lastfm_client.get_user(username)`.
  - Queries `tiles = self._get_tiles_from_top_items(user=user, limit=cols*rows, period=period)`.
  - Executes `self._create_image(tiles, self.config.cols, self.config.rows)`.
- **Canvas Composition `_create_image`** (lines 80–115):
  - Allocates canvas: `new_image = Image.new("RGB", (cols * 300, rows * 300))`.
  - Iterates over `tiles`: opens `Image.open(BytesIO(tile.data))`, pastes at `cursor = (x, y)`.
  - Formats title: `f"{tile.title}" + (f". ({tile.playcount})" if show_playcount else "")`.
  - Calls `_insert_tile_title(image=new_image, title=title, cursor=cursor)`.
  - Calculates next cursor: `x = cursor[0] + width`; when `cursor[0] >= collage_width - width`, wraps to `y = cursor[1] + height, x = 0`.
- **Overlay & Banner Rendering `_insert_tile_title`** (lines 117–141):
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
- **Text Wrapping `_insert_newline_characters_to_text`** (lines 143–157):
  - Greedily accumulates characters and measures pixel length via `font.getlength(processed_text)`.
  - When `font_w >= 275`, appends accumulated text to `text_lines` and resets `processed_chars`.
  - Does not inspect word boundaries or spaces, splitting words mid-character.
- **Blank Tile Fallback `_generate_blank_tile`** (lines 159–165):
  - Creates 300x300 black image: `Image.new("RGB", (300, 300))` and saves PNG bytes into `BytesIO`.
- **Concurrent Worker Pool `_create_tiles_from_top_items`** (lines 176–193):
  - Submits jobs to `concurrent.futures.ThreadPoolExecutor`.
  - Gathers completed futures via `concurrent.futures.as_completed(futures)`.
  - Sorts results descending: `tiles.sort(key=lambda x: int(x.playcount), reverse=True)`.

#### 1.3.3 Concrete Builder Implementations
- **`ArtistCollageBuilder`** (lines 202–269):
  - `ENTITY = ENTITY_ARTIST ("artist")`.
  - `_get_tiles_from_top_items`: queries `lastfm_client.get_top_artists(user, limit, period)`.
  - Web scraping in `_get_artist_image(artist)`:
    - Requests `https://www.last.fm/music/{urllib.parse.quote_plus(artist.name)}`.
    - Parses HTML DOM with `BeautifulSoup(resp.content, 'html5lib')`.
    - Locates class `.header-new-background-image`, reads `content` URL attribute.
    - Downloads image from URL, creates 300x300 thumbnail via `img.thumbnail((300, 300))`, saves as PNG.
    - Catches `(ArtistNotFound, ArtistImageNotFound)` and returns `_generate_blank_tile()`.
- **`AlbumCollageBuilder`** (lines 270–318):
  - `ENTITY = ENTITY_ALBUM ("album")`.
  - `_get_tiles_from_top_items`: queries `lastfm_client.get_top_albums(user, limit, period)`.
  - `_get_album_cover(item)`: calls `item.get_cover_image()`, catches `IndexError`, downloads via `requests.get(url).content`.
- **`TrackCollageBuilder`** (lines 319–336):
  - `ENTITY = ENTITY_TRACK ("track")`.
  - Subclasses `AlbumCollageBuilder`, overriding `_get_tiles_from_top_items` to query `lastfm_client.get_top_tracks(user, limit, period)`.
  - Inherits `_create_tile_from_top_item` and `_get_album_cover` from `AlbumCollageBuilder`.

#### 1.3.4 Factory Layer: `CollageBuilderFactory` (lines 338–355)
- Uses `__new__` to dispatch to `entity_collage_builders`:
  ```python
  entity_collage_builders = {
      ENTITY_ARTIST: ArtistCollageBuilder,
      ENTITY_ALBUM: AlbumCollageBuilder,
      ENTITY_TRACK: TrackCollageBuilder,
  }
  ```
- Validates entity key and instantiates the concrete builder with `(config, lastfm_client)`.

---

### 1.4 Deep Dive: Client Adapter Layer (`src/lastfmcollagegenerator/lastfm/client.py`)

- **Class `LastfmClient`** (lines 7–44):
  ```python
  class LastfmClient:
      def __init__(self, api_key: str, api_secret: str):
          self.network = pylast.LastFMNetwork(
              api_key=api_key,
              api_secret=api_secret
          )

      def get_user(self, username: str) -> User:
          return self.network.get_user(username)

      @staticmethod
      def get_top_albums(user: User, limit: int, period: str) -> List[TopItem]:
          return user.get_top_albums(period=period, limit=limit)

      @staticmethod
      def get_top_artists(user: User, limit: int, period: str) -> List[TopItem]:
          return user.get_top_artists(period=period, limit=limit)

      @staticmethod
      def get_top_tracks(user: User, limit: int, period: str) -> List[TopItem]:
          return user.get_top_tracks(period=period, limit=limit)
  ```
- Contains TODO comments on lines 22, 31, and 40: *"TODO: It will be necessary to do a custom request because pylast doesn't support page param in this query"*.

---

### 1.5 Supporting Modules: Constants, Exceptions & Assets

- **`constants.py`** (lines 1–20):
  - Imports periods from `pylast`: `PERIOD_7DAYS`, `PERIOD_1MONTH`, `PERIOD_3MONTHS`, `PERIOD_6MONTHS`, `PERIOD_12MONTHS`, `PERIOD_OVERALL`.
  - Defines `ENTITY_ALBUM = "album"`, `ENTITY_ARTIST = "artist"`, `ENTITY_TRACK = "track"`.
  - Exposes `ENTITIES` and `PERIODS` tuples.
- **`exceptions.py`** (lines 1–7):
  - Defines `ArtistNotFound(Exception)` and `ArtistImageNotFound(Exception)`.
  - Neither exception derives from a common package base exception.
- **`fonts/`**:
  - `DejaVuSansMono.ttf` and `DejaVuSansMono-Bold.ttf` packaged inside `src/lastfmcollagegenerator/fonts/`.
  - Declared in `MANIFEST.in`: `recursive-include src/lastfmcollagegenerator/fonts *.ttf`.
- **`pyproject.toml`**:
  - Configured with `hatchling` build backend and Python constraint `>=3.8.1`.
  - Locked production dependencies: `requests==2.32.3`, `pylast==5.3.0`, `Pillow==10.4.0`, `beautifulsoup4==4.12.3`, `html5lib==1.1`.
  - Dev dependencies in `dependency-groups.dev`: `pytest`, `pytest-cov`, `flake8`, `black`, `mypy`.

---

## 2. Logic Chain

This section details the step-by-step reasoning from direct observations to technical mechanics, architectural assessments, defect identification, and extension patterns.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        1. Facade: CollageGenerator                     │
│                        - Validates input parameters                     │
│                        - Stores credentials in LastfmConfig            │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                    2. Factory: CollageBuilderFactory                   │
│                    - Inspects entity ("album"|"artist"|"track")        │
│                    - Instantiates concrete Builder                     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                    3. Builder: BaseCollageBuilder                      │
│                    - Template method: create(username)                 │
│                    - ThreadPoolExecutor parallel image acquisition     │
│                    - Pillow canvas allocation & alpha banner rendering │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                    4. Client Adapter: LastfmClient                     │
│                    - Wraps pylast.LastFMNetwork                        │
│                    - Executes TopItem queries (albums, artists, tracks)│
└────────────────────────────────────────────────────────────────────────┘
```

---

### 2.1 4-Layer Architecture Data Flow & Boundary Isolation

1. **Facade Layer (`CollageGenerator`)**:
   - Isolates consumers from internal complexity (credential packaging, factory dispatch, Pillow canvas initialization).
   - *Boundary Violation / Gap*: Fails to expose fine-grained builder controls (e.g. `show_playcount`, `font_bold`, custom tile dimensions) or provide the convenience methods documented in `README.md`.
2. **Factory Layer (`CollageBuilderFactory`)**:
   - Decouples client callers from concrete builder classes using dynamic `__new__` resolution.
   - Cleanly maps entity strings to specialized builders.
3. **Builder Layer (`BaseCollageBuilder` & Subclasses)**:
   - Employs the **Template Method Pattern**: `create()` enforces the three-stage lifecycle (fetch data -> construct canvas -> composite text/overlays), while subclasses implement entity-specific data extraction.
   - Subclass specialization is minimal and cleanly separated: `AlbumCollageBuilder` uses REST API cover images, `ArtistCollageBuilder` scrapes HTML DOM, and `TrackCollageBuilder` inherits album cover fallback behavior.
4. **Client Adapter Layer (`LastfmClient`)**:
   - Isolates direct dependency on `pylast.LastFMNetwork`.
   - Prevents `pylast` types from leaking into higher rendering layers.

---

### 2.2 Pillow Image Compositing Pipeline Analysis

1. **Canvas Allocation**:
   - `Image.new("RGB", (cols * 300, rows * 300))` creates a solid black 24-bit RGB memory buffer.
2. **Tile Placement**:
   - Tiles are decoded from raw in-memory byte arrays via `Image.open(BytesIO(tile.data))`.
   - Pasted directly onto the canvas at coordinate `(x, y)` calculated by cursor advancement.
3. **Alpha Compositing & Banner Overlay Geometry**:
   - `ImageDraw.Draw(image, "RGBA")` creates a 2D drawing context supporting alpha blending.
   - Banner rectangle intended to cover the bottom 65px of each 300x300 tile with translucent black `(0, 0, 0, 123)`.
4. **Mathematical Breakdown of the Multi-Row Coordinate Drift Defect (`collage.py:126-130`)**:
   - Code:
     ```python
     y_0 = y + 235
     y_1 = y * 2 + self.TILE_WIDTH
     if y_1 == 0:
         y_1 += self.TILE_WIDTH * 2
     draw.rectangle(((x, y_0), (x + self.TILE_WIDTH, y_1)), (0, 0, 0, 123))
     ```
   - Coordinate evaluation across grid rows:
     - **Row 0 (`y = 0`)**: `y_0 = 235`, `y_1 = 0 * 2 + 300 = 300`. Banner spans `235` to `300` (height = `65px`). **Renders correctly.**
     - **Row 1 (`y = 300`)**: `y_0 = 535`, `y_1 = 300 * 2 + 300 = 900`. Tile bottom is at `600`. Banner extends to `900` (height = `365px`), completely covering Row 2 with dark tint.
     - **Row 2 (`y = 600`)**: `y_0 = 835`, `y_1 = 600 * 2 + 300 = 1500`. Banner height = `665px`, obscuring all lower rows.
     - **Row 3 (`y = 900`)**: `y_0 = 1135`, `y_1 = 900 * 2 + 300 = 2100`. Bleeds off the canvas bottom.
   - **Remediation**: The correct calculation is `y_1 = y + self.TILE_HEIGHT` (or `y + 300`), ensuring every banner is strictly 65px tall regardless of row index.
5. **Typography & Font Rendering**:
   - Loads `DejaVuSansMono.ttf` relative to module directory (`os.path.dirname(__file__)`).
   - Monospace font ensures predictable character widths (`font.getlength()`).
   - Line wrapping in `_insert_newline_characters_to_text`: character-based greedy accumulation splitting at 275px. Because it does not check word boundaries, words longer than remaining line capacity are split arbitrarily (e.g. `"Radiohe\nad"`).

---

### 2.3 Concurrency & Sorting Mechanics

1. **Worker Pool Execution**:
   - `_create_tiles_from_top_items` initializes a default `ThreadPoolExecutor()` (spawning `min(32, os.cpu_count() + 4)` worker threads).
   - Submits `_create_tile_from_top_item` for all `limit = cols * rows` items simultaneously.
2. **Non-Deterministic Arrival Order**:
   - Iterating over `concurrent.futures.as_completed(futures)` yields results as network I/O finishes. Faster CDNs or cached DNS responses arrive before slower ones.
3. **Playcount Sorting Non-Determinism**:
   - Code executes: `tiles.sort(key=lambda x: int(x.playcount), reverse=True)`.
   - Python's Timsort is stable. When two tracks/albums share identical scrobble counts (e.g. 5 plays each), their relative ordering is determined by network arrival speed rather than rank.
   - **Remediation**: Include item rank index or title as a secondary sort key: `tiles.sort(key=lambda x: (int(x.playcount), x.title), reverse=True)`.

---

### 2.4 Web Scraping Mechanics & Network Resilience

1. **Scraping Pipeline**:
   - Resolves artist names via URL encoding: `urllib.parse.quote_plus(artist.name)`.
   - Fetches HTML DOM from `https://www.last.fm/music/<artist>`.
   - Parses DOM via `bs4.BeautifulSoup(resp.content, 'html5lib')`.
   - Extracts image URL from CSS class `.header-new-background-image` attribute `content`.
   - Downloads image bytes, resizes to 300x300 thumbnail with aspect ratio preservation, and serializes as PNG bytes.
2. **Vulnerabilities & Resilience Deficiencies**:
   - **Missing User-Agent**: Uses default `python-requests` User-Agent header, triggering 403 Forbidden or CAPTCHA challenges on Cloudflare/Last.fm.
   - **Missing Timeouts**: Invocations of `requests.get()` omit `timeout=...`. A hung connection or stalled CDN blocks thread pool workers indefinitely.
   - **Uncaught HTTP Exceptions**:
     - `AlbumCollageBuilder._get_album_cover`: `requests.get(url).content` does not catch `requests.RequestException`. A 502/503 response or connection drop raises an uncaught exception in the worker thread, causing `future.result()` in `_create_tiles_from_top_items` to crash collage generation.
     - `ArtistCollageBuilder._get_artist_image`: Catches only `(ArtistNotFound, ArtistImageNotFound)`, but not `requests.RequestException` or `PIL.UnidentifiedImageError`.
   - **Single Selector Brittleness**: Relies solely on `.header-new-background-image`. Any Last.fm web redesign immediately breaks all artist collages, causing 100% black tile fallbacks.

---

### 2.5 Extensibility Points & Architecture Expansion

| Extension Dimension | Architectural Integration Point | Implementation Strategy |
|---|---|---|
| **New Entity Types** (e.g. `tag`, `recent_tracks`, `user_friends`) | `constants.py`, `BaseCollageBuilder`, `CollageBuilderFactory` | 1. Add `ENTITY_TAG = "tag"` to `constants.py`.<br>2. Subclass `BaseCollageBuilder` as `TagCollageBuilder`.<br>3. Implement `_get_tiles_from_top_items` and `_create_tile_from_top_item`.<br>4. Register in `CollageBuilderFactory.entity_collage_builders`. |
| **Custom Layout Strategies** (e.g. Hero Tile, Leaderboard, Billboard) | `BaseCollageBuilder._create_image` | Extract canvas layout logic into a **Strategy Pattern** (`GridLayoutStrategy`, `HeroLayoutStrategy`, `LeaderboardLayoutStrategy`). Pass strategy into builder configuration. |
| **Visual Styling & Themes** (e.g. Dark, Light, Neon, Minimalist, No-Banner) | `CollageBuilderConfig`, `_insert_tile_title` | Introduce `StyleConfig` dataclass (banner color, alpha, font family, font size, border width, text color) into `CollageBuilderConfig`. Expose via `CollageGenerator.generate(..., style=...)`. |
| **Caching Layers** (Artwork & Scraped DOM) | `AlbumCollageBuilder`, `ArtistCollageBuilder` | Introduce an HTTP caching session (`requests_cache` or custom disk/memory LRU cache) to avoid redundant network queries for recurring artists/albums across generation runs. |
| **Export Formats & Optimizations** | `BaseCollageBuilder.create` | Add format selection (`PNG`, `JPEG`, `WEBP`) with configurable compression quality settings. |

---

## 3. Caveats

1. **No Live Network Execution in Automated Testing**: Investigation was conducted offline using static code analysis, AST inspection, and offline synthetic mock execution (`scripts/debug_collage.py --mock`). Live Last.fm API queries require external network access and user credentials.
2. **Current Test Suite Inactive**: The existing repository test directory `tests/` contains only `__init__.py` with 0 tests. Test execution assertions rely on the newly added development test tools in `.gemini/skills/`.
3. **Scraping DOM Coupling**: Last.fm web DOM structure may change without notice. Fallback blank tiles mitigate hard crashes, but fallback rate will rise if Last.fm alters CSS classes.

---

## 4. Conclusion

The `lastfm-collage-generator` codebase possesses a clean, well-factored 4-layer object-oriented architecture (Facade -> Factory -> Builder -> Client Adapter) with effective concurrency via `ThreadPoolExecutor`.

However, the analysis revealed **five critical defects and architectural discrepancies**:
1. **Critical Title Overlay Geometry Bug (`collage.py:127`)**: `y_1 = y * 2 + self.TILE_WIDTH` causes exponential coordinate drift, corrupting all multi-row collages below Row 0.
2. **Documentation & API Drift (`README.md:48`)**: `README.md` documents `generate_top_albums_collage()`, which does not exist in `CollageGenerator`.
3. **Incomplete Input Boundary Validation (`collage_generator.py:69`)**: Non-positive integers (`cols <= 0`, `rows <= 0`) pass validation and crash PIL image allocation.
4. **Network Fragility & Missing Timeouts (`collage.py:234, 251, 308`)**: HTTP requests omit custom `User-Agent` headers, timeouts, and comprehensive `requests.RequestException` error handling.
5. **Non-Deterministic Tile Sorting on Equal Playcounts (`collage.py:191`)**: Timsort with a single playcount key produces non-deterministic order on tied scrobbles due to `as_completed` arrival jitter.

Addressing these five items will elevate the codebase to production readiness, opening the path for Phase 2 styling, caching, and custom layout enhancements.

---

## 5. Verification Method

To independently verify all findings, execute the following commands and inspections:

1. **Verify Empty Test Suite**:
   ```bash
   uv run pytest tests/ -v
   # Result: collected 0 items
   ```
2. **Verify Offline Mock Rendering Pipeline**:
   ```bash
   uv run python scripts/debug_collage.py --mock -g 3x3
   # Result: Generates 900x900 PNG at output/debug_mock_album_3x3.png
   ```
3. **Inspect Multi-Row Coordinate Math**:
   - Open `src/lastfmcollagegenerator/collage.py` at lines 126–130.
   - Trace `y=300`: `y_0 = 535`, `y_1 = 300 * 2 + 300 = 900`. Note that tile bounds are `300` to `600`, proving banner overflows into row 2.
4. **Inspect Parameter Validation**:
   - Open `src/lastfmcollagegenerator/collage_generator.py` at line 69.
   - Verify only `cols > self.MAX_COLS` is checked; `cols < 1` is completely absent.
5. **Inspect Public Facade Interface**:
   - Open `src/lastfmcollagegenerator/collage_generator.py`.
   - Verify `generate()` is the sole public generation method; `generate_top_albums_collage()` is not implemented.
