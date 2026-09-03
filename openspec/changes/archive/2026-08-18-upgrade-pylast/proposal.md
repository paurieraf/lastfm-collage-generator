## Why

The current package pins `pylast==5.3.0` (released in May 2024) and targets legacy Python `>=3.8.1` (Python 3.8 and 3.9 have both reached end-of-life). Upgrading to `pylast>=7.1.0` brings full static typing support (`py.typed` / PEP 561) for `mypy`, eliminates potential socket resource warnings through `httpx.Client` context managers, and fixes upstream bugs in artist playcount calculations.

## What Changes

- **Dependency Upgrade**: Upgrade `pylast` dependency specification in `pyproject.toml` from `5.3.0` to `^7.1.0`.
- **Python Runtime Requirement**: Update `requires-python` from `>=3.8.1` to `>=3.10` to match pylast 6+ and 7+ baseline runtime requirements.
- **Lockfile & Environment**: Regenerate `uv.lock` and synchronize environment via `uv sync`.
- **Documentation**: Update `AGENTS.md`, `PROJECT_OVERVIEW.md`, and `README.md` to reflect the updated dependency version and Python `>=3.10` requirement.

## Capabilities

### New Capabilities
<!-- None -->

### Modified Capabilities
- `collage-core-engine`: Update runtime environment requirements to Python 3.10+ and integrate with `pylast>=7.1.0`.

## Impact

- `pyproject.toml`: `dependencies` and `requires-python` updated.
- `uv.lock`: Dependency resolution updated to `pylast 7.1.0` and compatible dependencies.
- `src/lastfmcollagegenerator/lastfm/client.py`: Retains full compatibility with pylast 7.x API surface.
- `tests/`: All unit test suites continue passing with updated mock definitions and type checkers.
- Documentation: `AGENTS.md`, `PROJECT_OVERVIEW.md`, `README.md`.
