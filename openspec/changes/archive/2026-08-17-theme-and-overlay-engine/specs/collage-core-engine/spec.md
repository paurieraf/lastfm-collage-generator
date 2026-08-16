## MODIFIED Requirements

### Requirement: Facade Convenience Methods
The system SHALL provide dedicated convenience methods on the `CollageGenerator` facade for generating top albums, top artists, and top tracks collages without requiring explicit `entity` parameter configuration, forwarding all dimension, tile size, theme, and overlay style parameters.

#### Scenario: Generating top albums collage via convenience method
- **WHEN** `generate_top_albums_collage(username, cols, rows, period, tile_size, theme, overlay_style, show_text, font_path)` is called on `CollageGenerator`
- **THEN** the system delegates to `generate(entity="album", ...)` and returns the composited album collage image

#### Scenario: Generating top artists collage via convenience method
- **WHEN** `generate_top_artists_collage(username, cols, rows, period, tile_size, theme, overlay_style, show_text, font_path)` is called on `CollageGenerator`
- **THEN** the system delegates to `generate(entity="artist", ...)` and returns the composited artist collage image

#### Scenario: Generating top tracks collage via convenience method
- **WHEN** `generate_top_tracks_collage(username, cols, rows, period, tile_size, theme, overlay_style, show_text, font_path)` is called on `CollageGenerator`
- **THEN** the system delegates to `generate(entity="track", ...)` and returns the composited track collage image

### Requirement: Strict Input Parameter Validation
The system SHALL strictly validate all grid dimensions, maximum tile limits, custom tile sizes, username inputs, entity types, time aggregation periods, theme choices, and overlay style options before initiating image compositing or network queries.

#### Scenario: Validating lower and upper grid bounds
- **WHEN** `generate()` is called with `cols < 1`, `rows < 1`, `cols > 20`, `rows > 20`, or total items `cols * rows > 400`
- **THEN** the system raises a `ValueError` indicating invalid dimensions or exceeded maximum capacity

#### Scenario: Validating tile size bounds
- **WHEN** `generate()` is called with a custom `tile_size < 50`, `tile_size > 600`, or a non-integer `tile_size`
- **THEN** the system raises a `ValueError` or `TypeError` indicating invalid tile size bounds

#### Scenario: Validating empty or whitespace username
- **WHEN** `generate()` is called with an empty, whitespace-only, or non-string username
- **THEN** the system raises a `ValueError` indicating that a valid username is required

#### Scenario: Validating entity and period values
- **WHEN** `generate()` is called with an invalid entity or period
- **THEN** the system raises a `ValueError` listing the allowed choices

#### Scenario: Validating theme and overlay style values
- **WHEN** `generate()` is called with an unsupported theme name or invalid overlay style string
- **THEN** the system raises a `ValueError` listing the allowed options
