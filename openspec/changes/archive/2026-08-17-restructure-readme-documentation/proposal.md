## Why

The current `README.md` is overly long (829 lines) and dense, mixing end-user documentation with internal architectural diagrams, post-mortem defect catalogs, maintainer PyPI release instructions, and corporate roadmap tables. A developer looking for a Last.fm collage generator needs a clean, honest, descriptive, and community-friendly overview of what the library does and how to use it in under 30 seconds.

## What Changes

- **Rewrite `README.md`**: Reduce size from ~830 to ~200 lines, focusing strictly on library capabilities, clear installation, simple quickstart, visual recipes (artists, presets, themes, async, export), compact parameters cheat sheet, and a GitHub Action profile widget snippet.
- **Tone Adjustment**: Adopt an honest, direct, developer-friendly voice without promotional puffery or corporate jargon.
- **Add Visual Collage Previews**: Generate and include real/mock preview assets in `assets/` to visually demonstrate output formats (3x3 grid, stories, themes).
- **Create `CONTRIBUTING.md`**: Extract all developer workflow instructions (uv sync, offline test execution, linters, mock debugging) into a dedicated contributing guide.
- **Relocate Internal Architecture & Defect Catalogs**: Ensure internal design specs and bug histories are preserved exclusively in `PROJECT_OVERVIEW.md` and `AGENTS.md`.

## Capabilities

### New Capabilities

*(None. This change refactors documentation and assets; no new library functional capabilities are introduced.)*

### Modified Capabilities

*(None. Library behavioral specifications remain unchanged.)*

## Impact

- **Documentation**: `README.md` becomes significantly more readable, scannable, and developer-focused. `CONTRIBUTING.md` is introduced.
- **Assets**: Adds visual sample assets in `assets/`.
- **Code & APIs**: Zero changes or breaking changes to library code, public APIs, or dependencies.
