## Why

The current library limits grid geometry to a maximum of $5 \times 5$ (25 items) with a fixed $300 \times 300\text{ px}$ tile resolution. Users desiring larger listening recaps (e.g. $10 \times 10$ 100-album grids, $8 \times 8$, $20 \times 20$, or custom rectangular shapes like $3 \times 10$) are restricted by legacy boundary validation. Furthermore, allocating fixed $300\text{px}$ tiles for high-density grids causes excessive memory footprint (e.g. $20 \times 20$ at 300px yields 36 megapixels / 108 MB uncompressed canvas).

Introducing arbitrary $N \times M$ matrix grid support with dynamic resolution downscaling and proportional typography/overlay scaling fulfills Phase 2 of Roadmap Pillar 3 (Advanced Layouts), delivering high-density collage generation while preserving memory safety and visual harmony.

## What Changes

- **Expand Grid Boundary Limits**: Allow custom grid dimensions up to `MAX_COLS = 20` and `MAX_ROWS = 20` with a maximum total tile cap `MAX_TILES = 400` (e.g. $10 \times 10$, $8 \times 8$, $3 \times 10$, $20 \times 20$).
- **Dynamic Resolution Scaling Engine**: Automatically select optimal tile resolution based on maximum grid dimension when no explicit `tile_size` is provided:
  - $\le 5$: $300 \times 300\text{ px}$ (standard high-res)
  - $6$ to $10$: $150 \times 150\text{ px}$ (medium density)
  - $> 10$ (up to $20$): $100 \times 100\text{ px}$ (high density)
- **Configurable `tile_size` Parameter**: Permit callers to explicitly override tile resolution with a custom `tile_size` (bounded between 50 and 600 px) across all `CollageGenerator` methods.
- **Proportional Typography and Overlay Geometry**: Dynamically scale font size, banner overlay height, text padding, and line-wrap width proportionally to the active `tile_size`, ensuring title overlays are visually balanced and strictly bounded on any tile size.
- **Developer Debug CLI & Tools**: Update `scripts/debug_collage.py` to accept `--cols`, `--rows` up to 20 and an optional `--tile-size` flag.

## Capabilities

### New Capabilities
<!-- None: expanding existing collage-core-engine capability -->

### Modified Capabilities
- `collage-core-engine`: Expand grid dimension bounds (`cols <= 20`, `rows <= 20`, `cols * rows <= 400`), introduce `tile_size` validation, and specify dynamic resolution downscaling and proportional overlay/typography rendering.

## Impact

- **Affected Code**:
  - `src/lastfmcollagegenerator/collage_generator.py`: Grid bounds constants, validation logic, and method signatures accepting `tile_size`.
  - `src/lastfmcollagegenerator/collage.py`: `CollageBuilderConfig`, `BaseCollageBuilder` layout, canvas allocation, image resizing, and proportional overlay drawing.
  - `scripts/debug_collage.py`: CLI arguments and synthetic mock generator.
- **Affected Tests**:
  - `tests/test_validation.py`: Tests for new boundary limits and `tile_size` validation.
  - `tests/test_geometry.py`: Multi-row coordinate tests with scaled tile sizes.
  - `tests/test_facade.py`: Convenience methods with custom dimensions and tile sizes.
  - `tests/test_builders.py`: Tile image resizing and typography wrapping at various scales.
- **API Compatibility**: Fully backward-compatible. Default behavior for $\le 5 \times 5$ grids remains identical (300px tiles).
- **Dependencies**: Zero new runtime dependencies.
