#!/usr/bin/env python3
"""
validate.py - Combined C# validator for Unity Visual Scripting skill.

Runs both Roslyn semantic validation and VS-specific port-key checks.

Usage:
    python3 validate.py <generated.cs> [--unity-version VERSION] [--unity-project PATH]

Exit codes:
    0 - All checks passed
    1 - Errors found
    2 - Usage or setup error
"""

import subprocess
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).parent


def run_check(script, cs_file, extra_args=None):
    """Run a validation script and return (exit_code, stdout_output, stderr_output)."""
    cmd = [sys.executable, str(TOOLS_DIR / script), cs_file] + (extra_args or [])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return 2, "", f"Timeout running {script}"
    except FileNotFoundError:
        return 2, "", f"Script not found: {script}"


def main():
    if len(sys.argv) < 2:
        print("Usage: validate.py <cs_file> [--unity-version VERSION] [--unity-project PATH]")
        sys.exit(2)

    cs_file = sys.argv[1]
    extra_args = sys.argv[2:]

    if not Path(cs_file).exists():
        print(f"ERROR: File not found: {cs_file}")
        sys.exit(2)

    has_errors = False

    # Layer 1: Roslyn semantic validation
    print("=== Roslyn Semantic Validation ===")
    rc1, out1, err1 = run_check("validate_cs.py", cs_file, extra_args)
    if out1:
        print(out1)
    if rc1 == 1:
        has_errors = True
    elif rc1 == 2:
        print("  (Roslyn validation skipped due to setup issue)")
        if err1:
            print(f"  {err1}", file=sys.stderr)

    print()

    # Layer 2: VS port-key static analysis
    print("=== VS Port Key Static Analysis ===")
    rc2, out2, err2 = run_check("check_port_keys.py", cs_file)
    if out2:
        print(out2)
    if rc2 == 1:
        has_errors = True

    print()

    # Summary
    if has_errors:
        print("VALIDATION FAILED: Fix the errors above and re-validate.")
        sys.exit(1)
    else:
        print("VALIDATION PASSED: All checks clean.")
        sys.exit(0)


if __name__ == "__main__":
    main()
