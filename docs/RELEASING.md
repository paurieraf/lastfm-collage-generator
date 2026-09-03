# Release & Distribution Guide

This guide is intended for maintainers publishing new releases of `lastfm-collage-generator` (`lastfmcollagegenerator`) to [PyPI](https://pypi.org/project/lastfmcollagegenerator/).

---

## 1. Prerequisites

- Build tool: [uv](https://docs.astral-sh/uv/) (backed by `hatchling`).
- A PyPI maintainer account with API token permissions for `lastfmcollagegenerator`.

---

## 2. Release Steps

### 1. Update Package Version

Update the version string in `pyproject.toml`:

```toml
[project]
name = "lastfmcollagegenerator"
version = "X.Y.Z"
```

### 2. Verify QA & Tests

Ensure the offline test suite and all linters pass:

```bash
uv run pytest tests/ -v
uv run flake8 src/ tests/
uv run black --check src/ tests/
uv run mypy src/
```

### 3. Build Distribution Artifacts

Always delete previous builds in `dist/` before packaging:

```bash
# Clean previous build artifacts
rm -rf dist/

# Build source distribution (.tar.gz) and binary wheel (.whl)
uv build
```

### 4. Configure PyPI Authentication

`uv publish` authenticates automatically using the `UV_PUBLISH_TOKEN` environment variable or standard `~/.pypirc` / `~/.netrc`:

#### Via Shell Environment Variable (Recommended for CI / Terminals)
```bash
export UV_PUBLISH_TOKEN="pypi-AgEI..."
```

#### Via Global `~/.pypirc`
```ini
[distutils]
index-servers = pypi

[pypi]
username = __token__
password = pypi-AgEI...
```

### 5. Publish to PyPI

Upload the built wheel and sdist to PyPI:

```bash
uv publish
```

Verify that the new release appears on [PyPI](https://pypi.org/project/lastfmcollagegenerator/) and can be installed via:

```bash
pip install --upgrade lastfmcollagegenerator
```
