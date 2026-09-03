## Why

The current `README.md` is 829 lines long and acts as an internal engineering design specification rather than an inviting open-source entrypoint. It buries quickstart usage beneath deep architectural matrices, internal bug catalogs (`BUG-01` to `BUG-05`), and PyPI publishing instructions. Developers seeking a Last.fm collage generator in Python need an immediate visual showcase, a 5-line quickstart, and practical use cases without corporate bureaucracy.

## What Changes

- **Refactor `README.md`**: Completely overhaul into a clean, community-oriented guide (~200 lines) following modern Python open-source conventions (inspired by Rich, FastAPI, Pillow, and Spotipy):
  - Add visual hero showcase banner (`assets/showcase.png`).
  - Clear installation via `pip` and `uv`.
  - Immediate 5-line quickstart.
  - Practical use cases: Social Media presets (Instagram Stories 9:16, Twitter headers), GitHub Profile README automation via GitHub Actions, Async Discord/Telegram bots with in-memory buffers, and visual styling/themes.
  - Feature highlights emphasizing strengths (album/artist/track support, scraped high-res artist imagery, auto-scaled grids from 1x1 to 20x20, resilient caching & gradient fallbacks).
  - Straightforward Last.fm API credential setup.
  - Links to advanced documentation and community contribution files.
- **Generate Showcase Asset (`assets/showcase.png`)**: Create a crisp, aesthetic collage preview image demonstrating library output.
- **Create `CONTRIBUTING.md`**: Move developer setup (`uv sync`), offline pytest execution, linting (`flake8`, `black`, `mypy`), debug CLI runner (`scripts/debug_collage.py`), VS Code F5 profiles, and PR checklist out of `README.md` into a dedicated guide for contributors.
- **Create `docs/RELEASING.md`**: Move maintainer-specific packaging and PyPI publishing instructions (`uv publish`, authentication tokens) out of `README.md`.
- **Remove Internal Clutter from Public Readme**: Eliminate internal defect catalogs and redundant class architecture diagrams from `README.md` (retaining them in existing `PROJECT_OVERVIEW.md` and `AGENTS.md`).

## Capabilities

### New Capabilities
None. This change refactors public documentation, developer guidelines, and media assets without altering runtime library capabilities.

### Modified Capabilities
None. No runtime requirements or public API contracts are modified (`skip_specs: true`).

## Impact

- **Public Documentation**: `README.md` becomes significantly more engaging, readable, and focused on consumer adoption.
- **Contributor Experience**: `CONTRIBUTING.md` provides an isolated, comprehensive onboarding guide for open-source contributors.
- **Code & Runtime**: Zero breaking changes or modifications to `src/lastfmcollagegenerator/`.
