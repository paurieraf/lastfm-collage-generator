## Why

The current visual styling architecture in `lastfm-collage-generator` (Pilar 1) relies on a rigid `Theme` dataclass with pre-defined static colors (e.g., `overlay_bg`, `text_color`). While this works for simple overlays, it falls short for the advanced roadmap features such as Adaptive Themes (extracting dynamic color palettes from album artwork) and Image Filters (Duotone, CRT, Gradient Maps). To support these features, the system must evolve from a "static overlay painter" into a true "image processing pipeline" where image filtering and dynamic color extraction happen before grid compositing.

## What Changes

- Refactor the rendering pipeline in `BaseCollageBuilder` to support pre-compositing image manipulation (Image Filters).
- Introduce a new `ImageFilter` protocol/interface for applying pixel-level transformations to tiles (e.g., `DuotoneFilter`, `GrayscaleFilter`).
- Introduce a `ColorExtractor` utility to extract dominant or vibrant colors from an image (using Pillow's `ImageStat` or basic pixel bucketing).
- Extend the `Theme` engine to support "Dynamic Themes", where colors are computed dynamically per tile or per collage rather than hardcoded at instantiation.
- Add an implementation for a `Duotone` effect.
- Maintain backward compatibility with the existing static themes (`dark`, `light`, `glassmorphic`, etc.).

## Capabilities

### New Capabilities
- `visual-pipeline/adaptive-themes`: Support for extracting a vibrant color palette from the #1 Top Item (or per-tile) and dynamically applying it to the collage overlays and typography.
- `visual-pipeline/image-filters`: Support for applying sequential image filters (like Duotone or CRT effects) to the downloaded tiles before they are pasted onto the main collage grid.

### Modified Capabilities

## Impact

- **Affected Code**: `src/lastfmcollagegenerator/collage.py` (specifically `_insert_tile_title`, `_render_*_overlay`, and the image compositing loop), `src/lastfmcollagegenerator/theme.py`.
- **APIs**: The `CollageGenerator.generate` API will likely accept new parameters for `filters` or `effects` and support dynamic strings like `theme="adaptive"`.
- **Dependencies**: May require additional imports from `PIL` (e.g., `ImageOps`, `ImageStat`), but no external third-party dependencies beyond the existing Pillow requirement.
