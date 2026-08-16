# Comprehensive Multi-Phase Feature Roadmap & Architectural Strategy Report

**Agent**: Explorer 2 (`teamwork_preview_explorer_survey_2`)  
**Target Repository**: `lastfm-collage-generator` (`lastfmcollagegenerator` v0.4.13)  
**Date**: 2026-08-16  
**Document Status**: Final Production-Grade Handoff  

---

## 1. Observation

Direct examination of the current repository structure, source code, tests, and documentation revealed the following exact baseline facts:

### 1.1 Architecture & Component State
- **Entrypoint & Facade (`src/lastfmcollagegenerator/collage_generator.py`)**:
  - `CollageGenerator` encapsulates `LastfmConfig` and exposes `generate(entity, username, cols, rows, period) -> Image` (lines 24-34).
  - Hardcoded bounds: `MAX_COLS = 5`, `MAX_ROWS = 5` (lines 14-15). Parameter validation in `_validate_parameters()` (lines 57-78) checks `cols > 5 or rows > 5` but allows `cols <= 0` or `rows <= 0`.
  - Missing convenience methods documented in `README.md:48` (`generate_top_albums_collage`), resulting in immediate runtime `AttributeError`.
- **Factory & Builders (`src/lastfmcollagegenerator/collage.py`)**:
  - `CollageBuilderFactory` (lines 338-355) instantiates `AlbumCollageBuilder`, `ArtistCollageBuilder`, or `TrackCollageBuilder`.
  - `BaseCollageBuilder` (lines 50-201) defines template method `create()` orchestrating item retrieval, canvas construction, and tile title insertion.
  - Image acquisition runs synchronously via `concurrent.futures.ThreadPoolExecutor` (lines 181-192). Results are collected via `as_completed` and sorted descending by `int(tile.playcount)`.
  - Title overlay math in `_insert_tile_title` (lines 126-130) contains a critical coordinate calculation defect: `y_1 = y * 2 + self.TILE_WIDTH` causes exponential banner height drift on all rows below the first.
  - Typography rendering in `_insert_newline_characters_to_text` (lines 143-157) measures cumulative character width with `font.getlength() >= 275` but splits text mid-word without word-boundary awareness.
  - Solid black 300x300 PNG bytes are generated as the sole fallback via `_generate_blank_tile()` (lines 160-165).
- **Client Adapter & Retrieval (`src/lastfmcollagegenerator/lastfm/client.py` & `collage.py:228-261`)**:
  - `LastfmClient` wraps `pylast.LastFMNetwork` for `get_top_albums`, `get_top_artists`, and `get_top_tracks`.
  - `ArtistCollageBuilder._get_artist_image` fetches `https://www.last.fm/music/<artist>` using `requests.get` and `bs4.BeautifulSoup(..., 'html5lib')` looking for `.header-new-background-image`.
  - HTTP requests lack explicit timeouts, custom `User-Agent` headers, caching, rate limiting, and network exception resilience.
- **Packaging & Testing (`pyproject.toml` & `tests/`)**:
  - `pyproject.toml` uses `hatchling` backend with pinned dependencies (`pylast==5.3.0`, `Pillow==10.4.0`, `requests==2.32.3`, `beautifulsoup4==4.12.3`, `html5lib==1.1`).
  - `tests/` contains only `__init__.py` (0% automated test coverage).

---

## 2. Logic Chain

From these observations, we trace the rationale for a modern, multi-phase evolution:

```
[Observation: Fixed 300x300 black square fallback, 15px monospace text, fixed 65px black banner]
     │
     ▼
[Pillar 1: Visual Styling & Custom Themes]
- Implement ThemeEngine (Dark, Light, Glassmorphic, Gradients, Custom Palettes)
- Implement TypographyEngine (Custom TTF/OTF, auto-scaling, word-boundary wrapping)
- Implement GeometryEngine (Rounded corners, borders, tile padding/margins)
- Implement OverlayRenderer (Full tint, gradient fade, badge/pill, clean mode)

[Observation: Blocking ThreadPoolExecutor, 0 HTTP caching, no rate limiting, burst requests]
     │
     ▼
[Pillar 2: Performance, Caching & Resilience]
- Multi-tier Cache Architecture (In-memory LRU + Persistent SQLite/Disk Cache with TTL)
- AsyncIO / httpx non-blocking concurrent acquisition pipeline
- Resilience Middleware (Token-bucket rate limiting, exponential backoff, circuit breaker)
- Generative Fallbacks (Initials gradients, procedural patterns, custom placeholders)

[Observation: Hardcoded 5x5 rectangular grid, fixed (cols*300, rows*300) canvas, PNG only]
     │
     ▼
[Pillar 3: Advanced Layouts & Modern Formats]
- Layout Strategies (Hero Grid 1+4+16, Bento Grid, Hexagonal Honeycomb, Spiral)
- High-Density Grids (Arbitrary NxM up to 10x10+, dynamic resolution downscaling)
- Modern Export Formats (WebP, AVIF, SVG Vector, Animated GIF/MP4, Print PDF)
- Social Media Presets (Instagram 9:16, Twitter 3:1, Desktop 16:9 / 4K with acrylic blur)

[Observation: Library-only package, no CLI entrypoint, no web server or bot ecosystem]
     │
     ▼
[Pillar 4: CLI & Ecosystem Integrations]
- Rich Standalone CLI (`lastfm-collage`) with progress bars and colorized terminals
- FastAPI / Starlette REST API microservice wrapper with Docker container
- Discord, Telegram, and Slack bot integrations with slash commands
- GitHub Actions & Cron automation workflow for profile README updates
```

---

## 3. Comprehensive 4-Pillar Feature Roadmap Specification

### Pillar 1: Visual Styling & Custom Themes

```
┌────────────────────────────────────────────────────────────────────────────┐
│ PILLAR 1: VISUAL STYLING & CUSTOM THEMES                                   │
├───────────────────────┬──────────────────────┬─────────────┬───────────────┤
│ Feature Item          │ Target Milestone     │ Complexity  │ Prerequisites │
├───────────────────────┼──────────────────────┼─────────────┼───────────────┤
│ 1.1 Dynamic Themes    │ v0.6.0 (Phase 2)     │ Medium      │ v0.5.0 Fixes  │
│ 1.2 Typography Engine │ v0.6.0 (Phase 2)     │ Medium      │ v0.5.0 Fixes  │
│ 1.3 Tile Geometry     │ v0.6.0 (Phase 2)     │ Medium      │ Pillow 10+    │
│ 1.4 Overlay Styles    │ v0.6.0 (Phase 2)     │ Medium      │ Pillow 10+    │
└───────────────────────┴──────────────────────┴─────────────┴───────────────┘
```

#### 1.1 Dynamic Theme Engine
- **Description**: A modular theming subsystem allowing users to select pre-packaged themes or construct custom palettes.
  - **Themes Supported**:
    - `Dark` (default): Charcoal/translucent black overlays with crisp white typography.
    - `Light`: Semi-transparent frosted white banners `(255, 255, 255, 180)` with dark slate text `(20, 20, 20)`.
    - `Glassmorphism`: Acrylic/frosted-glass simulation utilizing localized box/Gaussian blurs (`ImageFilter.GaussianBlur(radius=8)`) beneath translucent banners with subtle white highlight borders.
    - `Gradient Overlays`: Linear (horizontal, vertical, diagonal) and radial alpha gradients blending smoothly from cover art into title metadata.
    - `Custom Palette`: User-defined hex/RGB colors for canvas background, overlay tint, primary title text, secondary playcount text, and accent borders.
- **Architectural Impact**:
  - New module: `src/lastfmcollagegenerator/styling/theme.py` defining `@dataclass class CollageTheme` and `THEME_PRESETS`.
  - Refactor `CollageBuilderConfig` to accept `theme: Union[str, CollageTheme] = "dark"`.
  - Update `BaseCollageBuilder._create_image` and `_insert_tile_title` to delegate rendering parameters to the resolved theme instance.
- **Target Version**: `v0.6.0` (Phase 2)
- **Complexity Rating**: `Medium`
- **Dependencies / Prerequisites**: Pillow 10.4+ (`ImageDraw`, `ImageFilter`, `ImageColor`).

#### 1.2 Configurable Typography & Auto-Scaling Text
- **Description**: Robust font management and text rendering engine.
  - **Font Management**: Ability to supply custom TrueType (`.ttf`) or OpenType (`.otf`) font paths, register custom system font aliases, or select bundled font weights (Regular, Bold, Mono, Sans).
  - **Word-Boundary Wrapping**: Replace character-by-character splitting with word-aware wrapping via Python's `textwrap` module, measuring line pixel widths using `font.getlength()`.
  - **Auto-Scaling Font Size**: Binary search / iterative downscaling algorithm that dynamically decreases font size (e.g., from 16px down to 10px) if a lengthy album/artist title would overflow the banner vertical height, followed by graceful truncation with an ellipsis (`"..."`) only when minimum font size is reached.
- **Architectural Impact**:
  - New module: `src/lastfmcollagegenerator/styling/typography.py` (`TypographyConfig`, `FontManager`, `TextLayoutEngine`).
  - Deprecate `BaseCollageBuilder._insert_newline_characters_to_text()` in favor of `TextLayoutEngine.format_and_scale_text()`.
- **Target Version**: `v0.6.0` (Phase 2)
- **Complexity Rating**: `Medium`
- **Dependencies / Prerequisites**: Python `textwrap`, `Pillow.ImageFont`.

#### 1.3 Customizable Tile Borders, Rounded Corners & Spacing Geometry
- **Description**: Canvas geometry engine supporting modern UI aesthetics.
  - **Corner Radiuses (Rounded Tiles)**: Applies squircle or rounded-corner masking to individual tiles (`radius: int = 12`) via PIL alpha channel masking (`ImageDraw.rounded_rectangle`) before pasting onto canvas.
  - **Tile Borders**: Configurable stroke width (`border_width: int`) and stroke color (`border_color: Tuple[int, int, int, int]`) around each tile.
  - **Tile Spacing & Canvas Margins**: Inter-tile padding (`tile_spacing: int = 10`) and outer canvas margins (`margin: int = 20`).
  - **Dynamic Canvas Size Math**: Canvas dimensions computed dynamically as:
    $$\text{Width} = \text{cols} \times W_{\text{tile}} + (\text{cols} - 1) \times S_{\text{tile}} + 2 \times M$$
    $$\text{Height} = \text{rows} \times H_{\text{tile}} + (\text{rows} - 1) \times S_{\text{tile}} + 2 \times M$$
- **Architectural Impact**:
  - New module: `src/lastfmcollagegenerator/styling/geometry.py` (`GeometryConfig`).
  - Refactor `BaseCollageBuilder._create_image` cursor iteration to apply offsets and alpha mask clipping.
- **Target Version**: `v0.6.0` (Phase 2)
- **Complexity Rating**: `Medium`
- **Dependencies / Prerequisites**: Pillow (`Image.composite`, `ImageDraw.Draw.rounded_rectangle`).

#### 1.4 Overlay Styles & Positioning Engine
- **Description**: Flexible overlay presentation modes.
  - **Overlay Styles**:
    - `Banner` (default): Rectangular lower third strip.
    - `Full Tint`: Translucent tint over entire tile with centered typography.
    - `Gradient Fade`: Smooth alpha fade from transparent at top to opaque at bottom.
    - `Minimalist Badge / Pill`: Compact rounded chip positioned in corner displaying rank + playcount only.
    - `Clean Mode (No-Text)`: Bypasses overlay rendering entirely, producing an immaculate cover-only artwork grid (`show_text=False`).
  - **Positioning**: Configurable overlay placement (`"bottom"`, `"top"`, `"center"`, `"hover_badge"`).
- **Architectural Impact**:
  - New module: `src/lastfmcollagegenerator/styling/overlay.py` (`OverlayStyle` enum, `OverlayPosition` enum, `OverlayRenderer`).
  - Pluggable strategy pattern in `BaseCollageBuilder` delegating overlay drawing to `OverlayRenderer`.
- **Target Version**: `v0.6.0` (Phase 2)
- **Complexity Rating**: `Medium`
- **Dependencies / Prerequisites**: Pillow alpha compositing.

---

### Pillar 2: Performance, Caching & Resilience

```
┌────────────────────────────────────────────────────────────────────────────┐
│ PILLAR 2: PERFORMANCE, CACHING & RESILIENCE                                │
├───────────────────────┬──────────────────────┬─────────────┬───────────────┤
│ Feature Item          │ Target Milestone     │ Complexity  │ Prerequisites │
├───────────────────────┼──────────────────────┼─────────────┼───────────────┤
│ 2.1 Multi-Tier Cache  │ v0.7.0 (Phase 3)     │ High        │ v0.6.0 Core   │
│ 2.2 AsyncIO Pipeline  │ v1.0.0 (Phase 4)     │ Arch / High │ httpx / aio   │
│ 2.3 Resilience Engine │ v0.7.0 (Phase 3)     │ Medium      │ v0.5.0 Fixes  │
│ 2.4 Dynamic Fallbacks │ v0.6.0 (Phase 2)     │ Medium      │ Pillow 10+    │
└───────────────────────┴──────────────────────┴─────────────┴───────────────┘
```

#### 2.1 Multi-Tier Caching Architecture
- **Description**: Comprehensive caching subsystem to eliminate redundant network requests and avoid Last.fm / CDN rate limits.
  - **Tier 1 (L1 In-Memory LRU)**: Thread-safe in-memory cache holding decoded PIL `Image` objects and parsed HTML DOM trees for immediate reuse in long-running services or batch exports (`maxsize=256`).
  - **Tier 2 (L2 Persistent On-Disk Cache)**: SQLite-backed or filesystem-backed cache storing raw image binary payloads, HTTP ETag/Last-Modified metadata, and query responses.
  - **Configurable TTL Policies**:
    - Album cover art & release assets: 30-day TTL (virtually immutable).
    - Retrieved artist hero headers: 7-day TTL.
    - User top scrobble query results: 1-hour to 24-hour TTL (configurable).
  - **Cache Management API**: Methods to clear cache, inspect hit/miss statistics, prune expired records, or set cache directory (`~/.cache/lastfm-collage/`).
- **Architectural Impact**:
  - New package: `src/lastfmcollagegenerator/caching/`:
    - `manager.py`: `CacheManager` facade.
    - `memory.py`: `MemoryLRUCache`.
    - `sqlite.py`: `SqliteCache` with schema `(cache_key TEXT PRIMARY KEY, data BLOB, content_type TEXT, created_at INTEGER, expires_at INTEGER, etag TEXT)`.
  - Integration into `LastfmClient`, `AlbumCollageBuilder`, and `ArtistCollageBuilder`.
- **Target Version**: `v0.7.0` (Phase 3)
- **Complexity Rating**: `High`
- **Dependencies / Prerequisites**: Standard library `sqlite3`, `hashlib`, `time`.

#### 2.2 AsyncIO & Non-Blocking Concurrent Acquisition Pipeline
- **Description**: Modernize the I/O engine from synchronous blocking `ThreadPoolExecutor` + `requests` to native asynchronous coroutines using `httpx` or `aiohttp`.
  - **Asynchronous Architecture**: Full async execution flow (`async def generate_async()`, `async def create_async()`) allowing single-threaded event loops to concurrently fetch 25-100 artwork assets with low memory overhead.
  - **Concurrency Throttling**: Asynchronous semaphore (`asyncio.Semaphore(concurrency_limit=10)`) to prevent socket starvation and network congestion.
  - **Dual API Support**: Maintain seamless synchronous `CollageGenerator.generate()` for scripts and notebooks via internal `asyncio.run()` or dual sync/async client wrappers.
- **Architectural Impact**:
  - New dependency: `httpx >= 0.25.0` (provides both sync and async HTTP client interfaces).
  - New client: `src/lastfmcollagegenerator/lastfm/async_client.py` (`AsyncLastfmClient`).
  - Add async methods to `BaseCollageBuilder`: `create_async()`, `_get_tiles_from_top_items_async()`, `_fetch_tile_async()`.
- **Target Version**: `v1.0.0` (Phase 4)
- **Complexity Rating**: `Architectural / High`
- **Dependencies / Prerequisites**: Python 3.8+ `asyncio`, `httpx`.

#### 2.3 Advanced Rate Limiting, Exponential Backoff & Circuit Breaker
- **Description**: Enterprise-grade network resilience layer for API calls and web retrieval.
  - **Token Bucket Rate Limiting**: Enforces Last.fm's policy of maximum 5 requests per second across all threads/coroutines.
  - **Exponential Backoff with Full Jitter**: Automatically retries transient failures (HTTP 429 Too Many Requests, HTTP 500/502/503/504, connection timeouts) with randomized exponential delays:
    $$T_{\text{sleep}} = \text{random}(0, \min(T_{\text{max}}, T_{\text{base}} \times 2^{\text{attempt}}))$$
  - **Circuit Breaker**: Tracks consecutive retrieval failures. If Last.fm web portal blocks requests or changes DOM structure (e.g. 5 consecutive retrieval failures), the circuit trips to `OPEN`, immediately falling back to synthetic placeholder generation for remaining artists without blocking execution.
- **Architectural Impact**:
  - New module: `src/lastfmcollagegenerator/resilience/` (`rate_limiter.py`, `retry.py`, `circuit_breaker.py`).
  - Injected as middleware into HTTP transport in `LastfmClient` and retrieval routines.
- **Target Version**: `v0.7.0` (Phase 3)
- **Complexity Rating**: `Medium`
- **Dependencies / Prerequisites**: Python stdlib `time`, `random`, `threading`.

#### 2.4 Robust Fallback Strategies for Missing Artwork
- **Description**: Replace unappealing solid black squares with aesthetically pleasing procedural fallback tiles.
  - **Dynamic Initials & Typography Tile**: Generates a smooth pastel or vibrant two-color diagonal gradient based on the SHA-256 hash of the artist/album name, with cleanly rendered large artist/album initials and typography.
  - **Algorithmic Generative Patterns**: Visual hashes (identicons, geometric tessellations, subtle wave/concentric circle patterns) derived from entity metadata.
  - **Custom User Placeholders**: Allows caller to supply a custom placeholder image file path (`placeholder_image="path/to/custom_vinyl.png"`).
- **Architectural Impact**:
  - New module: `src/lastfmcollagegenerator/rendering/fallback.py` (`TileFallbackEngine`, `GradientTileGenerator`, `PatternTileGenerator`).
  - Refactor `BaseCollageBuilder._generate_blank_tile()` to invoke `TileFallbackEngine.generate(title, entity, size)`.
- **Target Version**: `v0.6.0` (Phase 2)
- **Complexity Rating**: `Medium`
- **Dependencies / Prerequisites**: Pillow (`ImageDraw`, `ImageFont`, `colorsys`), Python `hashlib`.

---

### Pillar 3: Advanced Layouts & Modern Formats

```
┌────────────────────────────────────────────────────────────────────────────┐
│ PILLAR 3: ADVANCED LAYOUTS & MODERN FORMATS                                │
├───────────────────────┬──────────────────────┬─────────────┬───────────────┤
│ Feature Item          │ Target Milestone     │ Complexity  │ Prerequisites │
├───────────────────────┼──────────────────────┼─────────────┼───────────────┤
│ 3.1 Non-Uniform Grid  │ v1.0.0 (Phase 4)     │ Arch / High │ GeometryEngine│
│ 3.2 High-Density Grid │ v0.6.0 (Phase 2)     │ Medium      │ v0.5.0 Fixes  │
│ 3.3 Modern Formats    │ v1.0.0 (Phase 4)     │ High        │ Pillow 10+    │
│ 3.4 Social Presets    │ v0.7.0 (Phase 3)     │ Medium      │ ThemeEngine   │
└───────────────────────┴──────────────────────┴─────────────┴───────────────┘
```

#### 3.1 Non-Uniform & Asymmetric Grid Layouts
- **Description**: Elevate collage aesthetics beyond simple uniform grids by supporting varied visual hierarchies.
  - **Layout Architectures**:
    - `Hero Grid (1 + 4 + 16)`: #1 Top entity occupies a prominent large $2\times2$ or $3\times3$ tile block (600x600px), items #2-#5 occupy medium $1\times1$ tiles (300x300px), and remaining items occupy compact $0.5\times0.5$ tiles (150x150px).
    - **Bento Box Grid**: Modern asymmetric editorial grid where tiles dynamically span $2\times1$, $1\times2$, or $1\times1$ cells based on scrobble dominance.
    - **Hexagonal / Honeycomb Grid**: Tiles cropped into regular hexagons via polygon alpha masks and packed into a honeycomb tessellation.
    - **Spiral Grid**: Top scrobbles spiral outwards from the center of the canvas.
- **Architectural Impact**:
  - New package: `src/lastfmcollagegenerator/layouts/`:
    - `base.py`: Abstract `BaseLayoutStrategy` defining `calculate_tile_placements(item_count, canvas_bounds) -> List[TilePlacement]`.
    - `uniform.py`: Standard uniform grid strategy.
    - `hero.py`: `HeroLayoutStrategy`.
    - `bento.py`: `BentoLayoutStrategy`.
    - `hexagonal.py`: `HexagonalLayoutStrategy`.
  - Refactor `BaseCollageBuilder._create_image` to iterate over layout-generated `TilePlacement(x, y, width, height, tile_index, mask_shape)`.
- **Target Version**: `v1.0.0` (Phase 4)
- **Complexity Rating**: `Architectural / High`
- **Dependencies / Prerequisites**: Pillow (`Image.resize(..., Resampling.LANCZOS)`, polygon masking).

#### 3.2 High-Density Grids & Dynamic Scaling
- **Description**: Support high-density matrix collages without artificial dimension limits.
  - **Arbitrary Grid Sizes**: Lift `MAX_COLS = 5` constraint to support arbitrary $N \times M$ grids (e.g. `10x10` for 100 albums, `7x7`, `12x12`).
  - **Dynamic Resolution Scaling**: Configurable maximum canvas bounding box (`max_canvas_dim = 3000`). If a 10x10 grid with 300px tiles would exceed 3000px, tiles are automatically rendered at 150px or 100px resolution with proportional typography scaling.
  - **Memory-Safe Tile Assembly**: Streamlined PIL image allocation preventing high memory consumption during massive matrix rendering.
- **Architectural Impact**:
  - Update `CollageGenerator._validate_parameters` to allow dynamic upper limits (configurable `max_cols: int = 25`).
  - Update `CollageBuilderConfig` to calculate optimal `tile_width` and `tile_height` dynamically based on requested grid dimensions.
- **Target Version**: `v0.6.0` (Phase 2)
- **Complexity Rating**: `Medium`
- **Dependencies / Prerequisites**: Pillow.

#### 3.3 Modern Export Formats & Dynamic Motion
- **Description**: Broaden export capabilities across modern web, vector, print, and video formats.
  - **WebP & AVIF Support**: Direct export to `.webp` (lossy/lossless with quality control) and `.avif` for modern web optimization (reducing file sizes by 60-80% relative to PNG).
  - **SVG Vector Composite**: Export as SVG container embedding base64-encoded cover art with crisp, scalable vector typography (`<text>` nodes) and vector rounded rectangles (`<rect rx="12">`).
  - **PDF Print Export**: High-DPI (300 DPI) PDF rendering for physical poster and card printing.
  - **Animated GIF / MP4 Scrobble Transitions**: Generate animated recaps showing listening evolution across time horizons (e.g., smoothly transitioning from `7day` $\to$ `1month` $\to$ `3month` $\to$ `12month` with crossfade/slide animation).
- **Architectural Impact**:
  - New module: `src/lastfmcollagegenerator/export/` (`exporter.py`, `webp_exporter.py`, `svg_exporter.py`, `animation_exporter.py`).
  - Introduce `CollageResult` object wrapping PIL Image with fluent export methods: `.save_png()`, `.save_webp(quality=85)`, `.save_svg()`, `.to_bytes(format="WEBP")`.
- **Target Version**: `v1.0.0` (WebP/SVG/PDF) / `v1.1.0` (Animated GIF/MP4)
- **Complexity Rating**: `High`
- **Dependencies / Prerequisites**: Pillow, optional `imageio` / `pillow-heif`.

#### 3.4 Social Media Presets & Backdrop Decorators
- **Description**: One-click generation of collages tailored to popular social media formats.
  - **Preset Formats**:
    - `Instagram Story / Reel` (`9:16`, $1080 \times 1920$ px).
    - `Instagram Post` (`1:1` $1080 \times 1080$ px or `4:5` $1080 \times 1350$ px).
    - `Twitter / X Header` (`3:1`, $1500 \times 500$ px).
    - `Twitter / X Post` (`16:9`, $1200 \times 675$ px).
    - `Desktop Wallpaper` (`16:9`, $1920 \times 1080$, $2560 \times 1440$, $3840 \times 2160$ 4K).
    - `Mobile Wallpaper` (`19.5:9`, $1170 \times 2532$ px).
  - **Background Decoration**: Automatically fills non-square aspect ratio letterboxing with an acrylic blurred backdrop derived from the user's #1 top artwork (`ImageFilter.GaussianBlur(radius=30)` with slight dark vignette).
- **Architectural Impact**:
  - New module: `src/lastfmcollagegenerator/styling/presets.py` (`SocialPreset` enum, `AspectDecorator`).
  - Integrated into `CollageGenerator.generate(preset="instagram_story")`.
- **Target Version**: `v0.7.0` (Phase 3)
- **Complexity Rating**: `Medium`
- **Dependencies / Prerequisites**: Pillow (`ImageFilter`, `ImageOps`).

---

### Pillar 4: CLI & Ecosystem Integrations

```
┌────────────────────────────────────────────────────────────────────────────┐
│ PILLAR 4: CLI & ECOSYSTEM INTEGRATIONS                                     │
├───────────────────────┬──────────────────────┬─────────────┬───────────────┤
│ Feature Item          │ Target Milestone     │ Complexity  │ Prerequisites │
├───────────────────────┼──────────────────────┼─────────────┼───────────────┤
│ 4.1 Standalone CLI    │ v0.6.0 (Phase 2)     │ Low-Med     │ Typer / Rich  │
│ 4.2 REST API Server   │ v1.1.0 (Phase 5)     │ Medium      │ FastAPI       │
│ 4.3 Chatbots & Bots   │ v1.2.0 (Phase 5)     │ Med-High    │ Async Engine  │
│ 4.4 Actions / Cron    │ v0.8.0 (Phase 3)     │ Low-Med     │ CLI Runner    │
└───────────────────────┴──────────────────────┴─────────────┴───────────────┘
```

#### 4.1 Full-Featured Standalone CLI Tool
- **Description**: Command-line executable `lastfm-collage` providing an intuitive, beautiful terminal interface.
  - **CLI Capabilities**:
    - Standard flags: `--username`, `--entity` (`album`, `artist`, `track`), `--cols`, `--rows`, `--period`, `--output`, `--theme`, `--layout`, `--preset`.
    - `--mock` mode for local offline generation and visual testing without API keys.
    - Rich interactive UI via `rich`: real-time progress bars with download speeds and ETA, scrobble count summary tables, colorized logging, and optional terminal ASCII artwork preview.
    - Automatic credential resolution from environment variables (`LASTFM_API_KEY`, `LASTFM_API_SECRET`) or local config file (`~/.config/lastfm-collage/config.toml`).
- **Architectural Impact**:
  - New package: `src/lastfmcollagegenerator/cli/` (`main.py`, `commands.py`, `config.py`, `terminal_ui.py`).
  - Declare entry point in `pyproject.toml`:
    ```toml
    [project.scripts]
    lastfm-collage = "lastfmcollagegenerator.cli.main:app"
    ```
- **Target Version**: `v0.6.0` (Phase 2)
- **Complexity Rating**: `Low to Medium`
- **Dependencies / Prerequisites**: `typer >= 0.9.0`, `rich >= 13.0.0`.

#### 4.2 Web Server & REST API Service Wrapper
- **Description**: Production-ready FastAPI microservice wrapper enabling on-demand collage generation as a web service.
  - **API Endpoints**:
    - `GET /api/v1/collage`: Query parameters for username, entity, grid size, period, theme, format (`image/png`, `image/webp`). Streams binary image with HTTP `Cache-Control: public, max-age=3600`.
    - `GET /api/v1/health`: Service health and cache statistics.
    - `GET /docs`: Interactive OpenAPI / Swagger UI.
  - **Deployment Ready**: Bundled multi-stage `Dockerfile` and `docker-compose.yml` for single-command container deployment.
- **Architectural Impact**:
  - Optional dependency extra: `lastfmcollagegenerator[api]`.
  - New package: `src/lastfmcollagegenerator/api/` (`server.py`, `routes.py`, `schemas.py`, `middleware.py`).
- **Target Version**: `v1.1.0` (Phase 5)
- **Complexity Rating**: `Medium`
- **Dependencies / Prerequisites**: `fastapi >= 0.100.0`, `uvicorn[standard] >= 0.22.0`, `pydantic >= 2.0.0`.

#### 4.3 Discord, Telegram & Slack Chatbot Connectors
- **Description**: Ready-to-deploy bot connectors for major chat platforms.
  - **Bot Features**:
    - Slash commands (e.g. `/collage period:7day entity:album size:3x3 theme:glass`).
    - User account binding (`/setuser lastfm_username`).
    - Ephemeral progress updates ("Fetching 3x3 album collage for @user...").
    - Rich embed messages with direct image attachments and scrobble highlights.
- **Architectural Impact**:
  - Optional sub-packages: `src/lastfmcollagegenerator/bots/` (`discord_bot.py`, `telegram_bot.py`, `slack_bot.py`).
- **Target Version**: `v1.2.0` (Phase 5)
- **Complexity Rating**: `Medium to High`
- **Dependencies / Prerequisites**: `discord.py >= 2.3.0`, `python-telegram-bot >= 20.0`, `slack-sdk >= 3.20.0`.

#### 4.4 GitHub Actions & Automated Scheduled Recaps
- **Description**: Automated GitHub Action workflow allowing developers to automatically update their personal GitHub Profile README with their weekly/monthly Last.fm collage.
  - **Capabilities**:
    - Configured via `action.yml` in repository root.
    - Runs on a cron schedule (e.g., every Sunday at midnight).
    - Generates collage, commits asset to profile repository, and updates README markdown link.
    - Supports webhook dispatching to Discord, Telegram, or Mastodon.
- **Architectural Impact**:
  - New root assets: `action.yml`, `.github/workflows/scheduled-collage-example.yml`.
  - CLI subcommand: `lastfm-collage automate --schedule ...`.
- **Target Version**: `v0.8.0` (Phase 3)
- **Complexity Rating**: `Low to Medium`
- **Dependencies / Prerequisites**: GitHub Actions runtime environment, CLI runner.

---

## 4. Multi-Phase Release & Milestone Master Plan

The complete prioritized release schedule is mapped across 5 structured phases:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ MASTER MULTI-PHASE RELEASE TIMELINE                                         │
├─────────┬──────────────────────┬────────────────────────────────────────────┤
│ Phase   │ Version & Target Date│ Core Deliverables                          │
├─────────┼──────────────────────┼────────────────────────────────────────────┤
│ Phase 1 │ v0.5.0 (Immediate)   │ Stability & Defect Remediation:            │
│         │                      │ - Fix multi-row overlay geometry bug       │
│         │                      │ - Strict parameter boundary validation     │
│         │                      │ - HTTP timeouts & custom User-Agent        │
│         │                      │ - Convenience methods on CollageGenerator  │
│         │                      │ - 100% offline pytest suite (>90% cov)     │
│         │                      │ - Word-boundary wrapping foundation        │
├─────────┼──────────────────────┼────────────────────────────────────────────┤
│ Phase 2 │ v0.6.0 (Near-term)   │ Visual Styling, Themes & High-Density:     │
│         │                      │ - Dynamic Theme Engine (Dark/Light/Glass)  │
│         │                      │ - Configurable Typography & Auto-scaling   │
│         │                      │ - Tile Geometry (Rounded corners, borders) │
│         │                      │ - Overlay Styles (Tint, fade, badge, clean)│
│         │                      │ - High-Density Grids (NxM, arbitrary size) │
│         │                      │ - Dynamic Gradient/Pattern Fallbacks       │
│         │                      │ - Standalone Rich CLI (`lastfm-collage`)   │
├─────────┼──────────────────────┼────────────────────────────────────────────┤
│ Phase 3 │ v0.7.0 - v0.8.0      │ Performance, Caching & Social Presets:     │
│         │                      │ - Multi-tier Cache (In-memory + SQLite L2) │
│         │                      │ - Token-bucket rate limiting & retries     │
│         │                      │ - Circuit breaker for web fetcher          │
│         │                      │ - Social Presets (Story 9:16, Banner 3:1)  │
│         │                      │ - Acrylic blur background decorator        │
│         │                      │ - GitHub Action (`action.yml`) automation  │
├─────────┼──────────────────────┼────────────────────────────────────────────┤
│ Phase 4 │ v1.0.0 (Major Release│ Asynchronous Concurrency & Modern Formats: │
│         │                      │ - Native AsyncIO & httpx client pipeline   │
│         │                      │ - Asymmetric Layouts (Hero, Bento, Hexagon)│
│         │                      │ - Modern Export Formats (WebP, SVG, PDF)   │
│         │                      │ - Public API stabilization & type freeze   │
├─────────┼──────────────────────┼────────────────────────────────────────────┤
│ Phase 5 │ v1.1.0 - v1.2.0      │ Web Services, Bots & Motion Ecosystem:     │
│         │                      │ - FastAPI microservice wrapper & Docker    │
│         │                      │ - Discord, Telegram, Slack chat bots       │
│         │                      │ - Animated GIF / MP4 scrobble transitions  │
└─────────┴──────────────────────┴────────────────────────────────────────────┘
```

---

## 5. Architectural Module Mapping & Structural Layout

The proposed directory layout preserves existing package boundaries while cleanly introducing new modules:

```
src/lastfmcollagegenerator/
├── __init__.py                          # Package root exports
├── collage_generator.py                 # Facade (CollageGenerator) with sync/async entrypoints
├── collage.py                           # Legacy compatibility & builder registration
├── constants.py                         # ENTITIES, PERIODS, THEMES, LAYOUTS
├── exceptions.py                        # Centralized LastfmCollageGeneratorError hierarchy
│
├── core/                                # Core data structures & builder abstractions
│   ├── __init__.py
│   ├── config.py                        # CollageBuilderConfig, ThemeConfig, LayoutConfig
│   ├── models.py                        # CollageTile, TilePlacement, CollageResult
│   ├── factory.py                       # CollageBuilderFactory
│   └── builders/                        # Concrete builders
│       ├── base.py                      # BaseCollageBuilder
│       ├── album.py                     # AlbumCollageBuilder
│       ├── artist.py                    # ArtistCollageBuilder (with retrieval resilience)
│       └── track.py                     # TrackCollageBuilder
│
├── styling/                             # Visual Styling & Custom Themes (Pillar 1)
│   ├── __init__.py
│   ├── theme.py                         # CollageTheme, ThemePresets (Dark, Light, Glass)
│   ├── typography.py                    # FontManager, TextLayoutEngine, auto-scaling
│   ├── geometry.py                      # Rounded corners, tile borders, spacing math
│   ├── overlay.py                       # OverlayRenderer (Banner, Tint, Fade, Badge, Clean)
│   └── presets.py                       # SocialPresets (Story, Banner, Wallpaper, Blur)
│
├── caching/                             # Multi-tier Caching Subsystem (Pillar 2)
│   ├── __init__.py
│   ├── manager.py                       # CacheManager facade
│   ├── memory.py                        # In-memory LRU cache
│   └── sqlite.py                        # SQLite persistent disk cache with TTL
│
├── resilience/                          # Concurrency & Resilience (Pillar 2)
│   ├── __init__.py
│   ├── rate_limiter.py                  # Token-bucket rate limiter
│   ├── retry.py                         # Exponential backoff with jitter
│   └── circuit_breaker.py               # Circuit breaker for fetcher
│
├── layouts/                             # Layout Strategies (Pillar 3)
│   ├── __init__.py
│   ├── base.py                          # BaseLayoutStrategy
│   ├── uniform.py                       # NxM uniform grid
│   ├── hero.py                          # Hero 1+4+16 layout
│   ├── bento.py                         # Bento box editorial grid
│   └── hexagonal.py                     # Honeycomb hexagon layout
│
├── export/                              # Modern Export Formats (Pillar 3)
│   ├── __init__.py
│   ├── exporter.py                      # CollageExporter facade
│   ├── webp.py                          # WebP lossy/lossless exporter
│   ├── svg.py                           # Scalable vector graphics exporter
│   └── animation.py                     # Animated GIF/MP4 transition generator
│
├── cli/                                 # Standalone CLI (Pillar 4)
│   ├── __init__.py
│   ├── main.py                          # Typer application entrypoint
│   ├── commands.py                      # CLI commands & flags
│   └── terminal_ui.py                   # Rich progress bars & formatters
│
├── api/                                 # Optional REST API microservice (Pillar 4)
│   ├── __init__.py
│   ├── server.py                        # FastAPI application instance
│   └── routes.py                        # GET /api/v1/collage endpoints
│
├── lastfm/                              # Last.fm Client Adapters
│   ├── __init__.py
│   ├── client.py                        # Sync LastfmClient (wraps pylast)
│   └── async_client.py                  # AsyncLastfmClient (httpx async pipeline)
│
└── fonts/                               # Bundled TrueType typography assets
    ├── DejaVuSansMono.ttf
    └── DejaVuSansMono-Bold.ttf
```

---

## 6. Caveats

1. **Third-Party API & Retrieval Vulnerabilities**:
   - Artist hero image acquisition depends on web retrieval `https://www.last.fm/music/<artist>` because Last.fm's API deprecated artist images. Frontend DOM updates by Last.fm may necessitate updating CSS selectors in `ArtistCollageBuilder`.
   - Rate limiting on Last.fm's web servers requires strict token bucket enforcement (5 req/sec) and persistent disk caching to avoid IP throttling.
2. **Backward Compatibility**:
   - All enhancements to `CollageGenerator.generate()` must maintain full backward compatibility with the signature `generate(entity, username, cols, rows, period)` returning a `PIL.Image.Image`. New styling, layout, and theme options must default to classical values (`theme="dark"`, `layout="uniform"`).
3. **Optional Dependencies & Packaging Footprint**:
   - Advanced ecosystem features (`fastapi`, `uvicorn`, `discord.py`, `moviepy`) must be specified as optional dependency extras (`project.optional-dependencies`) in `pyproject.toml` so the base library remains lightweight and fast to install.

---

## 7. Conclusion

The formulated 4-pillar roadmap transforms `lastfm-collage-generator` from a rudimentary script wrapper into a comprehensive, extensible, and production-ready music visualization framework:
1. **Pillar 1 (Visual Styling & Themes)** delivers rich aesthetic personalization (glassmorphism, custom typography, rounded tiles, versatile overlays).
2. **Pillar 2 (Performance & Resilience)** eliminates network bottlenecks and CDN fragility through multi-tier caching, async acquisition, and generative fallbacks.
3. **Pillar 3 (Advanced Layouts & Modern Formats)** introduces asymmetric editorial layouts (Hero, Bento, Honeycomb) and modern exports (WebP, SVG, Social Presets).
4. **Pillar 4 (CLI & Ecosystem)** expands the project into a multi-platform utility featuring a standalone Rich CLI, FastAPI microservice, Discord/Telegram bots, and GitHub Actions automation.

---

## 8. Verification Method

To independently verify the architecture and roadmap compliance:

1. **Inspect Core Implementation Files**:
   - `src/lastfmcollagegenerator/collage_generator.py`
   - `src/lastfmcollagegenerator/collage.py`
   - `src/lastfmcollagegenerator/lastfm/client.py`
   - `PROJECT_OVERVIEW.md`
   - `AGENTS.md`
2. **Run Pytest Test Suite**:
   ```bash
   uv run pytest tests/ -v
   ```
3. **Validate CLI Mock Workflow**:
   ```bash
   uv run python .gemini/skills/collage-cli-workflow/scripts/generate_collage_cli.py \
     --mock -u testuser -e album -c 3 -r 3 -o test_collage.png
   ```
4. **Assert Image Dimensions & Geometry**:
   - Output canvas size must match `(cols * 300, rows * 300)`.
   - Title overlay rectangle on Row 1 must strictly occupy `y + 235` to `y + 300` (65px height).
