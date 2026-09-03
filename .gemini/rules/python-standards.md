# Python Standards & Conventions

**Scope**: All Python source code (`src/`), tests (`tests/`), scripts, and tooling for `lastfm-collage-generator`.

---

## 1. Runtime & Python Version Compatibility

- **Target Version**: Python `^3.8` (compatible with Python 3.8, 3.9, 3.10, 3.11, and 3.12).
- **Standard Library Typing**: Use `from typing import List, Tuple, Dict, Optional, Union, Callable, Any` for full compatibility with Python 3.8 runtimes (do not use bare `list[str]` or `tuple[int, int]` in type annotations without `from __future__ import annotations`).
- **Path Handling**: Use `pathlib.Path` or `os.path` for robust cross-platform path resolution.

---

## 2. Type Annotations & Code Clarity

- **Strict Type Hints**: All functions, methods, class attributes, and module-level constants must include explicit type annotations.
- **Return Types**: Every function/method must declare its return type (e.g., `-> None`, `-> PIL.Image.Image`, `-> List[CollageTile]`).
- **Docstrings**: All public classes, public methods, and module exports must include Google-style or PEP 257 docstrings explaining parameters, return types, and potential exceptions.

```python
# Good: Explicit type hints and clear docstring
def generate(
    self,
    entity: str,
    username: str,
    cols: int,
    rows: int,
    period: str = "7day",
) -> Image.Image:
    """Generate an NxM composite collage from user scrobbles.

    Args:
        entity: Musical entity type ('album', 'artist', or 'track').
        username: Last.fm profile username.
        cols: Number of grid columns (1 to 5).
        rows: Number of grid rows (1 to 5).
        period: Last.fm aggregation period ('7day', '1month', etc.).

    Returns:
        A composited PIL.Image.Image in RGB mode.

    Raises:
        ValueError: If parameters violate domain bounds.
        LastfmAPIError: If Last.fm API communication fails.
    """
```

---

## 3. Pillow (PIL) Image Handling & Resource Hygiene

- **Resource Lifecycle Management**:
  - Image streams (`io.BytesIO`) and temporary `PIL.Image` objects must be properly closed or used within context managers to prevent file descriptor leaks and memory bloat.
  - When loading images from byte buffers, seek to byte offset 0 (`stream.seek(0)`) before opening.
  - When saving synthetic images to bytes, use `io.BytesIO` and extract bytes via `.getvalue()`.
- **Image Mode & Format**:
  - Canvas creation: Always allocate composite canvas in `"RGB"` mode (`Image.new("RGB", (width, height))`) unless alpha transparency is specifically required.
  - Title overlay: Allocate overlay buffers in `"RGBA"` mode when performing alpha blending or translucent rectangle drawing.
  - Truncated Images: Enable `ImageFile.LOAD_TRUNCATED_IMAGES = True` to safely handle incomplete CDN transfers without raising `OSError`.
- **Pixel Geometry & Memory Footprint**:
  - Avoid creating unnecessarily large intermediate images. Standard tile size is `300 x 300` pixels (`TILE_WIDTH = 300`, `TILE_HEIGHT = 300`).
  - When resizing external images, use `img.thumbnail((300, 300))` or `img.resize((300, 300), Image.Resampling.LANCZOS)` (or `Image.ANTIALIAS` with backward compatibility fallback).

```python
# Resource cleanup example
def create_thumbnail_bytes(image_data: bytes, width: int = 300, height: int = 300) -> bytes:
    with io.BytesIO(image_data) as in_stream:
        in_stream.seek(0)
        with Image.open(in_stream) as img:
            img.thumbnail((width, height))
            with io.BytesIO() as out_stream:
                img.save(out_stream, format="PNG")
                return out_stream.getvalue()
```

---

## 4. Dataclasses Usage & Immutability

- **Data Transfer Objects**: Use `@dataclass` for pure data container structures (e.g., `CollageTile`, `CollageBuilderConfig`, `LastfmConfig`).
- **Immutability & Safety**:
  - For configuration objects that should not change during execution, prefer `@dataclass(frozen=True)`.
  - Avoid mutable default arguments; use `field(default_factory=...)` where needed.
- **Dead Code Prevention**:
  - Do not introduce unused or orphaned dataclasses. Every defined dataclass must have an active role in data flow.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class CollageTile:
    """Immutable data transfer object representing a single collage tile."""
    data: bytes
    playcount: int
    title: str

@dataclass(frozen=True)
class CollageBuilderConfig:
    """Configuration parameters for building a collage matrix."""
    cols: int
    rows: int
    period: str
    show_playcount: bool = True
    font_bold: bool = False
```

---

## 5. Domain Exception Hierarchy

- **Centralized Definition**: All custom exceptions must reside in `src/lastfmcollagegenerator/exceptions.py`.
- **Base Exception**: All project-specific exceptions must derive from a common base class: `LastfmCollageGeneratorError(Exception)`.
- **Hierarchy Structure**:
  - `LastfmCollageGeneratorError` (Base)
    - `ValidationError` (Base for invalid input parameters)
      - `InvalidEntityError`
      - `InvalidGridDimensionsError`
      - `InvalidPeriodError`
    - `ScrapingError` (Base for HTML scraping failures)
      - `ArtistNotFound`
      - `ArtistImageNotFound`
    - `LastfmClientError` (Base for API client failures)
- **Defensive Error Handling**: Never catch bare `except:`. Catch specific exceptions (`requests.RequestException`, `ArtistNotFound`, `KeyError`) and transform or handle them gracefully.

```python
# exceptions.py hierarchy
class LastfmCollageGeneratorError(Exception):
    """Base exception for all lastfm-collage-generator errors."""
    pass

class ValidationError(LastfmCollageGeneratorError, ValueError):
    """Raised when user-supplied generation parameters fail validation."""
    pass

class InvalidEntityError(ValidationError):
    """Raised when an unrecognized entity string is provided."""
    pass

class InvalidGridDimensionsError(ValidationError):
    """Raised when columns or rows exceed allowed limits or are non-positive."""
    pass

class ScrapingError(LastfmCollageGeneratorError):
    """Base exception for web scraping failures."""
    pass

class ArtistNotFound(ScrapingError):
    """Raised when Last.fm returns HTTP 404 for an artist URL."""
    pass

class ArtistImageNotFound(ScrapingError):
    """Raised when no artist hero image is found in Last.fm HTML."""
    pass
```

---

## 6. Defensive Programming & Immutability Principles

- **Early Input Validation**: Validate all inputs at the entrypoint (`CollageGenerator._validate_parameters`) before allocating resources, spawning thread pools, or performing network I/O.
- **Immutable Constants**: Store fixed domain collections in tuples (`ENTITIES`, `PERIODS`) inside `constants.py` to prevent accidental runtime mutation.
- **No Global Mutable State**: Avoid global state or singleton instances with mutable properties. Pass dependencies (`LastfmClient`, `CollageBuilderConfig`) explicitly via constructor injection.
