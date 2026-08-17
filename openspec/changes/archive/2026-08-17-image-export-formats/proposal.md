## Why

The library currently only returns `PIL.Image.Image` objects and relies on consumers to handle file saving. This leads to crashes when consumers attempt to save collages with alpha channels (transparency) into formats that don't support it, like JPEG. To improve developer experience, reduce file sizes, and support Phase 3 of the project roadmap, we need an official robust image export utility.

## What Changes

- Introduce a new utility function `export_image(image: PIL.Image.Image, output_path: str, format: Optional[str] = None, quality: int = 85)` in the core library.
- Add automatic format inference from the file extension if the format is not explicitly provided.
- Add intelligent RGBA to RGB conversion with a solid background when exporting to JPEG to prevent Pillow crashes due to alpha channels.
- Apply optimized defaults (`quality=85` for JPEG/WebP) to significantly reduce the file size of generated collages.

## Capabilities

### New Capabilities
- `image-export`: Core library functionality for safely exporting PIL Images to disk across multiple formats (JPEG, WebP, PNG) while handling color space conversions.

### Modified Capabilities
- 

## Impact

- **Core Library**: A new utility function added (e.g., in `collage_generator.py` or a dedicated module).
- **Consumers**: CLI scripts and other users can now call `export_image()` instead of manually invoking `image.save()` and handling color mode conversions themselves.
