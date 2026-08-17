## Context

See `proposal.md` for motivation. The project currently locks `pylast==5.3.0` and declares Python `>=3.8.1`. Pylast 6.0+ dropped support for Python 3.8 and 3.9, introducing PEP 561 typing (`py.typed`), modernized HTTP connection handling with `httpx`, and proxy configuration refinements.

## Goals / Non-Goals

**Goals:**
- Upgrade `pylast` to `^7.1.0` (or `~=7.1.0`) in `pyproject.toml`.
- Update `requires-python` to `>=3.10` in `pyproject.toml`.
- Regenerate `uv.lock` via `uv lock` / `uv sync`.
- Verify `LastfmClient` type safety and API compatibility.
- Ensure all 44+ offline unit tests pass cleanly.
- Update project documentation (`AGENTS.md`, `PROJECT_OVERVIEW.md`, `README.md`).

**Non-Goals:**
- Replace artist web scraping with external APIs (e.g., Spotify, Deezer) — Last.fm REST API still lacks artist imagery, so web scraping with fallback remains the standard approach.
- Modify collage layout geometry, visual theme pipelines, or typography engines.

## Decisions

### Decision: Upgrade to `pylast>=7.1.0` and Python `>=3.10`
- **Rationale**: `pylast` 6.0+ requires Python 3.10+. Python 3.8 and 3.9 are end-of-life upstream. The project's static analysis (`mypy`) is already configured for Python 3.10. Upgrading allows taking advantage of `py.typed` markers.
- **Alternatives considered**:
  - Pinned `5.3.0`: Retains legacy Python 3.8 support, but misses upstream bug fixes and static type definitions.
  - Upgrade only to `5.5.0`: Keeps Python 3.9, but leaves the package on an older release series.

### Decision: Retain existing artist image retrieval strategy
- **Rationale**: `pylast` removed `Artist.get_cover_image` in v4.0.0 because the Last.fm REST API does not provide artist images. Maintaining `ArtistCollageBuilder` HTML extraction with resilient fallback tiles is necessary without requiring external API keys.

## Risks / Trade-offs

- **[Python Runtime Incompatibility]** Users running Python 3.8 or 3.9 cannot install new versions of `lastfmcollagegenerator`.
  → *Mitigation*: Clearly document Python `>=3.10` in `pyproject.toml`, `README.md`, and `AGENTS.md`.
- **[Upstream API Surface Shifts]** Any minor breaking change in pylast method signatures.
  → *Mitigation*: Automated test suites in `tests/test_client.py` and `tests/test_builders.py` verify all pylast entity interactions.
