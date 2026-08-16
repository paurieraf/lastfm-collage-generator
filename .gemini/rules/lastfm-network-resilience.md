# Last.fm Retrieval Resilience & Network Safety

**Scope**: Web retrieval mechanisms, HTTP network requests, timeout policies, fallback strategies, and concurrency safety for `lastfm-collage-generator`.

---

## 1. Background & Retrieval Context

Due to changes in the Last.fm Audioscrobbler REST API v2.0, artist image URLs are no longer returned in API responses. To enable artist collages, `ArtistCollageBuilder` fetches the artist profile webpage (`https://www.last.fm/music/<artist>`) to extract the hero background image URL from the DOM.

Because web retrieval is inherently fragile and subject to CDN rate limiting, CAPTCHAs, and DOM layout changes, the following safety and resilience standards must be strictly enforced.

---

## 2. User-Agent Header Requirements

- **Prohibition of Default Python User-Agent**: Never issue requests using the default `python-requests/x.y.z` header. Cloudflare and Last.fm edge routers frequently block or challenge standard script user agents with HTTP 403 Forbidden.
- **Compliant Custom Headers**: Every HTTP request (both for web page retrieval and for binary image downloads) must include a custom, descriptive User-Agent header:

```python
DEFAULT_HEADERS = {
    "User-Agent": "lastfm-collage-generator/0.5.0 (+https://github.com/paurieraf/lastfm-collage-generator; contact: support@example.com)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}
```

---

## 3. Explicit HTTP Timeouts (Connect & Read)

- **Mandatory Timeout Parameter**: Every invocation of `requests.get()` MUST pass an explicit `timeout` argument.
- **Recommended Timeout Values**:
  - Connect timeout: `3.05` seconds (to handle TCP handshake delays without blocking).
  - Read timeout: `10.0` seconds (to allow image downloads under moderate bandwidth).
  - Example: `requests.get(url, headers=DEFAULT_HEADERS, timeout=(3.05, 10.0))`
- **Unbounded Calls Prohibited**: Invocations of `requests.get(url)` without `timeout=` are strictly prohibited to prevent worker threads from hanging indefinitely during CDN network interruptions.

---

## 4. URL Sanitization & Encoding

- Artist names in URLs must always be sanitized and properly percent-encoded using `urllib.parse.quote_plus(artist.name)` (or `quote(artist.name, safe='')`).
- Special characters (e.g., `"AC/DC"`, `"Tyler, The Creator"`, `"? / !"`), non-ASCII characters, and unicode artist names must never produce malformed URLs.

```python
import urllib.parse

def build_artist_url(artist_name: str) -> str:
    encoded_name = urllib.parse.quote_plus(artist_name.strip())
    return f"https://www.last.fm/music/{encoded_name}"
```

---

## 5. Blank Tile Fallback Policies

- **Zero Uncaught Exceptions**: Failures during retrieval or image downloading MUST NEVER crash the collage generation pipeline or abort sibling tile downloads.
- **Comprehensive Exception Catching**:
  - HTTP 404 (Artist not found) → catch `ArtistNotFound`, return blank tile.
  - DOM selector missing (Image not found) → catch `ArtistImageNotFound`, return blank tile.
  - Network timeouts & connection resets → catch `requests.RequestException`, return blank tile.
  - Image decoding errors (corrupt bytes) → catch `(OSError, IOError, ValueError)`, return blank tile.
- **Blank Tile Uniformity**:
  - Use `BaseCollageBuilder._generate_blank_tile()` to produce a uniform `300x300` solid black PNG byte array as the fallback tile.

```python
# Resilient retrieval pattern
@classmethod
def _get_artist_image(cls, artist: Artist) -> bytes:
    try:
        url_artist = urllib.parse.quote_plus(artist.name)
        target_url = f"https://www.last.fm/music/{url_artist}"
        resp = requests.get(target_url, headers=DEFAULT_HEADERS, timeout=(3.05, 10.0))
        
        if resp.status_code == 404:
            raise ArtistNotFound(f"Artist '{artist.name}' not found on Last.fm")
        resp.raise_for_status()

        soup = bs4.BeautifulSoup(resp.content, "html5lib")
        header_elem = soup.find(class_="header-new-background-image")
        if not header_elem or not header_elem.get("content"):
            raise ArtistImageNotFound(f"No hero image found for artist '{artist.name}'")

        img_url = str(header_elem.get("content"))
        img_resp = requests.get(img_url, headers=DEFAULT_HEADERS, timeout=(3.05, 10.0))
        img_resp.raise_for_status()

        with io.BytesIO(img_resp.content) as in_stream:
            in_stream.seek(0)
            with Image.open(in_stream) as img:
                img.thumbnail((cls.TILE_WIDTH, cls.TILE_HEIGHT))
                with io.BytesIO() as out_stream:
                    img.save(out_stream, format="PNG")
                    return out_stream.getvalue()
    except (ArtistNotFound, ArtistImageNotFound, requests.RequestException, OSError, Exception) as exc:
        logger.warning("Falling back to blank tile for artist '%s': %s", getattr(artist, "name", "unknown"), exc)
        return cls._generate_blank_tile()
```

---

## 6. Thread Safety under `ThreadPoolExecutor`

- **Isolated Thread Scope**: Each worker thread in `_create_tiles_from_top_items()` must operate exclusively on its own local parameters, request buffers, and PIL image instances.
- **No Shared Mutable State**: Do not share mutable collections or global request sessions across threads without synchronization locks.
- **Deterministic Ordering**: Because `concurrent.futures.as_completed()` yields futures in non-deterministic arrival order, the collected list of `CollageTile` objects MUST be deterministically sorted prior to canvas placement:
  ```python
  # Deterministic secondary sort key prevents flaky ordering on tied playcounts
  tiles.sort(key=lambda x: (int(x.playcount), x.title), reverse=True)
  ```
