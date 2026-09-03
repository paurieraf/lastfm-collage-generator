## 1. Exception Hierarchy and Package Hygiene

- [x] 1.1 Update `exceptions.py` to establish `LastfmCollageGeneratorError` base exception and inherit `ArtistNotFound` and `ArtistImageNotFound`
- [x] 1.2 Remove unused `CollageConfig` dataclass and unused `logger` in `src/lastfmcollagegenerator/collage.py`

## 2. Geometry and Rendering Core Fixes

- [x] 2.1 Fix title overlay bounding box coordinate math in `BaseCollageBuilder._insert_tile_title` (`y_0` and `y_1` bounding)
- [x] 2.2 Implement deterministic secondary sort key `(int(playcount), title)` in `BaseCollageBuilder._create_tiles_from_top_items`

## 3. Network Resilience and Scraping Error Handling

- [x] 3.1 Configure `DEFAULT_HEADERS` with custom User-Agent and `DEFAULT_TIMEOUT` in `src/lastfmcollagegenerator/collage.py`
- [x] 3.2 Wrap `AlbumCollageBuilder._get_album_cover` and `ArtistCollageBuilder._get_artist_image` with explicit timeouts and exception fallback to `_generate_blank_tile()`

## 4. Facade API and Parameter Validation

- [x] 4.1 Implement strict boundary (`1 <= cols <= 5`, `1 <= rows <= 5`), non-empty username, and type validation in `CollageGenerator._validate_parameters`
- [x] 4.2 Implement convenience methods `generate_top_albums_collage`, `generate_top_artists_collage`, and `generate_top_tracks_collage` on `CollageGenerator`

## 5. Comprehensive Offline Test Suite

- [x] 5.1 Create `tests/conftest.py` with synthetic in-memory image fixtures and mock Last.fm client
- [x] 5.2 Create `tests/test_geometry.py` testing pixel boundaries across multi-row grids
- [x] 5.3 Create `tests/test_validation.py` testing dimension boundaries, invalid entities, and empty usernames
- [x] 5.4 Create `tests/test_facade.py` testing convenience methods and builder dispatch
- [x] 5.5 Create `tests/test_resilience.py` testing HTTP timeouts, 404/500 responses, and blank tile fallbacks
- [x] 5.6 Run complete test suite and assert 100% pass rate without external network access
