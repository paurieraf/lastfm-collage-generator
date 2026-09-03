# Contributing to lastfm-collage-generator

Thank you for your interest in contributing! Whether you are fixing a bug, adding support for a new feature, or improving documentation, your help is welcome.

---

## 🛠️ Development Setup

The project uses [uv](https://docs.astral-sh/uv/) for fast, deterministic Python environment and dependency management.

### 1. Clone the Repository

```bash
git clone https://github.com/paurieraf/lastfm-collage-generator.git
cd lastfm-collage-generator
```

### 2. Install Dependencies

Install the project dependencies and configure the virtual environment in one step:

```bash
uv sync
```

This creates a local `.venv` and installs all runtime and development dependencies.

### 3. Local Editable Installation (Optional)

If you are building an application alongside this library (such as a Discord bot or web service):

```bash
# Within your consuming project's virtual environment:
uv pip install -e /path/to/lastfm-collage-generator
# or with standard pip:
pip install -e /path/to/lastfm-collage-generator
```

Any changes made in `src/` will be immediately reflected in your consumer app.

---

## 🧪 Testing & Quality Assurance

We enforce a strict **zero live network calls** policy for automated tests. All tests in `tests/` execute 100% offline using synthetic in-memory fixtures.

### Running the Pytest Suite

```bash
# Run all unit tests
uv run pytest tests/ -v

# Run with line and branch coverage report
uv run pytest --cov=lastfmcollagegenerator --cov-report=term-missing tests/

# Enforce minimum 90% coverage threshold
uv run pytest --cov=lastfmcollagegenerator --cov-fail-under=90 tests/
```

### Static Analysis & Linters

Run formatting and static type checkers before submitting code:

```bash
# Check code style with flake8
uv run flake8 src/ tests/

# Check formatting with Black
uv run black --check src/ tests/

# Run static type checking with mypy
uv run mypy src/
```

To automatically format your code with Black:

```bash
uv run black src/ tests/
```

---

## 🔍 Development & Debugging Tools

### Zero-Build Debug Runner (`scripts/debug_collage.py`)

A standalone runner script is available in `scripts/` to generate collages instantly during development:

#### Offline Mock Mode (No API keys or internet needed)

Generates synthetic colored tiles with geometric artwork to test canvas allocation, fonts, coordinate math, and overlays instantly:

```bash
# Generate 3x3 mock album collage
uv run python scripts/debug_collage.py --mock -g 3x3

# Generate 5x5 mock artist collage and open in your default image viewer
uv run python scripts/debug_collage.py --mock -e artist -g 5x5 --open

# Generate asymmetric 3x5 track collage without banners
uv run python scripts/debug_collage.py --mock -e track -c 3 -r 5 --no-title -o output/mock_track.png
```

#### Live Mode with `.env`

Test against the real Last.fm API and web scraping:

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Fill in your `LASTFM_API_KEY`, `LASTFM_API_SECRET`, and `LASTFM_USERNAME`.
3. Run the live generator:
   ```bash
   uv run python scripts/debug_collage.py --live -e album -g 3x3 --open
   ```

### VS Code Breakpoint Debugging

Pre-configured launch configurations are included in `.vscode/launch.json`:
- `🎨 Debug: Mock Album Collage (3x3)`: Step through Pillow rendering offline.
- `🎨 Debug: Mock Artist Collage (5x5)`: Step through multi-row grid math.
- `🌐 Debug: Live Album Collage (.env)`: Step through live Last.fm API calls.
- `🌐 Debug: Live Artist Collage (.env)`: Step through web scraping pipeline.
- `🎵 Debug: Live Track Collage (.env)`: Step through track cover fallbacks.
- `🧪 Debug: Current Test File (Pytest)`: Step through test cases under the debugger.

---

## 📋 Pull Request Quality Checklist

Before submitting a Pull Request, please ensure that:

- [ ] All new code has complete Python 3.8-compatible type annotations (`typing.List`, `typing.Optional`, etc.).
- [ ] No live network requests are made during test execution (use synthetic mocks).
- [ ] All `PIL.Image` and `io.BytesIO` streams are cleanly closed or managed via context managers.
- [ ] HTTP requests specify explicit timeouts (`timeout=(3.05, 10.0)`) and custom `User-Agent` headers.
- [ ] New domain exceptions inherit from `LastfmCollageGeneratorError`.
- [ ] Pytest suite passes cleanly with zero warnings or failures: `uv run pytest tests/ -v`.
- [ ] Linters pass: `uv run flake8 src/ tests/`, `uv run black --check src/ tests/`, `uv run mypy src/`.

---

## 🏛️ Architecture & Internal Design

For an in-depth explanation of the 4-layer architecture (Facade → Factory → Builder → Client Adapter), coordinate geometry, and defect remediation history, refer to:
- [`PROJECT_OVERVIEW.md`](./PROJECT_OVERVIEW.md)
- [`AGENTS.md`](./AGENTS.md)
