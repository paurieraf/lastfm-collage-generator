## 1. Constants and Theme Subsystem

- [x] 1.1 Add theme and overlay style constants to `src/lastfmcollagegenerator/constants.py`
- [x] 1.2 Implement `Theme` dataclass, preset definitions (`dark`, `light`, `glassmorphic`, `sunset`, `neon`), and `resolve_theme()` helper in `src/lastfmcollagegenerator/theme.py`
- [x] 1.3 Export theme components in `src/lastfmcollagegenerator/__init__.py`

## 2. Typography Subsystem

- [x] 2.1 Implement word-boundary text wrapping `wrap_text_to_width` in `src/lastfmcollagegenerator/typography.py`
- [x] 2.2 Implement auto-scaling font helper `get_auto_scaled_font` with dynamic downscaling
- [x] 2.3 Support custom font paths in font loading routines

## 3. Builder and Overlay Rendering Pipeline

- [x] 3.1 Update `CollageBuilderConfig` to include `theme`, `overlay_style`, `show_text`, and `font_path`
- [x] 3.2 Implement overlay renderers in `BaseCollageBuilder`: `_render_banner_overlay`, `_render_full_tint_overlay`, `_render_gradient_overlay`, and `_render_pill_overlay`
- [x] 3.3 Update `BaseCollageBuilder._create_image` to handle overlay styles and `show_text=False` clean mode

## 4. Facade and Validation Updates

- [x] 4.1 Update `CollageGenerator._validate_parameters` to validate `theme`, `overlay_style`, and `font_path`
- [x] 4.2 Update `CollageGenerator.generate` and convenience methods (`generate_top_albums_collage`, etc.) to accept and forward theme/overlay parameters

## 5. Developer CLI and Test Verification

- [x] 5.1 Update `scripts/debug_collage.py` with `--theme`, `--overlay-style`, `--no-text`, and `--font-path` options
- [x] 5.2 Add unit tests for `Theme` presets, validation, and resolution in `tests/test_theme.py`
- [x] 5.3 Add unit tests for typography wrapping and auto-downscaling in `tests/test_typography.py`
- [x] 5.4 Add unit tests for all overlay styles and facade options in `tests/test_overlays.py` and `tests/test_facade.py`
- [x] 5.5 Verify 100% test pass rate and backward compatibility
