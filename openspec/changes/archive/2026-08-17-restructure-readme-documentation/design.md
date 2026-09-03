## Context

The repository documentation (`README.md`) grew to 829 lines, containing maintainer-specific guides, deep UML diagrams, internal coordinate math, and defect catalogs. This design outlines how we decouple user documentation from maintainer guides, create visual assets, and provide a clear, honest, and lightweight `README.md`.

## Goals / Non-Goals

**Goals:**
- Provide a clean, scannable, and developer-friendly `README.md` (< 250 lines) focused on what the library does, how to install it, a 5-line quickstart, essential recipes (artists, tracks, presets, styling, async, export), and a parameters cheat sheet.
- Create `CONTRIBUTING.md` containing developer commands (`uv sync`, `pytest`, `flake8`, `black`, `mypy`, debug scripts).
- Generate a visual demo collage asset in `assets/` so readers immediately see what output looks like.
- Ensure all maintainer knowledge and internal architectural details remain safely preserved in `PROJECT_OVERVIEW.md` and `AGENTS.md`.

**Non-Goals:**
- Rewriting or refactoring library Python code in `src/`.
- Changing existing public API signatures or behavior.
- Adding complex documentation site generators (e.g. Sphinx/MkDocs).

## Decisions

1. **Document Structure & Voice**:
   - *Decision*: Plain, direct English without corporate puffery or marketing hype.
   - *Rationale*: Python open-source developers appreciate clear, descriptive documentation that gets straight to the point.
   - *Alternatives considered*: Keeping long-form sections in collapsible `<details>` blocks (rejected: still creates excessive length and clutter).

2. **Developer & Contributor Guidance**:
   - *Decision*: Extract all developer setup, linting, testing, and debugging runner details into `CONTRIBUTING.md`.
   - *Rationale*: Standard Python ecosystem convention. Keeps the README dedicated to users while giving contributors a dedicated checklist.

3. **Visual Showcase Asset Generation**:
   - *Decision*: Generate synthetic preview composite(s) in `assets/collage_preview.png` illustrating typical output formats (3x3 grid, story format, themes).
   - *Rationale*: Shows concrete output immediately at the top of the README without requiring users to run the code first.

## Risks / Trade-offs

- **[Risk] Broken image link on PyPI / GitHub if relative paths are misconfigured** → Use standard relative path `assets/collage_preview.png` which renders properly on both GitHub and PyPI packaging.
- **[Risk] Loss of architectural knowledge for new maintainers** → Verify that all UML models and coordinate references are already present in `PROJECT_OVERVIEW.md` and `AGENTS.md`.
