# Unity Visual Scripting - API Reference

## Table of Contents

1. [Graph Asset Format](#1-graph-asset-format)
2. [Unit Types Catalog](#2-unit-types-catalog)
3. [Port Name Reference](#3-port-name-reference)
4. [Member Object Format](#4-member-object-format)
5. [Connection Format](#5-connection-format)
6. [Variable System](#6-variable-system)
7. [Assignment to GameObjects](#7-assignment-to-gameobjects)
8. [File Writing](#8-file-writing)

---

## 1. Graph Asset Format

### YAML Template

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
    _json: 'JSON_CONTENT'
    _objectReferences: []
```

- `m_Script` guid `95e66c6366d904e98bc83428217d4fd7` = ScriptGraphAsset (constant)
- JSON is a single-line string inside YAML single quotes
- Single quotes in JSON string values must be escaped as `''`

### JSON Structure

```json
{
  "graph": {
    "variables": {
      "Kind": "Flow",
      "collection": {"$content": [], "$version": "A"},
      "$version": "A"
    },
    "controlInputDefinitions": [],
    "controlOutputDefinitions": [],
    "valueInputDefinitions": [],
    "valueOutputDefinitions": [],
    "title": null,
    "summary": null,
    "pan": {"x": 0.0, "y": 0.0},
    "zoom": 1.0,
    "elements": [],
    "$version": "A"
  }
}
```

The `elements` array is a flat list of ALL units followed by ALL connections.

### $id / $ref System

- Every **unit** gets a sequential `$id` (string integer: `"1"`, `"2"`, ...)
- **Connections** reference units via `{"$ref": "ID"}` — connections themselves do NOT have `$id`
- Every unit AND connection gets a unique `guid` (UUID v4)

---

## 2. Unit Types Catalog

All classes in `Unity.VisualScripting` namespace. The `$type` column shows the JSON serialization type string.

### Event Units (Entry Points — no ControlInput)

| Class | $type | ControlOutput | ValueOutputs | Extra Fields |
|-------|-------|--------------|-------------|--------------|
| `Start` | `Unity.VisualScripting.Start` | `trigger` | — | `coroutine`, `defaultValues: {}` |
| `Update` | `Unity.VisualScripting.Update` | `trigger` | — | `coroutine`, `defaultValues: {}` |
| `FixedUpdate` | `Unity.VisualScripting.FixedUpdate` | `trigger` | — | `coroutine`, `defaultValues: {}` |
| `LateUpdate` | `Unity.VisualScripting.LateUpdate` | `trigger` | — | `coroutine`, `defaultValues: {}` |
| `OnEnable` | `Unity.VisualScripting.OnEnable` | `trigger` | — | `coroutine`, `defaultValues: {}` |
| `OnDisable` | `Unity.VisualScripting.OnDisable` | `trigger` | — | `coroutine`, `defaultValues: {}` |
| `OnDestroy` | `Unity.VisualScripting.OnDestroy` | `trigger` | — | `coroutine`, `defaultValues: {}` |
| `OnTriggerEnter` | `Unity.VisualScripting.OnTriggerEnter` | `trigger` | `collider` | `coroutine`, `defaultValues: {"target": null}` |
| `OnTriggerExit` | `Unity.VisualScripting.OnTriggerExit` | `trigger` | `collider` | `coroutine`, `defaultValues: {"target": null}` |
| `OnTriggerStay` | `Unity.VisualScripting.OnTriggerStay` | `trigger` | `collider` | `coroutine`, `defaultValues: {"target": null}` |
| `OnCollisionEnter` | `Unity.VisualScripting.OnCollisionEnter` | `trigger` | `collider`, `contacts`, `impulse`, `relativeVelocity` | `coroutine`, `defaultValues: {"target": null}` |
| `OnCollisionExit` | `Unity.VisualScripting.OnCollisionExit` | `trigger` | `collider` | `coroutine`, `defaultValues: {"target": null}` |
| `OnTriggerEnter2D` | `Unity.VisualScripting.OnTriggerEnter2D` | `trigger` | `collider` | `coroutine`, `defaultValues: {"target": null}` |
| `OnCollisionEnter2D` | `Unity.VisualScripting.OnCollisionEnter2D` | `trigger` | `collider` | `coroutine`, `defaultValues: {"target": null}` |
| `OnKeyboardInput` | `Unity.VisualScripting.OnKeyboardInput` | `trigger` | — | `coroutine`, `key` (KeyCode int), `action` (PressState int) |
| `CustomEvent` | `Unity.VisualScripting.CustomEvent` | `trigger` | `argument_0`..`argument_N` | `coroutine`, `argumentCount` |

### Member Access Units

| Class | $type | ControlIn | ControlOut | ValueIn | ValueOut | Extra Fields |
|-------|-------|-----------|-----------|---------|---------|--------------|
| `GetMember` | `Unity.VisualScripting.GetMember` | — | — | `target`* | `value` | `member` |
| `SetMember` | `Unity.VisualScripting.SetMember` | `assign` | `assigned` | `target`*, `input` | `output` | `member` |
| `InvokeMember` | `Unity.VisualScripting.InvokeMember` | `enter` | `exit` | `target`*, `%paramName` | `result`**, `targetOutput`** | `member`, `chainable`, `parameterNames` |

\* `target` only for instance members (omitted for static)
\** `result` only for non-void methods; `targetOutput` null for void instance methods

### Literal

| $type | Extra Fields | Port |
|-------|-------------|------|
| `Unity.VisualScripting.Literal` | `type`, `value` | `output` (ValueOutput) |

### Scalar Math

| Class | $type | ValueInput | ValueOutput | Extra Fields |
|-------|-------|-----------|------------|--------------|
| `ScalarSum` | `Unity.VisualScripting.ScalarSum` | `0`, `1` | `sum` | `inputCount` |
| `ScalarSubtract` | `Unity.VisualScripting.ScalarSubtract` | `minuend`, `subtrahend` | `difference` | — |
| `ScalarMultiply` | `Unity.VisualScripting.ScalarMultiply` | `a`, `b` | `product` | — |
| `ScalarDivide` | `Unity.VisualScripting.ScalarDivide` | `dividend`, `divisor` | `quotient` | — |
| `ScalarModulo` | `Unity.VisualScripting.ScalarModulo` | `dividend`, `divisor` | `remainder` | — |

**Note**: `ScalarAdd` does not exist — use `ScalarSum`. Input port keys for Sum units are index strings (`"0"`, `"1"`), not `a`/`b`.

### Generic Arithmetic

| Class | $type | ValueInput | ValueOutput | Extra Fields |
|-------|-------|-----------|------------|--------------|
| `GenericSum` | `Unity.VisualScripting.GenericSum` | `0`, `1` | `sum` | `inputCount` |
| `GenericSubtract` | `Unity.VisualScripting.GenericSubtract` | `minuend`, `subtrahend` | `difference` | — |
| `GenericMultiply` | `Unity.VisualScripting.GenericMultiply` | `a`, `b` | `product` | — |
| `GenericDivide` | `Unity.VisualScripting.GenericDivide` | `dividend`, `divisor` | `quotient` | — |

### Flow Control

| Class | $type | ControlIn | ControlOut | ValueIn | ValueOut | Extra Fields |
|-------|-------|----------|-----------|---------|---------|--------------|
| `If` | `Unity.VisualScripting.If` | `enter` | `ifTrue`, `ifFalse` | `condition` | — | — |
| `Sequence` | `Unity.VisualScripting.Sequence` | `enter` | `0`, `1`, ... | — | — | `outputCount` |
| `For` | `Unity.VisualScripting.For` | `enter` | `body`, `exit` | `firstIndex`, `lastIndex`, `step` | `currentIndex` | — |
| `ForEach` | `Unity.VisualScripting.ForEach` | `enter` | `body`, `exit` | `collection` | `currentItem`, `currentIndex`, `currentKey` | — |
| `While` | `Unity.VisualScripting.While` | `enter` | `body`, `exit` | `condition` | — | — |
| `Once` | `Unity.VisualScripting.Once` | `enter`, `reset` | `once`, `after` | — | — | — |
| `NullCheck` | `Unity.VisualScripting.NullCheck` | `enter` | `ifNotNull`, `ifNull` | `input` | — | — |
| `SwitchOnEnum` | `Unity.VisualScripting.SwitchOnEnum` | `enter` | dynamic `branches` | `enum` | — | — |
| `SelectUnit` | `Unity.VisualScripting.SelectUnit` | — | — | `condition`, `ifTrue`, `ifFalse` | `selection` | — |

`Sequence` output port keys: `"0"`, `"1"`, ... (index strings). Set `outputCount` (default 2, max 10).

### Variable Units

| Class | $type | ControlIn | ControlOut | ValueIn | ValueOut | Extra Fields |
|-------|-------|----------|-----------|---------|---------|--------------|
| `GetVariable` | `Unity.VisualScripting.GetVariable` | — | — | `name`, `@object`* | `value` | `kind` |
| `SetVariable` | `Unity.VisualScripting.SetVariable` | `assign` | `assigned` | `name`, `input`, `@object`* | `output` | `kind` |
| `IsVariableDefined` | `Unity.VisualScripting.IsVariableDefined` | — | — | `name`, `@object`* | `isDefined` | `kind` |

\* `@object` only when `kind == "Object"`

`kind` values: `"Graph"`, `"Object"`, `"Scene"`, `"Application"`, `"Saved"`, `"Flow"`

Variable name set in `defaultValues.name`: `{"$content": "varName", "$type": "System.String"}`

### Logic / Comparison

| Class | $type | ValueIn | ValueOut |
|-------|-------|---------|---------|
| `And` | `Unity.VisualScripting.And` | `a`, `b` | `result` |
| `Or` | `Unity.VisualScripting.Or` | `a`, `b` | `result` |
| `Negate` | `Unity.VisualScripting.Negate` | `input` | `output` |
| `Equal` | `Unity.VisualScripting.Equal` | `a`, `b` | `equal` |
| `NotEqual` | `Unity.VisualScripting.NotEqual` | `a`, `b` | `notEqual` |
| `Greater` | `Unity.VisualScripting.Greater` | `a`, `b` | `comparison` |
| `Less` | `Unity.VisualScripting.Less` | `a`, `b` | `comparison` |
| `GreaterOrEqual` | `Unity.VisualScripting.GreaterOrEqual` | `a`, `b` | `comparison` |
| `LessOrEqual` | `Unity.VisualScripting.LessOrEqual` | `a`, `b` | `comparison` |

### Time Units

| Class | $type | ControlIn | ControlOut | ValueIn | ValueOut |
|-------|-------|----------|-----------|---------|---------|
| `WaitForSecondsUnit` | `Unity.VisualScripting.WaitForSecondsUnit` | `enter` | `exit` | `seconds`, `unscaledTime` | — |
| `WaitUntilUnit` | `Unity.VisualScripting.WaitUntilUnit` | `enter` | `exit` | `condition` | — |
| `Cooldown` | `Unity.VisualScripting.Cooldown` | `enter`, `reset` | `tick`, `becameReady` | `seconds`, `unscaledTime` | `remaining` |

### Special Units

| Class | $type | Purpose |
|-------|-------|---------|
| `This` | `Unity.VisualScripting.This` | Reference to current GameObject. Port: `self` (ValueOutput) |
| `Formula` | `Unity.VisualScripting.Formula` | Math expression. Property: `formula` (string) |
| `TriggerCustomEvent` | `Unity.VisualScripting.TriggerCustomEvent` | Fires custom events. Property: `argumentCount` |

---

## 3. Port Name Reference

Port keys are the exact strings used in `sourceKey`/`destinationKey` of connections.

### Event Units

All event units: `trigger` (ControlOutput)

### GetMember

| Port | Type | Key |
|------|------|-----|
| `target` | ValueInput | `"target"` |
| `value` | ValueOutput | `"value"` |

### SetMember

| Port | Type | Key |
|------|------|-----|
| `assign` | ControlInput | `"assign"` |
| `assigned` | ControlOutput | `"assigned"` |
| `target` | ValueInput | `"target"` |
| `input` | ValueInput | `"input"` |
| `output` | ValueOutput | `"output"` |

### InvokeMember

| Port | Type | Key |
|------|------|-----|
| `enter` | ControlInput | `"enter"` |
| `exit` | ControlOutput | `"exit"` |
| `target` | ValueInput | `"target"` |
| parameter N | ValueInput | `"%paramName"` |
| `result` | ValueOutput | `"result"` |
| `targetOutput` | ValueOutput | `"targetOutput"` |

Parameter port keys are prefixed with `%` and match the `parameterNames` array (e.g., `%message`, `%xAngle`, `%value`).

**Note**: `targetOutput` is null for void instance methods. `result` does not exist for void methods.

### Literal

| Port | Type | Key |
|------|------|-----|
| `output` | ValueOutput | `"output"` |

### ScalarSum / GenericSum

| Port | Type | Key |
|------|------|-----|
| input 0 | ValueInput | `"0"` |
| input 1 | ValueInput | `"1"` |
| `sum` | ValueOutput | `"sum"` |

### ScalarMultiply

| Port | Type | Key |
|------|------|-----|
| `a` | ValueInput | `"a"` |
| `b` | ValueInput | `"b"` |
| `product` | ValueOutput | `"product"` |

### If

| Port | Type | Key |
|------|------|-----|
| `enter` | ControlInput | `"enter"` |
| `condition` | ValueInput | `"condition"` |
| `ifTrue` | ControlOutput | `"ifTrue"` |
| `ifFalse` | ControlOutput | `"ifFalse"` |

### For

| Port | Type | Key |
|------|------|-----|
| `enter` | ControlInput | `"enter"` |
| `body` | ControlOutput | `"body"` |
| `exit` | ControlOutput | `"exit"` |
| `firstIndex` | ValueInput | `"firstIndex"` |
| `lastIndex` | ValueInput | `"lastIndex"` |
| `step` | ValueInput | `"step"` |
| `currentIndex` | ValueOutput | `"currentIndex"` |

### Sequence

| Port | Type | Key |
|------|------|-----|
| `enter` | ControlInput | `"enter"` |
| output N | ControlOutput | `"0"`, `"1"`, etc. |

### Variable Units

| Port | Type | Key |
|------|------|-----|
| `value` (Get) | ValueOutput | `"value"` |
| `assign` (Set) | ControlInput | `"assign"` |
| `assigned` (Set) | ControlOutput | `"assigned"` |
| `input` (Set) | ValueInput | `"input"` |
| `output` (Set) | ValueOutput | `"output"` |

---

## 4. Member Object Format

The `member` field describes a C# member for `GetMember`, `SetMember`, `InvokeMember`.

### JSON Format

```json
{
  "name": "memberName",
  "parameterTypes": ["System.Type1", "System.Type2"],
  "targetType": "Full.Namespace.ClassName",
  "targetTypeName": "Full.Namespace.ClassName",
  "$version": "A"
}
```

- `parameterTypes`: array of type strings for methods, `null` for properties/fields
- `targetType` and `targetTypeName` are always identical

### Common Member Examples

#### Static Properties

```json
{"name": "deltaTime", "parameterTypes": null, "targetType": "UnityEngine.Time", "targetTypeName": "UnityEngine.Time", "$version": "A"}
{"name": "time", "parameterTypes": null, "targetType": "UnityEngine.Time", "targetTypeName": "UnityEngine.Time", "$version": "A"}
```

#### Instance Properties

```json
{"name": "position", "parameterTypes": null, "targetType": "UnityEngine.Transform", "targetTypeName": "UnityEngine.Transform", "$version": "A"}
{"name": "rotation", "parameterTypes": null, "targetType": "UnityEngine.Transform", "targetTypeName": "UnityEngine.Transform", "$version": "A"}
{"name": "gameObject", "parameterTypes": null, "targetType": "UnityEngine.Component", "targetTypeName": "UnityEngine.Component", "$version": "A"}
{"name": "name", "parameterTypes": null, "targetType": "UnityEngine.GameObject", "targetTypeName": "UnityEngine.GameObject", "$version": "A"}
{"name": "material", "parameterTypes": null, "targetType": "UnityEngine.Renderer", "targetTypeName": "UnityEngine.Renderer", "$version": "A"}
{"name": "color", "parameterTypes": null, "targetType": "UnityEngine.Material", "targetTypeName": "UnityEngine.Material", "$version": "A"}
```

#### Static Methods

```json
{"name": "Log", "parameterTypes": ["System.Object"], "targetType": "UnityEngine.Debug", "targetTypeName": "UnityEngine.Debug", "$version": "A"}
{"name": "LogWarning", "parameterTypes": ["System.Object"], "targetType": "UnityEngine.Debug", "targetTypeName": "UnityEngine.Debug", "$version": "A"}
{"name": "LogError", "parameterTypes": ["System.Object"], "targetType": "UnityEngine.Debug", "targetTypeName": "UnityEngine.Debug", "$version": "A"}
{"name": "GetKey", "parameterTypes": ["UnityEngine.KeyCode"], "targetType": "UnityEngine.Input", "targetTypeName": "UnityEngine.Input", "$version": "A"}
{"name": "GetKeyDown", "parameterTypes": ["UnityEngine.KeyCode"], "targetType": "UnityEngine.Input", "targetTypeName": "UnityEngine.Input", "$version": "A"}
{"name": "GetAxis", "parameterTypes": ["System.String"], "targetType": "UnityEngine.Input", "targetTypeName": "UnityEngine.Input", "$version": "A"}
{"name": "Find", "parameterTypes": ["System.String"], "targetType": "UnityEngine.GameObject", "targetTypeName": "UnityEngine.GameObject", "$version": "A"}
{"name": "Instantiate", "parameterTypes": ["UnityEngine.Object"], "targetType": "UnityEngine.Object", "targetTypeName": "UnityEngine.Object", "$version": "A"}
{"name": "Destroy", "parameterTypes": ["UnityEngine.Object"], "targetType": "UnityEngine.Object", "targetTypeName": "UnityEngine.Object", "$version": "A"}
{"name": "Distance", "parameterTypes": ["UnityEngine.Vector3", "UnityEngine.Vector3"], "targetType": "UnityEngine.Vector3", "targetTypeName": "UnityEngine.Vector3", "$version": "A"}
{"name": "Lerp", "parameterTypes": ["UnityEngine.Vector3", "UnityEngine.Vector3", "System.Single"], "targetType": "UnityEngine.Vector3", "targetTypeName": "UnityEngine.Vector3", "$version": "A"}
{"name": "Clamp", "parameterTypes": ["System.Single", "System.Single", "System.Single"], "targetType": "UnityEngine.Mathf", "targetTypeName": "UnityEngine.Mathf", "$version": "A"}
```

#### Instance Methods

```json
{"name": "Rotate", "parameterTypes": ["System.Single", "System.Single", "System.Single"], "targetType": "UnityEngine.Transform", "targetTypeName": "UnityEngine.Transform", "$version": "A"}
{"name": "Translate", "parameterTypes": ["UnityEngine.Vector3"], "targetType": "UnityEngine.Transform", "targetTypeName": "UnityEngine.Transform", "$version": "A"}
{"name": "LookAt", "parameterTypes": ["UnityEngine.Transform"], "targetType": "UnityEngine.Transform", "targetTypeName": "UnityEngine.Transform", "$version": "A"}
{"name": "SetActive", "parameterTypes": ["System.Boolean"], "targetType": "UnityEngine.GameObject", "targetTypeName": "UnityEngine.GameObject", "$version": "A"}
{"name": "AddForce", "parameterTypes": ["UnityEngine.Vector3"], "targetType": "UnityEngine.Rigidbody", "targetTypeName": "UnityEngine.Rigidbody", "$version": "A"}
{"name": "SetTrigger", "parameterTypes": ["System.String"], "targetType": "UnityEngine.Animator", "targetTypeName": "UnityEngine.Animator", "$version": "A"}
{"name": "SetBool", "parameterTypes": ["System.String", "System.Boolean"], "targetType": "UnityEngine.Animator", "targetTypeName": "UnityEngine.Animator", "$version": "A"}
{"name": "SetFloat", "parameterTypes": ["System.String", "System.Single"], "targetType": "UnityEngine.Animator", "targetTypeName": "UnityEngine.Animator", "$version": "A"}
{"name": "Play", "parameterTypes": [], "targetType": "UnityEngine.AudioSource", "targetTypeName": "UnityEngine.AudioSource", "$version": "A"}
{"name": "PlayOneShot", "parameterTypes": ["UnityEngine.AudioClip"], "targetType": "UnityEngine.AudioSource", "targetTypeName": "UnityEngine.AudioSource", "$version": "A"}
```

#### System Methods

```json
{"name": "ToString", "parameterTypes": [], "targetType": "System.Object", "targetTypeName": "System.Object", "$version": "A"}
{"name": "Concat", "parameterTypes": ["System.String", "System.String"], "targetType": "System.String", "targetTypeName": "System.String", "$version": "A"}
{"name": "Parse", "parameterTypes": ["System.String"], "targetType": "System.Int32", "targetTypeName": "System.Int32", "$version": "A"}
{"name": "GetType", "parameterTypes": [], "targetType": "System.Object", "targetTypeName": "System.Object", "$version": "A"}
{"name": "CreateInstance", "parameterTypes": ["System.Type", "System.Int32"], "targetType": "System.Array", "targetTypeName": "System.Array", "$version": "A"}
{"name": "SetValue", "parameterTypes": ["System.Object", "System.Int32"], "targetType": "System.Array", "targetTypeName": "System.Array", "$version": "A"}
```

### Static vs Instance

- **Static**: no `target` port, no `"target"` in defaultValues (e.g., `Time.deltaTime`, `Debug.Log`)
- **Instance**: has `target` port, `"target": null` in defaultValues (e.g., `Transform.position`, `Transform.Rotate`)
- When `target` is unconnected on a ScriptMachine, it auto-resolves to the component on the owning GameObject

---

## 5. Connection Format

### Control Connection

```json
{
  "sourceUnit": {"$ref": "1"},
  "sourceKey": "trigger",
  "destinationUnit": {"$ref": "2"},
  "destinationKey": "enter",
  "guid": "UUID_HERE",
  "$type": "Unity.VisualScripting.ControlConnection"
}
```

- ControlOutput → ControlInput
- ControlOutput: **single** outgoing connection only (use `Sequence` to fan out)
- ControlInput: multiple incoming connections allowed
- No `$id` on connections

### Value Connection

```json
{
  "sourceUnit": {"$ref": "3"},
  "sourceKey": "output",
  "destinationUnit": {"$ref": "2"},
  "destinationKey": "%message",
  "guid": "UUID_HERE",
  "$type": "Unity.VisualScripting.ValueConnection"
}
```

- ValueOutput → ValueInput
- ValueInput: **single** incoming connection only
- ValueOutput: multiple outgoing connections allowed
- No `$id` on connections

---

## 6. Variable System

### Declaring Graph Variables

Add variables to the JSON root `graph.variables.collection.$content` array:

```json
"variables": {
  "Kind": "Flow",
  "collection": {
    "$content": [
      {"name": "health", "value": {"$content": 100, "$type": "System.Int32"}, "$version": "A"},
      {"name": "speed", "value": {"$content": 5.5, "$type": "System.Single"}, "$version": "A"},
      {"name": "name", "value": {"$content": "Player", "$type": "System.String"}, "$version": "A"},
      {"name": "isAlive", "value": {"$content": true, "$type": "System.Boolean"}, "$version": "A"},
      {"name": "dir", "value": {"x": 0.0, "y": 0.0, "z": 0.0, "$type": "UnityEngine.Vector3"}, "$version": "A"}
    ],
    "$version": "A"
  },
  "$version": "A"
}
```

### VariableKind Values

| Kind String | Scope |
|-------------|-------|
| `"Flow"` | Current execution only |
| `"Graph"` | Current graph instance |
| `"Object"` | Per GameObject (needs Variables component) |
| `"Scene"` | Per scene |
| `"Application"` | Cross-scene, until app closes |
| `"Saved"` | Persistent (PlayerPrefs) |

### Variable Unit JSON

```json
{
  "kind": "Graph",
  "defaultValues": {
    "name": {"$content": "health", "$type": "System.String"}
  },
  "position": {"x": 0.0, "y": 0.0},
  "guid": "UUID_HERE",
  "$version": "A",
  "$type": "Unity.VisualScripting.GetVariable",
  "$id": "N"
}
```

---

## 7. Assignment to GameObjects

After generating a `.asset` file, assignment is manual in the Unity Editor:

1. Place the `.asset` file in the project (e.g., `Assets/VisualScripting/`)
2. Unity auto-imports the asset when the Editor gains focus
3. Select the target GameObject in the Scene
4. In the Inspector, add a **Script Machine** component (or **State Machine** for StateGraphAsset)
5. Set **Source** to **Graph** (Macro)
6. Drag the `.asset` file into the **Graph** field

No C# editor script is needed for assignment.

---

## 8. File Writing

### Where to Save

```
Assets/VisualScripting/{GraphName}.asset
```

Create the directory first if it does not exist:
```bash
mkdir -p Assets/VisualScripting
```

### Generating the File

1. Build the elements array (units + connections) with proper `$id`/`$ref` references
2. Construct the full JSON graph object
3. Minify the JSON to a single line (no newlines within the JSON)
4. Wrap in the YAML boilerplate template
5. Write to `.asset` file

### UUID Generation

Every unit and connection needs a unique UUID v4:
```bash
uuidgen | tr '[:upper:]' '[:lower:]'
```

### Common Pitfalls

1. **JSON must be single-line** — no newlines inside the `_json` YAML value
2. **YAML single-quote escaping** — single quotes in JSON string values become `''` (e.g., `it''s`)
3. **$id must be unique** — use sequential integers as strings (`"1"`, `"2"`, ...)
4. **guid must be unique** — every unit AND connection needs its own UUID v4
5. **Port keys are case-sensitive** — `"trigger"` not `"Trigger"`, `"%message"` not `"message"`
6. **InvokeMember parameter keys need %** — `"%message"` not `"message"` in connection destinationKey
7. **ScalarSum input keys are index strings** — `"0"`, `"1"` (NOT `"a"`, `"b"`)
8. **Connections do NOT have $id** — only units get `$id`
9. **Static members have no target port** — do not include `"target"` in defaultValues
10. **Void methods have no result port** — do not wire `"result"` from void InvokeMember
11. **All units need $version: "A"** — and all member objects too
12. **Position layout** — ~250px horizontal spacing, ~150px vertical between related units
