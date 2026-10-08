#!/usr/bin/env python3
"""Run C# compilation and domain heuristics. Exit 0=pass, 1=errors, 2=incomplete."""

import argparse
from pathlib import Path
import subprocess
import sys

TOOLS_DIR = Path(__file__).resolve().parent
STATIC_CHECKER = "check_port_keys.py"


def run_check(script, cs_file, extra_args=None):
    """Return the actual subprocess status and both output streams."""
    try:
        result = subprocess.run(
            [sys.executable, str(TOOLS_DIR / script), cs_file] + (extra_args or []),
            capture_output=True, text=True, timeout=60,
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 2, "", str(exc)


def combine_status(codes):
    """Known errors fail; skipped, crashed, or timed-out layers remain incomplete."""
    if 1 in codes:
        return 1
    return 2 if any(code != 0 for code in codes) else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cs_file")
    parser.add_argument("--static-only", action="store_true", help="Run heuristics only; do not claim compilation")
    parser.add_argument("--unity-project")
    parser.add_argument("--unity-version")
    parser.add_argument("--unity-managed-dir")
    args = parser.parse_args()
    if not Path(args.cs_file).is_file():
        parser.error(f"File not found: {args.cs_file}")
    extra = []
    for name in ("unity_project", "unity_version", "unity_managed_dir"):
        value = getattr(args, name)
        if value:
            extra.extend(["--" + name.replace("_", "-"), value])
    checks = [(STATIC_CHECKER, [])]
    if not args.static_only:
        checks.insert(0, ("validate_cs.py", extra))
    codes = []
    for script, options in checks:
        print(f"--- {script} ---", flush=True)
        code, stdout, stderr = run_check(script, args.cs_file, options)
        codes.append(code)
        if stdout:
            print(stdout)
        if stderr:
            print(stderr, file=sys.stderr)
    code = combine_status(codes)
    scope = "STATIC CHECKS ONLY (compilation not run)" if args.static_only else "PREFLIGHT (Unity execution not checked)"
    status = {0: "PASSED", 1: "FAILED", 2: "INCOMPLETE"}[code]
    print(f"{scope}: {status}")
    sys.exit(code)


if __name__ == "__main__":
    main()
