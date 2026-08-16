![](https://img.shields.io/pypi/dm/lastfmcollagegenerator?)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# lastfm-collage-generator

Python library to create Last.fm collages from user's top items. 

It supports different configurations like grid size, entity types, and time periods.

---

## Features

- Choose entity types: `album`, `artist`, `track`.
- Choose the number of rows and columns (up to 5x5).
- Choose the aggregation period: `7day`, `1month`, `3month`, `6month`, `12month`, `overall` (Default: `7day`).
- Displays dark translucent overlay banners with artist/title and playcount.

---

## Installation

### Using uv
```bash
uv add lastfmcollagegenerator
```

### Using pip
```bash
pip install lastfmcollagegenerator
```

---

## Usage / Examples

```python
from lastfmcollagegenerator.collage_generator import CollageGenerator

collage_generator = CollageGenerator(
    lastfm_api_key="YOUR_API_KEY", 
    lastfm_api_secret="YOUR_API_SECRET"
)

# Returns a PIL Image object
image = collage_generator.generate(
    entity="album", 
    username="username", 
    cols=5, 
    rows=5, 
    period="7day"
)
image.save("5x5_album_collage.png", "png")
```

### Options Reference

- **Entity**: `"album"`, `"artist"`, `"track"`
- **Period**: `"7day"`, `"1month"`, `"3month"`, `"6month"`, `"12month"`, `"overall"`
- **Grid Dimensions**: `cols` (1–5), `rows` (1–5)

---

## Development

The project uses [uv](https://docs.astral.sh/uv/) for project and package management.

### Prerequisites

Install `uv` (if not already installed):
```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using Homebrew
brew install uv
```

No other external dependencies or global package managers are required—`uv` manages Python versions and virtual environments automatically.

### Setup Environment

Clone the repository and install all dependencies (including dev tools):
```bash
uv sync
```

### Running Tests & Linters

```bash
# Run unit tests
uv run pytest tests/

# Run tests with coverage
uv run pytest --cov=src/lastfmcollagegenerator tests/

# Run linters & type checking
uv run flake8 src/ tests/
uv run black --check src/ tests/
uv run mypy src/
```

### Building the Package

Build the source distribution (`.tar.gz`) and wheel (`.whl`):
```bash
uv build
```

---

## License

[MIT](https://choosealicense.com/licenses/mit/)

---

## Authors

- [@paurieraf](https://www.github.com/paurieraf)
