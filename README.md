# Unity Visual Scripting Skill

Create, edit, and diagnose Unity Visual Scripting assets with Codex. Updated for GPT-6 Astra:
focused instructions, version-aware references, and explicit validation results.

## Install

Copy [`.agents/skills/unity-visual-scripting/`](.agents/skills/unity-visual-scripting/) into your Unity
project at the same relative path. The folder contains everything the skill needs;
the sample Unity project is not required. Codex discovers repository skills from
[`.agents/skills/`](https://learn.chatgpt.com/docs/build-skills).

For use across projects, place that folder under `~/.agents/skills/` instead. Select
GPT-6 Astra in your Codex session. The skill does not change model or account settings.

The `.claude/skills/` entry is a relative symlink to the same source. On systems
without Git symlink support, copy the canonical skill folder into the target project's
`.claude/skills/` instead. Copy only this skill, not the repository's whole settings tree.

## Use

```text
Use $unity-visual-scripting. Create a Script Graph that rotates this object each frame, assign it, and verify the behavior.
```

Python 3.9+ runs static checks. Optional C# compilation uses .NET SDK 8+ and the matching Unity editor. Actual graph execution still requires Unity.

This repository distributes a skill; use a separate Unity project with Visual Scripting for editor tests. Package versions in a target project take precedence over bundled
examples. A static check passing does not establish a working or visually correct graph.

See [the skill](.agents/skills/unity-visual-scripting/SKILL.md) for workflows and
[development notes](docs/DEVELOPMENT.md) for checks, evaluation scenarios, and migration details.
