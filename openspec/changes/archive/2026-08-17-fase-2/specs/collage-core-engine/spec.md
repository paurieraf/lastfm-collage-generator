## MODIFIED Requirements

### Requirement: Facade Convenience Methods
The system SHALL provide dedicated convenience methods on the `CollageGenerator` facade for generating top albums, top artists, and top tracks collages without requiring explicit `entity` parameter configuration, forwarding all dimension, tile size, theme, overlay style, and typography formatting parameters.

#### Scenario: Generating top albums collage via convenience method
- **WHEN** `generate_top_albums_collage(username, cols, rows, period, tile_size, theme, overlay_style, show_text, font_path, show_playcount, font_bold)` is called on `CollageGenerator`
- **THEN** the system delegates to `generate(entity="album", ...)` and returns the composited album collage image

#### Scenario: Generating top artists collage via convenience method
- **WHEN** `generate_top_artists_collage(username, cols, rows, period, tile_size, theme, overlay_style, show_text, font_path, show_playcount, font_bold)` is called on `CollageGenerator`
- **THEN** the system delegates to `generate(entity="artist", ...)` and returns the composited artist collage image

#### Scenario: Generating top tracks collage via convenience method
- **WHEN** `generate_top_tracks_collage(username, cols, rows, period, tile_size, theme, overlay_style, show_text, font_path, show_playcount, font_bold)` is called on `CollageGenerator`
- **THEN** the system delegates to `generate(entity="track", ...)` and returns the composited track collage image
