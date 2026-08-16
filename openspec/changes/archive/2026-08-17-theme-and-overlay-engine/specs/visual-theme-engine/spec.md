## Purpose

Provides a visual styling and typography engine supporting pre-configured theme presets, custom color palettes, multiple overlay rendering styles, word-boundary text wrapping, and dynamic font downscaling.

## ADDED Requirements

### Requirement: Theme Presets and Custom Theme Support
The system SHALL provide built-in theme presets (`dark`, `light`, `glassmorphic`, `sunset`, `neon`) and allow custom theme definitions specifying overlay background color, text color, accent color, and alpha opacity.

#### Scenario: Using built-in dark theme
- **WHEN** a collage is generated with `theme="dark"` (or by default)
- **THEN** the system applies a dark semi-transparent overlay with white monospace typography

#### Scenario: Using built-in light theme
- **WHEN** a collage is generated with `theme="light"`
- **THEN** the system applies a high-contrast light semi-transparent overlay with dark typography

#### Scenario: Using built-in glassmorphic theme
- **WHEN** a collage is generated with `theme="glassmorphic"`
- **THEN** the system applies a translucent frosted overlay with subtle white border highlighting

#### Scenario: Using custom Theme instance or dictionary
- **WHEN** a collage is generated with a custom `Theme` object or custom hex palette definition
- **THEN** the system parses the colors and renders overlays and typography according to the custom palette

### Requirement: Versatile Overlay Styles
The system SHALL support multiple overlay rendering styles including `banner`, `full_tint`, `gradient`, `pill`, and `clean` (or `show_text=False`).

#### Scenario: Classic banner overlay style
- **WHEN** `overlay_style="banner"` is configured
- **THEN** the system renders a translucent rectangular overlay strictly bounded to the bottom of each tile containing the entity title and playcount

#### Scenario: Full-tint overlay style
- **WHEN** `overlay_style="full_tint"` is configured
- **THEN** the system applies a semi-transparent color tint covering the entire tile with centered title and playcount text

#### Scenario: Gradient overlay style
- **WHEN** `overlay_style="gradient"` is configured
- **THEN** the system renders a vertical alpha gradient transitioning smoothly from transparent at the top to tinted at the bottom with text overlaid

#### Scenario: Pill overlay style
- **WHEN** `overlay_style="pill"` is configured
- **THEN** the system renders a compact rounded badge / chip at the bottom-center of each tile displaying the title and scrobble count

#### Scenario: Clean mode without text
- **WHEN** `overlay_style="clean"` or `show_text=False` is configured
- **THEN** the system composites pure artwork tiles with zero text overlays or banner backgrounds

### Requirement: Word-Boundary Typography and Dynamic Font Downscaling
The system SHALL format multi-line text using word-boundary wrapping and dynamically downscale font size to ensure that lengthy artist/album titles fit within the overlay bounds without vertical truncation or clipping.

#### Scenario: Word-boundary wrapping
- **WHEN** rendering long item titles with spaces
- **THEN** the text wrapping breaks on word boundaries rather than mid-word character splits

#### Scenario: Dynamic font downscaling for lengthy titles
- **WHEN** an item title exceeds the available height of the overlay at default font size
- **THEN** the system automatically downscales the font size until the text fits within the target overlay dimensions

#### Scenario: Custom font file loading
- **WHEN** a valid custom `font_path` (TrueType/OpenType) is supplied
- **THEN** the system loads and renders typography using the specified font file
