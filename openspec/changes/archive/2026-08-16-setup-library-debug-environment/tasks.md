## 1. Environment & Git Ignore Setup

- [x] 1.1 Create `.env.example` template containing `LASTFM_API_KEY`, `LASTFM_API_SECRET`, `LASTFM_USERNAME`, and default options
- [x] 1.2 Update `.gitignore` to ensure `.env`, `.env.local`, and `output/` directories are ignored

## 2. Debug Runner Implementation

- [x] 2.1 Implement `scripts/debug_collage.py` with zero-dependency `.env` parsing and CLI argument parsing
- [x] 2.2 Implement offline mock generation pipeline with synthetic tile graphics
- [x] 2.3 Implement live Last.fm API generation pipeline with `CollageGenerator`
- [x] 2.4 Add automatic `output/` directory creation, execution timing metrics, and OS viewer opening (`--open`)

## 3. Visual Studio Code Integration

- [x] 3.1 Create `.vscode/launch.json` with F5 debug profiles (Mock Album/Artist, Live Album/Artist/Track with `.env`, and Pytest)
- [x] 3.2 Create `.vscode/settings.json` with `.venv` interpreter path, Pytest settings, and `src` analysis paths

## 4. Documentation

- [x] 4.1 Update `README.md` with a comprehensive "Development & Debugging" section covering `.env` configuration, CLI usage, offline mock mode, and VS Code F5 workflows
- [x] 4.2 Add "Packaging & Publishing to PyPI" section to `README.md` detailing version bump checklist, `uv build`, and `uv publish` workflow

## 5. Verification & Validation

- [x] 5.1 Verify offline mock generation runs and produces valid image in `output/`
- [x] 5.2 Verify VS Code debug profiles and CLI argument variations
