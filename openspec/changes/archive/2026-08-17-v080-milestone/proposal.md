# v0.8.0 Milestone: Caching, Layout Presets & Ecosystem Automation

## Why

The library is visually complete (v0.7.0) but still re-downloads every artwork on each run, offers no social-ready output formats, renders failure tiles as plain black squares, and has no automation story for GitHub users. This milestone closes Roadmap Pillars 2 (Phase 3), 3 (Phase 3), Pillar 1/2 leftovers (tile geometry, fallback artwork), and Pillar 4 (Phase 3, the versioned v0.8.0 target).

## What Changes

- **Multi-Tier Caching Subsystem**: Tier-1 in-memory LRU cache (`maxsize=256`) + Tier-2 SQLite persistent disk cache at `~/.cache/lastfm-collage/` with 30-day TTL for album covers and 7-day TTL for retrieved artist hero images.
- **Network Resilience Middleware**: Token-bucket rate limiter (5 req/sec), exponential backoff with full jitter for transient HTTP errors, and a circuit breaker that fast-fails retrieval to blank-tile fallbacks.
- **Social Media Dimension Presets**: One-click presets for Instagram Story (9:16, 1080x1920), Instagram Post (1:1, 1080x1080), Twitter Header (3:1, 1500x500), and Desktop Wallpaper (16:9, 1920x1080 / 4K).
- **Acrylic Backdrop Blur**: Letterboxed non-square canvas areas are filled with a Gaussian-blurred, darkened backdrop derived from the #1 top artwork instead of flat black.
- **Tile Geometry & Rounded Corners**: Rounded squircle corner masking (`radius=12`), configurable border stroke widths/colors, and inter-tile spacing margins.
- **Dynamic Fallback Artwork Engine**: Algorithmic two-color pastel gradients plus initials typography derived from SHA-256 entity hashes replace solid black fallback tiles.
- **GitHub Actions Automation**: A reusable `action.yml` enabling scheduled GitHub workflows that refresh a profile README with weekly listening recap collages.

## Capabilities

### New Capabilities

- `caching-resilience`: Multi-tier artwork caching (LRU + SQLite TTL) and network resilience middleware (rate limiting, backoff with jitter, circuit breaker) for all HTTP acquisition paths.
- `social-layout-presets`: Social media dimension presets and acrylic backdrop blur for non-square canvases.
- `github-actions-automation`: Reusable GitHub Action (`action.yml`) for scheduled profile-README collage refresh.

### Modified Capabilities

- `visual-theme-engine`: Tile geometry additions — rounded corners, border strokes, and inter-tile spacing parameters.
- `collage-core-engine`: Fallback artwork behavior changes from solid black tiles to deterministic algorithmic gradient tiles.

## Impact

- **Code**: `src/lastfmcollagegenerator/collage.py` (tile geometry, fallback artwork, caching integration, backdrop blur), new modules `src/lastfmcollagegenerator/cache.py`, `src/lastfmcollagegenerator/network.py`, `src/lastfmcollagegenerator/presets.py`, `src/lastfmcollagegenerator/fallback_art.py`; `collage_generator.py` (new parameters + preset facade methods).
- **API**: New optional parameters (`cache_dir`, `cache_ttl`, `rate_limit`, `preset`, `border_width`, `border_color`, `corner_radius`, `spacing`, `fallback_style`, `backdrop_blur`). All defaults preserve current behavior — no breaking changes.
- **Dependencies**: None new (stdlib `sqlite3`, `functools.lru_cache`). `action.yml` + workflow docs at repo root.
- **Packaging**: New root-level `action.yml`; cache directory under `~/.cache/lastfm-collage/` (user-scoped, ignored by Git).
- **Docs**: README roadmap checkboxes for the delivered items; new sections for caching, presets, and the GitHub Action.
