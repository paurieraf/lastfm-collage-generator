# Testing Standards & Mocking Guidelines

**Scope**: All automated test suites (`tests/`), test fixtures, CI/CD verification, and quality gates for `lastfm-collage-generator`.

---

## 1. Zero Network Calls Policy

- **MANDATORY**: Test suites MUST execute 100% offline. Outbound network traffic to Last.fm API endpoints (`ws.audioscrobbler.com`), Last.fm web pages (`www.last.fm/music/...`), or CDNs is strictly prohibited during automated test execution.
- **Enforcement**:
  - Tests must pass when running in air-gapped environments or without internet connectivity.
  - Any test attempting live network I/O is considered defective and must be patched with appropriate mocks.
  - CI test runners should use socket-blocking fixtures (e.g. `pytest-socket` or custom mock monkeypatching) to guarantee no network leaks.

---

## 2. Mocking Guidelines

### 2.1 Mocking `pylast` API Objects
- Mock the network boundary: `pylast.LastFMNetwork` should never be instantiated with live credentials in tests.
- Mock `pylast.User` and top item queries (`get_top_albums`, `get_top_artists`, `get_top_tracks`).
- Return mock `pylast.TopItem` instances wrapping mock `Album`, `Artist`, or `Track` objects:

```python
from unittest.mock import MagicMock
import pytest

@pytest.fixture
def mock_top_album():
    """Generates a mock pylast TopItem for an album."""
    item = MagicMock()
    item.artist = "Radiohead"
    item.title = "OK Computer"
    item.get_cover_image.return_value = "https://mock.cdn/ok_computer.jpg"
    
    top_item = MagicMock()
    top_item.item = item
    top_item.weight = 150
    return top_item
```

### 2.2 Mocking HTTP Requests & Web Retrieval
- Use `unittest.mock.patch("requests.get")` or `requests_mock` fixture to intercept calls in `ArtistCollageBuilder` and `AlbumCollageBuilder`.
- Test both success and edge-case responses:
  - **HTTP 200 with Valid HTML**: Contains `<div class="header-new-background-image" content="https://mock.cdn/artist.jpg">`.
  - **HTTP 200 with Missing Element**: HTML without `.header-new-background-image` (must trigger `ArtistImageNotFound` and fallback to blank tile).
  - **HTTP 404 Not Found**: Simulates non-existent artist (must trigger `ArtistNotFound` and fallback to blank tile).
  - **HTTP 500 / Network Timeout**: Simulates CDN / server failures (must gracefully fallback to blank tile without crashing).

```python
# Example: Mocking artist retrieval
MOCK_ARTIST_HTML = """
<!DOCTYPE html>
<html>
<head><title>Artist Page</title></head>
<body>
  <div class="header-new-background-image" content="https://mock.cdn/artist_hero.png"></div>
</body>
</html>
"""

def test_artist_retrieve(monkeypatch, synthetic_png_bytes):
    def mock_get(url, *args, **kwargs):
        resp = MagicMock()
        if "last.fm/music" in url:
            resp.status_code = 200
            resp.content = MOCK_ARTIST_HTML.encode("utf-8")
        else:
            resp.status_code = 200
            resp.content = synthetic_png_bytes
        return resp
    
    monkeypatch.setattr("requests.get", mock_get)
```

---

## 3. Synthetic In-Memory Image Generation

- **Zero Binary Bloat**: Do not check in large `.jpg` or `.png` binary files into the Git repository for test fixtures.
- **In-Memory Generation**: Use Pillow to dynamically generate solid-color PNG/JPEG byte streams via `io.BytesIO`.
- **Fast Execution**: Generate minimal dimensions (e.g., `10x10` or `300x300`) to maintain sub-second test execution speeds.

```python
import io
from PIL import Image

def generate_synthetic_image_bytes(width: int = 300, height: int = 300, color: str = "red") -> bytes:
    """Generates an in-memory PNG image byte stream for testing."""
    img = Image.new("RGB", (width, height), color=color)
    with io.BytesIO() as buffer:
        img.save(buffer, format="PNG")
        return buffer.getvalue()
```

---

## 4. Test Directory Structure & Organization

Organize tests by module and responsibility:

```
tests/
├── __init__.py
├── conftest.py                   # Shared pytest fixtures (mock clients, synthetic images, mock HTML)
├── test_validation.py            # Facade input validation (cols/rows bounds, entity, period)
├── test_factory.py               # CollageBuilderFactory entity resolution and error cases
├── test_rendering_engine.py      # Pillow canvas composition, layout geometry, typography
├── test_builders.py              # Concrete builders (AlbumCollageBuilder, TrackCollageBuilder)
├── test_retrieve.py              # ArtistCollageBuilder web retrieval and fallback behavior
└── test_integration.py           # End-to-end Facade generate() with mocked client backend
```

---

## 5. Visual & Geometric Regression Assertions

- **Coordinate Verification**: Tests for image compositing must assert that pixels at specific coordinates match expected colors.
- **Overlay Boundary Check**:
  - For a `3x3` collage, verify that row 1 tile banner (`y = 535` to `y = 600`) does NOT bleed into row 2 (`y = 600` to `y = 900`).
  - Test canvas dimensions: assert `image.size == (cols * 300, rows * 300)`.
  - Test color modes: assert `image.mode == "RGB"`.

---

## 6. Coverage Thresholds & Quality Gates

- **Minimum Line Coverage**: 90% across `src/lastfmcollagegenerator/`.
- **Minimum Branch Coverage**: 85% for all conditional branches.
- **Required Test Categories**:
  1. Happy path execution for each entity type (`album`, `artist`, `track`).
  2. Boundary condition tests (`cols=1`, `cols=5`, `rows=1`, `rows=5`).
  3. Negative validation tests (`cols=0`, `cols=6`, `rows=-1`, `period="invalid"`).
  4. Error resilience tests (network timeouts, empty image URLs, 404 responses, HTML parser errors).
  5. Title banner formatting tests (with playcount, without playcount, long titles).
