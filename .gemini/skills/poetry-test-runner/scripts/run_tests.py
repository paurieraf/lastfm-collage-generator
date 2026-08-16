#!/usr/bin/env python3
"""Test Runner & QA Script for lastfm-collage-generator.

Executes pytest test suites, coverage reports, and linters with unified summary metrics.
"""

import argparse
import os
import subprocess
import sys
from typing import List, Optional, Tuple


class TestRunner:
    """Orchestrates test execution, coverage collection, and linting checks."""

    def __init__(
        self,
        tests_dir: str = "tests",
        src_dir: str = "src",
        fail_under: int = 90,
        verbose: bool = False,
    ) -> None:
        self.tests_dir = tests_dir
        self.src_dir = src_dir
        self.fail_under = fail_under
        self.verbose = verbose
        self.project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
        )

    def _run_command(self, cmd: List[str], desc: str) -> Tuple[int, str]:
        """Runs a subprocess command and prints progress."""
        print(f"\n[+] Running {desc}: {' '.join(cmd)}")
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=not self.verbose,
                text=True,
            )
            if self.verbose:
                print(f"[✓] {desc} finished with return code {result.returncode}")
            else:
                if result.returncode == 0:
                    print(f"[✓] {desc} PASSED")
                else:
                    print(f"[✗] {desc} FAILED (Exit Code: {result.returncode})")
                    if result.stdout:
                        print("\n--- Standard Output ---")
                        print(result.stdout)
                    if result.stderr:
                        print("\n--- Standard Error ---")
                        print(result.stderr)
            return result.returncode, (result.stdout or "") + (result.stderr or "")
        except FileNotFoundError:
            tool_name = cmd[0]
            print(f"[!] Tool '{tool_name}' not found. Ensure it is installed in your environment.")
            return 127, f"Tool '{tool_name}' not found"

    def run_unit_tests(self) -> int:
        """Executes pytest unit test suite."""
        cmd = ["pytest"]
        if self.verbose:
            cmd.append("-v")
        cmd.append(self.tests_dir)
        code, _ = self._run_command(cmd, "Pytest Unit Tests")
        return code

    def run_coverage(self) -> int:
        """Executes pytest with coverage collection and threshold enforcement."""
        cmd = [
            "pytest",
            f"--cov={self.src_dir}",
            f"--cov-fail-under={self.fail_under}",
            "--cov-report=term-missing",
            self.tests_dir,
        ]
        if self.verbose:
            cmd.append("-v")
        code, _ = self._run_command(cmd, f"Test Coverage (Threshold: {self.fail_under}%)")
        return code

    def run_linters(self) -> int:
        """Executes flake8, black --check, and mypy."""
        results = []

        # 1. Flake8
        flake8_cmd = ["flake8", self.src_dir, self.tests_dir]
        results.append(self._run_command(flake8_cmd, "Flake8 Style Check")[0])

        # 2. Black
        black_cmd = ["black", "--check", self.src_dir, self.tests_dir]
        results.append(self._run_command(black_cmd, "Black Formatting Check")[0])

        # 3. Mypy
        mypy_cmd = ["mypy", self.src_dir]
        results.append(self._run_command(mypy_cmd, "Mypy Static Type Analysis")[0])

        return 0 if all(r == 0 for r in results) else 1


def parse_args() -> argparse.Namespace:
    """Parses CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Run test suite, coverage checks, and linters for lastfm-collage-generator."
    )
    parser.add_argument(
        "--unit",
        action="store_true",
        help="Run pytest unit tests only.",
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run pytest with test coverage analysis.",
    )
    parser.add_argument(
        "--lint",
        action="store_true",
        help="Run static analysis linters (flake8, black, mypy).",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run unit tests, coverage, and all linters.",
    )
    parser.add_argument(
        "--fail-under",
        type=int,
        default=90,
        help="Minimum coverage percentage required (default: 90).",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output during execution.",
    )
    parser.add_argument(
        "--tests-dir",
        type=str,
        default="tests",
        help="Directory containing test suites (default: tests).",
    )
    parser.add_argument(
        "--src-dir",
        type=str,
        default="src",
        help="Source directory for coverage/linting (default: src).",
    )
    return parser.parse_args()


def main() -> int:
    """Main CLI entrypoint."""
    args = parse_args()
    runner = TestRunner(
        tests_dir=args.tests_dir,
        src_dir=args.src_dir,
        fail_under=args.fail_under,
        verbose=args.verbose,
    )

    # Default to running unit tests if no specific mode selected
    if not (args.unit or args.coverage or args.lint or args.all):
        args.unit = True

    overall_status = 0

    print("=" * 60)
    print("lastfm-collage-generator QA & Test Runner")
    print(f"Target Source: {args.src_dir} | Tests: {args.tests_dir}")
    print("=" * 60)

    if args.all or args.unit:
        status = runner.run_unit_tests()
        if status != 0:
            overall_status = status

    if args.all or args.coverage:
        status = runner.run_coverage()
        if status != 0:
            overall_status = status

    if args.all or args.lint:
        status = runner.run_linters()
        if status != 0:
            overall_status = status

    print("\n" + "=" * 60)
    if overall_status == 0:
        print("[🎉] ALL QA CHECKS COMPLETED SUCCESSFULLY")
    else:
        print(f"[❌] QA CHECKS COMPLETED WITH FAILURES (Exit Code: {overall_status})")
    print("=" * 60)

    return overall_status


if __name__ == "__main__":
    sys.exit(main())
