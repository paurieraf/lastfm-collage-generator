## Purpose
Enables robust and efficient export of generated collages to various image formats (PNG, JPEG, WebP) while handling color space requirements safely.

## ADDED Requirements

### Requirement: Save image to specified format
The system SHALL export the collage image to the disk in the specified format, preserving the visual fidelity of the generated composite.

#### Scenario: Successful export to PNG
- **WHEN** the export is invoked with a PNG target path
- **THEN** the system writes a valid PNG file to disk with the original RGBA color mode intact

#### Scenario: Successful export to WebP
- **WHEN** the export is invoked with a WebP target path
- **THEN** the system writes a valid WebP file to disk, maintaining transparency support

### Requirement: Format inference
The system SHALL infer the correct target format based on the file extension of the output path if the format is not explicitly provided by the caller.

#### Scenario: Format inferred from extension
- **WHEN** the export is invoked with output path "collage.jpg" and no format argument
- **THEN** the system processes and saves the image as a JPEG file

### Requirement: Safe alpha channel handling for JPEG
The system SHALL safely convert images containing an alpha channel (RGBA mode) to RGB mode by flattening them onto a solid background before exporting to formats that do not support transparency, such as JPEG.

#### Scenario: RGBA to JPEG safe conversion
- **WHEN** the export is invoked with a JPEG target path and an RGBA image
- **THEN** the system blends the image onto a black background, converts the image to RGB mode, and saves it as a valid JPEG without crashing

### Requirement: Quality optimization
The system SHALL apply an optimized default quality setting (e.g., quality=85) when saving to lossy formats to ensure smaller file sizes by default.

#### Scenario: Default quality application
- **WHEN** the export is invoked for JPEG or WebP without specifying a quality parameter
- **THEN** the system saves the image using the default quality setting of 85
