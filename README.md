# Unity Visual Scripting Skill

Create and edit Unity Visual Scripting graphs with natural-language requests in Codex.
Maintained for GPT-6 Astra, this skill helps Codex build editable gameplay logic,
assign graphs to objects, and diagnose connections and serialized data.

## What you can do

- Create Script Graphs for events, movement, variables, UI interactions, and component calls.
- Create State Graphs and configure state transitions.
- Assign graph assets to `ScriptMachine` or `StateMachine` components and save scene changes.
- Modify existing graphs while preserving unit identities, object references, and unaffected logic.

The package includes C# authoring patterns, port references, guidance for targeted
YAML/JSON edits, and validation tools.

## Requirements

- Codex and a Unity project with the Visual Scripting package installed.
- Python 3.9+ for validation tools.
- .NET SDK 8+ and the matching Unity editor for optional C# compilation checks.
- Unity Editor to execute generated scripts, save graph assignments, and verify behavior.

References target Visual Scripting 1.9.x; the skill checks the target project's APIs
and input system. This repository distributes the skill only, so use your own Unity project.

## Install

1. Download or clone this repository.
2. Copy the entire [skill folder](.agents/skills/unity-visual-scripting/) to `.agents/skills/unity-visual-scripting/` at the root of your Unity project.
3. Open that project in Codex, select GPT-6 Astra, and try a prompt below.

For all projects, use `~/.agents/skills/unity-visual-scripting/`. See
[Codex skill locations](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills).
The skill folder contains its own tools and references.

For Claude Code, copy the same skill folder to `.claude/skills/unity-visual-scripting/`.
This repository's Claude Code entry is a symlink to the canonical `.agents` folder.

## Example prompts

```text
Use $unity-visual-scripting. Create a Script Graph that rotates the selected
object around its Y axis at 90 degrees per second. Assign it, save the scene,
and verify the behavior in Play Mode.
```

```text
Use $unity-visual-scripting. Create an Idle/Patrol State Graph for the selected
NPC. Switch to Patrol on a StartPatrol custom event and return to Idle on StopPatrol.
```

## Validate a generator

From the target project root after a project-local install, replace the script path
with the editor script Codex generated:

```sh
python3 .agents/skills/unity-visual-scripting/tools/validate.py Assets/Editor/CreateRotationGraph.cs --unity-project .
```

This compiles the C# script and checks common port-key mistakes. Use `--static-only`
for port heuristics alone. Execute the script in Unity, reopen the graph and scene,
and exercise the behavior in Play Mode to verify the result. See [validation details](.agents/skills/unity-visual-scripting/references/validation.md).

## Documentation

- [Skill instructions](.agents/skills/unity-visual-scripting/SKILL.md)
- [Code patterns](.agents/skills/unity-visual-scripting/references/code_patterns.md) and [serialized graph editing](.agents/skills/unity-visual-scripting/references/serialized_edits.md)
- [Development, tests, and validation history](docs/DEVELOPMENT.md)

Related skills: [Shader Graph](https://github.com/from2001/UnityShaderGraphSkill) ·
[VFX Graph](https://github.com/from2001/UnityVfxGraphSkill).

## License

[MIT](LICENSE).
