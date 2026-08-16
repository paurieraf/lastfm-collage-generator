# Handoff Report: Empirical Challenge & Verification

**Agent**: Challenger 2 (`teamwork_preview_challenger_2`)  
**Role**: critic, specialist  
**Date**: 2026-08-16  
**Verdict**: **`REQUEST_CHANGES`**

---

## 1. Observation

### Observation 1.1: Live CLI Generation Crashes with `TypeError` on `show_playcount`
- **File**: `scripts/debug_collage.py:171-179`
- **Invocation**:
  ```bash
  uv run python scripts/debug_collage.py --live --api-key "fake_key" --api-secret "fake_secret" -u "testuser"
  ```
- **Verbatim Error Output**:
  ```text
  [!] Error occurred after 0.04s: CollageGenerator.generate() got an unexpected keyword argument 'show_playcount'
  Traceback (most recent call last):
    File "scripts/debug_collage.py", line 387, in main
      image = run_live_generation(
          ...
          show_playcount=not args.no_title,
      )
    File "scripts/debug_collage.py", line 171, in run_live_generation
      return generator.generate(
          entity=entity,
          username=username,
          cols=cols,
          rows=rows,
          period=period,
          show_playcount=show_playcount,
      )
  TypeError: CollageGenerator.generate() got an unexpected keyword argument 'show_playcount'
  ```
- **Code Inspection**:
  - `src/lastfmcollagegenerator/collage_generator.py:23-30` defines:
    ```python
    def generate(
            self,
            entity: str,
            username: str,
            cols: int,
            rows: int,
            period: str
    ) -> Image:
    ```
  - `CollageGenerator.generate()` accepts only 5 positional/keyword arguments (`entity`, `username`, `cols`, `rows`, `period`). It does not accept `show_playcount`.

### Observation 1.2: Documented Convenience Methods Missing from Facade
- **File**: `README.md:258-286`, `README.md:518`, `README.md:570` vs `src/lastfmcollagegenerator/collage_generator.py`
- **Documented in README**:
  ```python
  album_collage = generator.generate_top_albums_collage(username="rj", cols=3, rows=3, period="7day")
  artist_collage = generator.generate_top_artists_collage(username="rj", cols=5, rows=5, period="1month")
  track_collage = generator.generate_top_tracks_collage(username="rj", cols=4, rows=3, period="overall")
  ```
  - `README.md:518` marks as complete: `- [x] Implement generate_top_albums_collage(), generate_top_artists_collage(), generate_top_tracks_collage() convenience methods on CollageGenerator.`
  - `README.md:570` states: `BUG-02 ... Added in v0.5.0 facade.`
- **Empirical Execution**:
  ```bash
  uv run python -c "
  from lastfmcollagegenerator.collage_generator import CollageGenerator
  gen = CollageGenerator('k', 's')
  for m in ['generate_top_albums_collage', 'generate_top_artists_collage', 'generate_top_tracks_collage']:
      print(m, hasattr(gen, m))
  "
  ```
- **Output**:
  ```text
  generate_top_albums_collage False
  generate_top_artists_collage False
  generate_top_tracks_collage False
  ```
- **Result**: Invoking any documented convenience method raises `AttributeError: 'CollageGenerator' object has no attribute 'generate_top_albums_collage'`.

### Observation 1.3: Incomplete Lower Boundary Validation in `CollageGenerator._validate_parameters`
- **File**: `src/lastfmcollagegenerator/collage_generator.py:69-73`
- **Code**:
  ```python
  if cols > self.MAX_COLS or rows > self.MAX_ROWS:
      raise ValueError(
          f"Invalid number of columns or rows: {cols}x{rows}: "
          f"Max values are: {self.MAX_ROWS}x{self.MAX_COLS}"
      )
  ```
- **Empirical Execution**:
  ```bash
  uv run python -c "
  from lastfmcollagegenerator.collage_generator import CollageGenerator
  gen = CollageGenerator('k', 's')
  for c, r in [(0, 3), (3, 0), (0, 0), (-1, 3), (-5, -5)]:
      gen._validate_parameters('album', c, r, '7day')
      print(f'cols={c}, rows={r}: PASSED (no exception)')
  "
  ```
- **Output**:
  ```text
  cols=0, rows=3: PASSED (no exception)
  cols=3, rows=0: PASSED (no exception)
  cols=0, rows=0: PASSED (no exception)
  cols=-1, rows=3: PASSED (no exception)
  cols=-5, rows=-5: PASSED (no exception)
  ```
- **Impact**: Passing `cols=0` bypasses validation and allocates a 0-width PIL canvas `(0, 900)`. Passing negative values crashes with `ValueError: Width and height must be >= 0` inside PIL rather than raising a validation error.
- **Discrepancy**: `README.md:89`, `README.md:244-245`, `README.md:519`, and `README.md:571` all assert that `1 <= cols <= 5` and `1 <= rows <= 5` boundary validation is implemented and marked as resolved `[x]`.

### Observation 1.4: CLI Options Functionality & Boundary Enforcement in `scripts/debug_collage.py`
- **Commands & Results**:
  1. `uv run python scripts/debug_collage.py --mock -e album -g 3x3 -o output/test_mock_album_3x3.png`: Exited 0, generated valid 900x900 PNG.
  2. `uv run python scripts/debug_collage.py --mock -e artist -g 5x5 -o output/test_mock_artist_5x5.png`: Exited 0, generated valid 1500x1500 PNG.
  3. `uv run python scripts/debug_collage.py --mock -e track -c 3 -r 5 --no-title -p overall -o output/test_mock_track_3x5_notitle.png`: Exited 0, generated valid 900x1500 PNG without title banners.
  4. `uv run python scripts/debug_collage.py --mock -g 0x0`: Exited 1 with `[!] Error: Grid dimensions 0x0 out of bounds (allowed: 1x1 to 5x5).`
  5. `uv run python scripts/debug_collage.py --mock -g 6x6`: Exited 1 with `[!] Error: Grid dimensions 6x6 out of bounds (allowed: 1x1 to 5x5).`
  6. `uv run python scripts/debug_collage.py --mock -c 0 -r 3`: Exited 1 with `[!] Error: Grid dimensions 0x3 out of bounds (allowed: 1x1 to 5x5).`
  7. `uv run python scripts/debug_collage.py --mock -c 6 -r 3`: Exited 1 with `[!] Error: Grid dimensions 6x3 out of bounds (allowed: 1x1 to 5x5).`
  8. `uv run python scripts/debug_collage.py --mock -g abc`: Exited 1 with `[!] Error: Invalid grid format 'abc'. Expected format like '3x3' or '4x5'.`
  9. `uv run python scripts/debug_collage.py --mock -g 4x2 -c 3 -r 5 -o output/test_override.png`: Exited 0, generated 1200x600 PNG (verifying `-g` overrides `-c`/`-r`).
  10. `uv run python scripts/debug_collage.py --mock --live`: Exited 2 with mutually exclusive argument error from `argparse`.
  11. `uv run python scripts/debug_collage.py --mock -g 2x2 -o output/nested/deep/test_deep.png`: Exited 0, automatically created nested directory tree and wrote valid 600x600 PNG.
  12. `uv run python scripts/debug_collage.py --live --api-key "" --api-secret ""`: Exited 1 with credential requirement error message.

### Observation 1.5: Font Bundle Integrity and Package Loading
- **Files**:
  - `src/lastfmcollagegenerator/fonts/DejaVuSansMono.ttf` (340,712 bytes, SHA256 `2627656503d8d0a8...`)
  - `src/lastfmcollagegenerator/fonts/DejaVuSansMono-Bold.ttf` (331,992 bytes, SHA256 `d9b4f6116035fc25...`)
- **Inspection & Build**:
  - Both TrueType font files load and render properly with `PIL.ImageFont.truetype(path, 15)`.
  - `MANIFEST.in` specifies `recursive-include src/lastfmcollagegenerator/fonts *.ttf`.
  - `uv build` builds `dist/lastfmcollagegenerator-0.4.13-py3-none-any.whl` which includes both font files in `lastfmcollagegenerator/fonts/`.
  - `BaseCollageBuilder` loads fonts dynamically relative to `os.path.dirname(lastfmcollagegenerator.collage.__file__)`, ensuring zero dependency on system fonts.

### Observation 1.6: Multi-Row Title Overlay Geometry Defect
- **File**: `src/lastfmcollagegenerator/collage.py:126-130`
- **Code**:
  ```python
  y_0 = y + 235
  y_1 = y * 2 + self.TILE_WIDTH
  if y_1 == 0:
      y_1 += self.TILE_WIDTH * 2
  draw.rectangle(((x, y_0), (x + self.TILE_WIDTH, y_1)), (0, 0, 0, 123))
  ```
- **Math**:
  - Row 0 (`y=0`): `y_0 = 235, y_1 = 300` (Banner height = 65px, correct).
  - Row 1 (`y=300`): `y_0 = 535, y_1 = 900` (Banner height = 365px, covering all of Row 2).
  - Row 2 (`y=600`): `y_0 = 835, y_1 = 1500` (Banner height = 665px, overflowing canvas).
- **Discrepancy**: `README.md:517` marks `[x] Correct multi-row overlay geometry bug (y_1 = y + self.TILE_HEIGHT)` as completed in Phase 1 (v0.5.0), but the codebase in the worktree still contains the defective code.

---

## 2. Logic Chain

1. **From Observation 1.1**:
   `scripts/debug_collage.py:177` passes `show_playcount=show_playcount` to `CollageGenerator.generate()`. Because `CollageGenerator.generate()` in `src/lastfmcollagegenerator/collage_generator.py:23-30` does not accept `show_playcount`, invoking `scripts/debug_collage.py --live` crashes with `TypeError`.
2. **From Observation 1.2**:
   `README.md:258-286` documents `generate_top_albums_collage()`, `generate_top_artists_collage()`, and `generate_top_tracks_collage()` as ready-to-use convenience methods, and `README.md:518` / `README.md:570` marks them as implemented in `v0.5.0` (`[x]`). Because they do not exist on `CollageGenerator`, any user executing the documented code examples encounters `AttributeError`.
3. **From Observation 1.3**:
   `CollageGenerator._validate_parameters` only checks `cols > 5 or rows > 5`. Non-positive integers (`0`, `-1`, `-5`) pass validation. Although `scripts/debug_collage.py` performs its own bounds check (`1 <= args.cols <= 5`), consumers using the library directly via `CollageGenerator` will crash inside PIL when passing `cols=0` or negative values. Furthermore, `README.md:519` / `README.md:571` incorrectly marks `1 <= cols <= 5` validation as completed `[x]` in `v0.5.0`.
4. **From Observation 1.4**:
   All CLI flags in `scripts/debug_collage.py` (`--mock`, `--entity`, `--grid`, `--cols`, `--rows`, `--period`, `--no-title`, `--output`, `--open`, `--api-key`, `--api-secret`) parse arguments, validate bounds, and execute synthetic mock generation cleanly and deterministically.
5. **From Observation 1.5**:
   Font packaging in `src/lastfmcollagegenerator/fonts/` is intact, valid, correctly packaged in `.whl` builds, and loaded relative to the module path.
6. **From Observation 1.6**:
   `README.md` roadmap marks legacy bugs (`BUG-01`, `BUG-02`, `BUG-03`) as resolved `[x]` in Phase 1 (`v0.5.0`), creating a documentation-to-code mismatch since the worktree remains at version `0.4.13` with these defects still present in the underlying library source.

---

## 3. Caveats

1. **Network-Isolated Environment**: Live Last.fm API queries and live artist web scraping were tested up to the network boundary with mock/synthetic credentials; live outbound network requests to `last.fm` servers were not performed in adherence to zero-network testing guidelines.
2. **Review-Only Constraint**: In accordance with the Review-Only role constraint, no implementation code modifications were applied by this agent.

---

## 4. Conclusion & Actionable Recommendations

**Verdict**: **`REQUEST_CHANGES`**

The documentation (`README.md`) and CLI runner (`scripts/debug_collage.py`) are exceptionally well-structured and comprehensive. However, three critical synchronization issues must be resolved before sign-off:

### Required Changes:
1. **Fix `scripts/debug_collage.py` live call**:
   - Update `run_live_generation` in `scripts/debug_collage.py:171-179` to either:
     - Remove `show_playcount=show_playcount` when calling `generator.generate(...)`, OR
     - Pass `show_playcount` through `CollageBuilderConfig` if/when `CollageGenerator.generate` is updated to accept it.
2. **Reconcile README Convenience Methods vs Facade**:
   - In `README.md`: Ensure the documentation accurately reflects whether `generate_top_albums_collage()`, `generate_top_artists_collage()`, and `generate_top_tracks_collage()` are implemented in the current release or scheduled for future release. If the codebase remains at `v0.4.13`, uncheck `[ ]` these items in the Roadmap (or document them under planned features rather than active Quickstart examples) to prevent user `AttributeError` exceptions.
3. **Reconcile Parameter Bounds Validation & Bug Checklist Status in README**:
   - In `README.md:516-520` (Roadmap Phase 1) and `README.md:567-574` (Known Bugs Catalog): Ensure that checklist status (`[x]` vs `[ ]`) and resolution status accurately reflect the state of the active codebase (or note that v0.5.0 is the upcoming release target where these remediations will land).

---

## 5. Verification Method

To independently reproduce and verify all findings, run the following commands:

```bash
# 1. Verify TypeError in debug_collage.py live mode
uv run python scripts/debug_collage.py --live --api-key "test" --api-secret "test" -u "testuser"

# 2. Verify AttributeError on documented convenience methods
uv run python -c "
from lastfmcollagegenerator.collage_generator import CollageGenerator
gen = CollageGenerator('test', 'test')
assert not hasattr(gen, 'generate_top_albums_collage')
assert not hasattr(gen, 'generate_top_artists_collage')
assert not hasattr(gen, 'generate_top_tracks_collage')
print('Convenience methods missing: VERIFIED')
"

# 3. Verify lower boundary bypass in CollageGenerator._validate_parameters
uv run python -c "
from lastfmcollagegenerator.collage_generator import CollageGenerator
gen = CollageGenerator('test', 'test')
gen._validate_parameters('album', 0, 0, '7day')
print('Lower boundary check omitted: VERIFIED (cols=0, rows=0 passed)')
"

# 4. Verify CLI runner options and bounds in mock mode
uv run python scripts/debug_collage.py --mock -e album -g 3x3 -o output/verify_mock_album_3x3.png
uv run python scripts/debug_collage.py --mock -e artist -g 5x5 -o output/verify_mock_artist_5x5.png
uv run python scripts/debug_collage.py --mock -g 6x6  # Must return exit code 1

# 5. Verify font bundle integrity and wheel packaging
uv run python -c "
import os
from PIL import ImageFont
import lastfmcollagegenerator.collage
pkg_dir = os.path.dirname(lastfmcollagegenerator.collage.__file__)
f1 = ImageFont.truetype(os.path.join(pkg_dir, 'fonts/DejaVuSansMono.ttf'), 15)
f2 = ImageFont.truetype(os.path.join(pkg_dir, 'fonts/DejaVuSansMono-Bold.ttf'), 15)
print('Font loading: VERIFIED')
"
uv build
```
