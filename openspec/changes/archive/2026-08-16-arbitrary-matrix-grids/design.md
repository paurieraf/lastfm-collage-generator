## Context

See `proposal.md` for motivation and overview.

Currently, `CollageGenerator` validates `cols` and `rows` against `MAX_COLS = 5` and `MAX_ROWS = 5`. `BaseCollageBuilder` assumes fixed dimensions of $300 \times 300\text{ px}$ per tile, a fixed font size of 15pt, and a fixed 65px title banner overlay.

To support arbitrary matrix layouts up to $20 \times 20$ without exceeding host memory limits or distorting text overlays, the architecture must decouple tile resolution from hardcoded constants and implement dynamic scaling.

## Goals / Non-Goals

**Goals:**
- Support arbitrary rectangular and square grid geometries up to $20 \times 20$ (max 400 tiles).
- Provide tiered automatic resolution scaling ($300\text{px} \to 150\text{px} \to 100\text{px}$) to keep canvas allocations memory-safe and efficient.
- Allow explicit user configuration of `tile_size` (50–600 px) across public API methods.
- Proportionally scale fonts, banner overlay heights, padding, and text wrap boundaries with tile size.
- Maintain 100% backward compatibility for all existing $\le 5 \times 5$ generation calls.

**Non-Goals:**
- Variable tile sizes within the same collage (e.g. Bento Box / Hero Grid layouts, scheduled for Phase 4).
- Asynchronous acquisition with `asyncio`/`httpx` (scheduled for Phase 4 / v1.0.0).
- Non-square tile aspect ratios (all individual tiles remain 1:1 squares).

## Decisions

### Decision 1: Boundary Limits & Capacity Capping
**Choice**: Set `MAX_COLS = 20`, `MAX_ROWS = 20`, and `MAX_TILES = 400`.
**Rationale**: Last.fm Audioscrobbler REST API supports up to 1000 items per request, but downloading and compositing 400 images strikes the optimal balance between high density (e.g. $20 \times 20$ full-year recaps) and network/memory performance.
**Alternatives Considered**: Unbounded grid sizes (rejected due to OOM risk and API rate limiting) vs $10 \times 10$ limit (too restrictive for large poster recaps).

### Decision 2: Resolution Scaling Tiers
**Choice**:
- `max(cols, rows) <= 5`: $300 \times 300\text{ px}$ (Canvas: $300\text{px} \dots 1500\text{px}$)
- `5 < max(cols, rows) <= 10`: $150 \times 150\text{ px}$ (Canvas: $900\text{px} \dots 1500\text{px}$)
- `max(cols, rows) > 10`: $100 \times 100\text{ px}$ (Canvas: $1100\text{px} \dots 2000\text{px}$)
- Callers may override via `tile_size: Optional[int] = None`.
**Rationale**: Prevents explosive canvas growth ($20 \times 20$ at 300px would be $6000 \times 6000 = 36\text{ MP}$ / 108 MB uncompressed RAM). At 100px, $20 \times 20$ is a crisp $2000 \times 2000 = 4\text{ MP}$ canvas.

### Decision 3: Proportional Typography & Overlay Geometry Formula
**Choice**: Calculate scaling ratio $k = \frac{\text{tile\_size}}{300.0}$:
- Banner height: $h_{\text{banner}} = \max(16, \text{round}(65 \times k))$
- Font size: $\text{size}_{\text{font}} = \max(8, \text{round}(15 \times k))$
- Banner bounding box: $y_0 = y + (\text{tile\_size} - h_{\text{banner}})$, $y_1 = y + \text{tile\_size}$
- Text origin: $(x + \max(2, \text{round}(8 \times k)), y_0 + \max(2, \text{round}(5 \times k)))$
- Text wrap limit: $w_{\text{wrap}} = \text{round}(275 \times k)$
**Rationale**: Guarantees that on any tile size (e.g. 100px, 150px, 200px, 300px), title overlays remain proportional, readable, and strictly bounded within the bottom of each tile without bleeding into adjacent rows.

### Decision 4: In-Memory Resizing via Pillow Lanczos
**Choice**: Use `tile_img.resize((tile_width, tile_height), Image.Resampling.LANCZOS)` when pasting into the master canvas.
**Rationale**: High-quality downsampling ensuring album covers and retrieved artist images maintain visual clarity without pixelation artifacts.

## Risks / Trade-offs

- **[Risk] High-density grids making 400 network queries**: Fetching 400 artist images via web retrieval could take substantial time.
  - *Mitigation*: Album and track covers use direct CDN URLs; artist retrieval uses `ThreadPoolExecutor` with timeouts and fallback blank tiles. Multi-tier disk caching in Phase 3 will further accelerate repeats.
- **[Risk] Small font legibility on 100px tiles**:
  - *Mitigation*: A minimum font size of 8pt is enforced, with line breaks wrapping at proportional pixel boundaries.
