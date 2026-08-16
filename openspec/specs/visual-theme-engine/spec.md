# visual-theme-engine Specification

## Purpose
Provides a visual styling and typography engine supporting pre-configured theme presets, custom color palettes, multiple overlay rendering styles, word-boundary text wrapping, and dynamic font downscaling.
## Requirements
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

### Requirement: Tile Geometry Customization
The system SHALL support rounded corner masking, configurable border strokes, and inter-tile spacing on collage tiles, with default values preserving the current edge-to-edge square rendering.

#### Scenario: Rounded corners with default radius
- **WHEN** a collage is generated with `corner_radius=12`
- **THEN** each tile is masked to a rounded-rectangle (squircle) with 12-pixel corner radius and the canvas background shows only where tiles were masked

#### Scenario: Default geometry preserves legacy output
- **WHEN** a collage is generated without geometry parameters (`corner_radius=0`, `border_width=0`, `spacing=0`)
- **THEN** the output is visually identical to the previous edge-to-edge rendering

#### Scenario: Border stroke rendering
- **WHEN** a collage is generated with `border_width=3` and a `border_color`
- **THEN** every tile is outlined with a 3-pixel stroke in the specified color, drawn inside the tile bounds

#### Scenario: Inter-tile spacing
- **WHEN** a collage is generated with `spacing=8`
- **THEN** tiles are separated by 8-pixel margins and the canvas dimension grows accordingly, with the background color visible between tiles

#### Scenario: Invalid geometry parameters are rejected
- **WHEN** `corner_radius`, `border_width`, or `spacing` is negative or exceeds the tile size
- **THEN** the system raises a `ValueError` indicating invalid tile geometry
