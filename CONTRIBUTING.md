# Contributing to lastfm-collage-generator

Thank you for your interest in contributing to `lastfm-collage-generator`!

This document covers local development setup, testing, code quality standards, and pull request guidelines.

---

## 🛠️ Development Setup

We use [uv](https://docs.astral.sh/uv/) for fast, reproducible dependency management and virtual environments.

### 1. Clone the repository

```bash
git clone https://github.com/paurieraf/lastfm-collage-generator.git
cd lastfm-collage-generator
```

### 2. Install dependencies

```bash
uv sync
```

This sets up a `.venv` with all runtime and development dependencies (pytest, black, flake8, mypy).

---

## 🧪 Testing

All automated tests in this repository run **100% offline** using synthetic in-memory image fixtures and mocks. Tests never make live network calls to Last.fm or external CDNs.

### Running tests

```bash
# Run the test suite
uv run pytest tests/ -v

# Run with test coverage
uv run pytest --cov=lastfmcollagegenerator --cov-report=term-missing tests/
```

---

## 🎨 Offline Mock Debug Runner

You can generate sample collages instantly without API credentials using the built-in debug runner:

```bash
# Generate a 3x3 album collage offline
uv run python scripts/debug_collage.py --mock -g 3x3 -o output/mock_3x3.png

# Generate a 5x5 artist collage with sunset theme
uv run python scripts/debug_collage.py --mock -e artist -g 5x5 --theme sunset -o output/sunset_5x5.png

# Generate a clean collage (no text overlay)
uv run python scripts/debug_collage.py --mock -g 4x4 --no-text -o output/clean.png
```

---

## 🔍 Code Style & Quality

Before opening a pull request, ensure your code passes all linters and type checkers:

```bash
# Code formatting
uv run black --check src/ tests/

# Syntax & PEP 8 linting
uv run flake8 src/ tests/

# Type checking
uv run mypy src/
```

---

## 📋 Pull Request Guidelines

1. **Focus on single concerns**: Keep PRs scoped to one feature, fix, or improvement.
2. **Offline tests**: Any new feature or bug fix must include offline pytest coverage in `tests/`.
3. **Type hints**: Maintain Python `>= 3.8` compatibility with complete type annotations.
4. **Clean resource handling**: Always close or use context managers for PIL `Image` and `io.BytesIO` streams.
5. **No network calls in tests**: Use synthetic image data rather than committing binary fixtures or making HTTP requests.

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).
