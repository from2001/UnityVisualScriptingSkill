---
name: unity-visual-scripting
description: Generate Unity Visual Scripting graphs programmatically via C# editor scripts and assign them to GameObjects. Use when the user asks to create a Visual Scripting graph, Script Graph, State Graph, flow graph, node graph, or any visual scripting asset in Unity. Also use when assigning a ScriptGraphAsset or StateGraphAsset to a GameObject via ScriptMachine or StateMachine components. Triggers on keywords like "visual scripting", "script graph", "state graph", "flow graph", "ScriptMachine", "ScriptGraphAsset", "node-based", or "bolt graph".
---

# Unity Visual Scripting - Editor Script Generation

Generate C# editor scripts that programmatically create Unity Visual Scripting graphs and assign them to GameObjects.

**Namespace**: `Unity.VisualScripting` | **Required assemblies**: `Unity.VisualScripting.Core`, `Unity.VisualScripting.Flow`

## Workflow

### Task 1: Create a Script Graph

1. Create `ScriptGraphAsset` and access its `FlowGraph`
2. Create units (nodes), add to graph, set positions
3. Wire control connections (execution flow) and value connections (data flow)
4. Save to AssetDatabase

```csharp
#if UNITY_EDITOR
using System;
using UnityEditor;
using UnityEngine;
using Unity.VisualScripting;

public static class MyGraphCreator
{
    [MenuItem("Tools/VS/Create My Graph")]
    public static void Create()
    {
        // 1. Create asset (graph is auto-initialized)
        var graphAsset = ScriptableObject.CreateInstance<ScriptGraphAsset>();
        var graph = graphAsset.graph;

        // 2. Create and add units
        var onUpdate = new Update();
        graph.units.Add(onUpdate);
        onUpdate.position = new Vector2(-300, 0);

        // 3. Wire connections
        // graph.controlConnections.Add(new ControlConnection(src.trigger, dst.enter));
        // graph.valueConnections.Add(new ValueConnection(src.output, dst.input));

        // 4. Save
        if (!AssetDatabase.IsValidFolder("Assets/VisualScripting"))
            AssetDatabase.CreateFolder("Assets", "VisualScripting");
        AssetDatabase.CreateAsset(graphAsset, "Assets/VisualScripting/MyGraph.asset");
        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();
    }
}
#endif
```

### Task 2: Assign a Graph to a GameObject

Add a `ScriptMachine` component and set its `nest.macro` to a `ScriptGraphAsset`.

```csharp
#if UNITY_EDITOR
using UnityEditor;
using UnityEngine;
using Unity.VisualScripting;

public static class MyGraphAssigner
{
    [MenuItem("Tools/VS/Assign My Graph")]
    public static void Assign()
    {
        var go = GameObject.Find("TargetObject");
        if (go == null) { Debug.LogError("TargetObject not found."); return; }

        var graphAsset = AssetDatabase.LoadAssetAtPath<ScriptGraphAsset>(
            "Assets/VisualScripting/MyGraph.asset");
        if (graphAsset == null) { Debug.LogError("Graph asset not found."); return; }

        var machine = go.GetComponent<ScriptMachine>();
        if (machine == null)
            machine = go.AddComponent<ScriptMachine>();

        machine.nest.source = GraphSource.Macro;
        machine.nest.macro = graphAsset;
        EditorUtility.SetDirty(go);
    }
}
#endif
```

For `StateMachine`, use `StateGraphAsset` and `StateMachine` instead.

## Essential API Quick Reference

### Creating Units

| Unit | Constructor | Key Ports |
|------|------------|-----------|
| Event | `new Start()`, `new Update()` | `trigger` (ControlOutput) |
| GetMember | `new GetMember(new Member(type, name))` | `value` (out), `target` (in, instance only) |
| SetMember | `new SetMember(new Member(type, name))` | `assign`/`assigned` (control), `input`/`output` (value) |
| InvokeMember | `new InvokeMember(new Member(type, name, paramTypes[]))` | `enter`/`exit` (control), `inputParameters[n]`/`result` (value) |
| Literal | `new Literal(typeof(T), value)` | `output` (ValueOutput) |
| ScalarSum | `new ScalarSum()` | `multiInputs[0]`, `multiInputs[1]` (in), `sum` (out) — extends `MultiInputUnit<float>` |
| ScalarMultiply | `new ScalarMultiply()` | `a`, `b` (in), `product` (out) |
| If | `new If()` | `enter` (control in), `condition` (value in), `ifTrue`/`ifFalse` (control out) |
| GetVariable | `new GetVariable() { kind }` (set `defaultValues["name"]` after Add) | `value` (out) |
| SetVariable | `new SetVariable() { kind }` (set `defaultValues["name"]` after Add) | `assign`/`assigned` (control), `input`/`output` (value) |

### Member Constructor Patterns

```csharp
// Static property
new Member(typeof(Time), nameof(Time.deltaTime))

// Instance property
new Member(typeof(Transform), "position")

// Method with overload disambiguation
new Member(typeof(Transform), "Rotate", new[] { typeof(float), typeof(float), typeof(float) })
new Member(typeof(Debug), "Log", new[] { typeof(object) })
```

### Connections

```csharp
// Control flow (ControlOutput -> ControlInput)
graph.controlConnections.Add(new ControlConnection(start.trigger, action.enter));

// Data flow (ValueOutput -> ValueInput)
graph.valueConnections.Add(new ValueConnection(literal.output, invoke.inputParameters[0]));
```

**Rules**: ControlOutput allows only 1 outgoing connection. ValueInput allows only 1 incoming connection. Use `Sequence` unit to fan out control flow.

### Position Layout

Set `unit.position` AFTER `graph.units.Add(unit)`. Recommended spacing: ~250px horizontal, ~150px vertical.

## Critical Rules

- Always wrap editor scripts in `#if UNITY_EDITOR` / `#endif`
- Never use `?.` or `??` with `UnityEngine.Object` types
- Always call `EditorUtility.SetDirty()` after modifying GameObjects
- Always call `AssetDatabase.SaveAssets()` after creating/modifying assets
- For instance methods (e.g., `Transform.Rotate`), the `target` port auto-resolves to the owning GameObject's component when unconnected
- Variable units (`GetVariable`/`SetVariable`/`IsVariableDefined`) have NO `defaultName` property — set `kind` before `graph.units.Add()`, then set `defaultValues["name"]` after Add
- `ScalarSum` and `GenericSum` extend `MultiInputUnit<T>` — their input ports are `multiInputs[0]`, `multiInputs[1]` (NOT `a`, `b`). Output is `sum`. Other binary math units (`ScalarMultiply`, `ScalarSubtract`, etc.) still use `a`/`b`
- `InvokeMember.targetOutput` is null for void instance methods — always null-check before wiring it

## Unit Verification Protocol (MANDATORY for undocumented units)

For any unit type NOT listed in `api_reference.md`, verify it against the actual package source before generating code. This prevents wrong class names and port keys.

### Source Location

```
Library/PackageCache/com.unity.visualscripting@*/Runtime/VisualScripting.Flow/Framework/
```

Use glob `com.unity.visualscripting@*` to handle hash changes across package updates.

### Verification Steps

1. **Verify class exists** — Grep for `class {ClassName}` under the Framework directory. If not found, the class doesn't exist. Common trap: UI display names differ from class names (e.g., "Add" node = `ScalarSum`, not `ScalarAdd`).

2. **Read `Definition()` method** — Port keys are the first argument to `ValueInput()` / `ValueOutput()` / `ControlInput()` / `ControlOutput()` calls. Usually `nameof(prop)` or `i.ToString()` for multi-input units.

3. **Check base classes** — If the class inherits from another (e.g., `ScalarSum : Sum<float> : MultiInputUnit<T>`), ALSO read the base class `Definition()` — ports are often defined there, not in the leaf class.

### Directory Quick-Reference

```
Framework/
├── Math/           — Base: Sum.cs, Multiply.cs, Subtract.cs, Divide.cs
│   ├── Scalar/     — ScalarSum, ScalarMultiply, ScalarSubtract, ...
│   ├── Generic/    — GenericSum, GenericMultiply, ...
│   └── Vector*/    — Vector2Sum, Vector3Sum, ...
├── Control/        — If, For, ForEach, While, Sequence, Once, ...
├── Logic/          — And, Or, Negate, Equal, Greater, Less, ...
├── Events/
│   ├── Lifecycle/  — Start, Update, FixedUpdate, OnEnable, OnDestroy
│   ├── Physics/    — OnCollisionEnter, OnTriggerEnter, ...
│   └── Input/      — OnKeyDown, OnMouseDown, ...
├── Variables/      — GetVariable, SetVariable, IsVariableDefined
├── Codebase/       — InvokeMember, GetMember, SetMember
├── Time/           — Timer, Cooldown, WaitForSecondsUnit, ...
├── Nulls/          — Null, NullCheck, NullCoalesce
├── Literal.cs
└── This.cs
```

### Skip-Verification List (already documented)

These units are fully documented in `api_reference.md` and do NOT need source verification:
`Literal`, `If`, `For`, `ForEach`, `While`, `Sequence`, `Once`, `NullCheck`, `SelectUnit`,
`Start`, `Update`, `FixedUpdate`, `OnTriggerEnter`, `OnCollisionEnter`, `OnKeyboardInput`, `CustomEvent`,
`GetMember`, `SetMember`, `InvokeMember`,
`GetVariable`, `SetVariable`, `IsVariableDefined`,
`ScalarSum`, `ScalarMultiply`, `ScalarSubtract`, `ScalarDivide`, `ScalarModulo`,
`GenericSum`, `GenericSubtract`, `GenericMultiply`, `GenericDivide`,
`And`, `Or`, `Negate`, `Equal`, `NotEqual`, `Greater`, `Less`, `GreaterOrEqual`, `LessOrEqual`,
`WaitForSecondsUnit`, `WaitUntilUnit`, `Cooldown`, `This`

## References

- **Detailed API Reference**: See [references/api_reference.md](references/api_reference.md) for complete port names, unit types catalog, variable system, and Member class details
- **Code Pattern Templates**: See [references/code_patterns.md](references/code_patterns.md) for complete working examples covering events, input, physics, transforms, variables, flow control, UI, animation, audio, and more
