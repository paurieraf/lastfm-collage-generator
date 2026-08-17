## MODIFIED Requirements

### Requirement: Multi-Tier Artwork Caching
The system SHALL cache downloaded artwork across two tiers: a Tier-1 in-memory LRU cache and a Tier-2 persistent SQLite-backed disk cache located under `~/.cache/lastfm-collage/`, with time-to-live (TTL) expiration of 30 days for album covers and 7 days for retrieved artist hero images. The Tier-1 in-memory cache specifically accelerates repetitive artist image web retrieval across same-process generations.

#### Scenario: Cache hit avoids network request
- **WHEN** an album cover or artist hero image URL has been fetched within its TTL and the same URL is requested again
- **THEN** the cached bytes are returned without issuing any HTTP request

#### Scenario: In-memory cache accelerates repeated artist retrieval
- **WHEN** the same artist is retrieved multiple times in the same process
- **THEN** the Tier-1 in-memory cache serves the image instantly without touching the SQLite disk cache or network

#### Scenario: Expired cache entry is refreshed
- **WHEN** an album cover cache entry is older than its TTL
- **THEN** the stale entry is discarded and a fresh HTTP request is issued, with the new bytes stored back into the cache

#### Scenario: Disk cache persists across processes
- **WHEN** a collage is generated in a new process after a previous run populated the disk cache
- **THEN** non-expired artwork is served from the SQLite disk cache without network access

#### Scenario: Cache is user-scoped and ignorable
- **WHEN** the cache directory does not exist or is not writable
- **THEN** caching degrades to network-only operation without raising errors
