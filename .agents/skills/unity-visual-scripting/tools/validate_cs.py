#!/usr/bin/env python3
"""Compile one editor script against a selected Unity installation.

Exit 0: compilation passed; 1: build failed; 2: setup/execution incomplete.
This preflight does not execute the script or reproduce Unity's assembly definitions.
"""

import argparse
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

PROJECT_FILE = Path(__file__).resolve().parent / "validation_project/ValidationProject.csproj"
PACKAGE_PATTERN = "Unity.VisualScripting*.dll"
ASSEMBLY_PROPERTY = "VSAssembliesDir"


def project_version(project):
    """Read the editor version pinned by the target project."""
    path = Path(project) / "ProjectSettings/ProjectVersion.txt"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"Cannot read {path}: {exc}") from exc
    match = re.search(r"^m_EditorVersion:\s*(\S+)", text, re.MULTILINE)
    if not match:
        raise ValueError(f"No m_EditorVersion in {path}")
    return match.group(1)


def find_unity_managed_dir(version):
    """Try common Hub locations for this exact version, never another version."""
    roots = [
        Path("/Applications/Unity/Hub/Editor"),
        Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Unity/Hub/Editor",
        Path.home() / "Unity/Hub/Editor",
        Path.home() / ".local/share/Unity/Hub/Editor",
    ]
    for root in roots:
        for suffix in ("Unity.app/Contents/Managed", "Editor/Data/Managed"):
            candidate = root / version / suffix
            if candidate.is_dir():
                return candidate
    return None


def validate(cs_path, unity_version=None, unity_project=None, managed_dir=None):
    """Return (exit code, evidence) without mutating the Unity project or skill."""
    source = Path(cs_path).resolve()
    if not source.is_file() or source.suffix.lower() != ".cs":
        return 2, f"C# source file not found or not a .cs file: {source}"
    if not PROJECT_FILE.is_file():
        return 2, f"Validation template missing: {PROJECT_FILE}"

    try:
        project = Path(unity_project).resolve() if unity_project else None
        pinned = project_version(project) if project else None
        if pinned and unity_version and pinned != unity_version:
            return 2, f"Requested editor {unity_version} differs from project version {pinned}."
        version = unity_version or pinned
        if managed_dir:
            managed = Path(managed_dir).expanduser().resolve()
        elif version:
            managed = find_unity_managed_dir(version)
        else:
            return 2, "Specify --unity-project, --unity-version, or --unity-managed-dir."
        if managed is None or not managed.is_dir():
            return 2, f"Unity {version or ''} Managed directory not found. Use --unity-managed-dir."
        if not (managed / "UnityEngine/UnityEngine.CoreModule.dll").is_file() and not (managed / "UnityEngine.dll").is_file():
            return 2, f"Unity engine assemblies not found in {managed}"

        assemblies = project / "Library/ScriptAssemblies" if project else None
        if assemblies is not None and not list(assemblies.glob(PACKAGE_PATTERN)):
            return 2, f"Package assemblies missing in {assemblies}; import/compile the target project in Unity."
        if shutil.which("dotnet") is None:
            return 2, ".NET SDK not found on PATH. Use Unity compilation or install an SDK separately."

        # Separate builds prevent cross-run cache races and allow read-only installs.
        with tempfile.TemporaryDirectory(prefix="unity-skill-csharp-") as tmp:
            work = Path(tmp)
            shutil.copyfile(source, work / "Input.cs")
            tree = ET.parse(PROJECT_FILE)
            props = ET.SubElement(tree.getroot(), "PropertyGroup")
            ET.SubElement(props, "ValidationSource").text = "Input.cs"
            ET.SubElement(props, "UnityManagedDir").text = str(managed)
            if assemblies is not None:
                ET.SubElement(props, ASSEMBLY_PROPERTY).text = str(assemblies)
            tree.write(work / "ValidationProject.csproj", encoding="utf-8", xml_declaration=True)
            result = subprocess.run(
                ["dotnet", "build", "ValidationProject.csproj", "--nologo", "-v", "quiet",
                 "-p:NuGetAudit=false"],
                cwd=work, capture_output=True, text=True, timeout=45,
            )
        output = "\n".join(part.strip() for part in (result.stdout, result.stderr) if part.strip())
        # MSBuild/NuGet/SDK errors do not necessarily match a C# diagnostic regex.
        if result.returncode != 0:
            return 1, output or f"dotnet build failed with exit code {result.returncode}."
        scope = f"Unity {version or 'custom installation'}; Managed={managed}"
        if assemblies is not None:
            scope += f"; package assemblies={assemblies}"
        return 0, f"{scope}\n{output}\nC# compilation PASSED (preflight only; Unity execution not checked)."
    except (OSError, ValueError, ET.ParseError, subprocess.TimeoutExpired) as exc:
        return 2, str(exc)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cs_file", help="Editor C# source file")
    parser.add_argument("--unity-version", help="Exact editor version; otherwise read the project")
    parser.add_argument("--unity-project", help="Target Unity project with compiled package assemblies")
    parser.add_argument("--unity-managed-dir", help="Explicit Managed directory for custom editor installs")
    args = parser.parse_args()
    code, evidence = validate(args.cs_file, args.unity_version, args.unity_project, args.unity_managed_dir)
    print(evidence)
    if code == 2:
        print("C# validation INCOMPLETE: compilation was not established.", file=sys.stderr)
    sys.exit(code)


if __name__ == "__main__":
    main()
