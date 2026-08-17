## 1. Parameters and Validation

- [x] 1.1 Update `CollageGenerator.generate` signature to accept `show_playcount=True`, `font_bold=False`, and explicit `tile_size=None`.
- [x] 1.2 Update `CollageGenerator.generate_top_*` convenience methods to forward the new typography parameters.
- [x] 1.3 Update `_validate_parameters` to relax `max_cols` and `max_rows` constraints up to 20x20.
- [x] 1.4 Update `CollageBuilderConfig` to store `font_bold` and `tile_size` alongside `show_playcount`.

## 2. Typography Engine

- [x] 2.1 Refactor `BaseCollageBuilder._insert_newline_characters_to_text` to use a word-aware algorithm using `font.getlength` and spaces as break boundaries.
- [x] 2.2 Modify `BaseCollageBuilder._insert_tile_title` to resolve the bold font path when `config.font_bold` is True.
- [x] 2.3 Modify `BaseCollageBuilder._insert_tile_title` to conditionally append the scrobble count based on `config.show_playcount`.

## 3. Caching and Performance

- [x] 3.1 Decorate `ArtistCollageBuilder._get_artist_image` with `@functools.lru_cache(maxsize=128)` to prevent redundant web retrieval within the same process.

## 4. Testing

- [x] 4.1 Add test cases for word-boundary wrapping in `test_typography.py`.
- [x] 4.2 Add test cases for `show_playcount` and `font_bold` parameters in `test_facade.py` or `test_builders.py`.
- [x] 4.3 Add test case ensuring `lru_cache` functions correctly (e.g. using `unittest.mock.patch` to verify network requests are not duplicated) in `test_resilience.py` or `test_builders.py`.
