## Context

See `proposal.md` for the motivation to transition from static themes to a dynamic visual processing pipeline that enables image filtering and dynamic color extraction.

## Goals / Non-Goals

**Goals:**
- Decouple image manipulation from the collage compositing logic.
- Support sequential pixel manipulation filters (e.g., Duotone) executed before typography overlays.
- Introduce dynamic color extraction mechanisms from Pillow `Image` instances.

**Non-Goals:**
- Re-architecting the asynchronous download logic (`httpx`).
- Changing the grid layout algebra (this is covered by Phase 4 - Asymmetric Layouts).

## Decisions

**Decision 1: Pipeline Architecture**
- **Rationale**: Currently, `BaseCollageBuilder` pastes images and immediately overlays text/banners. We will introduce a `VisualEffectPipeline` that holds a list of `ImageFilter` protocol objects. Before an image is pasted, the pipeline runs `.apply(image)`.
- **Alternatives Considered**: Modifying the `Theme` dataclass to execute image operations. Rejected because it violates Single Responsibility Principle.

**Decision 2: ImageFilter Protocol**
- **Rationale**: An interface taking an `Image.Image` and returning an `Image.Image`. This allows easy chaining (e.g., `GrayscaleFilter` -> `DuotoneFilter` -> `CRTFilter`).
- **Alternatives Considered**: Relying purely on Pillow's built-in `ImageFilter` module. Rejected because some effects (like Duotone) require `ImageOps` manipulation, not simple convolution kernels.

**Decision 3: Color Extraction**
- **Rationale**: We will implement `extract_dominant_colors(image: Image.Image) -> List[Tuple]` using Pillow's `ImageStat` or a basic downsample + bucketing algorithm, avoiding complex external dependencies like `scikit-learn` for KMeans.
- **Alternatives Considered**: Using `scipy` or `sklearn`. Rejected to keep the footprint lightweight.

## Risks / Trade-offs

- [Risk] Performance degradation from pixel operations -> Mitigation: Perform filters *after* downscaling images to the `tile_size` (e.g., 300x300), minimizing pixel count.
- [Risk] Duotone maps distorting album artwork recognizability -> Mitigation: Keep Duotone as an opt-in filter.
