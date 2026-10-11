#!/usr/bin/env python3
"""Run every check. Exits non-zero if anything fails."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SUITES = ["test_suite.py", "test_workbook_and_cli.py",
          "test_repo_hygiene.py"]

failed = 0
for s in SUITES:
    print(f"\n{'=' * 72}\n{s}\n{'=' * 72}")
    r = subprocess.run([sys.executable, os.path.join(HERE, s)])
    failed |= r.returncode
print("\nall suites passed" if not failed else "\nSOME SUITES FAILED")
sys.exit(1 if failed else 0)
