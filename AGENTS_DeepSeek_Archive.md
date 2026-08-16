# AGENTS.md: AI Agent Development & Architecture Guide

**Target Repository**: `lastfm-collage-generator`  
**Distributed Package**: `lastfmcollagegenerator` (v0.4.13)  
**Target Python Runtime**: Python `^3.8` (compatible with 3.8, 3.9, 3.10, 3.11, 3.12)  
**Build & Package Manager**: uv (`hatchling`)  
**Primary Architecture Specification**: [`PROJECT_OVERVIEW.md`](./PROJECT_OVERVIEW.md)  
**Antigravity Rules**: [`.gemini/rules/`](./.gemini/rules/)  
**Antigravity Skills**: [`.gemini/skills/`](./.gemini/skills/)

---

## 1. Project Identity & Purpose

`lastfm-collage-generator` is a specialized Python library designed to build visual composite image grids ("collages") from a Last.fm user's listening scrobble history.

### Core Capabilities
- **Multi-Entity Collages**:
  - **Top Albums (`album`)**: Fetches top albums via the Last.fm REST API (`pylast`), downloads cover artwork, and composites them into a grid.
  - **Top Artists (`artist`)**: Fetches top artists via `pylast`, fetches artist hero images directly from `https://www.last.fm/music/<artist>` (as artist images were deprecated in the Last.fm API), thumbnails images to 300x300px, and composites the grid.
  - **Top Tracks (`track`)**: Fetches top tracks via `pylast`, resolves associated album cover art (or applies blank tile fallback), and renders the collage.
- **Configurable Grid Geometry**: Generates rectangular or square grids up to `5x5` (e.g., `3x3`, `5x5`, asymmetric `3x5`). Standard tile size is `300 x 300` pixels.
- **Aggregation Horizons**: Supports all standard Last.fm periods: `7day`, `1month`, `3month`, `6month`, `12month`, `overall`.
- **Title Overlay Banners**: Renders a dark translucent banner overlay on each tile with white monospace typography (`DejaVuSansMono.ttf`) displaying entity name and scrobble playcount.

---

## 2. Technology Stack & Environment Setup

### 2.1 Dependencies & Roles

| Dependency | Version Constraint | Locked Version | Architectural Role |
|---|---|---|---|
| `python` | `^3.8` | 3.8 - 3.12 | Base execution runtime |
| `pylast` | `==5.3.0` | 5.3.0 | Last.fm Audioscrobbler REST API v2.0 wrapper |
| `Pillow` | `==10.4.0` | 10.4.0 | 2D raster image allocation, alpha compositing, font rendering |
| `requests` | `==2.32.3` | 2.32.3 | HTTP client for image downloads and artist HTML retrieval |
| `beautifulsoup4` | `==4.12.3` | 4.12.3 | HTML DOM parsing for artist web retrieval |
| `html5lib` | `1.1` | 1.1 | Standards-compliant HTML5 parser backend |

### 2.2 Bundled Distribution Assets
TrueType fonts are packaged directly inside the distribution package at `src/lastfmcollagegenerator/fonts/`:
- `DejaVuSansMono.ttf`: Default monospace font for tile title and playcount rendering.
- `DejaVuSansMono-Bold.ttf`: Bold monospace font variant.
- Declared in `MANIFEST.in`: `recursive-include src/lastfmcollagegenerator/fonts *.ttf`.

### 2.3 uv Development Commands

```bash
# Install dependencies into virtual environment
uv sync

# Run pytest test suite
uv run pytest tests/

# Execute CLI workflow in offline mock mode
uv run python .gemini/skills/collage-cli-workflow/scripts/generate_collage_cli.py --mock -u testuser -e album -c 3 -r 3 -o collage.png
```

---

## 3. Core Architecture & Design Patterns

The library strictly adheres to a 4-layer object-oriented design: **Facade → Factory → Builder → Client Adapter**.

```
┌────────────────────────────────────────────────────────┐
│ 1. Facade Layer: CollageGenerator                     │
│    - File: src/lastfmcollagegenerator/collage_generator.py│
│    - Public entrypoint, credential storage, validation │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ 2. Factory Layer: CollageBuilderFactory                │
│    - File: src/lastfmcollagegenerator/collage.py       │
│    - Maps ENTITY ("album", "artist", "track") -> Builder│
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ 3. Builder Layer: BaseCollageBuilder & Subclasses      │
│    - File: src/lastfmcollagegenerator/collage.py       │
│    - AlbumCollageBuilder / ArtistCollageBuilder / Track│
│    - ThreadPoolExecutor parallel image acquisition     │
│    - Pillow canvas creation, text wrapping, overlays   │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ 4. Client Adapter Layer: LastfmClient                  │
│    - File: src/lastfmcollagegenerator/lastfm/client.py │
│    - Wraps pylast.LastFMNetwork, isolates API calls    │
└────────────────────────────────────────────────────────┘
```

### 3.1 Component & Class Responsibilities

1. **`CollageGenerator`** (`collage_generator.py`):
   - Single public entrypoint.
   - Enforces parameter validation in `_validate_parameters()` (`cols <= 5`, `rows <= 5`, `entity in ENTITIES`, `period in PERIODS`).
   - Delegates execution to `CollageBuilderFactory`.
2. **`CollageBuilderFactory`** (`collage.py`):
   - Uses `__new__` to instantiate concrete builders (`AlbumCollageBuilder`, `ArtistCollageBuilder`, `TrackCollageBuilder`) based on entity key.
3. **`BaseCollageBuilder`** (`collage.py`):
   - Template Method `create(username)`:
     1. Calls `_get_tiles_from_top_items()` to fetch and download tiles.
     2. Calls `_create_image()` to allocate canvas and paste tiles.
     3. Calls `_insert_tile_title()` to render bottom dark banner and text.
   - Manages concurrent image downloads via `ThreadPoolExecutor`.
   - Generates 300x300 solid black fallback tiles via `_generate_blank_tile()`.
4. **`AlbumCollageBuilder`** (`collage.py`):
   - Queries `lastfm_client.get_top_albums`.
   - Downloads album cover art via `requests.get(item.get_cover_image())`.
5. **`ArtistCollageBuilder`** (`collage.py`):
   - Queries `lastfm_client.get_top_artists`.
   - Fetches `https://www.last.fm/music/<artist>` for `.header-new-background-image`.
   - Thumbnails retrieved image to 300x300px.
6. **`TrackCollageBuilder`** (`collage.py`):
   - Inherits from `AlbumCollageBuilder`. Queries `lastfm_client.get_top_tracks`.
7. **`LastfmClient`** (`lastfm/client.py`):
   - Thin wrapper around `pylast.LastFMNetwork` isolating network credentials.

### 3.2 Internal Data Models (`collage.py`)
- `LastfmConfig`: `@dataclass` holding `lastfm_api_key` and `lastfm_api_secret`.
- `CollageBuilderConfig`: `@dataclass` holding `cols`, `rows`, `period`, and `show_playcount`.
- `CollageTile`: `@dataclass` holding `data: bytes`, `playcount: int`, and `title: str`.
- `CollageConfig`: Dead code dataclass (defined but unused).

---

## 4. Code Layout & File Directory

```
lastfm-collage-generator/
├── pyproject.toml                         # Project configuration & PEP 621 metadata (hatchling backend)
├── uv.lock                                # uv locked dependency versions
├── README.md                              # Public documentation & usage examples
├── LICENSE                                # MIT License
├── MANIFEST.in                            # Asset inclusion declaration (*.ttf fonts)
├── PROJECT_OVERVIEW.md                    # Comprehensive architecture & technical analysis
├── AGENTS.md                              # Authoritative AI agent operational guide (THIS FILE)
│
├── src/lastfmcollagegenerator/            # Source package root
│   ├── __init__.py                        # Package init
│   ├── collage_generator.py               # Facade entrypoint (CollageGenerator)
│   ├── collage.py                         # Factory, BaseCollageBuilder, concrete builders, dataclasses
│   ├── constants.py                       # ENTITIES and PERIODS tuples
│   ├── exceptions.py                      # ArtistNotFound, ArtistImageNotFound
│   ├── fonts/                             # TrueType fonts bundled for rendering
│   │   ├── DejaVuSansMono.ttf             # Regular monospace font
│   │   └── DejaVuSansMono-Bold.ttf        # Bold monospace font
│   └── lastfm/                            # Last.fm client adapter module
│       ├── __init__.py
│       └── client.py                      # LastfmClient wrapper over pylast
│
├── tests/                                 # Automated test directory
│   ├── __init__.py
│   ├── conftest.py                        # (Recommended) Pytest fixtures & synthetic mocks
│   └── ...                                # Test suites
│
├── .gemini/                               # Antigravity operational rules & skills
│   ├── rules/                             # Project-specific architectural rules
│   │   ├── python-standards.md            # Typing, PIL memory safety, exception hierarchy
│   │   ├── architecture-conventions.md    # 4-layer boundaries, font paths, entity extension
│   │   ├── testing-standards.md           # Zero network calls, synthetic fixtures, quality gates
│   │   └── lastfm-network-resilience.md  # User-Agent headers, timeouts, fallback policies
│   └── skills/                            # Executable AI agent skills
│       ├── poetry-test-runner/            # Automated test runner & linting suite
│       │   ├── SKILL.md
│       │   └── scripts/run_tests.py
│       ├── lastfm-mocking-fixtures/       # Synthetic image & pylast mock fixtures
│       │   ├── SKILL.md
│       │   └── references/fixture_templates.py
│       └── collage-cli-workflow/          # CLI executable for live/mock collage generation
│           ├── SKILL.md
│           └── scripts/generate_collage_cli.py
│
└── .agents/                               # Multi-agent orchestrator & worker metadata
```

---

## 5. Coding Standards & Conventions

All agent contributions must comply with the rules established in `.gemini/rules/`:

### 5.1 Python Standards ([`.gemini/rules/python-standards.md`](./.gemini/rules/python-standards.md))
- **Typing Compatibility**: Use `from typing import List, Tuple, Dict, Optional, Union` to ensure full Python 3.8 runtime support.
- **Strict Return Types**: All methods and functions must specify return types (e.g., `-> Image.Image`, `-> List[CollageTile]`).
- **Pillow Lifecycle Management**: Wrap `io.BytesIO` streams and `Image` objects in context managers. Call `stream.seek(0)` before opening byte streams.
- **Exception Hierarchy**: Derive custom exceptions from a centralized `LastfmCollageGeneratorError(Exception)` base class in `exceptions.py`.

### 5.2 Architecture Conventions ([`.gemini/rules/architecture-conventions.md`](./.gemini/rules/architecture-conventions.md))
- **Strict Layer Isolation**:
  - `CollageGenerator` MUST NOT execute PIL drawing or direct HTTP calls.
  - `CollageBuilderFactory` MUST only perform builder dispatch.
  - `LastfmClient` MUST NOT reference Pillow or fonts.
- **Font Path Resolution**: Always resolve bundled fonts relative to `os.path.dirname(__file__)`. Never hardcode absolute filesystem paths.
- **Entity Extension Protocol**: Adding new entities requires declaring the constant in `constants.py`, implementing a `BaseCollageBuilder` subclass, and registering it in `CollageBuilderFactory.entity_collage_builders`.

### 5.3 Testing Standards ([`.gemini/rules/testing-standards.md`](./.gemini/rules/testing-standards.md))
- **Zero Live Network Calls**: Automated tests MUST execute 100% offline. Live calls to Last.fm or CDNs in test runs are strictly prohibited.
- **Synthetic In-Memory Images**: Use `PIL.Image.new()` inside `io.BytesIO` to create test image bytes dynamically without committing binary assets to Git.
- **Visual & Geometric Verification**: Write assertions verifying canvas dimensions `(cols * 300, rows * 300)` and checking pixel bounds.
- **Quality Gate**: Target >90% line coverage and 85% branch coverage.

### 5.4 Last.fm Retrieval Resilience ([`.gemini/rules/lastfm-network-resilience.md`](./.gemini/rules/lastfm-network-resilience.md))
- **Custom User-Agent Required**: Never use default `python-requests` User-Agent. Supply `User-Agent: lastfm-collage-generator/0.5.0 (+https://github.com/paurieraf/lastfm-collage-generator)`.
- **Mandatory Timeouts**: All `requests.get()` calls must provide explicit connect/read timeouts: `timeout=(3.05, 10.0)`.
- **URL Encoding**: Encode artist names via `urllib.parse.quote_plus()`.
- **Blank Tile Fallbacks**: Catch `(ArtistNotFound, ArtistImageNotFound, requests.RequestException, OSError)` and return `_generate_blank_tile()`. Never let network failures abort collage generation.

---

## 6. Custom Skills Catalog & Agent Workflows

Agents should leverage the custom skills in `.gemini/skills/` during development, testing, and debugging:

### 6.1 `poetry-test-runner` ([`.gemini/skills/poetry-test-runner/SKILL.md`](./.gemini/skills/poetry-test-runner/SKILL.md))
Provides unified test execution, coverage calculation, and static analysis:

```bash
# Run unit tests
uv run python .gemini/skills/poetry-test-runner/scripts/run_tests.py --unit

# Run unit tests with code coverage report
uv run python .gemini/skills/poetry-test-runner/scripts/run_tests.py --coverage

# Run linters (flake8, black --check, mypy)
uv run python .gemini/skills/poetry-test-runner/scripts/run_tests.py --lint

# Run entire QA pipeline (tests + coverage >= 90% + linting)
uv run python .gemini/skills/poetry-test-runner/scripts/run_tests.py --all
```

### 6.2 `lastfm-mocking-fixtures` ([`.gemini/skills/lastfm-mocking-fixtures/SKILL.md`](./.gemini/skills/lastfm-mocking-fixtures/SKILL.md))
Provides drop-in fixtures and factories in `references/fixture_templates.py`:
- `SyntheticImageFactory`: Generates raw PNG bytes in memory.
- `MockPylastEntityFactory`: Creates mock `Album`, `Artist`, `Track`, and `TopItem` objects.
- `MockLastfmNetwork` / `MockLastfmClient`: Intercepts `pylast` network instantiation.
- `MockHtmlResponses`: Pre-canned HTML fixtures for testing artist web retrieval.

### 6.3 `collage-cli-workflow` ([`.gemini/skills/collage-cli-workflow/SKILL.md`](./.gemini/skills/collage-cli-workflow/SKILL.md))
Provides a CLI runner (`scripts/generate_collage_cli.py`) for generating live or offline mock collages:

```bash
# Generate 3x3 album collage in offline mock mode (no API keys needed)
uv run python .gemini/skills/collage-cli-workflow/scripts/generate_collage_cli.py \
  --mock -u demo_user -e album -c 3 -r 3 -p 7day -o album_3x3.png

# Generate 5x5 artist collage in offline mock mode
uv run python .gemini/skills/collage-cli-workflow/scripts/generate_collage_cli.py \
  --mock -u demo_user -e artist -c 5 -r 5 -p overall -o artist_5x5.png

# Generate live collage with environment credentials
export LASTFM_API_KEY="your_api_key"
export LASTFM_API_SECRET="your_api_secret"
uv run python .gemini/skills/collage-cli-workflow/scripts/generate_collage_cli.py \
  -u your_username -e album -c 3 -r 3 -o output.png
```

---

## 7. Critical Defects, Pitfalls & Defect Catalog

Agents modifying the codebase must be aware of the following confirmed bugs and technical debt items:

### 7.1 Bug 1: Multi-Row Title Overlay Geometry Bug (`CRITICAL`)
- **Location**: `src/lastfmcollagegenerator/collage.py:126-130`
- **Defective Code**:
  ```python
  y_0 = y + 235
  y_1 = y * 2 + self.TILE_WIDTH
  if y_1 == 0:
      y_1 += self.TILE_WIDTH * 2
  draw.rectangle(((x, y_0), (x + self.TILE_WIDTH, y_1)), (0, 0, 0, 123))
  ```
- **Symptom**: On row 0 (`y=0`), `y_1 = 300` (correct 65px height). On row 1 (`y=300`), `y_1 = 900` (365px height, completely covering row 2). On row 2 (`y=600`), `y_1 = 1500`. Multi-row collages suffer severe visual corruption on all rows below the first.
- **Required Fix**:
  ```python
  y_0 = y + (self.TILE_HEIGHT - 65)  # y + 235
  y_1 = y + self.TILE_HEIGHT         # y + 300
  draw.rectangle(((x, y_0), (x + self.TILE_WIDTH, y_1)), (0, 0, 0, 123))
  ```

### 7.2 Bug 2: Documentation Mismatch on Convenience Methods (`HIGH`)
- **Location**: `README.md:48-49` vs `src/lastfmcollagegenerator/collage_generator.py`
- **Issue**: `README.md` documents calling `collage_generator.generate_top_albums_collage(...)`, but this method does NOT exist in `CollageGenerator`. Calling it raises `AttributeError`.
- **Reconciliation**: When extending `CollageGenerator`, implement convenience methods (`generate_top_albums_collage`, `generate_top_artists_collage`, `generate_top_tracks_collage`) or update `README.md` to reflect `generate()`.

### 7.3 Bug 3: Incomplete Parameter Boundary Validation (`MEDIUM`)
- **Location**: `src/lastfmcollagegenerator/collage_generator.py:69-73`
- **Issue**: `_validate_parameters` checks `cols > 5 or rows > 5`, but does not check `cols < 1 or rows < 1`. Passing `cols=0` or `rows=-1` passes validation and crashes PIL canvas allocation.
- **Required Fix**: Enforce `1 <= cols <= self.MAX_COLS` and `1 <= rows <= self.MAX_ROWS`.

### 7.4 Bug 4: Web Retrieval Fragility & Missing Timeouts (`MEDIUM`)
- **Location**: `src/lastfmcollagegenerator/collage.py:234, 251, 308`
- **Issue**: `requests.get()` is invoked with default User-Agent and no `timeout=...` parameter. Unhandled `requests.RequestException` or CDN 502/503 errors crash worker threads and abort generation.
- **Required Fix**: Supply `DEFAULT_HEADERS`, pass `timeout=(3.05, 10.0)`, and catch all network exceptions to fallback to `_generate_blank_tile()`.

### 7.5 Bug 5: Non-Deterministic Tile Ordering on Tied Playcounts (`LOW`)
- **Location**: `src/lastfmcollagegenerator/collage.py:191`
- **Issue**: `as_completed(futures)` appends tiles in non-deterministic arrival order. Sorting with `tiles.sort(key=lambda x: int(x.playcount), reverse=True)` leaves items with identical playcounts in arbitrary order.
- **Required Fix**: Use a secondary sort key: `tiles.sort(key=lambda x: (int(x.playcount), x.title), reverse=True)`.

### 7.6 Hygiene & Packaging Flaws
- `pyproject.toml:3`: `version = "0.4.13 "` contains a trailing space.
- `collage.py:45`: `CollageConfig` dataclass is unused dead code.
- `tests/`: Currently contains only `__init__.py` (0% test coverage).

---

## 8. Discrepancy Reconciliation Summary

The table below reconciles all contradictions between existing `README.md`, the actual codebase, and architectural best practices:

| Topic / Feature | README.md Statement | Codebase Reality | Architectural Design Spec | Agent Resolution Guidance |
|---|---|---|---|---|
| **Convenience Methods** | Mentions `generate_top_albums_collage()` | Only `generate()` exists; method raises `AttributeError` | Convenience methods should exist on Facade | Implement `generate_top_albums_collage()`, `generate_top_artists_collage()`, `generate_top_tracks_collage()` on `CollageGenerator` delegating to `generate()`. |
| **Grid Boundary Validation** | Mentions "up to 5" rows/cols | Validates `cols > 5`, but permits `0` or negative numbers | Must validate `1 <= cols <= 5` and `1 <= rows <= 5` | Update `_validate_parameters` to check `1 <= cols <= MAX_COLS` and `1 <= rows <= MAX_ROWS`. |
| **Title Overlay Geometry** | Shows visual overlay sample | Math `y * 2 + TILE_WIDTH` corrupts multi-row rendering | Banner must span `y + 235` to `y + 300` on every row | Correct `y_1` calculation to `y + self.TILE_HEIGHT`. |
| **Network Error Handling** | No mention of network failures | Unhandled HTTP exceptions crash collage creation | Resilient fallback to black blank tile | Wrap all HTTP and retrieval calls in `try...except` and return `_generate_blank_tile()`. |
| **Automated Test Coverage** | No mention of tests | `tests/` directory has 0 tests (empty `__init__.py`) | Full offline unit and integration test suite with >90% coverage | Author unit tests covering validation, builders, retrieval, geometry, and mock integration. |
| **Version String** | Lists PyPI package `0.4.13` | `version = "0.4.13 "` in `pyproject.toml` has trailing whitespace | Semantic versioning without whitespace (`0.4.13` or `0.5.0`) | Strip trailing whitespace in `pyproject.toml`. |

---

## 9. Testing & Verification Workflows

When developing or verifying changes, AI agents must follow this workflow:

1. **Verify Offline Isolation**:
   - Ensure all tests run with mock clients and synthetic images.
   - Do NOT run tests that make real requests to Last.fm or external domains.
2. **Execute Pytest Suite**:
   ```bash
   uv run pytest tests/ -v
   ```
3. **Execute CLI Visual Validation**:
   ```bash
   uv run python .gemini/skills/collage-cli-workflow/scripts/generate_collage_cli.py \
     --mock -u testuser -e album -c 3 -r 3 -o test_output.png
   ```
4. **Assert Image Dimensions & Color Properties**:
   - `test_output.png` must have size `(900, 900)`.
   - Banner pixels at `(x, y + 250)` must be dark translucent.
   - Row 1 pixels at `(x, 650)` must NOT be covered by Row 0 overlay.

---

## 10. Agent Checklist for Pull Requests & Code Changes

Before submitting any code modification or bug fix, confirm the following:

- [ ] **No Unrelated Refactoring**: Only modify lines required for the specific task.
- [ ] **Type Annotations**: All new/modified methods include full type annotations compatible with Python 3.8.
- [ ] **Resource Cleanup**: All `io.BytesIO` and `PIL.Image` objects are closed or managed via context managers.
- [ ] **Timeouts & User-Agent**: Any new HTTP request sets `DEFAULT_HEADERS` and `timeout=(3.05, 10.0)`.
- [ ] **Exception Derivation**: New custom exceptions inherit from `LastfmCollageGeneratorError`.
- [ ] **Offline Tests Added**: New functionality or bug fixes include unit tests in `tests/` using synthetic fixtures.
- [ ] **QA Suite Passes**: `uv run python .gemini/skills/poetry-test-runner/scripts/run_tests.py --all` executes cleanly.
