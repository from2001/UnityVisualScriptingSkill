#!/usr/bin/env python3
"""
validate_cs.py - Validate generated C# editor scripts using dotnet build.

Usage:
    python3 validate_cs.py <path_to_cs_file> [--unity-version VERSION] [--unity-project PATH]

Outputs human-readable error list. Exits 0 (clean) or 1 (errors found).
"""

import subprocess
import re
import sys
from pathlib import Path

TOOL_DIR = Path(__file__).parent
PROJECT_DIR = TOOL_DIR / "validation_project"
DEFAULT_UNITY_VERSION = "6000.0.68f1"
UNITY_EDITOR_BASE = Path("/Applications/Unity/Hub/Editor")

# MSBuild diagnostic pattern: file(line,col): severity code: message [project]
DIAG_PATTERN = re.compile(
    r"^(.+?)\((\d+),(\d+)\):\s+(error|warning)\s+(CS\d+):\s+(.+?)\s+\[.+\]$"
)


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


def parse_diagnostics(output):
    """Parse MSBuild output into diagnostic dicts."""
    diagnostics = []
    for line in output.splitlines():
        m = DIAG_PATTERN.match(line.strip())
        if m:
            diagnostics.append({
                "severity": "Error" if m.group(4) == "error" else "Warning",
                "code": m.group(5),
                "message": m.group(6),
                "line": int(m.group(2)),
                "column": int(m.group(3)),
            })
    return diagnostics


def validate(cs_path, unity_version, unity_project=None):
    """Run dotnet build validation on a C# file."""
    managed_dir = find_unity_managed_dir(unity_version)
    if not managed_dir:
        print("WARNING: Unity managed directory not found, skipping C# validation",
              file=sys.stderr)
        return []

    # Build properties passed to the template .csproj
    props = {
        "ValidationSource": str(Path(cs_path).resolve()),
        "UnityManagedDir": str(managed_dir),
    }

    if unity_project:
        script_assemblies = Path(unity_project) / "Library" / "ScriptAssemblies"
        if script_assemblies.exists():
            props["VSAssembliesDir"] = str(script_assemblies)

    args = [
        "dotnet", "build", str(PROJECT_DIR),
        "--nologo", "--no-restore", "-v", "quiet",
        "-clp:NoSummary",
    ]
    for key, val in props.items():
        args.append(f"-p:{key}={val}")

    result = subprocess.run(args, capture_output=True, text=True, timeout=30)

    # Parse diagnostics from both stdout and stderr (MSBuild may write to either)
    all_output = result.stdout + "\n" + result.stderr
    return parse_diagnostics(all_output)


def restore_project():
    """Run dotnet restore once to ensure packages are available."""
    result = subprocess.run(
        ["dotnet", "restore", str(PROJECT_DIR), "--nologo", "-v", "quiet"],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        print(f"Restore failed:\n{result.stderr}", file=sys.stderr)
        return False
    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="C# validator for Unity scripts")
    parser.add_argument("cs_file", help="Path to C# file to validate")
    parser.add_argument("--unity-version", default=DEFAULT_UNITY_VERSION,
                        help=f"Unity editor version (default: {DEFAULT_UNITY_VERSION})")
    parser.add_argument("--unity-project", default=None,
                        help="Path to Unity project (for VS DLLs)")
    args = parser.parse_args()

    if not Path(args.cs_file).exists():
        print(f"ERROR: File not found: {args.cs_file}", file=sys.stderr)
        sys.exit(2)

    # Ensure NuGet restore is done (first run only, near-instant after that)
    if not (PROJECT_DIR / "obj" / "project.assets.json").exists():
        print("Restoring project (first run)...", file=sys.stderr)
        if not restore_project():
            print("ERROR: Failed to restore project", file=sys.stderr)
            sys.exit(2)

    diagnostics = validate(args.cs_file, args.unity_version, args.unity_project)

    errors = [d for d in diagnostics if d.get("severity") == "Error"]
    warnings = [d for d in diagnostics if d.get("severity") == "Warning"]

    if not errors and not warnings:
        print("C# validation PASSED: No errors or warnings.")
        sys.exit(0)

    for d in errors:
        print(f"  ERROR {d['code']} (line {d['line']}): {d['message']}")
    for d in warnings:
        print(f"  WARNING {d['code']} (line {d['line']}): {d['message']}")

    print(f"\nTotal: {len(errors)} error(s), {len(warnings)} warning(s)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
