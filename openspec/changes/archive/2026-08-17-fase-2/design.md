## Context

The current `lastfm-collage-generator` implementation uses a character-by-character width measurement for text wrapping, which splits words abruptly. It limits grids to 5x5 natively (though some internal methods try to validate up to 20x20, the limit is inconsistently enforced and scaling logic is rigid). Artist image retrieval involves repeated HTTP requests for identical artists within a single session because there is no in-memory cache, causing performance bottlenecks. (See `proposal.md` for full motivation).

## Goals / Non-Goals

**Goals:**
- Provide proper word-boundary text wrapping using the Python standard library `textwrap` coupled with PIL `ImageFont.getlength()`.
- Add toggleable parameters for `show_playcount`, `font_bold`, and `tile_size` across the facade layer.
- Relax dimensions to support up to 20x20 grids.
- Add an in-memory `functools.lru_cache` to `ArtistCollageBuilder._get_artist_image`.

**Non-Goals:**
- We are not implementing the SQLite persistent disk cache in this phase (that is part of the broader caching spec, but the immediate goal is only the Tier-1 in-memory cache).
- We are not migrating the HTTP client to `asyncio` in this phase (that is Phase 3).

## Decisions

**1. Text Wrapping Implementation**
- **Decision**: Replace `_insert_newline_characters_to_text` with a word-boundary aware algorithm. Since `textwrap.wrap` only counts characters (not pixel width), we will implement a custom word-by-word accumulator using `font.getlength(word)`.
- **Alternatives Considered**: Using `textwrap.wrap` with a hardcoded character width limit. Rejected because monospace characters might have consistent width, but future-proofing for proportional fonts (or emojis) requires pixel-width measurement.

**2. In-Memory LRU Cache**
- **Decision**: Decorate `ArtistCollageBuilder._get_artist_image` with `@functools.lru_cache(maxsize=128)`.
- **Alternatives Considered**: Using `cachetools.TTLCache`. Rejected because `functools` is in the standard library, avoiding new dependencies, and the script lifespan is short, making a TTL strictly for the in-memory layer unnecessary for a single run.

**3. Tile Size and Grid Limit Adjustments**
- **Decision**: Ensure `CollageGenerator._validate_parameters` explicitly supports `cols <= 20` and `rows <= 20`. Route the `show_playcount`, `font_bold`, and explicit `tile_size` parameters down from the convenience methods (`generate_top_albums_collage`, etc.) into `generate()` and `CollageBuilderConfig`.

## Risks / Trade-offs

- **Risk: Memory exhaustion on 20x20 grids** → *Mitigation*: The dynamic scaling logic already downscales tile sizes to 100x100 for high-density grids (`max(cols, rows) > 10`), so memory usage remains bounded.
- **Risk: `functools.lru_cache` on class methods** → *Mitigation*: Decorating class methods with `lru_cache` can create memory leaks if instances are long-lived because `self` is cached. Since `ArtistCollageBuilder` instances are short-lived (one per run), this is acceptable. Alternatively, cache a static method or module-level function.
