# Project: lastfm-collage-generator Architecture Analysis & Antigravity Tooling

## Architecture
- **Language & Runtime**: Python (^3.8)
- **Packaging & Dependency Management**: uv (`pyproject.toml` with `hatchling` build backend)
- **Core Dependencies**:
  - `pylast` (==5.3.0): Last.fm API client wrapper
  - `requests` (==2.32.3): HTTP requests for image downloads and scraping
  - `Pillow` (==10.4.0): Image processing, grid layout, typography/font rendering
  - `beautifulsoup4` (==4.12.3) & `html5lib` (1.1): HTML scraping of artist images from Last.fm web pages
- **Design Pattern**:
  - **Facade Pattern**: `CollageGenerator` (`src/lastfmcollagegenerator/collage_generator.py`) serves as the single public entrypoint with direct and convenience methods.
  - **Factory Pattern**: `CollageBuilderFactory` (`src/lastfmcollagegenerator/collage.py`) instantiates concrete builders based on entity string.
  - **Builder Pattern**: Abstract `BaseCollageBuilder` (`src/lastfmcollagegenerator/collage.py`) with concrete builders `ArtistCollageBuilder`, `AlbumCollageBuilder`, `TrackCollageBuilder`.
  - **Concurrent Image Acquisition**: `ThreadPoolExecutor` fetches tile artwork asynchronously in parallel before composite assembly.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Album Collage Generation | Fetch top albums via pylast and composite grid with album art | M1 / M2 | survey |
| 2 | Artist Collage Generation | Fetch top artists via pylast, scrape artist image from Last.fm HTML, composite grid | M1 / M2 | survey |
| 3 | Track Collage Generation | Fetch top tracks via pylast, extract track album art or fallback, composite grid | M1 / M2 | survey |
| 4 | Tile Title Overlay Rendering | Optional banner overlay on bottom of each tile showing entity rank/name | M1 / M2 | survey |
| 5 | Custom Grid Dimensions | Configurable `cols` and `rows` for dynamic collage aspect ratios up to 5x5 | M1 / M2 | survey |
| 6 | Time Period Selection | Support for Last.fm periods (`overall`, `7day`, `1month`, `3month`, `6month`, `12month`) | M1 / M2 | survey |
| 7 | General Project Overview Artifact | Full documentation artifact covering architecture, data flow, defects, limitations | M1 | user request |
| 8 | Antigravity Project Rules | Rules in `.gemini/rules/` for Python standards, architecture, testing, and scraping | M2 | user request |
| 9 | Antigravity Custom Skills | Skills in `.gemini/skills/` for test running, mocking fixtures, and CLI workflows | M2 | user request |
| 10 | AGENTS.md Cross-Reference & Synthesis | Author authoritative `AGENTS.md` guiding future AI operations and reconciling drift | M3 | user request |
| 11 | Independent Review & Forensic Audit | Multi-agent review (Reviewers + Challengers + Forensic Auditor) for rule validation, skill schemas, and integrity | M4 | user request |
| 12 | Remediation of Documented Bugs & QA Suite | Fix geometry, validation, timeouts/headers, sorting, and add 100% coverage offline test suite | M5 | user request |

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
- `CollageGenerator.generate(entity: str, username: str, cols: int, rows: int, period: str = "overall") -> PIL.Image.Image`
- `CollageGenerator.generate_top_albums_collage(username: str, cols: int = 5, rows: int = 5, period: str = "overall") -> PIL.Image.Image`
- `CollageGenerator.generate_top_artists_collage(username: str, cols: int = 5, rows: int = 5, period: str = "overall") -> PIL.Image.Image`
- `CollageGenerator.generate_top_tracks_collage(username: str, cols: int = 5, rows: int = 5, period: str = "overall") -> PIL.Image.Image`
- Return: Composited `PIL.Image.Image` in RGB mode with dimensions `(cols * 300, rows * 300)`.

### Builder Interface
- `BaseCollageBuilder.create(username: str) -> PIL.Image.Image`
- `BaseCollageBuilder._get_tiles_from_top_items(user: User, limit: int, period: str) -> List[CollageTile]`

### Antigravity Tooling Contract
- Rules: `.gemini/rules/<name>.md` with clear scope and prescriptive constraints.
- Skills: `.gemini/skills/<skill-name>/SKILL.md` with valid YAML frontmatter (`name`, `description`), optional `scripts/` and `references/`.

## Code Layout
```
lastfm-collage-generator/
├── pyproject.toml                         # Project configuration & dependencies (hatchling backend)
├── uv.lock                                # uv locked dependency versions
├── README.md                              # Public documentation & usage examples
├── PROJECT_OVERVIEW.md                    # Comprehensive architecture & technical analysis
├── AGENTS.md                              # Authoritative AI agent operational guide
│
├── src/lastfmcollagegenerator/            # Source package root
│   ├── __init__.py
│   ├── collage_generator.py               # Facade entrypoint (CollageGenerator)
│   ├── collage.py                         # Factory, BaseCollageBuilder, concrete builders, dataclasses
│   ├── constants.py                       # ENTITIES and PERIODS tuples
│   ├── exceptions.py                      # LastfmCollageGeneratorError, ArtistNotFound, ArtistImageNotFound
│   ├── fonts/                             # TrueType fonts bundled for rendering
│   │   ├── DejaVuSansMono.ttf
│   │   └── DejaVuSansMono-Bold.ttf
│   └── lastfm/                            # Last.fm client adapter module
│       ├── __init__.py
│       └── client.py                      # LastfmClient wrapper over pylast
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
│   │   └── lastfm-scraping-resilience.md
│   └── skills/                            # Executable AI agent skills
│       ├── poetry-test-runner/
│       ├── lastfm-mocking-fixtures/
│       └── collage-cli-workflow/
└── .agents/                               # Orchestrator & subagent metadata
```
