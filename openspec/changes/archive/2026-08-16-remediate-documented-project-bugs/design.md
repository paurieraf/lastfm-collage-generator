## Context

See `proposal.md` for motivation and defect overview.

The library architecture follows a 4-tier pattern:
`CollageGenerator` (Facade) → `CollageBuilderFactory` (Factory) → `BaseCollageBuilder` (Builder Hierarchy) → `LastfmClient` (API Client Adapter).

We need to fix defects across the Facade, Builder, and Exceptions layers while maintaining strict architectural boundaries and ensuring 100% offline testability.

## Goals / Non-Goals

**Goals:**
- Correct overlay geometry across all grid rows (`0` to `rows - 1`).
- Provide public convenience methods on `CollageGenerator` matching documentation.
- Implement robust parameter validation protecting downstream Pillow canvas allocations.
- Guarantee non-crashing network and scraping fallbacks with custom headers and explicit timeouts.
- Guarantee deterministic collage layout on tied playcounts.
- Establish an extensible exception base class.
- Achieve >90% test coverage using offline pytest suites with synthetic fixtures.

**Non-Goals:**
- Migrating from `ThreadPoolExecutor` to `asyncio`/`httpx` (deferred to v1.0.0 roadmap).
- Modifying TrueType font assets or typography wrapping engines (deferred to Phase 2 roadmap).
- Adding new CLI binaries or external network dependencies.

## Decisions

### Decision 1: Title Overlay Coordinate Arithmetic
**Choice**: Use `y_0 = y + (self.TILE_HEIGHT - 65)` and `y_1 = y + self.TILE_HEIGHT`.
**Rationale**: `y` is the top-left coordinate of the current tile. The overlay banner is designed to occupy the bottom 65px of the tile. Thus `y_0` is `y + 235` and `y_1` is `y + 300`. This is row-invariant.
**Alternatives Considered**: Hardcoding relative crop offsets per tile vs canvas-level drawing. Canvas-level drawing with the corrected formula maintains the existing architecture while resolving all multi-row rendering bugs.

### Decision 2: Facade Convenience Methods API
**Choice**: Implement `generate_top_albums_collage`, `generate_top_artists_collage`, and `generate_top_tracks_collage` directly on `CollageGenerator`.
```python
def generate_top_albums_collage(self, username: str, cols: int = 5, rows: int = 5, period: str = "overall") -> Image.Image:
    return self.generate(entity=ENTITY_ALBUM, username=username, cols=cols, rows=rows, period=period)
```
**Rationale**: Aligns runtime code with `README.md` documented usage, preventing `AttributeError` without breaking existing `generate()` callers.

### Decision 3: Defensive Parameter Validation
**Choice**: Validate types (`isinstance(cols, int)`, `isinstance(rows, int)`, `isinstance(username, str)`), ranges (`1 <= cols <= MAX_COLS`, `1 <= rows <= MAX_ROWS`), and non-empty stripped usernames before builder dispatch.
**Rationale**: Prevents cryptic PIL allocation crashes on 0x0 or negative canvas sizes, and prevents invalid API calls to Last.fm.

### Decision 4: HTTP Resilience, Custom Headers & Timeouts
**Choice**:
- Define `DEFAULT_HEADERS = {"User-Agent": "lastfm-collage-generator/0.5.0 (+https://github.com/paurieraf/lastfm-collage-generator)"}`
- Define `DEFAULT_TIMEOUT = (3.05, 10.0)` (connect/read timeouts)
- Wrap all `requests.get()` invocations in `try...except (requests.RequestException, ArtistNotFound, ArtistImageNotFound, OSError, Exception)` and return `_generate_blank_tile()`.
**Rationale**: Guarantees that no individual HTTP network error or CDN failure aborts collage generation.

### Decision 5: Deterministic Secondary Sorting
**Choice**: Sort tiles via `tiles.sort(key=lambda x: (int(x.playcount), x.title), reverse=True)`.
**Rationale**: Disambiguates tied scrobble playcounts deterministically, avoiding non-deterministic layouts caused by thread completion timing.

### Decision 6: Centralized Exception Base Class
**Choice**: Define `LastfmCollageGeneratorError(Exception)` in `exceptions.py` and derive `ArtistNotFound` and `ArtistImageNotFound` from it.
**Rationale**: Allows consumers to catch all library-specific exceptions under one base class.

## Risks / Trade-offs

- **[Risk] Scraped image structure changes on Last.fm website**: Web scraping HTML is inherently prone to DOM changes.
  - *Mitigation*: The resilient fallback to `_generate_blank_tile()` ensures collage generation never fails even if CSS class names change.
- **[Risk] Slower downloads due to timeouts**:
  - *Mitigation*: Explicit connect timeout (3.05s) prevents worker threads from hanging indefinitely on stalled CDN hosts.
- **[Risk] Unused dataclass removal breaking consumers**:
  - *Mitigation*: `CollageConfig` is internal and was never exported in `__all__` or used anywhere in the codebase.
