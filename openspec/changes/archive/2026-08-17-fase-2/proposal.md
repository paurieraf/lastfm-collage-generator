## Why

The current version (v0.5.0) achieved stability and fixed critical defects. However, the collage generator still suffers from rigid layout constraints and subpar typography. Text wraps mid-word instead of at word boundaries, tile dimensions and grid sizes are strictly capped, and artist image web retrieval is slow and repetitive. Phase 2 (Enhanced Typography & Grid Flexibility) addresses these issues to make the library more flexible, aesthetically pleasing, and performant.

## What Changes

- Implement word-boundary line wrapping using `textwrap` to prevent words from being cut in half.
- Expose `show_playcount: bool` and `font_bold: bool` parameters in the public `CollageGenerator.generate()` method.
- Support customizable tile dimensions (e.g., 150px, 300px, 600px) instead of being locked to 300x300.
- Lift the arbitrary 5x5 dimension cap to support larger grids (e.g., 10x10).
- Introduce an in-memory LRU cache (`functools.lru_cache` or `cachetools`) for retrieved artist images to reduce redundant network calls and improve rendering speed.

## Capabilities

### New Capabilities

- `typography-engine`: Enhances the typography engine to support word-boundary line wrapping and text formatting options.

### Modified Capabilities

- `collage-core-engine`: Modifies the core generation engine to support larger grid boundaries and customizable tile sizes.
- `caching-resilience`: Enhances caching to include in-memory LRU cache for retrieved artist images.

## Impact

- **API**: `CollageGenerator.generate()` and convenience methods will receive new optional parameters (`show_playcount`, `font_bold`, `tile_size`). Grid size validation rules will be relaxed.
- **Performance**: Artist image retrieval will be significantly faster on repeated runs due to caching.
- **Dependencies**: No external dependencies added (Python standard library `functools` or `textwrap` will be utilized).
