## Why

Currently, `lastfm-collage-generator` only renders a single hardcoded visual style: a dark semi-transparent banner (`rgba(0,0,0,123)`) fixed to the lower third of each tile, using a naive character-by-character line splitting algorithm. Users cannot customize the collage appearance to match different visual aesthetics (such as light themes, glassmorphic styles, full-tint overlays, compact badge pills, or pure clean artwork grids without text), nor can they provide custom fonts or benefit from word-boundary text wrapping.

Implementing the **Theme & Overlay Engine** fulfills Phase 2 of Roadmap Pillar 1 (Visual Styling & Custom Themes) and enhances visual personalization and typography across all collage types while maintaining 100% backward compatibility.

## What Changes

- **Overlay Style Engine**: Support multiple overlay rendering modes via `overlay_style`:
  - `banner` (default): Classic bottom translucent banner overlay.
  - `full_tint`: Full tile semi-transparent tint overlay with centered text.
  - `gradient`: Smooth vertical gradient overlay from transparent at the top to tinted at the bottom.
  - `pill` / `badge`: Minimalist translucent rounded pill badge displaying title and playcount.
  - `clean` (or `show_text=False`): Pure artwork grid with all text and overlays disabled.
- **Theme System**: Pre-packaged themes and custom palette support via `theme`:
  - Built-in theme presets: `dark` (default), `light`, `glassmorphic`, `sunset`, and `neon`.
  - Custom `Theme` configuration support allowing custom overlay background color, text color, accent color, and alpha opacity.
- **Typography & Word-Wrapping Engine**:
  - Replace character-by-character splitting with word-boundary wrapping via `textwrap` and font width metrics.
  - Dynamic font downscaling to prevent text overflow when titles exceed the available overlay height.
  - Custom font support via optional `font_path` parameter.
- **Facade & Builder Integration**:
  - Expose `theme`, `overlay_style`, `show_text`, and `font_path` across `CollageGenerator.generate()` and all convenience methods (`generate_top_albums_collage`, `generate_top_artists_collage`, `generate_top_tracks_collage`).
  - Update `CollageBuilderConfig` and `BaseCollageBuilder` rendering pipeline.
- **Developer Debugging & CLI**:
  - Update `scripts/debug_collage.py` with `--theme`, `--overlay-style`, `--no-text`, and `--font-path` CLI options for easy visual testing in both mock and live modes.

## Capabilities

### New Capabilities
- `visual-theme-engine`: Defines theme presets (`dark`, `light`, `glassmorphic`, `sunset`, `neon`), custom `Theme` data structures, overlay styles (`banner`, `full_tint`, `gradient`, `pill`, `clean`), and word-boundary typography engine with font auto-downscaling and custom font loading.

### Modified Capabilities
- `collage-core-engine`: Extend facade entrypoints and builder rendering pipeline to accept and apply theme and overlay style configurations while preserving default visual output.

## Impact

- **Affected Code**:
  - `src/lastfmcollagegenerator/theme.py`: [NEW] Theme dataclass, presets, and color parsing utilities.
  - `src/lastfmcollagegenerator/typography.py`: [NEW] Text wrapping and dynamic font scaling utilities.
  - `src/lastfmcollagegenerator/collage.py`: Update `CollageBuilderConfig`, `BaseCollageBuilder._create_image`, overlay rendering routines.
  - `src/lastfmcollagegenerator/collage_generator.py`: Add validation and parameter forwarding for themes, overlay styles, `show_text`, and `font_path`.
  - `src/lastfmcollagegenerator/constants.py`: Define supported themes and overlay style constants.
  - `scripts/debug_collage.py`: Add CLI arguments for themes and overlay styles.
- **Affected Tests**:
  - New test suites for theme presets, custom themes, overlay rendering modes, word-wrapping, and font downscaling.
  - Existing tests remain 100% passing due to default parameter backward compatibility.
- **API Compatibility**: Fully backward-compatible. Defaults (`theme="dark"`, `overlay_style="banner"`, `show_text=True`) produce existing behavior.
- **Dependencies**: No external runtime dependencies (relies on standard library `textwrap` and bundled `Pillow`).
