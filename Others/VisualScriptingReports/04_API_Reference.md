# Unity Visual Scripting - Programmatic Graph Creation API Reference

A practical reference for creating Unity Visual Scripting graphs programmatically via C# editor scripts. Designed for use by AI agent skills and editor tool authors.

---

## Table of Contents

1. [Quick Start Pattern](#1-quick-start-pattern)
2. [ScriptGraphAsset Creation and Saving](#2-scriptgraphasset-creation-and-saving)
3. [FlowGraph Manipulation](#3-flowgraph-manipulation)
4. [Port System](#4-port-system)
5. [Connection API](#5-connection-api)
6. [Member Class for Reflection-Based Access](#6-member-class-for-reflection-based-access)
7. [Unit Types Quick Reference](#7-unit-types-quick-reference)
8. [Graph Variables API](#8-graph-variables-api)
9. [ScriptMachine / StateMachine Component Setup](#9-scriptmachine--statemachine-component-setup)
10. [Asset Management](#10-asset-management)
11. [Common Patterns with Code Examples](#11-common-patterns-with-code-examples)
12. [Port Name Reference](#12-port-name-reference)
13. [Error Handling and Validation](#13-error-handling-and-validation)

---

## 1. Quick Start Pattern

The minimal, proven pattern for creating a Visual Scripting graph programmatically (based on the working `CreateRotateGraph.cs` sample):

```csharp
#if UNITY_EDITOR
using UnityEditor;
using UnityEngine;
using Unity.VisualScripting;

public static class MyGraphCreator
{
    [MenuItem("Tools/Create My Graph")]
    public static void Create()
    {
        // 1. Create asset (graph is auto-created)
        var graphAsset = ScriptableObject.CreateInstance<ScriptGraphAsset>();
        var graph = graphAsset.graph;

        // 2. Create and add units
        var onUpdate = new Update();
        graph.units.Add(onUpdate);
        onUpdate.position = new Vector2(-300, 0);

        // 3. Create connections
        // graph.controlConnections.Add(new ControlConnection(source, dest));
        // graph.valueConnections.Add(new ValueConnection(source, dest));

        // 4. Save
        AssetDatabase.CreateAsset(graphAsset, "Assets/MyGraph.asset");
        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();
    }
}
#endif
```

**Key insight**: When you call `ScriptableObject.CreateInstance<ScriptGraphAsset>()`, the `graph` property is already initialized with an empty `FlowGraph`. You access it via `graphAsset.graph`.

---

## 2. ScriptGraphAsset Creation and Saving

### Creating a New ScriptGraphAsset

```csharp
// Method 1: Empty graph (auto-initialized)
var graphAsset = ScriptableObject.CreateInstance<ScriptGraphAsset>();
var graph = graphAsset.graph; // FlowGraph is already created

// Method 2: Assign a pre-built graph
var graphAsset = ScriptableObject.CreateInstance<ScriptGraphAsset>();
graphAsset.graph = FlowGraph.WithStartUpdate(); // Replaces the default graph
```

### Factory Methods

```csharp
// FlowGraph with Start + Update event units (standard for gameplay graphs)
FlowGraph.WithStartUpdate()
// Internally: new Start() at (-204, -144), new Update() at (-204, 60)

// FlowGraph with GraphInput + GraphOutput (for subgraphs)
FlowGraph.WithInputOutput()
// Internally: new GraphInput() at (-250, -30), new GraphOutput() at (105, -30)
```

### Saving to Disk

```csharp
// Ensure folder exists
if (!AssetDatabase.IsValidFolder("Assets/VisualScripting"))
    AssetDatabase.CreateFolder("Assets", "VisualScripting");

// Save the asset
AssetDatabase.CreateAsset(graphAsset, "Assets/VisualScripting/MyGraph.asset");
AssetDatabase.SaveAssets();
AssetDatabase.Refresh();
```

### StateGraphAsset

```csharp
var stateAsset = ScriptableObject.CreateInstance<StateGraphAsset>();
stateAsset.graph = StateGraph.WithStart();
AssetDatabase.CreateAsset(stateAsset, "Assets/MyStateGraph.asset");
AssetDatabase.SaveAssets();
```

---

## 3. FlowGraph Manipulation

### Core Properties

| Property | Type | Description |
|----------|------|-------------|
| `graph.units` | `GraphElementCollection<IUnit>` | All units (nodes) in the graph |
| `graph.controlConnections` | Collection of `ControlConnection` | Execution flow wires |
| `graph.valueConnections` | Collection of `ValueConnection` | Data flow wires |
| `graph.variables` | `VariableDeclarations` | Graph-level variable declarations |

### Adding Units

```csharp
// Create unit, add to graph, set position
var unit = new Update();
graph.units.Add(unit);
unit.position = new Vector2(-300, 0);

// Position MUST be set AFTER adding to graph (for proper initialization)
// Recommended spacing: 200-300px horizontal, 150-200px vertical
```

### Removing Units

```csharp
graph.units.Remove(unit);
```

---

## 4. Port System

### Port Types

| Port Class | Direction | Purpose | Multiple Connections? |
|------------|-----------|---------|----------------------|
| `ControlInput` | Incoming | Receives execution flow | Yes (many sources) |
| `ControlOutput` | Outgoing | Emits execution flow | **No** (single dest) |
| `ValueInput` | Incoming | Receives a data value | **No** (single source) |
| `ValueOutput` | Outgoing | Provides a data value | Yes (many dests) |

### Accessing Ports

Ports are accessed as **typed properties** on units after the unit is added to a graph:

```csharp
// Event units
var start = new Start();
graph.units.Add(start);
start.trigger          // ControlOutput

var update = new Update();
graph.units.Add(update);
update.trigger         // ControlOutput

// Literal
var lit = new Literal(typeof(float), 1.0f);
graph.units.Add(lit);
lit.output             // ValueOutput

// GetMember
var get = new GetMember(new Member(typeof(Time), nameof(Time.deltaTime)));
graph.units.Add(get);
get.value              // ValueOutput
get.target             // ValueInput (only for instance members, not static)

// SetMember
var set = new SetMember(new Member(typeof(Transform), "position"));
graph.units.Add(set);
set.assign             // ControlInput (named "assign")
set.assigned           // ControlOutput (named "assigned")
set.input              // ValueInput (value to set)
set.output             // ValueOutput (the set value)
set.target             // ValueInput (instance)

// InvokeMember
var invoke = new InvokeMember(new Member(typeof(Transform), "Rotate",
    new[] { typeof(float), typeof(float), typeof(float) }));
graph.units.Add(invoke);
invoke.enter                 // ControlInput
invoke.exit                  // ControlOutput
invoke.target                // ValueInput (instance, omitted for static)
invoke.inputParameters[0]    // ValueInput (1st parameter: xAngle)
invoke.inputParameters[1]    // ValueInput (2nd parameter: yAngle)
invoke.inputParameters[2]    // ValueInput (3rd parameter: zAngle)
invoke.result                // ValueOutput (return value, null for void)
invoke.targetOutput          // ValueOutput (for chaining)
invoke.outputParameters[n]   // ValueOutput (for out/ref parameters)

// ScalarMultiply
var mul = new ScalarMultiply();
graph.units.Add(mul);
mul.a                  // ValueInput
mul.b                  // ValueInput
mul.product            // ValueOutput

// If (Branch)
var ifUnit = new If();
graph.units.Add(ifUnit);
ifUnit.enter           // ControlInput
ifUnit.condition       // ValueInput (bool)
ifUnit.ifTrue          // ControlOutput
ifUnit.ifFalse         // ControlOutput
```

### Port Access via String Keys

Ports can also be accessed via string-indexed collections:

```csharp
unit.controlInputs["enter"]
unit.controlOutputs["trigger"]
unit.valueInputs["target"]
unit.valueOutputs["value"]
```

**Important**: Use typed property access (e.g., `start.trigger`) when available. It is safer and compile-time checked.

---

## 5. Connection API

### Control Connections (Execution Flow)

A `ControlConnection` links a `ControlOutput` to a `ControlInput`:

```csharp
// Direct collection add (recommended, used in sample code)
graph.controlConnections.Add(new ControlConnection(
    sourceUnit.trigger,    // ControlOutput
    destUnit.enter         // ControlInput
));
```

**Rules**:
- A `ControlOutput` can only have **one** outgoing connection. Adding a second silently disconnects the first.
- A `ControlInput` can receive from **multiple** `ControlOutput` sources.

### Value Connections (Data Flow)

A `ValueConnection` links a `ValueOutput` to a `ValueInput`:

```csharp
// Direct collection add (recommended, used in sample code)
graph.valueConnections.Add(new ValueConnection(
    sourceUnit.output,     // ValueOutput
    destUnit.input         // ValueInput
));
```

**Rules**:
- A `ValueInput` can only have **one** incoming connection. Adding a second silently disconnects the first.
- A `ValueOutput` can connect to **multiple** `ValueInput` destinations.
- Type compatibility is checked between source and destination ports.

### Alternative: ConnectToValid

```csharp
// Also works but less common in sample code
sourceUnit.trigger.ConnectToValid(destUnit.enter);
sourceUnit.output.ConnectToValid(destUnit.input);
```

### Proven Connection Pattern (from CreateRotateGraph.cs)

```csharp
// Control flow: Update -> Rotate
graph.controlConnections.Add(new ControlConnection(onUpdate.trigger, rotate.enter));

// Value flow: Literal -> Multiply input
graph.valueConnections.Add(new ValueConnection(xSpeed.output, multiplyX.a));
graph.valueConnections.Add(new ValueConnection(getDeltaTime.value, multiplyX.b));

// Value flow: Multiply result -> InvokeMember parameter
graph.valueConnections.Add(new ValueConnection(multiplyX.product, rotate.inputParameters[0]));
```

---

## 6. Member Class for Reflection-Based Access

The `Member` class describes a C# member (field, property, method, constructor) to access via reflection.

### Constructors

```csharp
// Field or property (auto-detected)
new Member(typeof(Time), nameof(Time.deltaTime))      // static property
new Member(typeof(Transform), "position")               // instance property
new Member(typeof(Rigidbody), "mass")                   // instance property

// Method without overload disambiguation
new Member(typeof(Debug), "Log")

// Method WITH overload disambiguation (recommended for methods)
new Member(typeof(Debug), "Log", new[] { typeof(object) })
new Member(typeof(Transform), "Rotate", new[] { typeof(float), typeof(float), typeof(float) })
new Member(typeof(Transform), "Translate", new[] { typeof(Vector3) })
new Member(typeof(Vector3), "Distance", new[] { typeof(Vector3), typeof(Vector3) })
new Member(typeof(Mathf), "Clamp", new[] { typeof(float), typeof(float), typeof(float) })
new Member(typeof(GameObject), "Find", new[] { typeof(string) })
new Member(typeof(Object), "Instantiate", new[] { typeof(Object) })
new Member(typeof(Object), "Destroy", new[] { typeof(Object) })
```

### Static vs Instance Members

```csharp
// Static member: no "target" port is created
new GetMember(new Member(typeof(Time), nameof(Time.deltaTime)))
// Only has: value (ValueOutput)

// Instance member: "target" port IS created
new GetMember(new Member(typeof(Transform), "position"))
// Has: target (ValueInput), value (ValueOutput)
// target expects the Transform instance
```

### Common Member Patterns

```csharp
// Debug.Log(object message) - static method
new InvokeMember(new Member(typeof(Debug), "Log", new[] { typeof(object) }))

// Transform.Rotate(float, float, float) - instance method
new InvokeMember(new Member(typeof(Transform), "Rotate",
    new[] { typeof(float), typeof(float), typeof(float) }))

// Transform.position (get) - instance property
new GetMember(new Member(typeof(Transform), "position"))

// Transform.position (set) - instance property
new SetMember(new Member(typeof(Transform), "position"))

// Time.deltaTime (get) - static property
new GetMember(new Member(typeof(Time), nameof(Time.deltaTime)))

// Input.GetKey(KeyCode) - static method
new InvokeMember(new Member(typeof(Input), "GetKey", new[] { typeof(KeyCode) }))

// Input.GetAxis(string) - static method
new InvokeMember(new Member(typeof(Input), "GetAxis", new[] { typeof(string) }))

// Physics.Raycast(Vector3, Vector3, float) - static method
new InvokeMember(new Member(typeof(Physics), "Raycast",
    new[] { typeof(Vector3), typeof(Vector3), typeof(float) }))

// GameObject.SetActive(bool) - instance method
new InvokeMember(new Member(typeof(GameObject), "SetActive", new[] { typeof(bool) }))

// Animator.SetTrigger(string) - instance method
new InvokeMember(new Member(typeof(Animator), "SetTrigger", new[] { typeof(string) }))

// AudioSource.PlayOneShot(AudioClip) - instance method
new InvokeMember(new Member(typeof(AudioSource), "PlayOneShot", new[] { typeof(AudioClip) }))
```

---

## 7. Unit Types Quick Reference

### Event Units (Entry Points)

| Class | Key Output Port | Description |
|-------|----------------|-------------|
| `Start` | `trigger` | OnStart lifecycle |
| `Update` | `trigger` | OnUpdate lifecycle |
| `FixedUpdate` | `trigger` | OnFixedUpdate lifecycle |
| `LateUpdate` | `trigger` | OnLateUpdate lifecycle |
| `OnEnable` | `trigger` | When object enabled |
| `OnDisable` | `trigger` | When object disabled |
| `OnDestroy` | `trigger` | When object destroyed |
| `OnTriggerEnter` | `trigger`, `collider` | 3D trigger enter |
| `OnTriggerExit` | `trigger`, `collider` | 3D trigger exit |
| `OnCollisionEnter` | `trigger`, `collider`, `contacts`, `impulse` | 3D collision |
| `OnCollisionExit` | `trigger`, `collider` | 3D collision end |
| `CustomEvent` | `trigger`, `arg_0`..`arg_N` | Custom event (set `argumentCount`) |

### Member Access Units

| Class | Constructor | Control Ports | Value Ports |
|-------|------------|---------------|-------------|
| `GetMember` | `new GetMember(member)` | None | `target`(in), `value`(out) |
| `SetMember` | `new SetMember(member)` | `assign`(in), `assigned`(out) | `target`(in), `input`(in), `output`(out) |
| `InvokeMember` | `new InvokeMember(member)` | `enter`(in), `exit`(out) | `target`(in), `inputParameters[n]`(in), `result`(out), `outputParameters[n]`(out) |

### Literal

| Class | Constructor | Value Ports |
|-------|------------|-------------|
| `Literal` | `new Literal(type, value)` | `output` |

```csharp
new Literal(typeof(float), 10f)
new Literal(typeof(string), "Hello")
new Literal(typeof(int), 42)
new Literal(typeof(bool), true)
new Literal(typeof(Vector3), new Vector3(1, 2, 3))
new Literal(typeof(Color), Color.red)
new Literal(typeof(KeyCode), KeyCode.Space)
```

### Scalar Math

| Class | Inputs | Output |
|-------|--------|--------|
| `ScalarAdd` | `a`, `b` | `sum` |
| `ScalarSubtract` | `minuend`, `subtrahend` | `difference` |
| `ScalarMultiply` | `a`, `b` | `product` |
| `ScalarDivide` | `dividend`, `divisor` | `quotient` |
| `ScalarModulo` | `dividend`, `divisor` | `remainder` |

**Multi-input variants** (`ScalarSum`, `ScalarMultiply` with `inputCount` property):
```csharp
var sum = new ScalarSum();
sum.inputCount = 3; // sum of 3 values
```

### Flow Control

| Class | Control In | Control Out | Value Ports |
|-------|-----------|-------------|-------------|
| `If` | `enter` | `ifTrue`, `ifFalse` | `condition`(bool, in) |
| `Sequence` | `enter` | `multiOutputs[0..N]` | (set `outputCount`) |
| `For` | `enter` | `body`, `exit` | `firstIndex`, `lastIndex`, `step`(in), `currentIndex`(out) |
| `ForEach` | `enter` | `body`, `exit` | `collection`(in), `currentItem`(out), `currentIndex`(out) |
| `While` | `enter` | `body`, `exit` | `condition`(bool, in) |
| `Once` | `enter`, `reset` | `once`, `after` | None |
| `NullCheck` | `enter` | `ifNotNull`, `ifNull` | `input`(in) |

### Variable Units

| Class | Control Ports | Value Ports | Properties |
|-------|--------------|-------------|------------|
| `GetVariable` | None | `value`(out), `name`(in), `@object`(in, Object scope only) | `kind`, `defaultName` |
| `SetVariable` | `assign`(in), `assigned`(out) | `input`(in), `output`(out), `name`(in), `@object`(in) | `kind`, `defaultName` |
| `IsVariableDefined` | None | `isDefined`(bool, out), `name`(in) | `kind`, `defaultName` |

### Time Units

| Class | Control Ports | Value Ports |
|-------|--------------|-------------|
| `WaitForSecondsUnit` | `enter`(in), `exit`(out) | `seconds`(float, in), `unscaledTime`(bool, in) |
| `WaitUntilUnit` | `enter`(in), `exit`(out) | `condition`(bool, in) |
| `Timer` | Various | `seconds`, `unscaledTime`, elapsed tracking |
| `Cooldown` | `enter`, `reset` | `seconds`, `unscaledTime` |

### Special Units

| Class | Purpose |
|-------|---------|
| `SubgraphUnit` | Nests another FlowGraph (was "SuperUnit") |
| `GraphInput` | Input interface inside subgraphs |
| `GraphOutput` | Output interface inside subgraphs |
| `StateUnit` | Embeds a StateGraph in a FlowGraph |
| `CustomEvent` | Receives custom events |
| `TriggerCustomEvent` | Fires custom events |

### Logic / Comparison

| Class | Inputs | Output |
|-------|--------|--------|
| `And` | `a`, `b` | `result` (bool) |
| `Or` | `a`, `b` | `result` (bool) |
| `Negate` | `input` | `output` (bool) |
| `Equal` | `a`, `b` | `comparison` (bool) |
| `NotEqual` | `a`, `b` | `comparison` (bool) |
| `Greater` | `a`, `b` | `comparison` (bool) |
| `Less` | `a`, `b` | `comparison` (bool) |
| `GreaterOrEqual` | `a`, `b` | `comparison` (bool) |
| `LessOrEqual` | `a`, `b` | `comparison` (bool) |

---

## 8. Graph Variables API

### Declaring Graph Variables on a FlowGraph

```csharp
var graph = graphAsset.graph;

// Declare variables with default values
graph.variables.Set("health", 100);
graph.variables.Set("speed", 5.5f);
graph.variables.Set("playerName", "Hero");
graph.variables.Set("isAlive", true);
graph.variables.Set("direction", Vector3.zero);
```

### Using GetVariable / SetVariable Units

```csharp
// Get a graph variable
var getHealth = new GetVariable();
getHealth.kind = VariableKind.Graph;
getHealth.defaultName = "health";
graph.units.Add(getHealth);
// Port: getHealth.value (ValueOutput)

// Set a graph variable
var setHealth = new SetVariable();
setHealth.kind = VariableKind.Graph;
setHealth.defaultName = "health";
graph.units.Add(setHealth);
// Ports: setHealth.assign (ControlInput), setHealth.assigned (ControlOutput),
//        setHealth.input (ValueInput), setHealth.output (ValueOutput)
```

### Runtime C# Variable Access

```csharp
// Object variables (requires Variables component on GameObject)
Variables.Object(gameObject).Set("health", 100);
int health = (int)Variables.Object(gameObject).Get("health");

// Scene variables
Variables.ActiveScene.Set("score", 0);

// Application variables
Variables.Application.Set("highScore", 9999);

// Saved variables (persists via PlayerPrefs)
Variables.Saved.Set("bestTime", 120.5f);
```

### VariableKind Enum

| Kind | Scope | Use Case |
|------|-------|----------|
| `VariableKind.Flow` | Current execution only | Temp values within a flow |
| `VariableKind.Graph` | Current graph instance | Per-graph private state |
| `VariableKind.Object` | Per GameObject | Shared across graphs on same object |
| `VariableKind.Scene` | Per scene | Scene-wide state |
| `VariableKind.Application` | Application lifetime | Cross-scene state |
| `VariableKind.Saved` | Persistent (PlayerPrefs) | Save data |

---

## 9. ScriptMachine / StateMachine Component Setup

### Attaching a ScriptMachine with Macro Source

```csharp
var go = GameObject.Find("MyObject");
if (go != null)
{
    var machine = go.GetComponent<ScriptMachine>();
    if (machine == null)
        machine = go.AddComponent<ScriptMachine>();

    machine.nest.source = GraphSource.Macro;
    machine.nest.macro = graphAsset;  // ScriptGraphAsset reference
    EditorUtility.SetDirty(go);
}
```

### Attaching a StateMachine

```csharp
var machine = go.AddComponent<StateMachine>();
machine.nest.source = GraphSource.Macro;
machine.nest.macro = stateGraphAsset;  // StateGraphAsset reference
EditorUtility.SetDirty(go);
```

### Embedded vs Macro Source

| Source | How | When to Use |
|--------|-----|-------------|
| `GraphSource.Macro` | References an external `.asset` file | Reusable across multiple objects |
| `GraphSource.Embed` | Graph serialized in the component | Unique to one object, supports scene refs |

```csharp
// Macro (external asset)
machine.nest.source = GraphSource.Macro;
machine.nest.macro = graphAsset;

// Embed (inline graph)
machine.nest.source = GraphSource.Embed;
machine.nest.embed = FlowGraph.WithStartUpdate();
```

### Loading an Existing Graph Asset

```csharp
var graphAsset = AssetDatabase.LoadAssetAtPath<ScriptGraphAsset>(
    "Assets/VisualScripting/MyGraph.asset"
);
```

---

## 10. Asset Management

### Create Folder if Missing

```csharp
if (!AssetDatabase.IsValidFolder("Assets/VisualScripting"))
    AssetDatabase.CreateFolder("Assets", "VisualScripting");
```

### Full Save Workflow

```csharp
// Create asset
AssetDatabase.CreateAsset(graphAsset, path);
AssetDatabase.SaveAssets();
AssetDatabase.Refresh();
```

### Modifying Existing Assets

```csharp
var asset = AssetDatabase.LoadAssetAtPath<ScriptGraphAsset>(path);
// ... modify asset.graph ...
EditorUtility.SetDirty(asset);
AssetDatabase.SaveAssets();
```

### Undo Support

```csharp
Undo.RecordObject(graphAsset, "Modify graph");
// ... make changes ...
// SetDirty is called automatically by Undo system
```

### Key Functions

| Function | Purpose |
|----------|---------|
| `ScriptableObject.CreateInstance<T>()` | Create in-memory asset instance |
| `AssetDatabase.CreateAsset(obj, path)` | Save asset to disk |
| `AssetDatabase.SaveAssets()` | Write all dirty assets to disk |
| `AssetDatabase.SaveAssetIfDirty(obj)` | Save only this specific asset (2020.3+) |
| `AssetDatabase.Refresh()` | Reimport changed assets |
| `AssetDatabase.IsValidFolder(path)` | Check if folder exists |
| `AssetDatabase.CreateFolder(parent, name)` | Create asset folder |
| `AssetDatabase.LoadAssetAtPath<T>(path)` | Load existing asset |
| `EditorUtility.SetDirty(obj)` | Mark object as needing save |

---

## 11. Common Patterns with Code Examples

### Pattern 1: Event -> Action (Start -> Debug.Log)

```csharp
var graph = graphAsset.graph;

var start = new Start();
graph.units.Add(start);
start.position = new Vector2(0, 0);

var debugLog = new InvokeMember(new Member(typeof(Debug), "Log", new[] { typeof(object) }));
graph.units.Add(debugLog);
debugLog.position = new Vector2(300, 0);

var message = new Literal(typeof(string), "Hello World!");
graph.units.Add(message);
message.position = new Vector2(100, 150);

// Control: Start -> Debug.Log
graph.controlConnections.Add(new ControlConnection(start.trigger, debugLog.enter));

// Value: message -> Debug.Log parameter
graph.valueConnections.Add(new ValueConnection(message.output, debugLog.inputParameters[0]));
```

### Pattern 2: Update Loop with DeltaTime

```csharp
var onUpdate = new Update();
graph.units.Add(onUpdate);
onUpdate.position = new Vector2(-300, 0);

var getDeltaTime = new GetMember(new Member(typeof(Time), nameof(Time.deltaTime)));
graph.units.Add(getDeltaTime);
getDeltaTime.position = new Vector2(-300, 200);

var speed = new Literal(typeof(float), 5f);
graph.units.Add(speed);
speed.position = new Vector2(-300, 100);

var multiply = new ScalarMultiply();
graph.units.Add(multiply);
multiply.position = new Vector2(-50, 100);

// speed * deltaTime
graph.valueConnections.Add(new ValueConnection(speed.output, multiply.a));
graph.valueConnections.Add(new ValueConnection(getDeltaTime.value, multiply.b));
// Result: multiply.product
```

### Pattern 3: Conditional Branch

```csharp
var ifUnit = new If();
graph.units.Add(ifUnit);
ifUnit.position = new Vector2(200, 0);

// Connect: someControl -> ifUnit.enter
graph.controlConnections.Add(new ControlConnection(prevUnit.exit, ifUnit.enter));

// Connect condition
graph.valueConnections.Add(new ValueConnection(conditionSource.output, ifUnit.condition));

// Connect branches
graph.controlConnections.Add(new ControlConnection(ifUnit.ifTrue, trueAction.enter));
graph.controlConnections.Add(new ControlConnection(ifUnit.ifFalse, falseAction.enter));
```

### Pattern 4: Get/Set Variable

```csharp
// Declare the variable
graph.variables.Set("score", 0);

// Get variable
var getScore = new GetVariable();
getScore.kind = VariableKind.Graph;
getScore.defaultName = "score";
graph.units.Add(getScore);

// Set variable
var setScore = new SetVariable();
setScore.kind = VariableKind.Graph;
setScore.defaultName = "score";
graph.units.Add(setScore);

// Connect: someControl -> setScore.assign
graph.controlConnections.Add(new ControlConnection(prevUnit.exit, setScore.assign));

// Connect value to set
graph.valueConnections.Add(new ValueConnection(newValue.output, setScore.input));
```

### Pattern 5: Self-Reference (This) for Instance Methods

For instance methods like `Transform.Rotate`, the `target` port automatically resolves to the current GameObject's component when left unconnected. However, to explicitly wire it:

```csharp
// The This unit provides a reference to the current GameObject
var thisUnit = new This();
graph.units.Add(thisUnit);

// Get the Transform component
var getTransform = new GetMember(new Member(typeof(GameObject), "transform"));
graph.units.Add(getTransform);

graph.valueConnections.Add(new ValueConnection(thisUnit.self, getTransform.target));
```

**Note**: For InvokeMember on instance methods, if no connection is made to the `target` port, it defaults to the GameObject that owns the ScriptMachine. This is usually the desired behavior.

### Pattern 6: Multiple Operations with Sequence

```csharp
var seq = new Sequence();
seq.outputCount = 3;
graph.units.Add(seq);

graph.controlConnections.Add(new ControlConnection(prevUnit.exit, seq.enter));
graph.controlConnections.Add(new ControlConnection(seq.multiOutputs[0], action1.enter));
graph.controlConnections.Add(new ControlConnection(seq.multiOutputs[1], action2.enter));
graph.controlConnections.Add(new ControlConnection(seq.multiOutputs[2], action3.enter));
```

### Pattern 7: For Loop

```csharp
var forLoop = new For();
graph.units.Add(forLoop);

var firstIdx = new Literal(typeof(int), 0);
graph.units.Add(firstIdx);

var lastIdx = new Literal(typeof(int), 10);
graph.units.Add(lastIdx);

var step = new Literal(typeof(int), 1);
graph.units.Add(step);

graph.valueConnections.Add(new ValueConnection(firstIdx.output, forLoop.firstIndex));
graph.valueConnections.Add(new ValueConnection(lastIdx.output, forLoop.lastIndex));
graph.valueConnections.Add(new ValueConnection(step.output, forLoop.step));

// forLoop.body -> loop body actions
// forLoop.exit -> after loop completes
// forLoop.currentIndex -> current iteration index (ValueOutput)
```

### Pattern 8: Complete Rotation Graph (from Sample)

See `/Users/yamaguchi/GitHub/UnityVisualScriptingSkill/Editor Script Samples/CreateRotateGraph.cs` for the full working example. Key takeaways:

1. `graphAsset.graph` gives you the pre-initialized FlowGraph
2. Units are created with `new` and added via `graph.units.Add(unit)`
3. Position is set after adding: `unit.position = new Vector2(x, y)`
4. Control connections: `new ControlConnection(output, input)`
5. Value connections: `new ValueConnection(output, input)`
6. InvokeMember parameters: `invoke.inputParameters[0]`, `invoke.inputParameters[1]`, etc.

---

## 12. Port Name Reference

### Event Units

| Unit | Port | Type | Key |
|------|------|------|-----|
| `Start` | trigger | ControlOutput | `"trigger"` |
| `Update` | trigger | ControlOutput | `"trigger"` |
| `FixedUpdate` | trigger | ControlOutput | `"trigger"` |
| `LateUpdate` | trigger | ControlOutput | `"trigger"` |
| `OnTriggerEnter` | trigger | ControlOutput | `"trigger"` |
| `OnCollisionEnter` | trigger | ControlOutput | `"trigger"` |

### Member Units

| Unit | Port | Type | Key |
|------|------|------|-----|
| `GetMember` | target | ValueInput | `"target"` |
| `GetMember` | value | ValueOutput | `"value"` |
| `SetMember` | assign | ControlInput | `"assign"` |
| `SetMember` | assigned | ControlOutput | `"assigned"` |
| `SetMember` | target | ValueInput | `"target"` |
| `SetMember` | input | ValueInput | `"input"` |
| `SetMember` | output | ValueOutput | `"output"` |
| `InvokeMember` | enter | ControlInput | `"enter"` |
| `InvokeMember` | exit | ControlOutput | `"exit"` |
| `InvokeMember` | target | ValueInput | `"target"` |
| `InvokeMember` | inputParameters[n] | ValueInput | `"%paramName"` or indexed |
| `InvokeMember` | result | ValueOutput | `"result"` |

### Literal

| Unit | Port | Type | Key |
|------|------|------|-----|
| `Literal` | output | ValueOutput | `"output"` |

### Math Units

| Unit | Port | Type | Key |
|------|------|------|-----|
| `ScalarMultiply` | a | ValueInput | `"a"` |
| `ScalarMultiply` | b | ValueInput | `"b"` |
| `ScalarMultiply` | product | ValueOutput | `"product"` |
| `ScalarAdd` | a | ValueInput | `"a"` |
| `ScalarAdd` | b | ValueInput | `"b"` |
| `ScalarAdd` | sum | ValueOutput | `"sum"` |

### Flow Control

| Unit | Port | Type | Key |
|------|------|------|-----|
| `If` | enter | ControlInput | `"enter"` |
| `If` | condition | ValueInput | `"condition"` |
| `If` | ifTrue | ControlOutput | `"ifTrue"` |
| `If` | ifFalse | ControlOutput | `"ifFalse"` |
| `For` | enter | ControlInput | `"enter"` |
| `For` | body | ControlOutput | `"body"` |
| `For` | exit | ControlOutput | `"exit"` |
| `For` | firstIndex | ValueInput | `"firstIndex"` |
| `For` | lastIndex | ValueInput | `"lastIndex"` |
| `For` | step | ValueInput | `"step"` |
| `For` | currentIndex | ValueOutput | `"currentIndex"` |
| `Sequence` | enter | ControlInput | `"enter"` |
| `Sequence` | multiOutputs[n] | ControlOutput | `"0"`, `"1"`, etc. |

### Variable Units

| Unit | Port | Type | Key |
|------|------|------|-----|
| `GetVariable` | value | ValueOutput | `"value"` |
| `SetVariable` | assign | ControlInput | `"assign"` |
| `SetVariable` | assigned | ControlOutput | `"assigned"` |
| `SetVariable` | input | ValueInput | `"input"` |
| `SetVariable` | output | ValueOutput | `"output"` |

### Time Units

| Unit | Port | Type | Key |
|------|------|------|-----|
| `WaitForSecondsUnit` | enter | ControlInput | `"enter"` |
| `WaitForSecondsUnit` | exit | ControlOutput | `"exit"` |
| `WaitForSecondsUnit` | seconds | ValueInput | `"seconds"` |

---

## 13. Error Handling and Validation

### Pre-Creation Checks

```csharp
// Check if folder exists before saving
if (!AssetDatabase.IsValidFolder("Assets/VisualScripting"))
    AssetDatabase.CreateFolder("Assets", "VisualScripting");

// Check if asset already exists
var existing = AssetDatabase.LoadAssetAtPath<ScriptGraphAsset>(path);
if (existing != null)
{
    Debug.LogWarning($"Asset already exists at {path}");
    return;
}
```

### Post-Creation Validation

```csharp
// Verify asset was created
AssetDatabase.SaveAssets();
var loaded = AssetDatabase.LoadAssetAtPath<ScriptGraphAsset>(path);
if (loaded == null)
{
    Debug.LogError($"Failed to create graph asset at {path}");
    return;
}
```

### GameObject Checks

```csharp
var go = GameObject.Find("TargetObject");
if (go == null)
{
    Debug.LogError("Target object not found in scene.");
    return;
}

var machine = go.GetComponent<ScriptMachine>();
if (machine == null)
    machine = go.AddComponent<ScriptMachine>();
```

### Common Errors to Avoid

1. **Asset path must end in `.asset`**: `AssetDatabase.CreateAsset` requires a `.asset` extension.
2. **Never create assets outside `Assets/` folder**: The path must be relative to the project root.
3. **Always call `AssetDatabase.SaveAssets()`** after creating or modifying assets.
4. **Mark dirty after modification**: `EditorUtility.SetDirty(go)` when modifying GameObjects.
5. **Wrap in `#if UNITY_EDITOR`**: All editor scripts must be conditionally compiled.
6. **Never use editor-only types in runtime graphs**: Nodes referencing `UnityEditor` types cause build errors.

---

*Reference based on Unity Visual Scripting packages 1.7-1.9 and verified against working sample code in `Editor Script Samples/CreateRotateGraph.cs`.*
