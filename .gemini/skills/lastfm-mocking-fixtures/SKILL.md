---
name: lastfm-mocking-fixtures
description: >-
  Provides mocking patterns, pytest fixtures, synthetic image generators, and mock builders for pylast entities (User, Album, Artist, Track) and Last.fm web scraping. Use when authoring or updating unit and integration tests for lastfm-collage-generator.
---

# Last.fm Mocking Fixtures & Patterns Skill

This skill provides ready-to-use pytest fixtures, synthetic image factories, and mock builders for testing `lastfm-collage-generator` without external network dependencies.

---

## 1. Reference Fixture Templates

Directly import or adapt fixture patterns from [`references/fixture_templates.py`](./references/fixture_templates.py) in your `tests/conftest.py`.

Key helper classes provided in the reference:
- **`SyntheticImageFactory`**: Creates in-memory PNG/JPEG byte streams of custom dimensions and colors without writing files to disk.
- **`MockPylastEntityFactory`**: Factory generating mock `Album`, `Artist`, `Track`, and `TopItem` objects with configurable playcounts and image URLs.
- **`MockLastfmNetwork` & `MockLastfmClient`**: Drop-in mock replacement for `pylast.LastFMNetwork` and `LastfmClient`.
- **`MockHtmlScraperResponses`**: HTML strings simulating valid artist pages, pages without background images, and 404 responses.

---

## 2. Common Mocking Recipes

### 2.1 Generating In-Memory Synthetic Images for Tests

```python
from unittest.mock import MagicMock
import io
from PIL import Image

def create_synthetic_png(width: int = 300, height: int = 300, color: str = "blue") -> bytes:
    """Creates raw PNG bytes in memory for mocking image downloads."""
    img = Image.new("RGB", (width, height), color=color)
    with io.BytesIO() as buf:
        img.save(buf, format="PNG")
        return buf.getvalue()
```

### 2.2 Mocking Album & Track Top Items in Pytest

```python
import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_top_albums():
    """Returns a list of 9 mock top albums for a 3x3 grid."""
    items = []
    for i in range(1, 10):
        album = MagicMock()
        album.artist = f"Artist {i}"
        album.title = f"Album {i}"
        album.get_cover_image.return_value = f"https://mock.cdn/album_{i}.png"
        
        top_item = MagicMock()
        top_item.item = album
        top_item.weight = 100 - i * 5
        items.append(top_item)
    return items
```

### 2.3 Mocking Artist HTML Web Scraping

```python
import pytest
from unittest.mock import patch, MagicMock

SAMPLE_ARTIST_HTML = """
<!DOCTYPE html>
<html>
<body>
  <div class="header-new-background-image" content="https://mock.cdn/artist_hero.png"></div>
</body>
</html>
"""

@pytest.fixture
def patch_artist_scraping(monkeypatch, synthetic_png_bytes):
    """Mocks both the HTML page request and the image download request."""
    def mock_requests_get(url, *args, **kwargs):
        response = MagicMock()
        if "last.fm/music" in url:
            response.status_code = 200
            response.content = SAMPLE_ARTIST_HTML.encode("utf-8")
        else:
            response.status_code = 200
            response.content = synthetic_png_bytes
        return response

    monkeypatch.setattr("requests.get", mock_requests_get)
```

### 2.4 Testing Scraping Fallback (HTTP 404 or Missing Image)

```python
def test_artist_not_found_fallback(monkeypatch):
    """Verifies that HTTP 404 returns a blank tile instead of crashing."""
    def mock_404_get(url, *args, **kwargs):
        response = MagicMock()
        response.status_code = 404
        return response

    monkeypatch.setattr("requests.get", mock_404_get)
    # Instantiate builder and verify blank tile is produced
```

---

## 3. Best Practices

1. **Avoid Live Network Calls**: Always verify no live calls are made by checking that tests pass offline.
2. **Keep Fixtures Minimal**: Generate small image sizes (`300x300` or `10x10`) in memory to ensure test execution takes <1 second.
3. **Assert Visual Invariants**: Check `image.size == (cols * 300, rows * 300)` and inspect pixel colors to ensure title overlays do not bleed into neighboring rows.
