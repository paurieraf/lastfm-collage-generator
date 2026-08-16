## 1. Update Project Configuration

- [x] 1.1 Remove `poetry-core` build-backend and poetry specific configuration from `pyproject.toml`
- [x] 1.2 Add `hatchling` as the build-backend in `pyproject.toml`
- [x] 1.3 Ensure `hatchling` is configured to correctly bundle the fonts in `src/lastfmcollagegenerator/fonts/*.ttf` when building the wheel

## 2. Lockfile Migration

- [x] 2.1 Delete `poetry.lock`
- [x] 2.2 Generate `uv.lock` using `uv lock`
- [x] 2.3 Run `uv sync` to verify environment resolution and installation succeeds

## 3. Documentation and Skills Update

- [x] 3.1 Update `AGENTS.md` to document using `uv run` and `uv sync` instead of Poetry commands
- [x] 3.2 Update `README.md` instructions from Poetry to `uv`
- [x] 3.3 Update any AI agent test running scripts (e.g., in `.gemini/skills/`) to use `uv run` instead of `poetry run`
