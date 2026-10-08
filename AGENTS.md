# Repository guidance

This repository maintains `unity-visual-scripting` for Codex, with GPT-6 Astra as the intended
model. The canonical package is `.agents/skills/unity-visual-scripting/`. The matching
`.claude/skills/unity-visual-scripting` symlink preserves Claude Code compatibility; edit the
canonical files only. Model selection belongs to the calling session, not this skill.

This repository distributes a skill; use a separate Unity project with Visual Scripting for editor tests.
Treat bundled examples as versioned references. `_Others/` holds historical research;
read it only when investigating the origin of a pattern. Resolve current package APIs
from the target project instead of a hard-coded PackageCache path.

- Write comments and documentation in English.
- Never use `?.` or `??` on `UnityEngine.Object`; use explicit Unity null checks.
- Run all Unity object access on the main Unity thread.
- Do not hand-author new C# `.meta` files. Preserve and commit existing tracked metadata
  alongside its assets when committing changes.
- Keep helper files self-contained within the skill so copying only that directory works.

Run `python3 -m unittest discover -s tests -v` for changed Python tools. Tests use
disposable fixtures and may run without further approval. Do not require Unity for a
prose-only edit. For graph behavior, use the relevant skill's Unity checks and state
what remains unverified if an editor is unavailable. Do not change sample project
packages or settings merely to modernize the instructions.
