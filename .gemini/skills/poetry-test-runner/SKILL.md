---
name: poetry-test-runner
description: >-
  Execute pytest test suites, generate coverage reports with pytest-cov, run code linters (flake8, black, mypy), and debug test failures using uv for the lastfm-collage-generator project. Use when running tests, checking test coverage, or validating code quality.
---

# Test Runner & Quality Assurance Skill

This skill provides workflow instructions, execution commands, and an automation script for executing tests, measuring code coverage, and running static analysis linters within the uv environment.

---

## 1. Quick Start: Test Execution Helper Script

Use the bundled helper script [`scripts/run_tests.py`](./scripts/run_tests.py) to run test suites and linters with unified reporting:

```bash
# Run all unit tests
uv run python .gemini/skills/poetry-test-runner/scripts/run_tests.py --unit

# Run unit tests with code coverage reporting
uv run python .gemini/skills/poetry-test-runner/scripts/run_tests.py --coverage

# Run linters (flake8, black --check, mypy)
uv run python .gemini/skills/poetry-test-runner/scripts/run_tests.py --lint

# Run complete test suite, coverage check (fail under 90%), and linting
uv run python .gemini/skills/poetry-test-runner/scripts/run_tests.py --all
```

---

## 2. Standard uv & Pytest Workflows

### 2.1 Running Pytest Directly

```bash
# Run all tests in the tests/ directory
uv run pytest -v tests/

# Run a specific test module
uv run pytest -v tests/test_validation.py

# Run a specific test function
uv run pytest -v tests/test_rendering_engine.py -k "test_title_overlay_coordinates"

# Stop on first failure (-x) and show print/log output (-s)
uv run pytest -x -s tests/
```

### 2.2 Measuring Code Coverage with `pytest-cov`

```bash
# Run coverage on the lastfmcollagegenerator package
uv run pytest --cov=lastfmcollagegenerator --cov-report=term-missing tests/

# Generate an HTML coverage report in htmlcov/
uv run pytest --cov=lastfmcollagegenerator --cov-report=html tests/

# Enforce minimum 90% coverage threshold
uv run pytest --cov=lastfmcollagegenerator --cov-fail-under=90 tests/
```

### 2.3 Static Analysis & Linting

```bash
# Check code style with flake8
uv run flake8 src/ tests/

# Check formatting with black
uv run black --check src/ tests/

# Run static type checking with mypy
uv run mypy src/
```

---

## 3. Debugging Test Failures

When a test fails, follow this diagnostic workflow:

1. **Isolate Failure**: Re-run the specific failing test with verbose output and traceback:
   ```bash
   uv run pytest -vv --tb=short tests/test_failing_module.py -k "test_name"
   ```
2. **Inspect Visual/Coordinate Failures**:
   - For image composite tests, inspect coordinate calculations in `src/lastfmcollagegenerator/collage.py`.
   - Verify `y_0 = y + (self.TILE_HEIGHT - 65)` and `y_1 = y + self.TILE_HEIGHT`.
3. **Inspect Network Leaks**:
   - Ensure all `requests.get` calls are patched using `unittest.mock.patch` or `requests_mock`.
   - Ensure `pylast.LastFMNetwork` is mocked.
4. **Fix and Verify**:
   - Apply minimal bug fix to source code.
   - Re-run `uv run python .gemini/skills/poetry-test-runner/scripts/run_tests.py --all` to verify resolution without regressions.
