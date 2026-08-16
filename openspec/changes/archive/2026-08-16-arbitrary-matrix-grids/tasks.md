## 1. Core Engine & Parameter Validation

- [x] 1.1 Update `CollageGenerator` constants `MAX_COLS = 20`, `MAX_ROWS = 20`, `MAX_TILES = 400`
- [x] 1.2 Implement dynamic resolution resolution logic `_resolve_tile_size` and harden `_validate_parameters` in `src/lastfmcollagegenerator/collage_generator.py`
- [x] 1.3 Add `tile_size: Optional[int] = None` to `generate()`, `generate_top_albums_collage()`, `generate_top_artists_collage()`, and `generate_top_tracks_collage()`

## 2. Builder Layer & Dynamic Resolution Scaling

- [x] 2.1 Update `CollageBuilderConfig` dataclass in `src/lastfmcollagegenerator/collage.py` with `tile_size: int = 300`
- [x] 2.2 Update `BaseCollageBuilder._create_image` to dynamically calculate canvas size and downscale tile images using Lanczos resampling
- [x] 2.3 Implement proportional typography scaling, banner bounding, and text wrap width in `BaseCollageBuilder._insert_tile_title` and `_insert_newline_characters_to_text`
- [x] 2.4 Update `_generate_blank_tile` to dynamically generate solid black tiles at active tile resolution

## 3. Developer Tooling & Scripts

- [x] 3.1 Update `scripts/debug_collage.py` argument parser to accept `--tile-size` and expanded grid dimensions up to 20

## 4. Comprehensive Test Suite

- [x] 4.1 Update `tests/test_validation.py` with tests for expanded grid limits (up to 20x20), 400 tile capacity, and `tile_size` validation
- [x] 4.2 Update `tests/test_geometry.py` with tests verifying multi-row overlay pixel bounds across scaled tile dimensions (100px, 150px, 200px, 300px)
- [x] 4.3 Update `tests/test_facade.py` and `tests/test_builders.py` testing high-density matrix collages ($10 \times 10$, $20 \times 20$, asymmetric $3 \times 10$) and custom `tile_size`
- [x] 4.4 Run full pytest suite and verify 100% pass rate

## 5. Documentation & OpenSpec Verification

- [x] 5.1 Update `README.md` and `PROJECT_OVERVIEW.md` documenting arbitrary matrix grids, dynamic resolution scaling tiers, and API reference
- [x] 5.2 Validate OpenSpec change proposal via `openspec validate arbitrary-matrix-grids`

