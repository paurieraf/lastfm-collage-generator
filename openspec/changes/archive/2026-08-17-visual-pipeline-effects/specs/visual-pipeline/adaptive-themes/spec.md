## Purpose

Enables dynamic extraction of color palettes from album artwork to create adaptive themes that match the mood of the most prominent items.

## ADDED Requirements

### Requirement: Extract dominant colors
The system SHALL provide a mechanism to extract dominant RGB colors from a downloaded image tile.

#### Scenario: Single prominent color extraction
- **WHEN** an image is analyzed by the color extractor
- **THEN** it returns an ordered list of dominant RGB tuples

### Requirement: Dynamic Theme Generation
The system SHALL be able to construct a `Theme` instance dynamically using colors extracted from the #1 tile in the collage sequence.

#### Scenario: Adaptive theme rendering
- **WHEN** the user selects the adaptive theme mode
- **THEN** the overlay background and text colors are derived from the most played item's artwork
