## Purpose

Provides a zero-build, rapid-feedback local development and debugging environment for developers testing visual image generation and Last.fm API integrations, alongside comprehensive packaging and PyPI publishing procedures.

## ADDED Requirements

### Requirement: Local Environment Variable Configuration
The system SHALL read configuration parameters from a local `.env` file when available, including `LASTFM_API_KEY`, `LASTFM_API_SECRET`, and `LASTFM_USERNAME`.

#### Scenario: Loading parameters from .env
- **WHEN** the debug runner is executed with `--live` and a `.env` file is present in the workspace
- **THEN** the system loads the API credentials and username from the `.env` file without requiring CLI flags

#### Scenario: Fallback when parameters are omitted
- **WHEN** required live API credentials are missing from both `.env` and CLI arguments
- **THEN** the system prints an informative error message and exits cleanly without crashing unhandled

### Requirement: Offline Mock Debugging Mode
The system SHALL provide an offline mock mode that generates synthetic collages without making external network or API calls.

#### Scenario: Running mock collage generation
- **WHEN** the debug runner is executed with the `--mock` flag
- **THEN** synthetic tiles with distinct background colors and titles are rendered into a collage image and saved to disk within 1 second

### Requirement: Live API and Retrieval Debugging Mode
The system SHALL provide a live debugging mode that interacts with the Last.fm REST API and fetches artist imagery using configured user credentials.

#### Scenario: Generating live album collage
- **WHEN** the debug runner is executed with `--live` and entity `album`
- **THEN** the system queries the user's top albums from Last.fm, fetches cover art, composites the collage, and saves the output to the `output/` directory

#### Scenario: Generating live artist collage
- **WHEN** the debug runner is executed with `--live` and entity `artist`
- **THEN** the system queries the user's top artists, fetches artist hero images from Last.fm web pages, and composites the collage

### Requirement: Visual Studio Code F5 Debug Profiles
The system SHALL provide pre-configured VS Code launch profiles supporting 1-click execution and breakpoint inspection for both mock and live scenarios.

#### Scenario: Triggering mock debug in VS Code
- **WHEN** the user selects the mock debug profile and presses F5 in Visual Studio Code
- **THEN** execution begins and stops at any active breakpoint set inside the library source code

#### Scenario: Triggering live debug in VS Code
- **WHEN** the user selects the live debug profile and presses F5 in Visual Studio Code
- **THEN** execution begins with `.env` credentials loaded and stops at any active breakpoint during API queries or image compositing

### Requirement: Automatic Image Opening and Output Management
The system SHALL save generated debug collages to a dedicated `output/` directory and optionally open the generated image in the operating system's default viewer.

#### Scenario: Output directory creation
- **WHEN** a debug collage is generated and the `output/` directory does not exist
- **THEN** the system automatically creates the directory and saves the PNG file

#### Scenario: Opening image on generation
- **WHEN** the `--open` flag is supplied to the debug runner
- **THEN** the system launches the default system image viewer to display the resulting collage file

### Requirement: Developer Documentation
The system documentation SHALL include clear setup and debugging instructions in the project's documentation.

#### Scenario: Viewing development documentation
- **WHEN** a developer inspects `README.md`
- **THEN** they find instructions detailing `.env` configuration, CLI debug usage, offline mock mode, and VS Code F5 launch workflows

### Requirement: Packaging and PyPI Release Documentation
The system documentation SHALL include clear step-by-step instructions for building distribution artifacts and publishing releases to PyPI.

#### Scenario: Viewing packaging and release documentation
- **WHEN** a developer views the release instructions in `README.md`
- **THEN** they find the exact commands for bumping the version in `pyproject.toml`, executing `uv build`, and uploading packages via `uv publish` or API token authentication
