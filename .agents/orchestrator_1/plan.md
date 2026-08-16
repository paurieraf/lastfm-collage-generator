# Project Orchestration Plan: Last.fm Collage Generator Architecture Analysis & Antigravity Tooling

## Objectives
1. Perform deep technical exploration of `lastfm-collage-generator` to identify architecture, tech stack, data models, APIs, rendering pipeline, CLI/UI interfaces, configuration, and limitations.
2. Produce a comprehensive General Project Overview artifact (`PROJECT_OVERVIEW.md` or similar).
3. Generate project-specific Rules in `.gemini/rules/` and Custom Skills in `.gemini/skills/` (with valid YAML frontmatter in SKILL.md and supporting scripts/docs) strictly following the `agy-customizations` standard.
4. Read and cross-reference `AGENTS.md`, compare findings, resolve discrepancies, and integrate insights.
5. Execute independent verification (Reviewers, Challengers, and Forensic Auditor) to ensure high-standard deliverables with zero integrity violations.

## Phases & Execution Strategy

### Phase 0: Survey (3 Explorers in Parallel)
- **Explorer 1**: Codebase Structure, Architecture, Module Boundaries, Data Flow, External Dependencies, Limitations.
- **Explorer 2**: Features, CLI / UI Workflows, Last.fm API Integration, Image Generation Engine, Existing Tests/CI.
- **Explorer 3**: Antigravity Customizations Analysis (`agy-customizations` skill), Rule & Skill design, and existing `AGENTS.md` initial review.

### Milestone 1: General Project Overview Artifact
- Synthesize explorer reports into `PROJECT.md` / `PROJECT_OVERVIEW.md`.
- Dispatch Worker to create structured documentation covering: system architecture, components, data flow, API specs, configuration, known limitations, and tech debt.
- Reviewer & Gate check.

### Milestone 2: Antigravity Project Rules & Custom Skills
- Dispatch Worker to generate `.gemini/rules/*.md` and `.gemini/skills/*/SKILL.md` (and supporting files) according to `agy-customizations` guidelines.
- Target custom rules: code style, testing standards, architecture constraints, API conventions.
- Target custom skills: CLI operations, Last.fm API interactions, collage rendering/testing, test execution.
- Reviewer & Gate check.

### Milestone 3: AGENTS.md Cross-Referencing & Synthesis
- Compare generated overview, rules, and skills with existing `AGENTS.md`.
- Dispatch Worker to reconcile differences, update documentation/customizations, or update AGENTS.md if appropriate.
- Reviewer & Gate check.

### Milestone 4: Independent Review & Verification
- Dispatch Reviewers and Challengers to validate rules, skill schemas, Markdown structure, scripts, and documentation completeness.
- Dispatch Forensic Auditor for integrity verification.
- Gate confirmation.

### Phase 5: Final Report & Handoff
- Produce comprehensive final summary.
- Update BRIEFING.md, progress.md, and handoff.md.
