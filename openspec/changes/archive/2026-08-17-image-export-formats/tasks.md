## 1. Export Utility Implementation

- [x] 1.1 Create `export_image` function in `src/lastfmcollagegenerator/collage_generator.py` (or new `export.py` module).
- [x] 1.2 Implement automatic format inference based on the `output_path` extension.
- [x] 1.3 Implement RGBA to RGB flattening logic (compositing onto black background) when format is JPEG.
- [x] 1.4 Add `image.save()` call with default `quality=85` for JPEG and WebP formats.

## 2. Testing

- [x] 2.1 Add unit tests for `export_image` validating format inference.
- [x] 2.2 Add unit tests verifying RGBA to RGB flattening for JPEG outputs.
- [x] 2.3 Add unit tests verifying standard saving to PNG and WebP formats.

## 3. Documentation

- [x] 3.1 Update `README.md` to document the new `export_image` utility function.
