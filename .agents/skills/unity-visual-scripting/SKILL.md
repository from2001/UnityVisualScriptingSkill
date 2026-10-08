---
name: unity-visual-scripting
description: Create, edit, and diagnose Unity Visual Scripting Script Graphs and State Graphs, including ScriptMachine and StateMachine assignments. Use for Unity.VisualScripting assets and ports, not Shader Graph, VFX Graph, or general node editors.
---

# Unity Visual Scripting

Deliver the requested graph behavior while preserving asset identity, object references,
and unaffected logic. Use the target project's installed Visual Scripting package.

## Establish context

Inspect the Unity version, resolved `com.unity.visualscripting` version, target asset,
and relevant machine or scene. Package sources may be embedded/local under `Packages/`
or resolved under `Library/PackageCache/com.unity.visualscripting@*`.
The references target 1.9.x; verify unfamiliar or changed units in their `Definition()`
and base classes. UI labels, serialized port keys, and C# accessors are not equivalent.
Use the project's configured input system and target platform instead of copying legacy
input patterns into a project that cannot run them.

Use the Unity tools actually available, or generate an editor entry point. Tool paths
below are relative to this `SKILL.md`, not to a fixed `.claude` or working directory.

## Select an editing path

- **Create a graph or change topology:** prefer a C# editor script using
  `Unity.VisualScripting`. Read the relevant portions of
  [API reference](references/api_reference.md) and
  [code patterns](references/code_patterns.md). Script and State Graphs have different
  asset/graph types; preserve the requested type.
- **Assign a graph:** load the existing `ScriptGraphAsset`/`StateGraphAsset`, reuse or
  add the matching machine, and set its nest source and macro. Record Undo and scene
  or prefab changes as appropriate. Saving an asset does not save a scene assignment.
- **Small serialized edit:** direct YAML/JSON patching can be appropriate when the
  existing format and references are understood. Read
  [serialized edits](references/serialized_edits.md). Prefer Unity APIs for nested
  states, shared objects, object-reference changes, or uncertain serialization.

## Graph constraints

- Configure units before adding them, then wire ports after their definitions exist.
  Preserve existing unit GUIDs, serialized IDs, graph variables, and machine bindings.
- ControlOutput allows one outgoing connection; ValueInput allows one incoming
  connection. Use `Sequence` when execution must fan out.
- `ScalarSum`/`GenericSum` use `multiInputs[n]` (serialized keys `"0"`, `"1"`, ...),
  while binary arithmetic units commonly use `a`/`b`.
- Comparison accessors use `comparison`; `Equal`/`NotEqual` serialize the keys `equal`
  and `notEqual`. Do not turn those keys into nonexistent C# properties.
- `InvokeMember` parameters use `%parameterName` keys and `inputParameters[n]` in C#.
  Specify exact parameter types for overloads. Void methods have no result port.
  Only instance members have a target; verify implicit targets on the intended machine.
- Set variable `kind` before adding the unit and `defaultValues["name"]` afterwards.
  Check coroutine support for waits, transition triggers for state graphs, and the
  configured input/event source for runtime interactions.
- Keep editor code in an editor-only scope. All Unity object access runs on the main
  thread, with explicit Unity-object null checks instead of `?.`/`??`. Let Unity
  generate new C# `.meta` files and retain existing tracked `.meta` files.

## Verify and report

For generated C#, run the optional preflight compiler and port heuristics:

```sh
python3 <skill-dir>/tools/validate.py <generator.cs> --unity-project <project>
```

Python 3.9+ is needed. Compilation also needs .NET SDK 8+ and the matching Unity editor;
`--unity-managed-dir <Managed>` supports custom installations. Exit `0` means the
requested preflight checks passed, `1` means detected errors, and `2` means incomplete
validation. `--static-only` deliberately checks only port heuristics. See
[validation](references/validation.md) for limits and setup.

Neither regex checks nor C# compilation verifies reflected member names, port existence
at runtime, serialization round trips, or execution. When Unity is available, execute
the generator, reopen the graph, inspect missing units/connections, and exercise the
requested behavior in Play Mode or a focused test. Verify state transitions and scene
persistence when those changed. Deliver prepared artifacts even without an editor,
clearly identifying the checks still pending. Report paths, versions, and evidence.
