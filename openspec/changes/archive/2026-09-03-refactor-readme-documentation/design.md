## Context

See `proposal.md` for motivation. The project currently has an 829-line monolithic `README.md` that contains user-facing instructions alongside developer onboarding, QA commands, architecture diagrams, and release protocols.

## Goals / Non-Goals

**Goals:**
- Provide a clean, engaging `README.md` focused on rapid onboarding, visual showcase, and realistic practical use cases.
- Isolate developer-focused and contributor instructions into a standardized `CONTRIBUTING.md`.
- Move maintainer release steps to `docs/RELEASING.md`.
- Generate and commit a crisp visual asset `assets/showcase.png` to serve as the hero visual.

**Non-Goals:**
- Rewriting runtime library code or modifying any Python files in `src/`.
- Deleting architecture specifications (they are already preserved in `PROJECT_OVERVIEW.md` and `AGENTS.md`).
- Removing existing offline tests or test fixtures.

## Decisions

### 1. Structure the README around 4 core use cases
- **Decision**: Highlight 4 distinct practical use cases:
  1. Social media presets (Instagram Story 9:16, Twitter Header, Desktop Wallpaper) with acrylic background blurring.
  2. GitHub Actions automated profile workflow (`action.yml` scheduled run).
  3. Async pipeline for Discord/Telegram bots or web APIs using `generate_async()` and in-memory `io.BytesIO` buffers.
  4. Visual styling and themes (theme presets, corner radiuses, border styling, clean mode).
- **Rationale**: Developers search for libraries that solve specific end-user problems; practical recipes convert curiosity into adoption much faster than dry parameter tables.
- **Alternatives Considered**: Pure minimalist README (only 1 basic example) was considered, but use cases demonstrate the rich capabilities of the library (social presets, async, github action) without bloat.

### 2. Isolate contributor workflows in `CONTRIBUTING.md`
- **Decision**: Create a dedicated `CONTRIBUTING.md` containing `uv sync`, `pytest` commands, `flake8`/`black`/`mypy` commands, `scripts/debug_collage.py` usage, VS Code F5 launch profile references, and a PR checklist.
- **Rationale**: Follows standard GitHub open-source community conventions. Contributor tooling should not clutter consumer documentation.
- **Alternatives Considered**: Keeping a small testing section in README. Rejected to maintain strict separation of concerns.

### 3. Generate Hero Image via Offline Mock Pipeline
- **Decision**: Use `scripts/debug_collage.py --mock -g 3x3 -o assets/showcase.png` (or a dedicated synthetic collage generation) to produce a high-contrast 3x3 sample collage.
- **Rationale**: Operates 100% offline without needing active Last.fm API keys or network access, ensuring reproducible visual assets.

### 4. Create `docs/RELEASING.md`
- **Decision**: Extract `uv publish`, environment token configuration, and PyPI release steps into `docs/RELEASING.md`.
- **Rationale**: Packaging release steps are maintainer-only tasks that confuse library consumers.

## Risks / Trade-offs

- **[Risk] Broken relative links or missing references** → Mitigation: Thoroughly verify all internal markdown links (`CONTRIBUTING.md`, `LICENSE`, `PROJECT_OVERVIEW.md`, `assets/showcase.png`).
- **[Risk] Showcase image file size** → Mitigation: Generate a compact PNG asset (< 500 KB) that loads quickly on GitHub and PyPI.
