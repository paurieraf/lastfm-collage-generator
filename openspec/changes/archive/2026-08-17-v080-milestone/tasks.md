# v0.8.0 Milestone — Task List

## 1. Multi-Tier Caching Subsystem

- [x] 1.1 Create `src/lastfmcollagegenerator/cache.py` with `ArtworkCache` (LRU tier via `OrderedDict`, `maxsize=256`, plus SQLite tier at `~/.cache/lastfm-collage/artwork.db`), thread-safe via a shared connection + `threading.Lock`
- [x] 1.2 Implement `get(key, kind)` / `set(key, data, kind)` with TTL validation (30d album/track covers, 7d artist hero) and lazy expiry cleanup of stale SQLite rows
- [x] 1.3 Make cache path and LRU size injectable; degrade to no-op caching when the cache directory is unwritable (spec: user-scoped and ignorable)
- [x] 1.4 Add offline unit tests in `tests/test_cache.py`: hit avoids fetch, expired refresh, persistence across instances (tmp cache dir), unwritable-dir degradation

## 2. Network Resilience Middleware

- [x] 2.1 Create `src/lastfmcollagegenerator/network.py` with `TokenBucket` rate limiter (default 5 req/sec, blocking acquire, thread-safe)
- [x] 2.2 Implement `retry_with_full_jitter` helper (exponential backoff with full jitter, max 3 attempts, transient errors: timeouts, connection errors, HTTP 429/5xx)
- [x] 2.3 Implement per-host `CircuitBreaker` (threshold 5 consecutive failures, 60s cooldown, half-open probe request)
- [x] 2.4 Implement `ResilientHttpFetcher.get(url, headers, timeout)` composing rate limit → circuit check → retry, wrapping the existing `requests.get` call signature
- [x] 2.5 Add offline tests in `tests/test_network.py`: throttle timing, retry-then-succeed, give-up-after-max-attempts, circuit open/fast-fail, half-open recovery, no-abort fallback

## 3. Builder Integration of Cache & Resilience

- [x] 3.1 Route `AlbumCollageBuilder._get_album_cover` and `ArtistCollageBuilder._get_artist_image` through `ResilientHttpFetcher` with cache read/write around each fetch
- [x] 3.2 Thread the cache and fetcher instances from `CollageGenerator` through `CollageBuilderFactory` into builders (constructor-injectable; defaults preserve v0.7.0 behavior)
- [x] 3.3 Add optional `cache_dir`, `cache_ttl_override`, and `rate_limit` parameters to `CollageGenerator.generate()` with validation
- [x] 3.4 Extend `tests/` with integration coverage: mocked `requests.get` counts network calls on cache hits/misses and honors circuit breaker state

## 4. Deterministic Fallback Artwork Engine

- [x] 4.1 Create `src/lastfmcollagegenerator/fallback_art.py` with `generate_fallback_tile(title, width, height)` — SHA-256-seeded two-color pastel gradient + up-to-2-word initials using bundled fonts
- [x] 4.2 Replace the default blank-tile path in `BaseCollageBuilder._generate_blank_tile` with the gradient engine; keep solid black reachable via an explicit legacy fallback style
- [x] 4.3 Add `fallback_style` parameter (`gradient` default / `black`) with validation
- [x] 4.4 Add tests in `tests/test_fallback_art.py`: determinism across runs, distinct output for distinct titles, correct dimensions, legacy black path

## 5. Tile Geometry Customization

- [x] 5.1 Add `corner_radius`, `border_width`, `border_color`, `spacing` to `CollageBuilderConfig` with validation (non-negative, bounded by tile size)
- [x] 5.2 Implement rounded-corner alpha masking (`ImageDraw.rounded_rectangle`) and border stroke drawing in `BaseCollageBuilder._create_image` / tile paste loop
- [x] 5.3 Implement inter-tile spacing with canvas growth `(cols*tile + (cols+1)*spacing, ...)` and background visibility between tiles
- [x] 5.4 Preserve a byte-identical fast path when all geometry params are defaults
- [x] 5.5 Add tests in `tests/test_geometry.py`: radius=12 corner pixels transparent, border stroke color at tile edges, spacing canvas dimensions, defaults identical output, invalid params raise `ValueError`

## 6. Social Media Presets & Acrylic Backdrop

- [x] 6.1 Create `src/lastfmcollagegenerator/presets.py` with `SOCIAL_PRESETS` (`instagram-story`, `instagram-post`, `twitter-header`, `desktop-wallpaper`, `desktop-wallpaper-4k`) mapping to exact dimensions and tile plans
- [x] 6.2 Add `preset` parameter to `CollageGenerator.generate()`; resolve grid/tile geometry from the preset (unknown preset → `ValueError`)
- [x] 6.3 Implement acrylic backdrop in `BaseCollageBuilder._create_image`: when letterboxed, fill with blurred (`GaussianBlur`) + darkened (`ImageEnhance.Brightness(0.4)`) #1 artwork; neutral dark fill on failure; skip entirely for exact-fit grids
- [x] 6.4 Add tests in `tests/test_presets.py`: exact canvas dimensions per preset, `ValueError` for unknown preset, backdrop pixel sampling (blurred vs neutral), no-op for square grids

## 7. GitHub Actions Automation

- [x] 7.1 Add `scripts/github_action_entrypoint.py` supporting live and `--mock` modes, writing the collage to `output-path`
- [x] 7.2 Add repository-root `action.yml` (composite): setup-python, install package, run entrypoint with `username`, `entity`, `cols`, `rows`, `period`, `output-path`, `mock` inputs and `LASTFM_API_KEY` / `LASTFM_API_SECRET` secrets
- [x] 7.3 Add `.github/workflows/weekly-recap.yml.example` with weekly cron, secret wiring, and a commit-push step
- [x] 7.4 Document the action in README (inputs table, secrets, example workflow snippet)

## 8. Version Bump, Documentation & QA Gate

- [x] 8.1 Bump version to `0.8.0` in `pyproject.toml` and package exports
- [x] 8.2 Update README roadmap checkboxes for delivered items; add caching/presets/action sections
- [x] 8.3 Run full QA suite: `uv run pytest tests/ -v` (100% offline), `flake8`, `black --check`, `mypy`
- [x] 8.4 Run `openspec validate v080-milestone` and fix any spec/artifact issues
