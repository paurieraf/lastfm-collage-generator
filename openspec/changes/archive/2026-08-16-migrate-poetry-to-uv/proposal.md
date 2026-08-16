## Why

The project currently uses Poetry for dependency management and packaging. Migrating to `uv` will significantly speed up dependency resolution, environment creation, and installation times. `uv` is a modern, fast Python package and project manager written in Rust that provides a drop-in replacement for many Poetry workflows with better performance.

## What Changes

- Remove `poetry` (specifically `poetry-core` build backend) and Poetry-specific configuration from `pyproject.toml`.
- Configure `pyproject.toml` for `uv` (using `hatchling` or another standard backend like `setuptools` as `uv` standardizes on standard PEP 621 metadata).
- Delete `poetry.lock`.
- Generate a new `uv.lock`.
- Update any documentation (like `AGENTS.md`) and scripts that rely on `poetry run` or `poetry install` to use `uv run` and `uv sync`.

## Capabilities

### New Capabilities

### Modified Capabilities

## Impact

- Development workflow changes: developers and agents will need to use `uv` commands instead of `poetry` commands.
- CI/CD pipelines (if any exist) will need to be updated to use `uv` instead of Poetry.
- The `lastfmcollagegenerator` package itself will remain unchanged in its runtime behavior and API; this is purely a tooling change.
