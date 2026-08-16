## MODIFIED Requirements

### Requirement: Resilient Image Acquisition and Network Timeouts
The system SHALL configure descriptive `User-Agent` HTTP headers, enforce connection and read timeouts on all outbound HTTP requests, and catch network failures, HTTP errors, or retrieval exceptions to cleanly produce a deterministic algorithmic fallback tile without aborting collage assembly.

#### Scenario: Handling CDN or network error during image download
- **WHEN** an HTTP request for album cover art or artist retrieval fails due to network drop, timeout, or HTTP 4xx/5xx status
- **THEN** the system catches the exception and returns a 300x300 deterministic algorithmic fallback tile derived from the entity title, allowing collage generation to complete successfully

#### Scenario: Deterministic fallback artwork
- **WHEN** the same entity's artwork repeatedly fails to download across separate runs
- **THEN** the fallback tile rendered for that entity is byte-for-byte identical between runs, with its colors and initials derived deterministically from the entity title

#### Scenario: Legacy solid black fallback still available
- **WHEN** the caller explicitly selects the legacy fallback style (or omits the new fallback configuration on a pre-v0.8.0 API surface)
- **THEN** a 300x300 solid black blank tile is produced as before

#### Scenario: Custom User-Agent header transmission
- **WHEN** web retrieval or image download requests are executed
- **THEN** the HTTP client includes a custom `User-Agent` identifying `lastfm-collage-generator`
