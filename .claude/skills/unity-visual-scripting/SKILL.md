---
name: unity-visual-scripting
description: Generate Unity Visual Scripting graph .asset files directly (no C# helper scripts). Use when the user asks to create a Visual Scripting graph, Script Graph, State Graph, flow graph, node graph, or any visual scripting asset in Unity. Also use when assigning a ScriptGraphAsset or StateGraphAsset to a GameObject via ScriptMachine or StateMachine components. Triggers on keywords like "visual scripting", "script graph", "state graph", "flow graph", "ScriptMachine", "ScriptGraphAsset", "node-based", or "bolt graph".
---

# Unity Visual Scripting - Direct .asset File Generation

Generate Unity Visual Scripting graph `.asset` files directly by writing YAML+JSON. No C# editor scripts, no compilation wait, no menu items.

**Format**: YAML wrapper containing serialized JSON graph data
**Output**: `.asset` file that Unity auto-imports on Editor focus

## Workflow

### Task 1: Create a Script Graph

1. **Design** the graph: identify units (nodes), connections, and layout positions
2. **Build** the JSON `elements` array (units first, then connections)
3. **Assign** sequential `$id` strings to each unit, generate UUID v4 for every element
4. **Wrap** in the YAML boilerplate template
5. **Write** to `Assets/VisualScripting/{Name}.asset`

#### UUID Generation

```bash
# Generate a UUID for each unit and connection
uuidgen | tr '[:upper:]' '[:lower:]'
```

#### YAML Boilerplate Template

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

- `m_Script` guid `95e66c6366d904e98bc83428217d4fd7` = ScriptGraphAsset (constant, never changes)
- `m_Name`: must match the filename (without `.asset` extension)
- `JSON_CONTENT_HERE`: entire graph JSON on a **single line**, wrapped in YAML single quotes
- Single quotes inside JSON string values must be escaped as `''` (YAML 1.1)

#### JSON Root Structure

```json
{"graph":{"variables":{"Kind":"Flow","collection":{"$content":[],"$version":"A"},"$version":"A"},"controlInputDefinitions":[],"controlOutputDefinitions":[],"valueInputDefinitions":[],"valueOutputDefinitions":[],"title":null,"summary":null,"pan":{"x":0.0,"y":0.0},"zoom":1.0,"elements":[UNITS_AND_CONNECTIONS],"$version":"A"}}
```

#### Minimal Example (Start → Debug.Log)

```json
{"graph":{"variables":{"Kind":"Flow","collection":{"$content":[],"$version":"A"},"$version":"A"},"controlInputDefinitions":[],"controlOutputDefinitions":[],"valueInputDefinitions":[],"valueOutputDefinitions":[],"title":null,"summary":null,"pan":{"x":0.0,"y":0.0},"zoom":1.0,"elements":[{"coroutine":false,"defaultValues":{},"position":{"x":0.0,"y":0.0},"guid":"UUID1","$version":"A","$type":"Unity.VisualScripting.Start","$id":"1"},{"chainable":false,"parameterNames":["message"],"member":{"name":"Log","parameterTypes":["System.Object"],"targetType":"UnityEngine.Debug","targetTypeName":"UnityEngine.Debug","$version":"A"},"defaultValues":{},"position":{"x":300.0,"y":0.0},"guid":"UUID2","$version":"A","$type":"Unity.VisualScripting.InvokeMember","$id":"2"},{"type":"System.String","value":{"$content":"Hello!","$type":"System.String"},"defaultValues":{},"position":{"x":100.0,"y":150.0},"guid":"UUID3","$version":"A","$type":"Unity.VisualScripting.Literal","$id":"3"},{"sourceUnit":{"$ref":"1"},"sourceKey":"trigger","destinationUnit":{"$ref":"2"},"destinationKey":"enter","guid":"UUID4","$type":"Unity.VisualScripting.ControlConnection"},{"sourceUnit":{"$ref":"3"},"sourceKey":"output","destinationUnit":{"$ref":"2"},"destinationKey":"%message","guid":"UUID5","$type":"Unity.VisualScripting.ValueConnection"}],"$version":"A"}}
```

### Task 2: Assign a Graph to a GameObject

Assignment is **manual** in Unity Editor (no C# script needed):

1. Unity auto-imports the `.asset` file when the Editor gains focus
2. Select the target GameObject in the Scene
3. In Inspector → Add Component → **Script Machine** (or **State Machine**)
4. Set Source to **Graph**
5. Drag the `.asset` file into the **Graph** field

## Essential API Quick Reference

### Unit JSON Format

Every unit has these common fields:

```json
{
  "position": {"x": 0.0, "y": 0.0},
  "guid": "uuid-v4-here",
  "$version": "A",
  "$type": "Unity.VisualScripting.ClassName",
  "$id": "N"
}
```

Plus type-specific fields (see below).

### Creating Units

| Unit | $type | Key Ports | Type-Specific Fields |
|------|-------|-----------|---------------------|
| Start | `Unity.VisualScripting.Start` | `trigger` (out) | `coroutine`, `defaultValues: {}` |
| Update | `Unity.VisualScripting.Update` | `trigger` (out) | `coroutine`, `defaultValues: {}` |
| GetMember | `Unity.VisualScripting.GetMember` | `value` (out), `target` (in) | `member` object |
| SetMember | `Unity.VisualScripting.SetMember` | `assign`/`assigned` (ctrl), `input`/`output` (val) | `member` object |
| InvokeMember | `Unity.VisualScripting.InvokeMember` | `enter`/`exit` (ctrl), `%param` (val in), `result` (val out) | `member`, `chainable`, `parameterNames` |
| Literal | `Unity.VisualScripting.Literal` | `output` (out) | `type`, `value` |
| ScalarSum | `Unity.VisualScripting.ScalarSum` | `0`, `1` (in), `sum` (out) | `inputCount` |
| ScalarMultiply | `Unity.VisualScripting.ScalarMultiply` | `a`, `b` (in), `product` (out) | — |
| If | `Unity.VisualScripting.If` | `enter` (ctrl in), `condition` (val in), `ifTrue`/`ifFalse` (ctrl out) | — |
| Sequence | `Unity.VisualScripting.Sequence` | `enter` (ctrl in), `0`/`1`/... (ctrl out) | `outputCount` |
| GetVariable | `Unity.VisualScripting.GetVariable` | `value` (out) | `kind`, `defaultValues.name` |
| SetVariable | `Unity.VisualScripting.SetVariable` | `assign`/`assigned` (ctrl), `input`/`output` (val) | `kind`, `defaultValues.name` |

### Member Object

```json
{
  "name": "Log",
  "parameterTypes": ["System.Object"],
  "targetType": "UnityEngine.Debug",
  "targetTypeName": "UnityEngine.Debug",
  "$version": "A"
}
```

- `parameterTypes`: array for methods, `null` for properties/fields
- `targetType` and `targetTypeName` are always identical
- Static members: no `target` port. Instance members: `"target": null` in defaultValues

### InvokeMember Extras

```json
{
  "chainable": false,
  "parameterNames": ["param1", "param2"],
  "member": { ... },
  "defaultValues": {
    "target": null,
    "%param1": {"$content": DEFAULT, "$type": "System.Type"},
    "%param2": {"$content": DEFAULT, "$type": "System.Type"}
  }
}
```

- `chainable`: always `false` for standard methods
- `parameterNames`: array of parameter name strings
- Parameter defaults in `defaultValues` are prefixed with `%`
- Static methods: omit `"target"` from defaultValues

### Connections

```json
// Control: ControlOutput -> ControlInput
{"sourceUnit":{"$ref":"1"},"sourceKey":"trigger","destinationUnit":{"$ref":"2"},"destinationKey":"enter","guid":"UUID","$type":"Unity.VisualScripting.ControlConnection"}

// Value: ValueOutput -> ValueInput
{"sourceUnit":{"$ref":"3"},"sourceKey":"output","destinationUnit":{"$ref":"2"},"destinationKey":"%message","guid":"UUID","$type":"Unity.VisualScripting.ValueConnection"}
```

- Connections do NOT have `$id`
- ControlOutput allows only 1 outgoing connection (use `Sequence` to fan out)
- ValueInput allows only 1 incoming connection

### Typed Values

| Type | JSON Format |
|------|------------|
| int | `{"$content": 42, "$type": "System.Int32"}` |
| float | `{"$content": 3.14, "$type": "System.Single"}` |
| string | `{"$content": "text", "$type": "System.String"}` |
| bool | `{"$content": true, "$type": "System.Boolean"}` |
| Vector3 | `{"x": 1.0, "y": 2.0, "z": 3.0, "$type": "UnityEngine.Vector3"}` |
| Color | `{"r": 1.0, "g": 0.0, "b": 0.0, "a": 1.0, "$type": "UnityEngine.Color"}` |
| Enum | `{"$content": INT_VALUE, "$type": "Namespace.EnumType"}` |
| null | `null` |

### Position Layout

Recommended spacing: ~250px horizontal, ~150px vertical between related units.

## Critical Rules

1. **$id system**: Sequential integers as strings (`"1"`, `"2"`, ...) — units only, NOT connections
2. **$ref system**: `{"$ref": "1"}` references the unit with `$id: "1"`
3. **guid**: UUID v4 for EVERY unit AND connection (all lowercase)
4. **$version**: Always `"A"` on units, members, and collection objects
5. **JSON must be single-line**: No newlines inside the `_json` YAML value
6. **YAML single-quote escaping**: `'` inside JSON string values → `''`
7. **Parameter port keys**: Prefixed with `%` (e.g., `%message`, `%xAngle`)
8. **ScalarSum/GenericSum input keys**: `"0"`, `"1"` (index strings, NOT `a`/`b`)
9. **Sequence output keys**: `"0"`, `"1"`, `"2"` (index strings)
10. **Void methods**: No `result` port — do NOT wire it. `targetOutput` is also null for void instance methods.
11. **Static vs Instance**: Static members have no `target` port or defaultValues entry. Instance members have `"target": null` in defaultValues.
12. **Never use `?.` or `??` with `UnityEngine.Object` types** (applies if writing any helper C# code)

## Unit Verification Protocol (MANDATORY for undocumented units)

For any unit type NOT listed in `api_reference.md`, verify it against the actual package source before generating the graph. This prevents wrong class names and port keys.

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

- **Detailed API Reference**: See [references/api_reference.md](references/api_reference.md) for complete port names, unit types catalog, member objects, and connection format
- **JSON Graph Patterns**: See [references/code_patterns.md](references/code_patterns.md) for complete working JSON examples covering events, physics, variables, flow control, member access, and more
