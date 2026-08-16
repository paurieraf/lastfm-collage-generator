## ADDED Requirements

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
