# caching-resilience Specification

## Purpose
Provides multi-tier artwork caching and network resilience middleware so repeated collage generation avoids redundant downloads and survives transient Last.fm/CDN failures gracefully.
## Requirements
### Requirement: Multi-Tier Artwork Caching
The system SHALL cache downloaded artwork across two tiers: a Tier-1 in-memory LRU cache and a Tier-2 persistent SQLite-backed disk cache located under `~/.cache/lastfm-collage/`, with time-to-live (TTL) expiration of 30 days for album covers and 7 days for retrieved artist hero images.

#### Scenario: Cache hit avoids network request
- **WHEN** an album cover URL has been fetched within its 30-day TTL and the same URL is requested again
- **THEN** the cached bytes are returned without issuing any HTTP request

#### Scenario: Expired cache entry is refreshed
- **WHEN** an album cover cache entry is older than its TTL
- **THEN** the stale entry is discarded and a fresh HTTP request is issued, with the new bytes stored back into the cache

#### Scenario: Disk cache persists across processes
- **WHEN** a collage is generated in a new process after a previous run populated the disk cache
- **THEN** non-expired artwork is served from the SQLite disk cache without network access

#### Scenario: Cache is user-scoped and ignorable
- **WHEN** the cache directory does not exist or is not writable
- **THEN** caching degrades to network-only operation without raising errors

### Requirement: HTTP Rate Limiting
The system SHALL limit outbound HTTP requests to Last.fm and artwork CDNs using a token-bucket rate limiter with a default rate of 5 requests per second.

#### Scenario: Burst requests are throttled
- **WHEN** collage generation issues more requests than the configured rate
- **THEN** the rate limiter delays or spaces requests so the sustained rate never exceeds the configured limit

### Requirement: Exponential Backoff with Full Jitter
The system SHALL retry transient HTTP failures (timeouts, connection errors, HTTP 429/5xx) using exponential backoff with full jitter, up to a bounded number of attempts.

#### Scenario: Transient failure is retried and recovers
- **WHEN** an HTTP request fails with a transient error and a subsequent retry succeeds
- **THEN** the artwork bytes are returned and no fallback tile is produced

#### Scenario: Persistent failure gives up gracefully
- **WHEN** all retry attempts for an artwork fail
- **THEN** the system stops retrying and returns the deterministic fallback artwork tile without aborting collage assembly

### Requirement: Circuit Breaker for Retrieval Fallbacks
The system SHALL maintain a circuit breaker per remote host (Last.fm web and artwork CDNs) that, after a threshold of consecutive failures, opens and fast-fails subsequent requests to fallback tiles for a cooldown period.

#### Scenario: Circuit opens after repeated failures
- **WHEN** a remote host fails a configured number of consecutive requests
- **THEN** the circuit breaker opens and subsequent requests to that host are rejected immediately, yielding fallback tiles without network waits

#### Scenario: Circuit half-opens and recovers
- **WHEN** the cooldown period of an open circuit elapses and a probe request succeeds
- **THEN** the circuit closes and normal request processing resumes

#### Scenario: Resilience failure never aborts generation
- **WHEN** rate limiting, retries, or circuit breaking prevent an artwork from being acquired
- **THEN** collage generation still completes with fallback tiles in place of the missing artwork
