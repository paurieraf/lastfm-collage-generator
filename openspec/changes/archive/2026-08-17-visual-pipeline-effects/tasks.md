## 1. Foundation & Filter Protocol

- [x] 1.1 Create `ImageFilter` protocol interface in a new module or within `theme.py`.
- [x] 1.2 Implement the `VisualEffectPipeline` class to hold and execute a list of `ImageFilter` objects.

## 2. Dynamic Colors & Adaptive Theme

- [x] 2.1 Implement `ColorExtractor` utility to sample dominant/vibrant colors from a Pillow `Image`.
- [x] 2.2 Extend `Theme` resolution logic in `resolve_theme` to support adaptive extraction from the primary artwork when requested.

## 3. Duotone Implementation

- [x] 3.1 Implement `DuotoneFilter(color1, color2)` adhering to the `ImageFilter` protocol using `ImageOps.colorize`.
- [x] 3.2 Ensure `DuotoneFilter` preserves transparency/alpha channels if present.

## 4. Pipeline Integration

- [x] 4.1 Refactor `BaseCollageBuilder` to initialize and run the `VisualEffectPipeline` on downloaded tiles before calling `_insert_tile_title`.
- [x] 4.2 Update `CollageGenerator.generate` API to accept `filters` and pass them to the builder configuration.
- [x] 4.3 Add unit tests verifying filter execution and adaptive color extraction in the `tests/` directory.
