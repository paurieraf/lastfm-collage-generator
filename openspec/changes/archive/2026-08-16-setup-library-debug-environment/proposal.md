## Why

Testing and debugging `lastfm-collage-generator` currently involves heavy friction: developers must build distribution packages, switch to external consumer applications, manually reinstall wheel files, and attempt remote debugging. Furthermore, the repository lacks clear, documented procedures for packaging releases and publishing updates to PyPI using modern tooling (`uv`).

This change establishes an in-repo developer experience and debugging environment that allows zero-build, instant debugging from both Visual Studio Code (1-click F5 with breakpoints) and the terminal (`uv run scripts/debug_collage.py` with mock and live `.env` modes), along with complete packaging and PyPI release guidelines.

## What Changes

- **Debug Runner CLI (`scripts/debug_collage.py`)**: A unified, zero-build developer harness supporting:
  - `--mock`: Fast, offline synthetic rendering (0 network calls, ideal for Pillow/layout/math debugging).
  - `--live`: Real Last.fm API queries and artist web scraping using credentials and username loaded from `.env`.
  - `--open`: Automatically opens generated collage images in the default system viewer.
  - Interactive REPL mode for dynamic object inspection.
- **Local Environment Configuration (`.env.example` & `.gitignore`)**:
  - Adds `.env.example` defining `LASTFM_API_KEY`, `LASTFM_API_SECRET`, `LASTFM_USERNAME`, and default parameters.
  - Ensures `.env` and `output/` directories are properly ignored in `.gitignore`.
- **VS Code Development Profiles (`.vscode/launch.json` & `.vscode/settings.json`)**:
  - Pre-configured launch configurations for F5 debugging (Mock Album/Artist, Live Album/Artist/Track with `.env`, Pytest active test).
  - Configures Python interpreter path (`.venv`), Pytest discovery, and source analysis paths.
- **Project Documentation Updates**:
  - Updates `README.md` with a comprehensive "Development & Debugging" section explaining the `.env` setup, CLI usage, VS Code F5 workflows, and offline mock modes.
  - Adds a detailed "Packaging & Publishing to PyPI" section detailing version bumping in `pyproject.toml`, clean build artifact generation (`uv build`), and secure PyPI upload workflows (`uv publish` / token auth).

## Capabilities

### New Capabilities
- `library-debug-environment`: Provides unified developer workflows, VS Code launch configurations, environment variable management (`.env`), dedicated CLI runner for live and mock debugging, packaging and PyPI release instructions, and developer documentation.

### Modified Capabilities
<!-- No requirement changes to existing end-user capabilities -->

## Impact

- **Affected Systems**: Developer tooling, `.vscode/` configurations, `scripts/` directory, `.gitignore`, documentation files (`README.md`), local execution environment.
- **Dependencies**: No new runtime dependencies required.
- **Breaking Changes**: None. Does not affect the public API of `lastfmcollagegenerator`.
