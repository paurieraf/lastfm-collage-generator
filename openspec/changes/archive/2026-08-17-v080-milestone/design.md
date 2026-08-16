# v0.8.0 Milestone — Technical Design

## Context

Current state (v0.7.0): `CollageGenerator` (facade) validates params and delegates to `CollageBuilderFactory` → builders in `collage.py`. Artwork acquisition is synchronous `requests.get` inside worker threads (`AlbumCollageBuilder._get_album_cover`, `ArtistCollageBuilder._get_artist_image`), failures fall back to `_generate_blank_tile()` (solid black). Canvas compositing happens in `BaseCollageBuilder._create_image`. Constraints: Python 3.8+ typing (no PEP 585 bare generics), Pillow 10.4, zero new runtime dependencies preferred, tests must stay 100% offline, and all new parameters must default to current behavior (see proposal.md — Impact).

## Goals / Non-Goals

**Goals:**
- Deliver the four roadmap areas (caching+resilience, social presets+backdrop, tile geometry+fallback art, GitHub Action) as one backward-compatible v0.8.0.
- Keep the 4-layer architecture: new logic as module-level helpers or builder capabilities, no PIL/HTTP leakage into the facade or `LastfmClient`.
- Maintain offline-testability: every new network/cache component injectable or mockable.

**Non-Goals:**
- No asyncio/httpx migration (Pillar 2 Phase 4, v1.0.0).
- No WebP/SVG/PDF export, no asymmetric layouts (Pillar 3 Phase 4).
- No rich CLI, no FastAPI/bots (Pillar 4, later phases).

## Decisions

**D1 — Cache: stdlib `sqlite3` + in-process LRU, single `ArtworkCache` class (`cache.py`).**
Two tiers behind one interface: `OrderedDict`-based LRU (`maxsize=256`) in front of a SQLite file at `~/.cache/lastfm-collage/artwork.db` (table: `key TEXT PRIMARY KEY, data BLOB, fetched_at REAL, kind TEXT`). TTL checked at read time (`30d` album/track covers, `7d` artist hero). Cache key = normalized URL. One shared `sqlite3.Connection` per process with `check_same_thread=False` + a `threading.Lock` (WAL mode not needed; writes are rare).
- *Alternative considered*: `requests-cache` library → rejected, new dependency for one table.
- *Alternative considered*: cache bytes on disk as files → rejected, no TTL metadata, cleanup harder.

**D2 — Resilience: token bucket + full-jitter backoff + per-host circuit breaker in `network.py`.**
A `ResilientHttpFetcher` wraps `requests.get`: (1) `TokenBucket(rate=5.0, capacity=5)` with lock, blocking acquire; (2) retry loop (max 3 attempts) on transient errors (`RequestException`, HTTP 429/5xx) with `sleep = min(cap, base * 2**attempt)` full-jittered; (3) `CircuitBreaker` per host (failure threshold 5, cooldown 60s, half-open probe). Builders route their fetches through it; on final failure the existing blank-tile catch path runs unchanged. Limiter/breaker are constructor-injectable so tests run with `rate=inf` and disabled breakers.
- *Alternative considered*: `tenacity` + `pyrate-limiter` → rejected, two dependencies replaceable by ~120 lines of stdlib code.

**D3 — Presets: declarative table in `presets.py` resolved by the facade.**
`SOCIAL_PRESETS: Dict[str, Preset]` with `(width, height, tile_plan)` entries; e.g. `instagram-post` → 1080x1080, grid 3x3, tile 360. A `preset=` param on `generate()` overrides `cols`/`rows`/`tile_size` resolution (explicit values win only when preset is None). Unknown preset → `ValueError` in `_validate_parameters` (existing pattern).
- *Alternative considered*: deriving everything from aspect ratio alone → rejected, presets must be exact spec'd dimensions.

**D4 — Backdrop: PIL-only blur in `_create_image`.**
When the canvas is larger than the composited grid area (letterboxing), the #1 tile's decoded image is resized to fill, `ImageFilter.GaussianBlur(radius≈40)`, darkened via `ImageEnhance.Brightness(0.4)`, pasted as the canvas base before tiles. Failure to acquire → neutral dark fill (spec). Square grids skip the path entirely.
- *Alternative considered*: storing backdrop separately during tile fetch → rejected, tiles are byte payloads; decode-once-then-reuse is simpler.

**D5 — Tile geometry: PIL mask compositing, legacy fast path.**
`CollageBuilderConfig` gains `corner_radius`, `border_width`, `border_color`, `spacing` (defaults `0`, `0`, `None`, `0`). Canvas = `(cols*tile + (cols+1)*spacing, rows*tile + (rows+1)*spacing)` when spacing > 0. Rounded corners via `ImageDraw.rounded_rectangle` alpha mask; border stroke drawn inside tile bounds after paste. When all geometry params are defaults, the code path is byte-identical to today's (spec requirement).
- *Alternative considered*: SSIM-different subpixel resampling for radius=0 → rejected, explicit legacy branch.

**D6 — Fallback art: deterministic hash-driven gradient (`fallback_art.py`).**
`generate_fallback_tile(title, width, height)` computes `sha256(title)` → seeds a small PRNG → two pastel colors from a fixed hue wheel → vertical gradient + up-to-2-word initials centered with the bundled DejaVu font. Deterministic across runs/processes (spec). `_generate_blank_tile` remains for the explicit legacy style.
- *Alternative considered*: PIL `ImageDraw` random gradients unseeded → rejected, violates determinism spec.

**D7 — GitHub Action: composite `action.yml` at repo root, no Docker.**
Steps: `actions/setup-python`, install via `pip install lastfmcollagegenerator` (or repo checkout + `uv sync`), run `scripts/github_action_entrypoint.py` with inputs (`username`, `entity`, `cols`, `rows`, `period`, `output-path`, `mock`) and `LASTFM_API_KEY`/`SECRET` secrets. Ship example workflow at `.github/workflows/weekly-recap.yml.example` with a weekly cron and auto-commit step.
- *Alternative considered*: Docker action → rejected, slower and needs registry publishing.

## Risks / Trade-offs

- [Concurrent SQLite access from ThreadPoolExecutor] → single shared connection + lock; cache operations are short (blob read/write).
- [Disk cache growth] → TTL expiry on access + lazy `DELETE` of expired rows + optional row cap with LRU eviction.
- [Rate limiter slowing real generation] → bucket only gates HTTP, hits rarely occur at 5 rps for ≤25 tiles; default rate documented and configurable.
- [Rounded-corner masking increasing memory for 20x20 grids] → mask built once per tile size and reused for all tiles.
- [Backdrop blur on large canvases (4K) is CPU-heavy] → blur radius scaled down (min(40, canvas/50)); only computed when letterboxing exists.
- [Composite action fragility across runner images] → pin Python version and use `uv` only if present, else fall back to `pip`; mock mode exercises the path in CI.

## Migration Plan

1. Land all code behind new optional parameters (defaults = current behavior); no signature changes to existing calls.
2. Bump version to 0.8.0 in `pyproject.toml`, update README roadmap checkboxes for delivered items.
3. Rollback: reverting the release restores v0.7.0 behavior; the cache directory is inert user data and can be deleted (`rm -rf ~/.cache/lastfm-collage/`) without impact.
