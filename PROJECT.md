# Project: lastfm-collage-generator Architecture, Roadmap & Documentation

## Architecture
The `lastfm-collage-generator` library is structured according to a strict 4-layer object-oriented design pattern:
1. **Facade Layer (`CollageGenerator`)**:
   - Primary public interface encapsulating `LastfmConfig` and parameter validation.
   - Enforces grid boundaries (`1 <= cols <= 20`, `1 <= rows <= 20`, `cols * rows <= 400`), `50 <= tile_size <= 600`, entity options (`album`, `artist`, `track`), non-empty usernames, and periods.
   - Exposes direct `generate()` and convenience methods (`generate_top_albums_collage()`, `generate_top_artists_collage()`, `generate_top_tracks_collage()`).
   - Dispatches to `CollageBuilderFactory`.
2. **Factory Layer (`CollageBuilderFactory`)**:
   - Resolves concrete builder classes by entity key (`album` -> `AlbumCollageBuilder`, `artist` -> `ArtistCollageBuilder`, `track` -> `TrackCollageBuilder`).
3. **Builder Layer (`BaseCollageBuilder` & Subclasses)**:
   - Implements Template Method `create(username)` managing `ThreadPoolExecutor` parallel asset fetching, Pillow RGB canvas creation, and translucent monospace banner overlay rendering (`DejaVuSansMono.ttf`).
   - `AlbumCollageBuilder`: Queries top albums via pylast and downloads cover art with timeout and blank tile fallbacks.
   - `ArtistCollageBuilder`: Queries top artists and fetches hero images from `last.fm/music/<artist>` via BeautifulSoup + html5lib with custom User-Agent and timeouts.
   - `TrackCollageBuilder`: Queries top tracks and extracts associated album artwork with blank tile fallbacks.
4. **Client Adapter Layer (`LastfmClient`)**:
   - Isolates `pylast.LastFMNetwork` API queries.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Album Collage Generation | Fetch top albums via pylast and composite grid with album art | M1 | Survey |
| 2 | Artist Collage Generation | Fetch top artists via pylast, fetch artist image from Last.fm HTML, composite grid | M1 | Survey |
| 3 | Track Collage Generation | Fetch top tracks via pylast, extract track album art or fallback, composite grid | M1 | Survey |
| 4 | Tile Title Overlay Rendering | Optional banner overlay on bottom of each tile showing entity rank/name | M1 | Survey |
| 5 | Custom Grid Dimensions | Configurable `cols` and `rows` for dynamic collage aspect ratios up to 5x5 | M1 | Survey |
| 6 | Time Period Selection | Support for Last.fm periods (`overall`, `7day`, `1month`, `3month`, `6month`, `12month`) | M1 | Survey |
| 7 | General Project Overview Artifact | Full documentation artifact covering architecture, data flow, defects, limitations | M1 | Survey |
| 8 | Antigravity Project Rules | Rules in `.gemini/rules/` for Python standards, architecture, testing, and retrieval | M2 | Survey |
| 9 | Antigravity Custom Skills | Skills in `.gemini/skills/` for test running, mocking fixtures, and CLI workflows | M2 | Survey |
| 10 | AGENTS.md Cross-Reference & Synthesis | Author authoritative `AGENTS.md` guiding future AI operations and reconciling drift | M3 | Survey |
| 11 | Independent Review & Forensic Audit | Multi-agent review (Reviewers + Challengers + Forensic Auditor) for rule validation, skill schemas, and integrity | M4 | Survey |
| 12 | Remediation of Documented Bugs & QA Suite | Fix geometry, validation, timeouts/headers, sorting, and add 100% coverage offline test suite | M5 | Survey |

## Milestones
| # | Name | Scope | Dependencies | Status | Key Outputs |
|---|------|-------|-------------|--------|-------------|
| 1 | General Project Overview Artifact | Author comprehensive `PROJECT_OVERVIEW.md` detailing architecture, data models, rendering pipeline, defects, and recommendations | Survey | DONE | `PROJECT_OVERVIEW.md` (654 lines) |
| 2 | Antigravity Rules & Custom Skills | Generate `.gemini/rules/*.md` and `.gemini/skills/*/SKILL.md` (plus scripts/references) following `agy-customizations` | M1 | DONE | 4 rules in `.gemini/rules/`, 3 skills in `.gemini/skills/` |
| 3 | AGENTS.md Reconciliation & Synthesis | Cross-reference repository findings with `AGENTS.md`, establish guidance for AI agents | M2 | DONE | `AGENTS.md` (authoritative multi-agent guide) |
| 4 | Independent Verification & Audit | Multi-agent review (Reviewers + Challengers + Forensic Auditor) for rule validation, skill schemas, and integrity | M3 | DONE | `GATE_STATUS.md` PASS, 4 APPROVE verdicts, 1 CLEAN audit |
| 5 | Remediation of Documented Bugs & QA Suite | Fix overlay geometry, convenience methods, validation, resilience, and establish 100% offline test suite | M4 | DONE | 44 passing unit tests, 100% coverage, OpenSpec archived change |

## Interface Contracts
### Facade Entrypoint
- `CollageGenerator.generate(entity: str, username: str, cols: int, rows: int, period: str = "overall", tile_size: Optional[int] = None) -> PIL.Image.Image`
- `CollageGenerator.generate_top_albums_collage(username: str, cols: int = 5, rows: int = 5, period: str = "overall", tile_size: Optional[int] = None) -> PIL.Image.Image`
- `CollageGenerator.generate_top_artists_collage(username: str, cols: int = 5, rows: int = 5, period: str = "overall", tile_size: Optional[int] = None) -> PIL.Image.Image`
- `CollageGenerator.generate_top_tracks_collage(username: str, cols: int = 5, rows: int = 5, period: str = "overall", tile_size: Optional[int] = None) -> PIL.Image.Image`
- Return: Composited `PIL.Image.Image` in RGB mode with dimensions `(cols * tile_size, rows * tile_size)`.

### Builder Interface
- `BaseCollageBuilder.create(username: str) -> PIL.Image.Image`
- `BaseCollageBuilder._get_tiles_from_top_items(user: User, limit: int, period: str) -> List[CollageTile]`

### Builder Layer ↔ Client Adapter
- `BaseCollageBuilder.lastfm_client.get_user(username: str) -> pylast.User`
- `AlbumCollageBuilder`: `lastfm_client.get_top_albums(user, limit, period) -> List[pylast.TopItem]`
- `ArtistCollageBuilder`: `lastfm_client.get_top_artists(user, limit, period) -> List[pylast.TopItem]`
- `TrackCollageBuilder`: `lastfm_client.get_top_tracks(user, limit, period) -> List[pylast.TopItem]`

## Code Layout
```
lastfm-collage-generator/
├── pyproject.toml                         # Project configuration & PEP 621 metadata (hatchling backend)
├── uv.lock                                # uv locked dependency versions
├── README.md                              # Public documentation & usage examples
├── LICENSE                                # MIT License
├── MANIFEST.in                            # Asset inclusion declaration (*.ttf fonts)
├── PROJECT_OVERVIEW.md                    # Comprehensive architecture & technical analysis
├── AGENTS.md                              # Authoritative AI agent operational guide
│
├── src/lastfmcollagegenerator/            # Source package root
│   ├── __init__.py                        # Package init
│   ├── collage_generator.py               # Facade entrypoint (CollageGenerator)
│   ├── collage.py                         # Factory, BaseCollageBuilder, concrete builders, dataclasses
│   ├── constants.py                       # ENTITIES and PERIODS tuples
│   ├── exceptions.py                      # LastfmCollageGeneratorError, ArtistNotFound, ArtistImageNotFound
│   ├── fonts/                             # TrueType fonts bundled for rendering
│   │   ├── DejaVuSansMono.ttf             # Regular monospace font
│   │   └── DejaVuSansMono-Bold.ttf        # Bold monospace font
│   └── lastfm/                            # Last.fm client adapter module
│       ├── __init__.py
│       └── client.py                      # LastfmClient wrapper over pylast
│
├── scripts/                               # Development and debugging runner scripts
│   └── debug_collage.py                   # Zero-build CLI runner with --mock and --live modes
│
├── tests/                                 # Automated test directory (44 offline unit tests, 100% coverage)
│   ├── __init__.py
│   ├── conftest.py                        # Synthetic image and pylast mock fixtures
│   ├── test_builders.py                   # Builder dispatch, sorting, text wrapping tests
│   ├── test_client.py                     # LastfmClient adapter tests
│   ├── test_facade.py                     # CollageGenerator direct and convenience method tests
│   ├── test_geometry.py                   # Multi-row overlay coordinate geometry tests
│   ├── test_resilience.py                 # Network error fallback, timeout, and exception hierarchy tests
│   └── test_validation.py                 # Input parameter and boundary validation tests
│
├── .gemini/                               # Antigravity operational rules & skills
│   ├── rules/                             # Project-specific architectural rules
│   │   ├── python-standards.md
│   │   ├── architecture-conventions.md
│   │   ├── testing-standards.md
│   │   └── lastfm-network-resilience.md
│   └── skills/                            # Executable AI agent skills
│       ├── poetry-test-runner/
│       ├── lastfm-mocking-fixtures/
│       └── collage-cli-workflow/
└── .agents/                               # Orchestrator & subagent metadata
```
