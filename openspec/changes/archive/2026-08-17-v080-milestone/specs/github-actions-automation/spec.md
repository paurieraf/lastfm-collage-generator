## Purpose

Provides a reusable GitHub Action that automates generation of weekly listening recap collages and updates a GitHub profile README on a schedule.

## ADDED Requirements

### Requirement: Reusable Collage GitHub Action
The system SHALL ship a repository-root `action.yml` defining a composite GitHub Action that installs the library, generates a collage for a configured username and entity, and writes the output image to a specified path.

#### Scenario: Action inputs are validated and applied
- **WHEN** the action runs with inputs `username`, `entity`, `cols`, `rows`, `period`, and `output-path`
- **THEN** the collage is generated with those parameters and saved to the configured output path within the repository

#### Scenario: Action supports secrets-backed credentials
- **WHEN** `LASTFM_API_KEY` and `LASTFM_API_SECRET` are provided as GitHub secrets to the workflow
- **THEN** the action generates the collage in live mode using those credentials without exposing them in logs

#### Scenario: Scheduled weekly recap workflow
- **WHEN** the provided example workflow is configured with a weekly cron schedule
- **THEN** the profile README collage image is regenerated and committed on each scheduled run

### Requirement: Deterministic Offline Testing of the Action
The system SHALL allow the action to run in mock mode without Last.fm credentials so CI can validate workflow syntax and output generation offline.

#### Scenario: Mock-mode CI validation
- **WHEN** the action is invoked with mock mode enabled and no API credentials
- **THEN** a valid collage image is produced and the workflow completes successfully without network calls to Last.fm
