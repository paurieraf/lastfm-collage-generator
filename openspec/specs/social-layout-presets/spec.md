# social-layout-presets Specification

## Purpose
Provides one-click social media dimension presets and acrylic backdrop blur filling for non-square collages, enabling share-ready output for Instagram, Twitter, and desktop wallpapers.
## Requirements
### Requirement: Social Media Dimension Presets
The system SHALL provide named dimension presets — Instagram Story (9:16, 1080x1920), Instagram Post (1:1, 1080x1080), Twitter Header (3:1, 1500x500), and Desktop Wallpaper (16:9, 1920x1080, plus a 4K variant) — that automatically derive grid geometry and tile sizes to fill the target canvas.

#### Scenario: Generating an Instagram Story preset
- **WHEN** a collage is requested with the `instagram-story` preset
- **THEN** the system produces a canvas of 1080x1920 pixels with the collage grid scaled to fill the 9:16 area

#### Scenario: Generating an Instagram Post preset
- **WHEN** a collage is requested with the `instagram-post` preset
- **THEN** the system produces a canvas of 1080x1080 pixels with a square collage grid

#### Scenario: Generating a Twitter Header preset
- **WHEN** a collage is requested with the `twitter-header` preset
- **THEN** the system produces a canvas of 1500x500 pixels with the collage grid scaled to fill the 3:1 area

#### Scenario: Generating a Desktop Wallpaper preset
- **WHEN** a collage is requested with the `desktop-wallpaper` preset
- **THEN** the system produces a canvas of 1920x1080 pixels (or 3840x2160 for the 4K variant) with the collage grid scaled to fill the 16:9 area

#### Scenario: Unknown preset is rejected
- **WHEN** an unsupported preset name is provided
- **THEN** the system raises a `ValueError` listing the supported presets

### Requirement: Acrylic Backdrop Blur for Non-Square Canvases
The system SHALL fill unused (letterboxed) canvas regions with an acrylic backdrop derived from the #1 top artwork: a Gaussian-blurred, darkened version of that image, rather than a flat background.

#### Scenario: Letterbox regions use blurred artwork backdrop
- **WHEN** a collage canvas has aspect ratio different from the grid's natural ratio and the #1 top artwork was successfully acquired
- **THEN** the letterboxed regions are filled with a Gaussian-blurred, darkened rendition of the #1 top artwork

#### Scenario: Backdrop falls back when artwork is unavailable
- **WHEN** the #1 top artwork cannot be acquired
- **THEN** the letterboxed regions are filled with a neutral dark background and collage generation completes

#### Scenario: Square grids skip backdrop processing
- **WHEN** the collage grid fills the entire canvas with no letterboxing
- **THEN** no backdrop rendering is performed
