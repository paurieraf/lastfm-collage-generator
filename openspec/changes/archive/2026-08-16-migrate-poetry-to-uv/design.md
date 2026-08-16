## Context

See `proposal.md` for the motivation to migrate from Poetry to `uv`. 

## Goals / Non-Goals

**Goals:**
- Replace Poetry with `uv` for dependency resolution, virtual environment management, and package installation.
- Select and configure a standard build backend since `poetry-core` will be removed.
- Update internal project documentation (`AGENTS.md`, `README.md`) and testing skills to use `uv` instead of Poetry.
- Ensure the packaged distribution continues to include the bundled `.ttf` fonts correctly.

**Non-Goals:**
- Changing the public API or internal architecture of the library.
- Changing the supported Python versions (`^3.8`).

## Decisions

**Decision 1: Build Backend**
- **Choice**: `hatchling`
- **Rationale**: `uv` uses standard PEP-621 `pyproject.toml` configuration and typically recommends `hatchling` for new projects (it's what `uv init` uses). It is modern, fast, and handles asset inclusion well.
- **Alternatives Considered**: `setuptools` (older, configuration can be more verbose), `flit-core` (also good, but `hatchling` is the prevailing modern default).

**Decision 2: Lockfile Generation**
- **Choice**: Replace `poetry.lock` with `uv.lock` via `uv lock`.
- **Rationale**: `uv` uses its own universal lockfile format which is significantly faster and standardizes the resolution for all platforms.

**Decision 3: Command Replacements**
- **Choice**: Replace `poetry run` with `uv run`, `poetry shell` with `uv run bash` (or just rely on implicit activation), and `poetry install` with `uv sync`.
- **Rationale**: Direct functional equivalents provided by `uv`.

## Risks / Trade-offs

- **Risk**: Asset Inclusion. Poetry used `MANIFEST.in` (and sometimes automatic inclusion) to bundle fonts (`src/lastfmcollagegenerator/fonts/*.ttf`). If `hatchling` isn't configured correctly, the distributed package might be missing fonts.
  - **Mitigation**: Configure `[tool.hatch.build.targets.wheel]` to explicitly include the `src` directory, or verify `hatchling` defaults correctly pick up the assets.

- **Risk**: Disruption to developers used to Poetry.
  - **Mitigation**: Update `AGENTS.md` and any AI agent skills in `.gemini/skills/` to reflect the new `uv` commands so AI agents and human developers know the new workflow.
