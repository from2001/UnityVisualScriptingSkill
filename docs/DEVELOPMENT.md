# Development and validation

The canonical skill is `.agents/skills/unity-visual-scripting/`. It must work when copied by
itself to another project or user skill directory. `.claude/skills/unity-visual-scripting` is
a compatibility symlink, not a second source tree. Third-party skills and historical
`_Others/` research are outside this migration.

## Local checks

```sh
python3 -m unittest discover -s tests -v
```

The tests use temporary files and mock unavailable external processes. They exercise
observable tool results and failure paths; they do not certify Unity graph behavior.
Use Python 3.9+. No Unity or .NET installation is required for these regression tests.
For real compiler/import/render evidence use the installed skill's documented checks.

## Behavioral evaluation

Use [eval scenarios](../.agents/skills/unity-visual-scripting/evals/evals.json) in a disposable
copy of a target project. Each scenario states a user request, environment assumptions,
and observable expectations. Evaluate positive routing, a neighboring task that should
not use the skill, editing preservation, and unavailable-editor handling. Record the
actual model, editor/package versions, artifacts and checks. These are evaluation
specifications, not claims that model trials passed. Read only the references needed
for the scenario, and keep generated artifacts outside this repository.

## Astra migration decisions

The entry point now carries task selection, important invariants, and evidence criteria;
long versioned examples are read on demand. Package source and existing assets take
precedence over a bundled catalog. Examples no longer justify changing a project's
pipeline, regenerating unrelated nodes, or inventing missing tools. Missing validation
is reported explicitly instead of being counted as a pass.

This follows OpenAI's [Astra skill guidance](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)
and [skill discovery documentation](https://learn.chatgpt.com/docs/build-skills).
The Unity sample package versions are intentionally retained. This change improves the
instructions and checks; it does not claim compatibility with every later Unity release
or a measured model-quality improvement without separate model trials.

## Local verification on 2026-10-08

- 12 Python regression tests passed.
- Skill frontmatter, UI metadata, local documentation links, and standalone-folder tool execution were checked.
- The rotation generator was compiled against the installed Unity 6000.0.70f1 / Visual Scripting 1.9.7 assemblies and passed the port checker. The UnityShaderGraphSkill sample project supplied those existing assemblies; this distribution repository has no Unity project. Graph execution and scene persistence were not tested.

No Unity Editor execution, visual inspection, target-device checks, or before/after
model-quality trials were performed in this maintenance pass. Evaluation JSON files
are scenario definitions for those future trials.
