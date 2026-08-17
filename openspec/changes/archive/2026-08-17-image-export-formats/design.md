## Context

Currently, the `lastfm-collage-generator` library only exposes a `generate()` function that yields a raw `PIL.Image.Image`. Pillow (`PIL`) is strict about color modes: attempting to save an `RGBA` image (which the collage generator might produce if custom overlays or rounded corners are introduced, or by default in some compositing steps) as a `JPEG` directly throws a runtime exception, as JPEG does not support transparency.

See `proposal.md` for motivation.

## Goals / Non-Goals

**Goals:**
- Provide a robust, one-line export utility for consumers of the library.
- Safely abstract the color space conversion (`RGBA` to `RGB`) when saving to formats like JPEG.
- Reduce default output file sizes using optimized defaults for lossy formats (JPEG/WebP).

**Non-Goals:**
- Removing the ability to return a raw `PIL.Image.Image` (this remains the core output of `generate()`).
- Supporting every obscure image format (focusing on PNG, JPEG, WebP).
- Re-architecting the rendering engine itself.

## Decisions

### 1. Dedicated `export_image` Utility Function
- **Rationale**: Instead of coupling file saving directly into the `CollageGenerator` class (which violates Single Responsibility), we create a standalone utility function `export_image(image, output_path, format=None, quality=85)`. This keeps `CollageGenerator` focused solely on building the image matrix.
- **Alternatives Considered**: 
  - Making the CLI handle it: Rejected because any Python consumer of the library would have to reinvent the safe-save logic themselves.

### 2. Alpha Channel Flattening (RGBA to RGB)
- **Rationale**: To prevent crashes when exporting to JPEG, `export_image` will inspect `image.mode`. If the mode is `RGBA` and the target format is `JPEG`, it will create a solid black `RGB` background (`Image.new("RGB", image.size, (0, 0, 0))`), composite the collage onto it using `Image.alpha_composite` (or paste with a mask), and then save the resulting `RGB` image.
- **Alternatives Considered**:
  - Crashing and letting the user figure it out: Rejected due to poor developer experience.
  - Converting without a background: Dropping the alpha channel directly can lead to weird rendering artifacts on translucent overlays.

### 3. File Extension Inference
- **Rationale**: If `format` is `None`, the function will use `os.path.splitext(output_path)` to determine the format. If the extension is unknown or missing, it will default to PNG.

## Risks / Trade-offs

- **Risk: Flattening changes visual appearance** → By flattening RGBA onto a solid black background, translucent pixels will darken. **Mitigation**: This is the mathematically correct behavior for exporting transparency to a non-transparent format. The default background will be black `(0, 0, 0)` as it matches the collage's existing visual styling (dark themes, translucent black banners).
