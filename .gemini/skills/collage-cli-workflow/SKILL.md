---
name: collage-cli-workflow
description: >-
  Run, test, preview, and visually validate Last.fm collage generation from the command line with custom grid dimensions, entity types, time periods, and mock offline mode. Use when generating test collages, testing CLI parameters, or verifying visual rendering.
---

# Collage CLI Workflow & Visual Validation Skill

This skill provides step-by-step procedures and a production-grade CLI executable (`scripts/generate_collage_cli.py`) for generating Last.fm collages, previewing layouts, validating typography, and testing offline/mock modes without requiring live API keys.

---

## 1. Quick Start: CLI Script

The skill provides [`scripts/generate_collage_cli.py`](./scripts/generate_collage_cli.py), a complete CLI wrapper around `lastfmcollagegenerator.CollageGenerator`.

### 1.1 Offline / Mock Mode (No API Credentials Required)

Run in mock mode to test grid geometry, typography, and image compositing instantly:

```bash
# Generate a 3x3 album collage in mock mode
poetry run python .gemini/skills/collage-cli-workflow/scripts/generate_collage_cli.py \
  --mock \
  --username testuser \
  --entity album \
  --cols 3 \
  --rows 3 \
  --period 7day \
  --output sample_album_3x3.png

# Generate a 5x5 artist collage in mock mode
poetry run python .gemini/skills/collage-cli-workflow/scripts/generate_collage_cli.py \
  --mock \
  --username testuser \
  --entity artist \
  --cols 5 \
  --rows 5 \
  --period overall \
  --output sample_artist_5x5.png

# Generate an asymmetric 3x5 track collage without playcount titles
poetry run python .gemini/skills/collage-cli-workflow/scripts/generate_collage_cli.py \
  --mock \
  --username testuser \
  --entity track \
  --cols 3 \
  --rows 5 \
  --period 1month \
  --no-title \
  --output sample_track_3x5.png
```

### 1.2 Live Generation Mode (Using Real Last.fm Credentials)

Set credentials via command-line arguments or environment variables:

```bash
# Export API credentials
export LASTFM_API_KEY="your_api_key"
export LASTFM_API_SECRET="your_api_secret"

# Generate live collage
poetry run python .gemini/skills/collage-cli-workflow/scripts/generate_collage_cli.py \
  --username your_lastfm_username \
  --entity album \
  --cols 3 \
  --rows 3 \
  --period 7day \
  --output my_collage.png
```

---

## 2. CLI Parameter Reference

| Parameter | Short | Type | Default | Description |
|---|---|---|---|---|
| `--username` | `-u` | `str` | `testuser` | Last.fm user profile name |
| `--entity` | `-e` | `str` | `album` | Musical entity: `album`, `artist`, or `track` |
| `--cols` | `-c` | `int` | `3` | Number of columns (1 to 5) |
| `--rows` | `-r` | `int` | `3` | Number of rows (1 to 5) |
| `--period` | `-p` | `str` | `7day` | Aggregation period: `7day`, `1month`, `3month`, `6month`, `12month`, `overall` |
| `--output` | `-o` | `str` | `collage.png` | Output file destination |
| `--api-key` | | `str` | `env: LASTFM_API_KEY` | Last.fm API Key |
| `--api-secret` | | `str` | `env: LASTFM_API_SECRET` | Last.fm API Secret |
| `--mock` | `-m` | `flag` | `False` | Run offline in mock generation mode |
| `--title` / `--no-title` | | `flag` | `True` | Toggle bottom title banner overlay |

---

## 3. Visual Validation Checklist

When generating sample collages to verify code changes or bug fixes:

1. **Matrix Dimensions**:
   - Verify that output image width is `cols * 300px` and height is `rows * 300px`.
   - E.g., a `3x3` image must be exactly `900 x 900` pixels.
2. **Title Overlay Multi-Row Geometry**:
   - Check rows below row 0 (Row 1, Row 2, etc.).
   - Verify that the dark translucent banner (`#000000` with alpha) spans only `y + 235` to `y + 300` (65px height) on each row and does NOT obscure the row below it.
3. **Typography & Text Legibility**:
   - Verify text is white, uses monospace `DejaVuSansMono.ttf`, and starts at `(x + 8, y + 240)`.
   - Verify text with playcount reads: `"Artist - Title. (123)"`.
4. **Blank Tile Fallback**:
   - Verify that missing cover art renders as a uniform `300x300` solid black tile without crashing the generator.
