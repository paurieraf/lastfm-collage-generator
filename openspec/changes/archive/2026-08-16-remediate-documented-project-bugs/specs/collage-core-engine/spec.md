## Purpose

Provides a robust and defect-free core collage generation engine for Last.fm listening history, ensuring correct multi-row visual layout geometry, strict parameter validation, public facade convenience methods, deterministic sorting, and resilient network fallbacks.

## ADDED Requirements

### Requirement: Multi-Row Title Overlay Geometry
The system SHALL render dark translucent title overlay banners on collage tiles such that each banner is strictly bounded within the bottom 65 pixels of its respective tile (`[y + 235, y + 300]`), without vertically overflowing or obscuring subsequent tile rows across any NxM grid configuration up to 5x5.

#### Scenario: Multi-row grid title banner bounding
- **WHEN** a multi-row collage (e.g. 3x3 or 5x5) is generated with title banners enabled
- **THEN** every row's title overlay is rendered between `y + 235` and `y + 300` relative to the tile top `y`, and no pixels at `y + 301` or beyond on lower rows are overwritten by prior rows

### Requirement: Facade Convenience Methods
The system SHALL provide dedicated convenience methods on the `CollageGenerator` facade for generating top albums, top artists, and top tracks collages without requiring explicit `entity` parameter configuration.

#### Scenario: Generating top albums collage via convenience method
- **WHEN** `generate_top_albums_collage(username, cols, rows, period)` is called on `CollageGenerator`
- **THEN** the system delegates to `generate(entity="album", ...)` and returns the composited album collage image

#### Scenario: Generating top artists collage via convenience method
- **WHEN** `generate_top_artists_collage(username, cols, rows, period)` is called on `CollageGenerator`
- **THEN** the system delegates to `generate(entity="artist", ...)` and returns the composited artist collage image

#### Scenario: Generating top tracks collage via convenience method
- **WHEN** `generate_top_tracks_collage(username, cols, rows, period)` is called on `CollageGenerator`
- **THEN** the system delegates to `generate(entity="track", ...)` and returns the composited track collage image

### Requirement: Strict Input Parameter Validation
The system SHALL strictly validate all grid dimensions, username inputs, entity types, and time aggregation periods before initiating image compositing or network queries.

#### Scenario: Validating lower and upper grid bounds
- **WHEN** `generate()` is called with `cols < 1`, `rows < 1`, `cols > 5`, or `rows > 5`
- **THEN** the system raises a `ValueError` indicating invalid dimensions

#### Scenario: Validating empty or whitespace username
- **WHEN** `generate()` is called with an empty, whitespace-only, or non-string username
- **THEN** the system raises a `ValueError` indicating that a valid username is required

#### Scenario: Validating entity and period values
- **WHEN** `generate()` is called with an invalid entity or period
- **THEN** the system raises a `ValueError` listing the allowed choices

### Requirement: Resilient Image Acquisition and Network Timeouts
The system SHALL configure descriptive `User-Agent` HTTP headers, enforce connection and read timeouts on all outbound HTTP requests, and catch network failures, HTTP errors, or scraping exceptions to cleanly produce a solid black fallback tile without aborting collage assembly.

#### Scenario: Handling CDN or network error during image download
- **WHEN** an HTTP request for album cover art or artist scraping fails due to network drop, timeout, or HTTP 4xx/5xx status
- **THEN** the system catches the exception and returns a 300x300 solid black blank tile, allowing collage generation to complete successfully

#### Scenario: Custom User-Agent header transmission
- **WHEN** web scraping or image download requests are executed
- **THEN** the HTTP client includes a custom `User-Agent` identifying `lastfm-collage-generator`

### Requirement: Deterministic Tile Ordering
The system SHALL sort fetched tiles deterministically using scrobble playcount descending as the primary key and item title descending as the secondary tie-breaker.

#### Scenario: Ordering tiles with tied playcounts
- **WHEN** multiple items have identical scrobble playcounts
- **THEN** the items are sorted deterministically regardless of asynchronous network download completion order

### Requirement: Base Exception Hierarchy
The system SHALL define a base exception class `LastfmCollageGeneratorError` from which all library-specific exceptions inherit.

#### Scenario: Catching library exceptions via base class
- **WHEN** an `ArtistNotFound` or `ArtistImageNotFound` exception is raised
- **THEN** it can be caught by handling `LastfmCollageGeneratorError`
