# Unity Visual Scripting - API Reference

## Table of Contents

1. [Graph Asset Types](#1-graph-asset-types)
2. [Unit Types Catalog](#2-unit-types-catalog)
3. [Port Name Reference](#3-port-name-reference)
4. [Member Class](#4-member-class)
5. [Connection API](#5-connection-api)
6. [Variable System](#6-variable-system)
7. [Machine Components](#7-machine-components)
8. [Asset Management](#8-asset-management)

---

## 1. Graph Asset Types

| Asset Type | Internal Graph | Machine Component | Use Case |
|-----------|---------------|-------------------|----------|
| `ScriptGraphAsset` | `FlowGraph` | `ScriptMachine` | Sequential flow-based logic |
| `StateGraphAsset` | `StateGraph` | `StateMachine` | State machine logic |

### FlowGraph Factory Methods

```csharp
FlowGraph.WithStartUpdate()   // Start + Update events (standard gameplay)
FlowGraph.WithInputOutput()   // GraphInput + GraphOutput (subgraphs)
StateGraph.WithStart()        // Initial state graph
```

### Creating Assets

```csharp
// Script Graph (auto-initializes FlowGraph)
var graphAsset = ScriptableObject.CreateInstance<ScriptGraphAsset>();
var graph = graphAsset.graph; // pre-initialized FlowGraph

// State Graph
var stateAsset = ScriptableObject.CreateInstance<StateGraphAsset>();
stateAsset.graph = StateGraph.WithStart();
```

---

## 2. Unit Types Catalog

All classes in `Unity.VisualScripting` namespace.

### Event Units (Entry Points - no ControlInput)

| Class | ControlOutput | ValueOutputs | Notes |
|-------|--------------|-------------|-------|
| `Start` | `trigger` | - | Unity Start lifecycle |
| `Update` | `trigger` | - | Every frame |
| `FixedUpdate` | `trigger` | - | Fixed timestep |
| `LateUpdate` | `trigger` | - | After all Updates |
| `OnEnable` | `trigger` | - | Object enabled |
| `OnDisable` | `trigger` | - | Object disabled |
| `OnDestroy` | `trigger` | - | Object destroyed |
| `OnTriggerEnter` | `trigger` | `collider` | 3D trigger |
| `OnTriggerExit` | `trigger` | `collider` | 3D trigger end |
| `OnTriggerStay` | `trigger` | `collider` | 3D trigger stay |
| `OnCollisionEnter` | `trigger` | `collider`, `contacts`, `impulse`, `relativeVelocity` | 3D collision |
| `OnCollisionExit` | `trigger` | `collider` | 3D collision end |
| `OnTriggerEnter2D` | `trigger` | `collider` | 2D trigger |
| `OnCollisionEnter2D` | `trigger` | `collider` | 2D collision |
| `OnKeyboardInput` | `trigger` | - | Properties: `key` (KeyCode), `action` (PressState) |
| `CustomEvent` | `trigger` | `arg_0`..`arg_N` | Set `argumentCount` property |

### Member Access Units

| Class | Constructor | ControlIn | ControlOut | ValueIn | ValueOut |
|-------|-----------|-----------|-----------|---------|---------|
| `GetMember` | `new GetMember(member)` | - | - | `target`* | `value` |
| `SetMember` | `new SetMember(member)` | `assign` | `assigned` | `target`*, `input` | `output` |
| `InvokeMember` | `new InvokeMember(member)` | `enter` | `exit` | `target`*, `inputParameters[n]` | `result`**, `outputParameters[n]` |

\* `target` only for instance members (omitted for static)
\** `result` only for non-void methods

### Literal

```csharp
new Literal(typeof(float), 10f)        // float
new Literal(typeof(int), 42)           // int
new Literal(typeof(string), "Hello")   // string
new Literal(typeof(bool), true)        // bool
new Literal(typeof(Vector3), new Vector3(1, 2, 3))   // Vector3
new Literal(typeof(Color), Color.red)  // Color
new Literal(typeof(KeyCode), KeyCode.Space) // Enum
```

Port: `output` (ValueOutput)

### Scalar Math

| Class | ValueInput | ValueOutput |
|-------|-----------|------------|
| `ScalarAdd` | `a`, `b` | `sum` |
| `ScalarSubtract` | `minuend`, `subtrahend` | `difference` |
| `ScalarMultiply` | `a`, `b` | `product` |
| `ScalarDivide` | `dividend`, `divisor` | `quotient` |
| `ScalarModulo` | `dividend`, `divisor` | `remainder` |

Multi-input variants: `ScalarSum`, `ScalarMultiply` (set `inputCount` property)

### Generic Arithmetic

| Class | ValueInput | ValueOutput |
|-------|-----------|------------|
| `GenericSum` | `a`, `b` | `sum` |
| `GenericSubtract` | `minuend`, `subtrahend` | `difference` |
| `GenericMultiply` | `a`, `b` | `product` |
| `GenericDivide` | `dividend`, `divisor` | `quotient` |

### Flow Control

| Class | ControlIn | ControlOut | ValueIn | ValueOut |
|-------|----------|-----------|---------|---------|
| `If` | `enter` | `ifTrue`, `ifFalse` | `condition` (bool) | - |
| `Sequence` | `enter` | `multiOutputs[0..N]` | - | - |
| `For` | `enter` | `body`, `exit` | `firstIndex`, `lastIndex`, `step` | `currentIndex` |
| `ForEach` | `enter` | `body`, `exit` | `collection` | `currentItem`, `currentIndex`, `currentKey` |
| `While` | `enter` | `body`, `exit` | `condition` (bool) | - |
| `Once` | `enter`, `reset` | `once`, `after` | - | - |
| `NullCheck` | `enter` | `ifNotNull`, `ifNull` | `input` | - |
| `SwitchOnEnum` | `enter` | dynamic `branches` | `enum` | - |
| `SelectUnit` | - | - | `condition`, `ifTrue`, `ifFalse` | `selection` |

`Sequence`: set `outputCount` property (default 2, max 10)

### Variable Units

| Class | ControlIn | ControlOut | ValueIn | ValueOut | Properties |
|-------|----------|-----------|---------|---------|-----------|
| `GetVariable` | - | - | `name`, `@object`* | `value` | `kind` (set before Add), `defaultValues["name"]` (set after Add) |
| `SetVariable` | `assign` | `assigned` | `name`, `input`, `@object`* | `output` | `kind` (set before Add), `defaultValues["name"]` (set after Add) |
| `IsVariableDefined` | - | - | `name`, `@object`* | `isDefined` (bool) | `kind` (set before Add), `defaultValues["name"]` (set after Add) |

\* `@object` only when `kind == VariableKind.Object`

### Logic / Comparison

| Class | ValueIn | ValueOut |
|-------|---------|---------|
| `And` | `a`, `b` | `result` (bool) |
| `Or` | `a`, `b` | `result` (bool) |
| `Negate` | `input` | `output` (bool) |
| `Equal` | `a`, `b` | `comparison` (bool) |
| `NotEqual` | `a`, `b` | `comparison` (bool) |
| `Greater` | `a`, `b` | `comparison` (bool) |
| `Less` | `a`, `b` | `comparison` (bool) |
| `GreaterOrEqual` | `a`, `b` | `comparison` (bool) |
| `LessOrEqual` | `a`, `b` | `comparison` (bool) |

### Time Units

| Class | ControlIn | ControlOut | ValueIn | ValueOut |
|-------|----------|-----------|---------|---------|
| `WaitForSecondsUnit` | `enter` | `exit` | `seconds` (float), `unscaledTime` (bool) | - |
| `WaitUntilUnit` | `enter` | `exit` | `condition` (bool) | - |
| `Cooldown` | `enter`, `reset` | `tick`, `becameReady` | `seconds`, `unscaledTime` | `remaining` |

### Special Units

| Class | Purpose |
|-------|---------|
| `SubgraphUnit` | Nests a FlowGraph (`new SubgraphUnit(scriptGraphAsset)`) |
| `GraphInput` | Input interface inside subgraphs |
| `GraphOutput` | Output interface inside subgraphs |
| `StateUnit` | Embeds a StateGraph in a FlowGraph |
| `TriggerCustomEvent` | Fires custom events (set `argumentCount`) |
| `This` | Reference to current GameObject (`self` ValueOutput) |
| `Formula` | Math expression (`formula` string property) |

---

## 3. Port Name Reference

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
| `inputParameters[n]` | ValueInput | `"%paramName"` or indexed |
| `result` | ValueOutput | `"result"` |
| `targetOutput` | ValueOutput | `"targetOutput"` |
| `outputParameters[n]` | ValueOutput | indexed |

### Literal

| Port | Type | Key |
|------|------|-----|
| `output` | ValueOutput | `"output"` |

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
| `multiOutputs[n]` | ControlOutput | `"0"`, `"1"`, etc. |

### Variable Units

| Port | Type | Key |
|------|------|-----|
| `value` (Get) | ValueOutput | `"value"` |
| `assign` (Set) | ControlInput | `"assign"` |
| `assigned` (Set) | ControlOutput | `"assigned"` |
| `input` (Set) | ValueInput | `"input"` |
| `output` (Set) | ValueOutput | `"output"` |

---

## 4. Member Class

Describes a C# member for reflection-based access by `GetMember`, `SetMember`, `InvokeMember`.

### Constructors

```csharp
// Property or field (auto-detected)
new Member(typeof(Time), nameof(Time.deltaTime))       // static
new Member(typeof(Transform), "position")               // instance

// Method (disambiguate overloads with param types)
new Member(typeof(Debug), "Log", new[] { typeof(object) })
new Member(typeof(Transform), "Rotate", new[] { typeof(float), typeof(float), typeof(float) })
new Member(typeof(Transform), "Translate", new[] { typeof(Vector3) })
new Member(typeof(Input), "GetKey", new[] { typeof(KeyCode) })
new Member(typeof(Input), "GetAxis", new[] { typeof(string) })
new Member(typeof(Physics), "Raycast", new[] { typeof(Vector3), typeof(Vector3), typeof(float) })
new Member(typeof(GameObject), "SetActive", new[] { typeof(bool) })
new Member(typeof(GameObject), "Find", new[] { typeof(string) })
new Member(typeof(Object), "Instantiate", new[] { typeof(Object) })
new Member(typeof(Object), "Destroy", new[] { typeof(Object) })
new Member(typeof(Animator), "SetTrigger", new[] { typeof(string) })
new Member(typeof(AudioSource), "PlayOneShot", new[] { typeof(AudioClip) })
new Member(typeof(Mathf), "Clamp", new[] { typeof(float), typeof(float), typeof(float) })
new Member(typeof(Vector3), "Distance", new[] { typeof(Vector3), typeof(Vector3) })
new Member(typeof(Vector3), "Lerp", new[] { typeof(Vector3), typeof(Vector3), typeof(float) })
```

### Static vs Instance

- **Static**: no `target` port (e.g., `Time.deltaTime`, `Debug.Log`, `Input.GetKey`)
- **Instance**: has `target` port (e.g., `Transform.position`, `Transform.Rotate`)
- When `target` is unconnected on a ScriptMachine, it auto-resolves to the component on the owning GameObject

---

## 5. Connection API

### Control Connections

```csharp
// ControlOutput -> ControlInput
graph.controlConnections.Add(new ControlConnection(source.trigger, dest.enter));
```

- ControlOutput: **single** outgoing connection only (use `Sequence` to fan out)
- ControlInput: multiple incoming connections allowed

### Value Connections

```csharp
// ValueOutput -> ValueInput
graph.valueConnections.Add(new ValueConnection(source.output, dest.input));
```

- ValueInput: **single** incoming connection only
- ValueOutput: multiple outgoing connections allowed

### Alternative

```csharp
source.trigger.ConnectToValid(dest.enter);
source.output.ConnectToValid(dest.input);
```

---

## 6. Variable System

### Declaring Graph Variables

```csharp
graph.variables.Set("health", 100);
graph.variables.Set("speed", 5.5f);
graph.variables.Set("name", "Player");
graph.variables.Set("isAlive", true);
graph.variables.Set("dir", Vector3.zero);
```

### VariableKind Enum

| Kind | Scope |
|------|-------|
| `VariableKind.Flow` | Current execution only |
| `VariableKind.Graph` | Current graph instance |
| `VariableKind.Object` | Per GameObject (needs Variables component) |
| `VariableKind.Scene` | Per scene |
| `VariableKind.Application` | Cross-scene, until app closes |
| `VariableKind.Saved` | Persistent (PlayerPrefs) |

### Runtime C# Access

```csharp
Variables.Object(gameObject).Set("health", 100);
int health = (int)Variables.Object(gameObject).Get("health");
Variables.ActiveScene.Set("score", 0);
Variables.Application.Set("highScore", 9999);
Variables.Saved.Set("bestTime", 120.5f);
```

---

## 7. Machine Components

### ScriptMachine (FlowGraph)

```csharp
var machine = go.AddComponent<ScriptMachine>();
machine.nest.source = GraphSource.Macro;
machine.nest.macro = graphAsset;  // ScriptGraphAsset
EditorUtility.SetDirty(go);
```

### StateMachine (StateGraph)

```csharp
var machine = go.AddComponent<StateMachine>();
machine.nest.source = GraphSource.Macro;
machine.nest.macro = stateAsset;  // StateGraphAsset
EditorUtility.SetDirty(go);
```

### GraphSource

| Source | Storage | When to Use |
|--------|---------|-------------|
| `GraphSource.Macro` | External `.asset` file | Reusable across objects |
| `GraphSource.Embed` | Serialized in component | Unique to object, supports scene refs |

---

## 8. Asset Management

```csharp
// Create folder
if (!AssetDatabase.IsValidFolder("Assets/VisualScripting"))
    AssetDatabase.CreateFolder("Assets", "VisualScripting");

// Create asset
AssetDatabase.CreateAsset(graphAsset, "Assets/VisualScripting/MyGraph.asset");
AssetDatabase.SaveAssets();
AssetDatabase.Refresh();

// Load existing
var asset = AssetDatabase.LoadAssetAtPath<ScriptGraphAsset>(path);

// Modify existing
EditorUtility.SetDirty(asset);
AssetDatabase.SaveAssets();

// Undo support
Undo.RecordObject(graphAsset, "Modify graph");

// Save specific asset only (Unity 2020.3+)
AssetDatabase.SaveAssetIfDirty(asset);
```

### Common Pitfalls

1. Always call `EditorUtility.SetDirty()` + `AssetDatabase.SaveAssets()` after modifications
2. Asset path must end in `.asset` and be relative to project root (`Assets/...`)
3. Port access works after `graph.units.Add(unit)` (unit must be added first)
4. ControlOutput supports only 1 connection - use `Sequence` to fan out
5. Never reference `UnityEditor` types in runtime graphs (causes build errors)
6. All editor API calls must run on the main Unity thread
7. Variable units have NO `defaultName` property — set `kind` before `graph.units.Add()`, then set `defaultValues["name"]` after Add
8. Generic math units (`GenericMultiply`, `GenericSum`, etc.) use same port names as scalar versions (`product`, `sum`, `difference`, `quotient`), NOT `result`
