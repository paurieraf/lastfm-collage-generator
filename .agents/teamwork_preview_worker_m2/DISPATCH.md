## 2026-08-16T13:38:15Z
You are the Worker for Milestone 2: Generating Project-Specific Rules (.gemini/rules/) and Custom Skills (.gemini/skills/) for lastfm-collage-generator.

Original user request path (MANDATORY TO READ FIRST):
/Users/priera/.gemini/antigravity/worktrees/lastfm-collage-generator/initialize_antigravity_architecture_analysis/.agents/ORIGINAL_REQUEST.md

Project Specification:
/Users/priera/.gemini/antigravity/worktrees/lastfm-collage-generator/initialize_antigravity_architecture_analysis/PROJECT.md

Project Overview:
/Users/priera/.gemini/antigravity/worktrees/lastfm-collage-generator/initialize_antigravity_architecture_analysis/PROJECT_OVERVIEW.md

Antigravity Customization Guidelines Skill:
/Users/priera/.gemini/antigravity/builtin/skills/agy-customizations/SKILL.md

Survey Explorer 3 Analysis:
/Users/priera/.gemini/antigravity/worktrees/lastfm-collage-generator/initialize_antigravity_architecture_analysis/.agents/teamwork_preview_explorer_survey_3/handoff.md

Your working directory:
/Users/priera/.gemini/antigravity/worktrees/lastfm-collage-generator/initialize_antigravity_architecture_analysis/.agents/teamwork_preview_worker_m2

Workspace root:
/Users/priera/.gemini/antigravity/worktrees/lastfm-collage-generator/initialize_antigravity_architecture_analysis

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Your Mission:
Create production-grade Antigravity rules in `.gemini/rules/` and custom skills in `.gemini/skills/` adhering strictly to `agy-customizations` standards.

Files to Create:

1. Project Rules in `.gemini/rules/`:
   - `.gemini/rules/python-standards.md`: Coding conventions, type hinting (Python 3.8+), PIL image handling & resource cleanup (`Image.close()`, `BytesIO`), dataclasses usage, custom domain exception hierarchy, and immutability.
   - `.gemini/rules/architecture-conventions.md`: Facade -> Factory -> Builder -> Client pattern rules, layer boundaries, font asset resolution conventions, entity extension protocols.
   - `.gemini/rules/testing-standards.md`: Zero network calls in test suites, mocking rules for `pylast` and HTTP/BeautifulSoup, synthetic image generation for test assertions, test directory structure, minimum coverage rules.
   - `.gemini/rules/lastfm-network-resilience.md`: Web retrieval safety rules, User-Agent header requirements, timeout policies (connect/read), blank tile fallback policies, thread safety under ThreadPoolExecutor.

2. Custom Skills in `.gemini/skills/`:
   - `.gemini/skills/poetry-test-runner/`:
     - `SKILL.md`: Valid YAML frontmatter (`name: poetry-test-runner`, `description`), workflow instructions for running pytest, measuring test coverage with `pytest-cov`, running code linters (`flake8`, `black`, `mypy`), and debugging test failures.
     - `scripts/run_tests.py`: Executable Python CLI script for executing tests, linting, and reporting summary metrics cleanly.
   - `.gemini/skills/lastfm-mocking-fixtures/`:
     - `SKILL.md`: Valid YAML frontmatter (`name: lastfm-mocking-fixtures`, `description`), guide and patterns for mocking `pylast.LastFMNetwork`, pylast entities (`Album`, `Artist`, `Track`), mocking Last.fm artist HTML retrieval, and generating synthetic Pillow images.
     - `references/fixture_templates.py`: Ready-to-use pytest fixtures and mock builder classes.
   - `.gemini/skills/collage-cli-workflow/`:
     - `SKILL.md`: Valid YAML frontmatter (`name: collage-cli-workflow`, `description`), comprehensive instructions for running collage generation from the command line, testing grid parameters, visual validation, and mock/offline generation mode.
     - `scripts/generate_collage_cli.py`: Production-grade CLI script wrapping `CollageGenerator` with argparse, supporting real API credentials or mock offline mode, grid dimensions, entity types, title overlay, and file output.

Deliverable:
- Write all rule files and skill files.
- Write your handoff report to `/Users/priera/.gemini/antigravity/worktrees/lastfm-collage-generator/initialize_antigravity_architecture_analysis/.agents/teamwork_preview_worker_m2/handoff.md`.
- Send a completion message back to parent.
