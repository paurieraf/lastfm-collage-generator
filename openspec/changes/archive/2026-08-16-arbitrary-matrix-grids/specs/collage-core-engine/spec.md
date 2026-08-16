## MODIFIED Requirements

### Requirement: Strict Input Parameter Validation
The system SHALL strictly validate all grid dimensions, maximum tile limits, custom tile sizes, username inputs, entity types, and time aggregation periods before initiating image compositing or network queries.

#### Scenario: Validating lower and upper grid bounds
- **WHEN** `generate()` is called with `cols < 1`, `rows < 1`, `cols > 20`, `rows > 20`, or total items `cols * rows > 400`
- **THEN** the system raises a `ValueError` indicating invalid dimensions or exceeded maximum capacity

#### Scenario: Validating tile size bounds
- **WHEN** `generate()` is called with a custom `tile_size < 50`, `tile_size > 600`, or a non-integer `tile_size`
- **THEN** the system raises a `ValueError` or `TypeError` indicating invalid tile size bounds

#### Scenario: Validating empty or whitespace username
- **WHEN** `generate()` is called with an empty, whitespace-only, or non-string username
- **THEN** the system raises a `ValueError` indicating that a valid username is required

#### Scenario: Validating entity and period values
- **WHEN** `generate()` is called with an invalid entity or period
- **THEN** the system raises a `ValueError` listing the allowed choices

## ADDED Requirements

### Requirement: Dynamic Tile Resolution and Proportional Scaling
The system SHALL dynamically downscale tile rendering resolution and proportionally scale typography, banner overlay height, and text wrapping based on the active grid density, or apply user-specified explicit tile sizes.

#### Scenario: Default tile sizing for standard grids
- **WHEN** a collage is generated with grid dimensions where `max(cols, rows) <= 5` and no explicit `tile_size` is provided
- **THEN** the system uses 300x300 pixel tiles resulting in canvas dimensions of `(cols * 300, rows * 300)` pixels

#### Scenario: Dynamic downscaling for medium density grids
- **WHEN** a collage is generated with grid dimensions where `5 < max(cols, rows) <= 10` (e.g. 10x10) and no explicit `tile_size` is provided
- **THEN** the system automatically downscales tile resolution to 150x150 pixels resulting in canvas dimensions of `(cols * 150, rows * 150)` pixels

#### Scenario: Dynamic downscaling for high density grids
- **WHEN** a collage is generated with grid dimensions where `max(cols, rows) > 10` (up to 20x20) and no explicit `tile_size` is provided
- **THEN** the system automatically downscales tile resolution to 100x100 pixels resulting in canvas dimensions of `(cols * 100, rows * 100)` pixels

#### Scenario: Explicit custom tile size configuration
- **WHEN** `generate()` is called with an explicit `tile_size` (e.g. 200)
- **THEN** the system uses the specified `tile_size` for canvas allocation `(cols * tile_size, rows * tile_size)` and resizes tile assets accordingly

#### Scenario: Proportional overlay banner and typography scaling
- **WHEN** a collage is generated at any tile size $S$
- **THEN** the title banner overlay height and font size scale proportionally ($h_{\text{banner}} \approx \text{round}(65 \times \frac{S}{300})$, $\text{size}_{\text{font}} \approx \max(8, \text{round}(15 \times \frac{S}{300}))$) and remains strictly bounded within the bottom of each tile
