## Context

See `proposal.md` for background and motivation.
Currently, `CollageBuilderConfig` only contains `cols`, `rows`, `period`, `show_playcount`, and `tile_size`. Overlay rendering is handled exclusively by `BaseCollageBuilder._insert_tile_title` which hardcodes a dark rectangular banner with naive character splitting.

## Goals / Non-Goals

**Goals:**
- Provide a clean, extensible Theme abstraction supporting built-in presets (`dark`, `light`, `glassmorphic`, `sunset`, `neon`) and user-defined custom themes.
- Support 5 distinct overlay presentation modes: `banner`, `full_tint`, `gradient`, `pill`, and `clean` (or `show_text=False`).
- Replace character-by-character text splitting with robust word-boundary wrapping and auto-downscaling typography.
- Enable custom `.ttf`/`.otf` font path loading.
- Maintain 100% backward compatibility for all existing method calls.

**Non-Goals:**
- External CSS styling engines or complex vector graphics layout engines.
- Adding heavy third-party dependencies (must rely solely on Python standard library and `Pillow`).
- Asymmetrical bento-box layouts (scheduled for Phase 4 / v1.0.0).

## Decisions

### 1. Dedicated `Theme` Dataclass and Preset Registry
- **Decision**: Create `src/lastfmcollagegenerator/theme.py` defining a `Theme` dataclass with RGBA overlay background, RGB text color, optional accent/border color, and optional font path.
- **Rationale**: Isolates color styling from grid drawing logic. Allows callers to pass either string names (`"light"`, `"glassmorphic"`) or custom `Theme` instances.
- **Alternatives Considered**: Passing separate `overlay_color`, `text_color`, `border_color` keyword arguments to every method. Rejected because it clutters the public API signature and prevents sharing pre-packaged themes.

### 2. Isolated `typography` Module with `textwrap` and Dynamic Downscaling
- **Decision**: Implement `wrap_text_to_width` and `get_auto_scaled_font` in `src/lastfmcollagegenerator/typography.py`.
- **Rationale**: Keeps text layout and font metrics isolated and independently unit-testable. Uses Python's standard `textwrap` library combined with `font.getlength()` measurements.
- **Alternatives Considered**: Inline regex or keeping the legacy `_insert_newline_characters_to_text` character iteration. Rejected because naive character splitting breaks words in awkward places (e.g. `Radioh` / `ead`).

### 3. Modular Overlay Rendering Strategy
- **Decision**: Dispatch overlay styles inside `BaseCollageBuilder` based on `config.overlay_style`:
  - `banner`: Lower-third bounded rectangle.
  - `full_tint`: Full tile alpha overlay.
  - `gradient`: Alpha gradient generated via PIL pixel manipulation / alpha compositing.
  - `pill`: Compact rounded badge centered at tile bottom.
  - `clean`: Skip overlay and text rendering entirely.
- **Rationale**: Encapsulates drawing routines in clear helper methods while sharing common text positioning and typography routines.

## Risks / Trade-offs

- **[Risk] Gradient and Pill Rendering Performance**: Generating alpha gradients or rounded badges could add overhead when compositing 400 tiles.
  - *Mitigation*: Gradient alpha masks are generated in memory and blended efficiently via Pillow's native C implementation (`Image.composite` or `ImageDraw.rounded_rectangle`).
- **[Risk] Font Downscaling Latency**: Iterative font size search could be slow for long text.
  - *Mitigation*: Limit downscaling steps to a binary or step-wise search bounded between `base_size` and `min_size` (e.g. 8px).
