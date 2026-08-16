# Project: lastfm-collage-generator Architecture, Roadmap & Documentation

## Architecture
The `lastfm-collage-generator` library is structured according to a strict 4-layer object-oriented design pattern:
1. **Facade Layer (`CollageGenerator`)**:
   - Primary public interface encapsulating `LastfmConfig` and parameter validation.
   - Enforces grid boundaries (`1 <= cols <= 5`, `1 <= rows <= 5`), entity options (`album`, `artist`, `track`), and periods.
   - Dispatches to `CollageBuilderFactory`.
2. **Factory Layer (`CollageBuilderFactory`)**:
   - Resolves concrete builder classes by entity key (`album` -> `AlbumCollageBuilder`, `artist` -> `ArtistCollageBuilder`, `track` -> `TrackCollageBuilder`).
3. **Builder Layer (`BaseCollageBuilder` & Subclasses)**:
   - Implements Template Method `create(username)` managing `ThreadPoolExecutor` parallel asset fetching, Pillow RGB canvas creation, and translucent monospace banner overlay rendering (`DejaVuSansMono.ttf`).
   - `AlbumCollageBuilder`: Queries top albums via pylast and downloads cover art.
   - `ArtistCollageBuilder`: Queries top artists and scrapes hero images from `last.fm/music/<artist>` via BeautifulSoup + html5lib.
   - `TrackCollageBuilder`: Queries top tracks and extracts associated album artwork with blank tile fallbacks.
4. **Client Adapter Layer (`LastfmClient`)**:
   - Isolates `pylast.LastFMNetwork` API queries.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | 4-Layer Architecture Analysis | Comprehensive analysis of Facade, Factory, Builder, and Client Adapter layers | M1 | Survey |
| 2 | Pillow Pipeline & Banner Math Analysis | Analysis of canvas allocation, coordinate math, and multi-row overlay geometry | M1 | Survey |
| 3 | Concurrency & Sorting Analysis | Analysis of ThreadPoolExecutor, as_completed, and deterministic sorting | M1 | Survey |
| 4 | Scraping Resilience Analysis | Analysis of bs4/html5lib artist scraping, User-Agent, timeouts, and fallbacks | M1 | Survey |
| 5 | Multi-Phase Roadmap: Visual Styling & Themes | Dynamic themes (Dark/Light/Glass), typography, tile geometry, overlay styles | M1 | Survey |
| 6 | Multi-Phase Roadmap: Performance & Caching | Multi-tier LRU/SQLite cache, async pipeline (httpx), rate limiting, fallbacks | M1 | Survey |
| 7 | Multi-Phase Roadmap: Advanced Layouts | Hero grids, bento layouts, honeycomb, arbitrary NxM, WebP/SVG/PDF exports | M1 | Survey |
| 8 | Multi-Phase Roadmap: CLI & Ecosystem | Standalone CLI (`lastfm-collage`), FastAPI microservice, chat bots, actions | M1 | Survey |
| 9 | Production-Grade README Documentation | Exhaustive 14-section README with hero header, architecture, API, and workflows | M2 | Survey |
| 10 | Complete Python API Reference in README | Accurate constructor, generate(), convenience methods, and PIL Image guide | M2 | Survey |
| 11 | Developer & Debugging Workflows in README | Documentation for `scripts/debug_collage.py`, mock/live modes, and VS Code | M2 | Survey |
| 12 | Test Suite Verification & Quality Gate | Reviewers, Challengers, and Forensic Auditor verification and test suite run | M3 | Survey |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Architectural & Roadmap Synthesis | Synthesize codebase analysis and 4-pillar multi-phase roadmap | none | DONE |
| M2 | Production README Implementation | Worker updates `README.md` to production standard with all 14 sections | M1 | PLANNED |
| M3 | Quality Gate, Review & Forensic Audit | 2 Reviewers, 2 Challengers, and 1 Forensic Auditor verify docs, API, and tests | M2 | PLANNED |

## Interface Contracts
### Facade Layer ↔ Factory Layer
- `CollageGenerator._get_collage_builder(entity: str, cols: int, rows: int, period: str) -> BaseCollageBuilder`
- Passes `CollageBuilderConfig(cols, rows, period, show_playcount)` and `LastfmClient(api_key, api_secret)` to `CollageBuilderFactory`.

### Factory Layer ↔ Concrete Builders
- `CollageBuilderFactory(entity: str, config: CollageBuilderConfig, lastfm_client: LastfmClient) -> BaseCollageBuilder`
- Returns instance of `AlbumCollageBuilder`, `ArtistCollageBuilder`, or `TrackCollageBuilder`.

### Builder Layer ↔ Client Adapter
- `BaseCollageBuilder.lastfm_client.get_user(username: str) -> pylast.User`
- `AlbumCollageBuilder`: `lastfm_client.get_top_albums(user, limit, period) -> List[pylast.TopItem]`
- `ArtistCollageBuilder`: `lastfm_client.get_top_artists(user, limit, period) -> List[pylast.TopItem]`
- `TrackCollageBuilder`: `lastfm_client.get_top_tracks(user, limit, period) -> List[pylast.TopItem]`

## Code Layout
```
lastfm-collage-generator/
├── pyproject.toml                         # Project configuration & PEP 621 metadata (hatchling backend)
├── README.md                              # Public documentation & usage examples (Worker target)
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
│   ├── exceptions.py                      # ArtistNotFound, ArtistImageNotFound
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
├── tests/                                 # Automated test directory
│   ├── __init__.py
│   └── ...                                # Test suites
│
└── .agents/                               # Multi-agent orchestrator & worker metadata
```
