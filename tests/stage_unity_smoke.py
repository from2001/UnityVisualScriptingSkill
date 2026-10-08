"""Stage the maintained rotation example and persistence/runtime checks in a disposable project."""
import argparse
from pathlib import Path
import re


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.run_id):
        parser.error("run-id must contain only letters, digits, underscores, or hyphens")
    project = args.project.resolve()
    if not (project / "ProjectSettings/ProjectVersion.txt").is_file():
        parser.error("project must be an existing disposable Unity project with Visual Scripting")
    root = Path(__file__).resolve().parents[1]
    output = "Assets/SkillSmokeVS/" + args.run_id
    if (project / output).exists():
        parser.error("output already exists; choose a new run-id")
    destination = project / "Assets/SkillSmokeVS/Editor"
    destination.mkdir(parents=True, exist_ok=True)
    (project / output).mkdir(parents=True)
    source = (root / ".agents/skills/unity-visual-scripting/references/code_patterns.md").read_text()
    blocks = re.findall(r"```csharp\n(.*?)```", source, re.S)
    example = next(b for b in blocks if "public static class CreateRotateGraph" in b)
    example = example.replace("Assets/VisualScripting", output)
    example = example.replace('AssetDatabase.CreateFolder("Assets", "VisualScripting");',
                              'throw new System.InvalidOperationException("Stage the fixture directory first.");')
    imports = "using UnityEditor;\nusing UnityEditor.SceneManagement;\nusing UnityEngine;\nusing Unity.VisualScripting;\n"
    (destination / "CreateRotateGraph.cs").write_text(imports + example)
    harness = (root / "tests/unity/VisualScriptingSkillSmoke.cs").read_text().replace("__OUTPUT_ROOT__", output)
    (destination / "VisualScriptingSkillSmoke.cs").write_text(harness)
    print(f"Staged fixtures in {destination}. Let Unity generate metadata.")
    print("Run VisualScriptingSkillSmoke.CreateFixtures() in Edit Mode, then CheckPlayMode() once during Play Mode.")


if __name__ == "__main__":
    main()
