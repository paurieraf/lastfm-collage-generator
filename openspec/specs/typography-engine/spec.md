# typography-engine Specification

## Purpose
Enhances the typography engine to support word-boundary line wrapping and text formatting options such as bold fonts and toggling playcounts.
## Requirements
### Requirement: Word-Boundary Line Wrapping
The system SHALL wrap text at word boundaries using a word-aware wrapping algorithm instead of splitting words arbitrarily when they exceed the tile width.

#### Scenario: Wrapping a long artist name
- **WHEN** a tile title contains words that collectively exceed the max text width
- **THEN** the text wraps to the next line at the nearest preceding space character, preserving whole words

### Requirement: Typography Formatting Options
The system SHALL allow rendering titles with a bold font weight and toggling the visibility of the scrobble playcount on the overlay banner.

#### Scenario: Rendering bold text
- **WHEN** the bold font formatting option is enabled
- **THEN** the bold font variant is used for the tile title

#### Scenario: Hiding playcounts
- **WHEN** the show playcount formatting option is disabled
- **THEN** the scrobble count is omitted from the tile title overlay

