---
name: unity-visual-scripting
description: Generate Unity Visual Scripting graphs programmatically via C# editor scripts (creation) or by directly editing .asset YAML files (modification). Use when the user asks to create, modify, or edit a Visual Scripting graph, Script Graph, State Graph, flow graph, node graph, or any visual scripting asset in Unity. Also use when assigning a ScriptGraphAsset or StateGraphAsset to a GameObject via ScriptMachine or StateMachine components. Triggers on keywords like "visual scripting", "script graph", "state graph", "flow graph", "ScriptMachine", "ScriptGraphAsset", "node-based", "bolt graph", or "modify graph".
---

# Unity Visual Scripting - Graph Creation & Modification

Generate Unity Visual Scripting graphs via **C# editor scripts** (creation) or **direct YAML/JSON editing** (modification of existing graphs).

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

### Task 3: Modify an Existing Graph via YAML

ScriptGraphAsset `.asset` files are YAML-wrapped JSON. For **modifying** existing graphs, directly edit the `.asset` file instead of writing a C# editor script. This is faster (no compilation wait) and avoids boilerplate.

**How it works**: The `.asset` file has a YAML header and a `_data._json` field containing the entire graph as a single-line JSON string. The JSON contains a `graph.elements` array with all units and connections.

#### YAML Structure Template

```yaml
%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!114 &11400000
MonoBehaviour:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_GameObject: {fileID: 0}
  m_Enabled: 1
  m_EditorHideFlags: 0
  m_Script: {fileID: 11500000, guid: 95e66c6366d904e98bc83428217d4fd7, type: 3}
  m_Name: GRAPH_NAME
  m_EditorClassIdentifier:
  _data:
    _json: 'JSON_CONTENT_HERE'
    _objectReferences: []
```

- `m_Script` guid `95e66c6366d904e98bc83428217d4fd7` is constant for all ScriptGraphAssets
- `m_Name` must match the filename without `.asset`
- `_json` is the entire graph JSON on a **single line** inside YAML single quotes

#### JSON Root Structure

```json
{
  "graph": {
    "variables": {"Kind":"Flow","collection":{"$content":[],"$version":"A"},"$version":"A"},
    "controlInputDefinitions": [],
    "controlOutputDefinitions": [],
    "valueInputDefinitions": [],
    "valueOutputDefinitions": [],
    "title": null,
    "summary": null,
    "pan": {"x":0.0,"y":0.0},
    "zoom": 1.0,
    "elements": [ ...UNITS_THEN_CONNECTIONS... ],
    "$version": "A"
  }
}
```

The `elements` array lists all **units first** (with sequential `$id`), then all **connections** (no `$id`).

#### Modification Workflow

1. **Read** the `.asset` file
2. **Extract** the `_json` value (everything between the YAML single quotes)
3. **Unescape** YAML single quotes (`''` → `'`)
4. **Parse** as JSON, modify the `graph.elements` array
5. **Re-escape** single quotes (`'` → `''`)
6. **Write** the JSON back as a single line in the YAML template
7. Unity Editor auto-reloads on file change

## Essential API Quick Reference

### Choosing Workflow: C# vs YAML

| Scenario | Use |
|----------|-----|
| **Create** a new graph from scratch | C# editor script (Task 1) |
| **Assign** a graph to a GameObject | C# editor script (Task 2) |
| **Modify** an existing `.asset` graph | YAML/JSON editing (Task 3) |
| **Create** a new graph without C# compilation | YAML/JSON writing (Task 3) |

### Creating Units

| Unit | Constructor | Key Ports |
|------|------------|-----------|
| Event | `new Start()`, `new Update()` | `trigger` (ControlOutput) |
| GetMember | `new GetMember(new Member(type, name))` | `value` (out), `target` (in, instance only) |
| SetMember | `new SetMember(new Member(type, name))` | `assign`/`assigned` (control), `input`/`output` (value) |
| InvokeMember | `new InvokeMember(new Member(type, name, paramTypes[]))` | `enter`/`exit` (control), `%paramName` (value in), `result` (non-void only) |
| Literal | `new Literal(typeof(T), value)` | `output` (ValueOutput) |
| ScalarSum | `new ScalarSum()` | `0`, `1` (value in, port keys), `sum` (out) — C# accessor: `multiInputs[0]`. Set `inputCount` for more inputs |
| ScalarMultiply | `new ScalarMultiply()` | `a`, `b` (in), `product` (out) |
| Sequence | `new Sequence()` | `enter` (ctrl in), `0`/`1`/... (ctrl out) — C# accessor: `multiOutputs[n]`. Set `outputCount` |
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

### Unit JSON Format (for YAML modification)

```json
{
  "position": {"x": 0.0, "y": 0.0},
  "guid": "uuid-v4-lowercase",
  "$version": "A",
  "$type": "Unity.VisualScripting.ClassName",
  "$id": "N"
}
```

Plus type-specific fields: `coroutine`, `defaultValues`, `member`, `parameterNames`, `kind`, `type`, `value`, `inputCount`, `outputCount`, etc.

### Connection JSON Format (for YAML modification)

```json
{"sourceUnit":{"$ref":"1"},"sourceKey":"trigger","destinationUnit":{"$ref":"2"},"destinationKey":"enter","guid":"uuid-v4","$type":"Unity.VisualScripting.ControlConnection"}
```

```json
{"sourceUnit":{"$ref":"3"},"sourceKey":"output","destinationUnit":{"$ref":"2"},"destinationKey":"%message","guid":"uuid-v4","$type":"Unity.VisualScripting.ValueConnection"}
```

### Member Object JSON Format (for YAML modification)

```json
{"name":"Log","parameterTypes":["System.Object"],"targetType":"UnityEngine.Debug","targetTypeName":"UnityEngine.Debug","$version":"A"}
```

- `parameterTypes`: array of fully-qualified type strings for methods, `null` for properties
- `targetType` and `targetTypeName` are always identical

### Typed Values (JSON)

| Type | JSON Format |
|------|-------------|
| `string` | `{"$content":"text","$type":"System.String"}` |
| `int` | `{"$content":42,"$type":"System.Int32"}` |
| `float` | `{"$content":3.14,"$type":"System.Single"}` |
| `bool` | `{"$content":true,"$type":"System.Boolean"}` |
| `Enum` | `{"$content":32,"$type":"UnityEngine.KeyCode"}` (integer value) |
| `Vector3` | `{"x":1.0,"y":2.0,"z":3.0,"$type":"UnityEngine.Vector3"}` (no `$content`) |
| `Color` | `{"r":1.0,"g":0.0,"b":0.0,"a":1.0,"$type":"UnityEngine.Color"}` (no `$content`) |
| `null` | `null` |

### Position Layout

Set `unit.position` AFTER `graph.units.Add(unit)`. Recommended spacing: ~250px horizontal, ~150px vertical.

## Critical Rules

### C# Creation Rules

- Always wrap editor scripts in `#if UNITY_EDITOR` / `#endif`
- Never use `?.` or `??` with `UnityEngine.Object` types
- Always call `EditorUtility.SetDirty()` after modifying GameObjects
- Always call `AssetDatabase.SaveAssets()` after creating/modifying assets
- For instance methods (e.g., `Transform.Rotate`), the `target` port auto-resolves to the owning GameObject's component when unconnected
- Variable units (`GetVariable`/`SetVariable`/`IsVariableDefined`) have NO `defaultName` property — set `kind` before `graph.units.Add()`, then set `defaultValues["name"]` after Add
- `ScalarSum` and `GenericSum` extend `MultiInputUnit<T>` — port keys are `"0"`, `"1"`, etc. C# accessor: `multiInputs[0]`, `multiInputs[1]` (NOT `a`, `b`). Output is `sum`. Other binary math units (`ScalarMultiply`, `ScalarSubtract`, etc.) still use `a`/`b`
- **Static vs instance members**: Static members (e.g., `Time.deltaTime`, `Debug.Log`, `Input.GetKey`) have no `target` port. Instance members (e.g., `Transform.position`, `Transform.Rotate`) have a `target` port that auto-resolves to the owning GameObject's component when unconnected
- **`%paramName` convention**: `InvokeMember` parameter port keys use `"%paramName"` format (e.g., `"%x"`, `"%y"`, `"%z"` for `Rotate`). C# accessor: `inputParameters[n]`
- **Void methods**: Void methods (e.g., `SetActive`, `Rotate`, `Play`) have no `result` port. `InvokeMember.targetOutput` is null for void instance methods — always null-check before wiring it
- **Comparison unit output — port key ≠ C# property**: ALL `BinaryComparisonUnit` subclasses (`Equal`, `NotEqual`, `Greater`, `Less`, `GreaterOrEqual`, `LessOrEqual`) expose their output via the C# property **`comparison`**. `Equal` and `NotEqual` override the port key string to `"equal"` / `"notEqual"` for backward compat, but the C# accessor is still `comparison`. Use `equal.comparison` (NOT ~~`equal.equal`~~) — the latter causes CS1061

### YAML Modification Rules

- **JSON must be single-line**: The entire JSON graph goes on one line inside the `_json` YAML value — no newlines
- **YAML single-quote escaping**: Single quotes inside JSON string values must be doubled (`'` → `''`)
- **`$id` system**: Sequential integers as strings (`"1"`, `"2"`, `"3"`, ...) — **units only**, NOT connections
- **`$ref` system**: Connections reference units via `{"$ref": "N"}` where N is the unit's `$id`
- **`guid`**: Every unit AND every connection gets a unique UUID v4 (all lowercase)
- **`$version`**: Always `"A"` on units, member objects, collection objects, and the graph root
- **Parameter port keys**: Prefixed with `%` in both `defaultValues` keys and connection `sourceKey`/`destinationKey` (e.g., `%message`, `%xAngle`)
- **Connections do NOT have `$id`**: Only units get `$id` fields
- **Elements ordering**: All units first, then all connections in the `elements` array
- **Static vs instance**: Static members have `"defaultValues": {}` (no `target`); instance members have `"target": null` in `defaultValues`
- **Structs vs scalars in typed values**: Structs (Vector3, Color) use direct field names without `$content`; scalars (int, float, string, bool) use `$content`
- **ScriptGraphAsset guid is constant**: `95e66c6366d904e98bc83428217d4fd7` — never changes

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
