## Why

The `lastfm-collage-generator` library contains several critical architectural and implementation defects documented in `PROJECT_OVERVIEW.md` and `AGENTS.md`. Specifically:
1. Multi-row collages suffer severe visual corruption because title overlay math expands exponentially across rows instead of staying bounded to 65px per tile.
2. The facade API lacks documented convenience methods (`generate_top_albums_collage`, etc.), throwing `AttributeError`.
3. Input validation permits zero/negative dimensions, empty usernames, and invalid types.
4. HTTP requests lack explicit timeouts, User-Agent headers, and resilient fallbacks when Last.fm/CDNs drop connections.
5. Tile ordering when scrobble counts tie is non-deterministic due to thread-pool completion order.
6. The project has 0% test coverage and lacks a unified exception hierarchy.

Remediating these defects establishes a stable, robust, and reliable foundation for the library.

## What Changes

- **Fix Title Overlay Geometry**: Correct coordinate arithmetic in `BaseCollageBuilder._insert_tile_title` so that title overlays are strictly bounded to `[y + 235, y + 300]` on every grid row.
- **Implement Facade Convenience Methods**: Add `generate_top_albums_collage`, `generate_top_artists_collage`, and `generate_top_tracks_collage` to `CollageGenerator` delegating to `generate()`.
- **Harden Parameter & Type Validation**: Enforce `1 <= cols <= MAX_COLS`, `1 <= rows <= MAX_ROWS`, non-empty trimmed username, valid entity and period checks, raising clear `ValueError` or `TypeError`.
- **Network Resilience & Timeouts**: Configure custom `User-Agent` headers, standard connect/read timeouts (`timeout=(3.05, 10.0)`), and exception handling (`requests.RequestException`, `ArtistNotFound`, `ArtistImageNotFound`, `OSError`) falling back to `_generate_blank_tile()`.
- **Deterministic Tile Ordering**: Ensure secondary sort key by entity title `(int(playcount), title)` so equal scrobble counts produce reproducible collage layouts.
- **Exception Hierarchy**: Introduce `LastfmCollageGeneratorError` base exception in `exceptions.py` from which `ArtistNotFound` and `ArtistImageNotFound` inherit.
- **Comprehensive Offline Test Suite**: Implement unit and integration tests with `pytest` using synthetic PIL fixtures and mock Last.fm client, covering 100% of remediated paths with zero live network calls.
- **Hygiene & Packaging**: Clean up unused dataclasses/imports in `collage.py`.

## Capabilities

### New Capabilities
- `collage-core-engine`: Core collage generation engine covering grid geometry rendering, facade convenience methods, parameter validation, HTTP/retrieval resilience with blank tile fallback, deterministic ordering, and unified exception handling.

### Modified Capabilities
<!-- No existing spec requirements modified -->

## Impact

- **Affected Code**: `src/lastfmcollagegenerator/collage.py`, `src/lastfmcollagegenerator/collage_generator.py`, `src/lastfmcollagegenerator/exceptions.py`.
- **New Tests**: `tests/test_validation.py`, `tests/test_geometry.py`, `tests/test_builders.py`, `tests/test_facade.py`, `tests/test_resilience.py`.
- **API Compatibility**: Fully backward-compatible; restores documented convenience methods that previously raised `AttributeError`.
- **Dependencies**: No new external dependencies required; utilizes existing `Pillow`, `requests`, `pylast`, and `pytest`.
