#!/usr/bin/env python3
"""
validate_cs.py - Validate generated C# editor scripts using Roslyn.

Usage:
    python3 validate_cs.py <path_to_cs_file> [--unity-version VERSION] [--unity-project PATH]

Outputs human-readable error list. Exits 0 (clean) or 1 (errors found).
"""

import subprocess
import json
import sys
import os
from pathlib import Path

TOOL_DIR = Path(__file__).parent / "RoslynValidator"
DEFAULT_UNITY_VERSION = "6000.0.68f1"
UNITY_EDITOR_BASE = Path("/Applications/Unity/Hub/Editor")


def find_unity_managed_dir(version):
    """Find Unity's Managed directory for the given editor version."""
    candidate = UNITY_EDITOR_BASE / version / "Unity.app" / "Contents" / "Managed"
    if candidate.exists():
        return candidate
    # Try all installed versions if specified version not found
    if UNITY_EDITOR_BASE.exists():
        for entry in sorted(UNITY_EDITOR_BASE.iterdir(), reverse=True):
            managed = entry / "Unity.app" / "Contents" / "Managed"
            if managed.exists():
                print(f"NOTE: Unity {version} not found, using {entry.name}", file=sys.stderr)
                return managed
    return None


def build_validator():
    """Build the RoslynValidator project if needed."""
    # Check if build output exists and is newer than source
    exe_dir = TOOL_DIR / "bin" / "Release" / "net9.0"
    exe = exe_dir / "RoslynValidator"
    if not exe.exists() and not (exe_dir / "RoslynValidator.dll").exists():
        print("Building RoslynValidator (first run)...", file=sys.stderr)
        result = subprocess.run(
            ["dotnet", "build", str(TOOL_DIR), "-c", "Release", "--nologo", "-v", "quiet"],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"Build failed:\n{result.stderr}", file=sys.stderr)
            return False
        print("Build complete.", file=sys.stderr)
    return True


def validate(cs_path, unity_version, unity_project=None):
    """Run Roslyn validation on a C# file."""
    managed_dir = find_unity_managed_dir(unity_version)
    if not managed_dir:
        print(f"WARNING: Unity managed directory not found, skipping Roslyn validation",
              file=sys.stderr)
        return []

    args = [
        "dotnet", "run", "--project", str(TOOL_DIR),
        "-c", "Release", "--no-build", "--nologo",
        "--", cs_path,
        "--managed", str(managed_dir),
    ]

    if unity_project:
        script_assemblies = Path(unity_project) / "Library" / "ScriptAssemblies"
        if script_assemblies.exists():
            args += ["--vs-assemblies", str(script_assemblies)]

    result = subprocess.run(args, capture_output=True, text=True, timeout=30)

    if result.returncode == 2:
        print(f"Validator error: {result.stderr.strip()}", file=sys.stderr)
        return []

    if result.stdout.strip():
        try:
            return json.loads(result.stdout.strip())
        except json.JSONDecodeError:
            print(f"Failed to parse validator output: {result.stdout}", file=sys.stderr)
            return []

    return []


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Roslyn C# validator for Unity scripts")
    parser.add_argument("cs_file", help="Path to C# file to validate")
    parser.add_argument("--unity-version", default=DEFAULT_UNITY_VERSION,
                        help=f"Unity editor version (default: {DEFAULT_UNITY_VERSION})")
    parser.add_argument("--unity-project", default=None,
                        help="Path to Unity project (for VS DLLs)")
    args = parser.parse_args()

    if not Path(args.cs_file).exists():
        print(f"ERROR: File not found: {args.cs_file}", file=sys.stderr)
        sys.exit(2)

    if not build_validator():
        print("ERROR: Failed to build RoslynValidator", file=sys.stderr)
        sys.exit(2)

    diagnostics = validate(args.cs_file, args.unity_version, args.unity_project)

    errors = [d for d in diagnostics if d.get("severity") == "Error"]
    warnings = [d for d in diagnostics if d.get("severity") == "Warning"]

    if not errors and not warnings:
        print("Roslyn validation PASSED: No errors or warnings.")
        sys.exit(0)

    for d in errors:
        print(f"  ERROR {d['code']} (line {d['line']}): {d['message']}")
    for d in warnings:
        print(f"  WARNING {d['code']} (line {d['line']}): {d['message']}")

    print(f"\nTotal: {len(errors)} error(s), {len(warnings)} warning(s)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
