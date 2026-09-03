## Context

See `proposal.md` for motivation. The project is a pure Python library managed with `uv` and `hatchling`. It packages code under `src/lastfmcollagegenerator/`. To test changes previously, a wheel had to be built and installed in an external consumer app. Furthermore, the build and PyPI distribution steps need clear documentation.

## Goals / Non-Goals

**Goals:**
- Provide instant in-repo execution and debugging against `src/lastfmcollagegenerator/` without packaging or installation steps.
- Support both offline mock rendering (zero external network calls) and live API querying with web scraping.
- Enable 1-click F5 debugging in VS Code with breakpoints that stop inside library source files.
- Enable automatic credential and user loading via `.env`.
- Provide automated output management saving to `output/` with optional OS image opening.
- Provide clear, user-friendly documentation in `README.md` for onboarding developers.
- Document exact release packaging (`uv build`) and PyPI upload (`uv publish`) procedures.

**Non-Goals:**
- Modifying production runtime library dependencies in `pyproject.toml`.
- Creating a heavy web GUI or complex electron app for previewing.

## Decisions

### 1. Zero-Dependency `.env` Parsing in Debug Runner
- **Decision**: Implement a lightweight `.env` parser inside `scripts/debug_collage.py` that reads key-value pairs without adding `python-dotenv` as a required production dependency.
- **Alternatives Considered**:
  - *Add `python-dotenv` to `dependencies`*: Rejected because it adds bloat to a published library.
  - *Require `export` in shell*: Rejected because it adds manual friction and does not work seamlessly with VS Code GUI launch configurations without extra setup.

### 2. VS Code Workspace Configurations (`.vscode/launch.json` & `.vscode/settings.json`)
- **Decision**: Create standard `.vscode/launch.json` targeting `scripts/debug_collage.py` and `pytest`, and `.vscode/settings.json` configuring Python interpreter path to `.venv` and setting `python.analysis.extraPaths: ["src"]`.
- **Alternatives Considered**:
  - *Rely on manual CLI debuggers only*: Rejected because the user specifically requested graphical VS Code debugging.

### 3. Dedicated `output/` Destination Directory
- **Decision**: Direct all generated collages to an `output/` folder in the workspace root, automatically created if absent and added to `.gitignore`.
- **Alternatives Considered**:
  - *Save in project root*: Pollutes git root with binary PNGs.

### 4. Comprehensive Developer Documentation in README.md
- **Decision**: Add dedicated "Development & Debugging" and "Packaging & Publishing to PyPI" sections in `README.md`.
- **Alternatives Considered**:
  - *Create a separate `CONTRIBUTING.md`*: Keep it in `README.md` for immediate visibility as the primary developer entrypoint.

### 5. Packaging & PyPI Release Tooling
- **Decision**: Standardize on `uv build` and `uv publish` (with `hatchling` backend) for building source distributions (`sdist`), wheels, and uploading releases using PyPI API tokens.
- **Alternatives Considered**:
  - *Legacy `setup.py` / `twine`*: Superseded by native `uv` toolchain.

## Risks / Trade-offs

- **[Risk] Developer commits secrets in `.env`** → *Mitigation*: Include `.env` in `.gitignore` and provide a safe template in `.env.example`.
- **[Risk] Accidental release publish without bump** → *Mitigation*: Document explicit version bump checklist in `pyproject.toml` and artifact inspection (`uv build`) prior to publishing.
- **[Risk] Python environment path variance across machines** → *Mitigation*: Use `"python": "${workspaceFolder}/.venv/bin/python"` or standard `${command:python.interpreterPath}` in `launch.json` so it works across macOS/Linux/Windows.
