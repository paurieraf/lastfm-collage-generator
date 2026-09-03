# Architecture Conventions & Design Patterns

**Scope**: Architectural design, layer boundaries, design pattern enforcement, and extensibility patterns for `lastfm-collage-generator`.

---

## 1. Architectural Overview & Layered Flow

The library follows a strict 4-layer design pattern: **Facade → Factory → Builder → Client Adapter**.

```
[ Public Consumer ]
        │
        ▼
┌────────────────────────────────────────┐
│ 1. Facade Layer: CollageGenerator      │
│    - Parameter validation              │
│    - Configuration assembly            │
└───────────────────┬────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────┐
│ 2. Factory Layer: CollageBuilderFactory│
│    - Resolves entity string to builder │
└───────────────────┬────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────┐
│ 3. Builder Layer: BaseCollageBuilder   │
│    - Concrete: Artist / Album / Track  │
│    - Template Method: create()         │
│    - ThreadPool concurrent tile fetch  │
│    - Pillow canvas rendering & text    │
└───────────────────┬────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────┐
│ 4. Client Layer: LastfmClient          │
│    - pylast.LastFMNetwork wrapper      │
│    - Network call isolation            │
└────────────────────────────────────────┘
```

---

## 2. Layer Responsibilities & Strict Boundaries

### 2.1 Facade Layer (`CollageGenerator` in `collage_generator.py`)
- **Single Public Entrypoint**: `CollageGenerator` is the primary public entrypoint.
- **Responsibilities**:
  - Store API credentials via `LastfmConfig`.
  - Validate parameters (`cols`, `rows`, `entity`, `period`, `username`) strictly in `_validate_parameters()`.
  - Provide convenience methods (`generate`, `generate_top_albums_collage`, `generate_top_artists_collage`, `generate_top_tracks_collage`).
  - Instantiate `LastfmClient` and delegate builder construction to `CollageBuilderFactory`.
- **Prohibitions**:
  - MUST NOT perform direct image drawing or PIL manipulation.
  - MUST NOT make direct HTTP or web scraping requests.

### 2.2 Factory Layer (`CollageBuilderFactory` in `collage.py`)
- **Responsibilities**:
  - Map entity string keys (`"album"`, `"artist"`, `"track"`) to corresponding concrete builder classes.
  - Instantiate and return the concrete builder with `(config, lastfm_client)`.
  - Raise a clear exception (`InvalidEntityError` or `ValueError`) when an unregistered entity key is passed.
- **Prohibitions**:
  - MUST NOT contain business logic, rendering code, or API calls.

### 2.3 Builder Layer (`BaseCollageBuilder` & Subclasses in `collage.py`)
- **Template Method Pattern (`create`)**:
  - `create(username: str) -> PIL.Image.Image`:
    1. Fetches top entities for limit `cols * rows` using `_get_tiles_from_top_items()`.
    2. Constructs canvas and composites tiles using `_create_image()`.
    3. Renders title overlays and typography via `_insert_tile_title()`.
    4. Returns the final `PIL.Image.Image`.
- **Concurrency**:
  - `_create_tiles_from_top_items()` uses `concurrent.futures.ThreadPoolExecutor` to parallelize network I/O when fetching individual tiles.
  - Must sort completed tiles deterministically by `(int(playcount), title)` descending.
- **Title Overlay Geometry Rule**:
  - The banner rectangle MUST be calculated relative to the tile's local bounding box:
    ```python
    # Correct calculation:
    y_0 = y + (self.TILE_HEIGHT - 65)  # 235px from tile top
    y_1 = y + self.TILE_HEIGHT         # 300px from tile top
    draw.rectangle(((x, y_0), (x + self.TILE_WIDTH, y_1)), (0, 0, 0, 123))
    ```
  - NEVER use `y * 2 + TILE_WIDTH`, which causes severe vertical coordinate drift on multi-row collages.

### 2.4 Client Layer (`LastfmClient` in `lastfm/client.py`)
- **Responsibilities**:
  - Encapsulate all interactions with `pylast.LastFMNetwork`.
  - Provide typed wrapper methods for `get_user`, `get_top_albums`, `get_top_artists`, `get_top_tracks`.
  - Handle Last.fm authentication and network exceptions.
- **Prohibitions**:
  - MUST NOT reference PIL, fonts, or image rendering logic.

---

## 3. Font Asset Resolution Conventions

- **Asset Storage**: Font files (`DejaVuSansMono.ttf`, `DejaVuSansMono-Bold.ttf`) are distributed inside the package at `src/lastfmcollagegenerator/fonts/`.
- **Resolution Path**:
  - Always resolve font file paths relative to the package directory using `os.path.dirname(__file__)` or `importlib.resources`.
  - Never use hardcoded absolute filesystem paths (`/usr/share/fonts/...` or `C:\Windows\Fonts\...`).
  - Example pattern:
    ```python
    import os
    from PIL import ImageFont

    package_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(package_dir, "fonts", "DejaVuSansMono.ttf")
    try:
        font = ImageFont.truetype(font_path, size=15)
    except (OSError, IOError):
        font = ImageFont.load_default()
    ```
- **Packaging**: Ensure `MANIFEST.in` includes `recursive-include src/lastfmcollagegenerator/fonts *.ttf`.

---

## 4. Entity Extension Protocol

To add support for a new musical entity (e.g., `"tag"`, `"loved_tracks"`, `"recent_tracks"`):

1. **Declare Constant**:
   - In `src/lastfmcollagegenerator/constants.py`:
     ```python
     ENTITY_TAG = "tag"
     ENTITIES = (ENTITY_ALBUM, ENTITY_ARTIST, ENTITY_TRACK, ENTITY_TAG)
     ```
2. **Add Client Method** (if required):
   - In `src/lastfmcollagegenerator/lastfm/client.py`:
     ```python
     def get_top_tags(self, user: User, limit: int, period: str) -> List[TopItem]:
         ...
     ```
3. **Implement Concrete Builder**:
   - In `src/lastfmcollagegenerator/collage.py`, create a subclass of `BaseCollageBuilder`:
     ```python
     class TagCollageBuilder(BaseCollageBuilder):
         ENTITY = ENTITY_TAG

         def _get_tiles_from_top_items(self, user: User, limit: int, period: str) -> List[CollageTile]:
             ...

         @classmethod
         def _create_tile_from_top_item(cls, top_item: TopItem) -> CollageTile:
             ...
     ```
4. **Register in Factory**:
   - In `CollageBuilderFactory.entity_collage_builders`:
     ```python
     entity_collage_builders = {
         ENTITY_ARTIST: ArtistCollageBuilder,
         ENTITY_ALBUM: AlbumCollageBuilder,
         ENTITY_TRACK: TrackCollageBuilder,
         ENTITY_TAG: TagCollageBuilder,
     }
     ```
5. **Write Unit Tests**:
   - Add unit tests in `tests/test_builders.py` and `tests/test_factory.py` asserting proper dispatch, data fetching, and tile generation.
