# Unity Visual Scripting: Editor Scripting Best Practices

## Table of Contents
1. [Overview](#1-overview)
2. [Core Architecture for Programmatic Graph Creation](#2-core-architecture-for-programmatic-graph-creation)
3. [ScriptGraphAsset and StateGraphAsset Creation](#3-scriptgraphasset-and-stategraphasset-creation)
4. [FlowGraph Manipulation](#4-flowgraph-manipulation)
5. [Adding Units to Graphs](#5-adding-units-to-graphs)
6. [Creating Connections Between Units](#6-creating-connections-between-units)
7. [Unit Types Reference](#7-unit-types-reference)
8. [Variables System](#8-variables-system)
9. [SubGraphs (SuperUnit / SubgraphUnit)](#9-subgraphs-superunit--subgraphunit)
10. [StateMachines and StateGraphs](#10-statemachines-and-stategraphs)
11. [ScriptMachine vs StateMachine Components](#11-scriptmachine-vs-statemachine-components)
12. [Graph Serialization and Asset Management](#12-graph-serialization-and-asset-management)
13. [Common Pitfalls and Workarounds](#13-common-pitfalls-and-workarounds)
14. [Complete Code Examples](#14-complete-code-examples)
15. [Sources and References](#15-sources-and-references)

---

## 1. Overview

Unity Visual Scripting (formerly Bolt) provides a node-based visual programming system. While the primary interface is the Graph Editor window, it is possible to create and manipulate graphs programmatically using C# editor scripts. This is useful for:

- Generating graphs from data or templates
- Automating repetitive graph creation tasks
- Building custom editor tools that produce Visual Scripting graphs
- Converting between code and visual scripts

**Important Note**: Many of the internal APIs used for programmatic graph creation are marked with `#if VISUAL_SCRIPT_INTERNAL` in the source code, indicating they are intended for internal use. These APIs may change between versions. The patterns documented here are based on the Visual Scripting package source code (versions 1.7-1.9) and community usage.

**Namespace**: All Visual Scripting types are in the `Unity.VisualScripting` namespace.

```csharp
using Unity.VisualScripting;
using UnityEngine;
using UnityEditor;
```

---

## 2. Core Architecture for Programmatic Graph Creation

### Key Classes

| Class | Role |
|-------|------|
| `ScriptGraphAsset` | ScriptableObject asset containing a FlowGraph (Script Graph) |
| `StateGraphAsset` | ScriptableObject asset containing a StateGraph |
| `FlowGraph` | The graph object containing units, connections, and variables |
| `StateGraph` | The graph object for state machines |
| `ScriptMachine` | MonoBehaviour component that executes a Script Graph |
| `StateMachine` | MonoBehaviour component that executes a State Graph |
| `GraphNest<TGraph, TMacro>` | Manages graph storage (macro vs embed) |
| `GraphSource` | Enum: `Macro` or `Embed` |
| `Unit` | Base class for all nodes in a FlowGraph |

### Graph Hierarchy

```
ScriptGraphAsset (ScriptableObject)
  └── graph (FlowGraph)
       ├── units (GraphElementCollection<IUnit>)
       ├── controlConnections (ControlConnection collection)
       ├── valueConnections (ValueConnection collection)
       ├── variables (VariableDeclarations)
       ├── controlInputDefinitions
       ├── controlOutputDefinitions
       ├── valueInputDefinitions
       └── valueOutputDefinitions

StateGraphAsset (ScriptableObject)
  └── graph (StateGraph)
       ├── states (FlowState, AnyState)
       └── transitions (FlowStateTransition)
```

---

## 3. ScriptGraphAsset and StateGraphAsset Creation

### Creating a ScriptGraphAsset

The standard pattern (based on `EmptyGraphWindow.CreateScriptGraphAsset` from the VS source):

```csharp
using Unity.VisualScripting;
using UnityEditor;
using UnityEngine;

public static class GraphFactory
{
    [MenuItem("Tools/Create Script Graph Asset")]
    public static void CreateScriptGraphAsset()
    {
        string path = EditorUtility.SaveFilePanelInProject(
            "Save Script Graph",
            "NewScriptGraph",
            "asset",
            "Choose a location to save the Script Graph."
        );

        if (string.IsNullOrEmpty(path))
            return;

        // Create the asset
        var graphAsset = ScriptableObject.CreateInstance<ScriptGraphAsset>();

        // Initialize with Start + Update events (the standard default)
        graphAsset.graph = FlowGraph.WithStartUpdate();

        // Save to AssetDatabase
        AssetDatabase.CreateAsset(graphAsset, path);
        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();
    }
}
```

### Creating a StateGraphAsset

```csharp
public static void CreateStateGraphAsset()
{
    string path = EditorUtility.SaveFilePanelInProject(
        "Save State Graph",
        "NewStateGraph",
        "asset",
        "Choose a location to save the State Graph."
    );

    if (string.IsNullOrEmpty(path))
        return;

    var stateGraphAsset = ScriptableObject.CreateInstance<StateGraphAsset>();
    stateGraphAsset.graph = StateGraph.WithStart();

    AssetDatabase.CreateAsset(stateGraphAsset, path);
    AssetDatabase.SaveAssets();
    AssetDatabase.Refresh();
}
```

### Factory Methods

FlowGraph provides two static factory methods:

```csharp
// Creates a FlowGraph with Start and Update event units
// Used for typical gameplay script graphs
public static FlowGraph WithStartUpdate()
{
    return new FlowGraph()
    {
        units =
        {
            new Start() { position = new Vector2(-204, -144) },
            new Update() { position = new Vector2(-204, 60) }
        }
    };
}

// Creates a FlowGraph with GraphInput and GraphOutput units
// Used for subgraphs / nested graphs that need input/output ports
public static FlowGraph WithInputOutput()
{
    return new FlowGraph()
    {
        units =
        {
            new GraphInput() { position = new Vector2(-250, -30) },
            new GraphOutput() { position = new Vector2(105, -30) }
        }
    };
}
```

---

## 4. FlowGraph Manipulation

### FlowGraph Properties

```csharp
FlowGraph graph = new FlowGraph();

// Units (nodes) in the graph
GraphElementCollection<IUnit> units = graph.units;

// Connections
// graph.controlConnections  - control flow (execution order)
// graph.valueConnections    - data flow (values between ports)
// graph.invalidConnections  - broken/invalid connections

// Port definitions (for subgraph input/output)
// graph.controlInputDefinitions
// graph.controlOutputDefinitions
// graph.valueInputDefinitions
// graph.valueOutputDefinitions

// Graph variables
VariableDeclarations variables = graph.variables;
```

### Creating a FlowGraph from Scratch

```csharp
var graph = new FlowGraph();

// Add units using collection initializer syntax
var startUnit = new Start() { position = new Vector2(0, 0) };
var debugLogUnit = new InvokeMember(
    new Member(typeof(Debug), nameof(Debug.Log), new[] { typeof(object) })
) { position = new Vector2(250, 0) };

graph.units.Add(startUnit);
graph.units.Add(debugLogUnit);
```

---

## 5. Adding Units to Graphs

### Basic Pattern

All units are added to the `graph.units` collection:

```csharp
FlowGraph graph = new FlowGraph();

// Method 1: Add to units collection
var unit = new Start();
unit.position = new Vector2(100, 100);
graph.units.Add(unit);

// Method 2: Collection initializer (when creating the graph)
var graph2 = new FlowGraph()
{
    units =
    {
        new Start() { position = new Vector2(-204, -144) },
        new Update() { position = new Vector2(-204, 60) }
    }
};
```

### Unit Position

Every unit has a `position` property (Vector2) that determines its location in the graph editor canvas:

```csharp
unit.position = new Vector2(x, y);
```

Recommended layout spacing: ~200-250 pixels horizontally between connected units, ~150-200 pixels vertically for parallel branches.

---

## 6. Creating Connections Between Units

### Connection Types

There are two types of connections:

1. **ControlConnection**: Links `ControlOutput` to `ControlInput` (execution flow)
2. **ValueConnection**: Links `ValueOutput` to `ValueInput` (data flow)

### Creating Control Connections

```csharp
// Connect a ControlOutput to a ControlInput
// The port's ConnectToValid method handles adding to the graph's collection

ControlOutput sourcePort = someUnit.controlOutputs["exit"];
ControlInput destPort = anotherUnit.controlInputs["enter"];

// Option 1: Use ConnectToValid (disconnects existing connections first)
sourcePort.ConnectToValid(destPort);

// Option 2: Directly add to graph's connection collection
graph.controlConnections.Add(new ControlConnection(sourcePort, destPort));
```

**Important**: Control outputs do NOT support multiple connections. When you connect a new destination, any existing connection from that output is automatically disconnected.

### Creating Value Connections

```csharp
// Connect a ValueOutput to a ValueInput
ValueOutput sourcePort = someUnit.valueOutputs["result"];
ValueInput destPort = anotherUnit.valueInputs["value"];

// Option 1: Use ConnectToValid
sourcePort.ConnectToValid(destPort);

// Option 2: Directly add to graph's collection
graph.valueConnections.Add(new ValueConnection(sourcePort, destPort));
```

**Important**: Value inputs do NOT support multiple connections. When you connect a new source, any existing connection to that input is automatically disconnected.

### Port Access Patterns

Units expose their ports through indexed collections:

```csharp
// Access ports by key name
unit.controlInputs["enter"];
unit.controlOutputs["exit"];
unit.valueInputs["target"];
unit.valueOutputs["result"];

// For units with typed port fields, access directly:
var ifUnit = new If();
// After adding to graph and defining:
// ifUnit.enter, ifUnit.ifTrue, ifUnit.ifFalse, ifUnit.condition
```

**Note**: Port keys must match the string keys used in the unit's `Definition()` method. The actual key names depend on the specific unit type.

---

## 7. Unit Types Reference

### Event Units

| Class Name | Description | Key Ports |
|-----------|-------------|-----------|
| `Start` | OnStart lifecycle event | `trigger` (ControlOutput) |
| `Update` | OnUpdate lifecycle event | `trigger` (ControlOutput) |
| `FixedUpdate` | OnFixedUpdate lifecycle | `trigger` (ControlOutput) |
| `LateUpdate` | OnLateUpdate lifecycle | `trigger` (ControlOutput) |
| `OnEnable` | OnEnable lifecycle | `trigger` (ControlOutput) |
| `OnDisable` | OnDisable lifecycle | `trigger` (ControlOutput) |
| `OnDestroy` | OnDestroy lifecycle | `trigger` (ControlOutput) |

**Note**: In version 1.7.1+, display names were changed (e.g., "Start" -> "On Start", "Update" -> "On Update"), but the underlying class names remain the same.

### Physics Event Units

| Class Name | Description |
|-----------|-------------|
| `OnCollisionEnter` | 3D collision enter |
| `OnCollisionExit` | 3D collision exit |
| `OnCollisionStay` | 3D collision stay |
| `OnTriggerEnter` | 3D trigger enter |
| `OnTriggerExit` | 3D trigger exit |
| `OnTriggerStay` | 3D trigger stay |
| `OnCollisionEnter2D` | 2D collision enter |
| `OnCollisionExit2D` | 2D collision exit |
| `OnTriggerEnter2D` | 2D trigger enter |
| `OnTriggerExit2D` | 2D trigger exit |

### Control Flow Units

| Class Name | Description | Key Ports |
|-----------|-------------|-----------|
| `If` | Conditional branch (formerly "Branch") | `enter`, `condition` (bool), `ifTrue`, `ifFalse` |
| `While` | While loop | `enter`, `condition` (bool), `body`, `exit` |
| `For` | For loop | `enter`, `firstIndex`, `lastIndex`, `step`, `currentIndex`, `body`, `exit` |
| `ForEach` | ForEach loop | `enter`, `collection`, `currentIndex`, `currentKey`, `currentItem`, `body`, `exit` |
| `Sequence` | Execute multiple outputs in order | `enter`, `multiOutputs[0..N]` |

The `If` unit implements `IBranchUnit`:

```csharp
var ifUnit = new If();
ifUnit.position = new Vector2(200, 0);
graph.units.Add(ifUnit);
// Ports: ifUnit.enter, ifUnit.condition, ifUnit.ifTrue, ifUnit.ifFalse
```

### Member Access Units

These use reflection to access C# members:

| Class Name | Description | Constructor Pattern |
|-----------|-------------|-------------------|
| `InvokeMember` | Call a method | `new InvokeMember(new Member(type, methodName, paramTypes))` |
| `GetMember` | Get field/property | `new GetMember(new Member(type, memberName))` |
| `SetMember` | Set field/property | `new SetMember(new Member(type, memberName))` |

```csharp
// Example: Debug.Log(message)
var debugLog = new InvokeMember(
    new Member(typeof(Debug), nameof(Debug.Log), new[] { typeof(object) })
);

// Example: Get Transform.position
var getPosition = new GetMember(
    new Member(typeof(Transform), nameof(Transform.position))
);

// Example: Set Transform.position
var setPosition = new SetMember(
    new Member(typeof(Transform), nameof(Transform.position))
);
```

### Literal Unit

The `Literal` unit represents a constant value:

```csharp
// Create with type and value
var stringLiteral = new Literal(typeof(string), "Hello World");
var intLiteral = new Literal(typeof(int), 42);
var floatLiteral = new Literal(typeof(float), 3.14f);
var vectorLiteral = new Literal(typeof(Vector3), new Vector3(1, 2, 3));

// Set value after creation
var literal = new Literal(typeof(string));
literal.value = "Updated Value";
```

### Arithmetic Units

| Class Name | Description | Input Ports | Output Port |
|-----------|-------------|-------------|------------|
| `GenericAdd` / `Add<T>` | Addition | `a`, `b` | `sum` |
| `GenericSubtract` / `Subtract<T>` | Subtraction | `minuend`, `subtrahend` | `difference` |
| `GenericMultiply` / `Multiply<T>` | Multiplication | `a`, `b` | `product` |
| `GenericDivide` / `Divide<T>` | Division | `dividend`, `divisor` | `quotient` |

### Variable Units

| Class Name | Description | Key Ports |
|-----------|-------------|-----------|
| `GetVariable` | Get a variable value | `name` (string), `value` (output) |
| `SetVariable` | Set a variable value | `assign` (control in), `name`, `input`, `assigned` (control out) |
| `IsVariableDefined` | Check if variable exists | `name`, `isDefined` (bool output) |

```csharp
// Create GetVariable for a graph variable named "health"
var getVar = new GetVariable();
// The kind property determines the variable scope
// VariableKind.Graph, VariableKind.Object, VariableKind.Scene, etc.
```

### Nesting Units

| Class Name | Description |
|-----------|-------------|
| `SubgraphUnit` | Embeds a subgraph (formerly SuperUnit) |
| `GraphInput` | Input node inside a subgraph |
| `GraphOutput` | Output node inside a subgraph |

---

## 8. Variables System

### Variable Scopes

Unity Visual Scripting supports five variable scopes:

| Scope | Access | Persistence |
|-------|--------|-------------|
| `VariableKind.Graph` | Per-graph instance (like private variables) | Per graph instance |
| `VariableKind.Object` | Per-GameObject (requires Variables component) | Per object |
| `VariableKind.Scene` | Per-scene | Per scene |
| `VariableKind.Application` | Global to application | Until app closes |
| `VariableKind.Saved` | Persistent across sessions | Uses PlayerPrefs |

### Declaring Graph Variables Programmatically

```csharp
FlowGraph graph = new FlowGraph();

// Declare graph variables
graph.variables.Set("health", 100);
graph.variables.Set("playerName", "Player1");
graph.variables.Set("speed", 5.5f);
graph.variables.Set("isAlive", true);
graph.variables.Set("direction", Vector3.zero);
```

### C# API for Runtime Variable Access

```csharp
// Note: In modern Unity Visual Scripting (1.7+), the namespace is Unity.VisualScripting
// In older Bolt versions, the namespaces were Ludiq and Bolt

// Object variables
Variables.Object(gameObject).Set("health", 100);
int health = (int)Variables.Object(gameObject).Get("health");
bool hasMana = Variables.Object(gameObject).IsDefined("mana");

// Scene variables
Variables.ActiveScene.Set("score", 0);
int score = (int)Variables.ActiveScene.Get("score");

// Application variables
Variables.Application.Set("highScore", 9999);
int highScore = (int)Variables.Application.Get("highScore");

// Saved variables (persistent)
Variables.Saved.Set("bestTime", 120.5f);
float bestTime = (float)Variables.Saved.Get("bestTime");

// Graph variables (requires a GraphReference)
var graphReference = GraphReference.New(scriptMachine, true);
Variables.Graph(graphReference).Set("localVar", 42);

// Graph variables for nested graphs
var nestedRef = GraphReference.New(scriptMachine,
    new IGraphParentElement[] { subgraphUnit }, true);
Variables.Graph(nestedRef).Set("nestedVar", "value");
```

### Variable Declarations (VariableDeclarations)

The `VariableDeclarations` class is the container for variable name-value pairs:

```csharp
VariableDeclarations declarations = graph.variables;

// Set a variable (creates if it does not exist)
declarations.Set("myVar", 42);

// Get a variable
object value = declarations.Get("myVar");

// Check if defined
bool exists = declarations.IsDefined("myVar");

// The OnVariableChanged action fires when any variable value changes
```

---

## 9. SubGraphs (SuperUnit / SubgraphUnit)

### Overview

SubGraphs (renamed from SuperUnit in v1.7.1) allow nesting a FlowGraph inside another FlowGraph. The `SubgraphUnit` class inherits from `NesterUnit<FlowGraph, ScriptGraphAsset>`.

### Creating a SubgraphUnit with a Macro

```csharp
// Reference an existing ScriptGraphAsset
ScriptGraphAsset subGraphAsset = AssetDatabase.LoadAssetAtPath<ScriptGraphAsset>(
    "Assets/Graphs/MySubGraph.asset"
);

var subgraphUnit = new SubgraphUnit(subGraphAsset);
subgraphUnit.position = new Vector2(300, 0);
graph.units.Add(subgraphUnit);
```

### Creating a SubgraphUnit with Embedded Graph

```csharp
var subgraphUnit = new SubgraphUnit();
subgraphUnit.nest.source = GraphSource.Embed;
subgraphUnit.nest.embed = FlowGraph.WithInputOutput();
subgraphUnit.position = new Vector2(300, 0);
graph.units.Add(subgraphUnit);

// Add units to the embedded subgraph
FlowGraph subGraph = subgraphUnit.nest.embed;
// subGraph now has GraphInput and GraphOutput units by default
```

### Input/Output Ports

Inside a subgraph, `GraphInput` and `GraphOutput` units define the interface:

- `GraphInput`: Fetches input values from the parent SubgraphUnit. Defines control outputs and value outputs based on the parent graph's port definitions.
- `GraphOutput`: Passes output values back to the parent SubgraphUnit. Defines control inputs and value inputs.

### Recursive Unit Traversal

To iterate all units including those in nested subgraphs:

```csharp
// The XFlowGraph.GetUnitsRecursive extension method traverses nested SubgraphUnits
// This is useful for operations that need to inspect the entire graph hierarchy
```

---

## 10. StateMachines and StateGraphs

### StateGraph vs FlowGraph

| Feature | FlowGraph (Script Graph) | StateGraph |
|---------|-------------------------|------------|
| Purpose | General-purpose logic | State machine behavior |
| Component | `ScriptMachine` | `StateMachine` |
| Asset | `ScriptGraphAsset` | `StateGraphAsset` |
| Contains | Units, connections | States, transitions |

### State Types

| Class | Description |
|-------|-------------|
| `FlowState` | A state containing a nested Script Graph with Enter/Update/Exit events |
| `AnyState` | A special state that can transition to any other state (cannot be a transition destination) |
| `SuperState` | A state containing a nested State Graph (hierarchical state machine) |

### Transition Types

| Class | Description |
|-------|-------------|
| `FlowStateTransition` | A transition containing a nested Script Graph that defines when to transition |

### Creating a StateGraph Programmatically

```csharp
var stateGraph = new StateGraph();

// Create states
var idleState = new FlowState();
// FlowState contains a nested ScriptGraph with Enter/Update/Exit events

var walkState = new FlowState();

// Create transition
var idleToWalk = new FlowStateTransition();
// FlowStateTransition contains a nested ScriptGraph that triggers the transition

// Add to graph
stateGraph.states.Add(idleState);
stateGraph.states.Add(walkState);
// Transitions connect source and destination states
```

### AnyState

```csharp
var anyState = new AnyState();
// AnyState can only be a source of transitions, never a destination
// anyState.canBeDestination always returns false
// When branching to a new destination, exits all other outgoing transitions' destinations
```

---

## 11. ScriptMachine vs StateMachine Components

### ScriptMachine

`ScriptMachine` executes a `FlowGraph` (Script Graph) on a GameObject:

```csharp
// Add a ScriptMachine to a GameObject and assign a macro graph
GameObject go = new GameObject("MyObject");
ScriptMachine sm = go.AddComponent<ScriptMachine>();

// Option 1: Reference a macro asset
ScriptGraphAsset asset = AssetDatabase.LoadAssetAtPath<ScriptGraphAsset>(
    "Assets/Graphs/MyGraph.asset"
);
sm.nest.source = GraphSource.Macro;
sm.nest.macro = asset;

// Option 2: Use an embedded graph
sm.nest.source = GraphSource.Embed;
sm.nest.embed = FlowGraph.WithStartUpdate();
```

### StateMachine

`StateMachine` executes a `StateGraph` on a GameObject:

```csharp
GameObject go = new GameObject("StateMachineObject");
StateMachine stm = go.AddComponent<StateMachine>();

// Reference a macro asset
StateGraphAsset stateAsset = AssetDatabase.LoadAssetAtPath<StateGraphAsset>(
    "Assets/Graphs/MyStateGraph.asset"
);
stm.nest.source = GraphSource.Macro;
stm.nest.macro = stateAsset;
```

### GraphNest: Macro vs Embed

The `GraphNest<TGraph, TMacro>` class manages how graphs are stored:

| Source | Storage | Reusability | Scene References |
|--------|---------|-------------|------------------|
| `GraphSource.Macro` | Separate `.asset` file | Reusable across objects | Not supported |
| `GraphSource.Embed` | Serialized in component | Unique to object | Supported |

```csharp
// Switch to macro
sm.nest.SwitchToMacro(someScriptGraphAsset);

// Switch to embed
sm.nest.SwitchToEmbed(new FlowGraph());
```

**Recommendation**: Use Macro (asset files) for reusable graphs. Use Embed only when you need scene references or the graph is unique to one object.

---

## 12. Graph Serialization and Asset Management

### Serialization System

Unity Visual Scripting uses **FullSerializer** (an internal JSON serialization library) for graph serialization:

- Graphs are serialized to JSON format internally
- `ScriptGraphAsset` and `StateGraphAsset` are `ScriptableObject` subclasses
- FullSerializer handles cyclic references, type information, and versioning
- Serialized data includes metadata: `$ref`, `$id`, `$type`, `$version`

### Saving Graph Assets

```csharp
// Create and save a new graph asset
var graphAsset = ScriptableObject.CreateInstance<ScriptGraphAsset>();
graphAsset.graph = FlowGraph.WithStartUpdate();
AssetDatabase.CreateAsset(graphAsset, "Assets/Graphs/NewGraph.asset");

// Mark as dirty after modifications
EditorUtility.SetDirty(graphAsset);

// Save to disk
AssetDatabase.SaveAssets();
// Or save only this specific asset (Unity 2020.3+)
AssetDatabase.SaveAssetIfDirty(graphAsset);
```

### Modifying Existing Graph Assets

```csharp
// Load existing asset
var asset = AssetDatabase.LoadAssetAtPath<ScriptGraphAsset>(
    "Assets/Graphs/ExistingGraph.asset"
);

// Modify the graph
FlowGraph graph = asset.graph;
graph.units.Add(new Start() { position = new Vector2(0, 0) });

// Mark dirty and save
EditorUtility.SetDirty(asset);
AssetDatabase.SaveAssets();
```

### Undo Support

For editor tools, use Undo for proper undo/redo support:

```csharp
// Record state before changes
Undo.RecordObject(graphAsset, "Add unit to graph");

// Make changes
graphAsset.graph.units.Add(newUnit);

// SetDirty is called automatically by Undo
```

---

## 13. Common Pitfalls and Workarounds

### 1. Forgetting to Mark Assets as Dirty

**Problem**: Changes to graph assets do not persist between Editor sessions.

**Solution**: Always call `EditorUtility.SetDirty(asset)` after modifying a graph asset, then `AssetDatabase.SaveAssets()`.

```csharp
// WRONG - changes may be lost
asset.graph.units.Add(newUnit);

// CORRECT
asset.graph.units.Add(newUnit);
EditorUtility.SetDirty(asset);
AssetDatabase.SaveAssets();
```

### 2. Using Editor Script Nodes in Builds

**Problem**: If you use nodes that reference `UnityEditor` types in graphs included in builds, Unity generates errors during the build process. Visual Scripting uses C# reflection to generate nodes, and editor-only assemblies are stripped from builds.

**Solution**: Never include editor-only nodes in runtime graphs. If generating graphs programmatically, ensure no editor-only types are referenced.

### 3. Port Key Mismatches

**Problem**: Accessing ports with wrong key names causes runtime errors.

**Solution**: Check the unit's `Definition()` method for the exact port key names. Common patterns:
- Event units: `"trigger"` for their output
- Control flow: `"enter"` for input, `"exit"` for output
- If: `"enter"`, `"condition"`, `"ifTrue"`, `"ifFalse"`

### 4. Missing Unit Definition Calls

**Problem**: Units added to graphs may not have their ports defined yet.

**Solution**: Ports are defined when `Definition()` is called, which typically happens when the unit is added to a graph. If accessing ports immediately after creation, you may need to ensure the unit is properly initialized.

### 5. Control Output Multiple Connection Limitation

**Problem**: Control outputs only support a single connection. Connecting a second destination silently disconnects the first.

**Solution**: Use the `Sequence` unit to fan out to multiple paths from a single control flow:

```csharp
var seq = new Sequence();
// seq.multiOutputs[0], seq.multiOutputs[1], etc.
```

### 6. Value Input Multiple Connection Limitation

**Problem**: Value inputs only support a single incoming connection.

**Solution**: This is by design. If you need the same value in multiple places, connect the value output to each input separately.

### 7. SaveAssets Side Effects

**Problem**: `AssetDatabase.SaveAssets()` saves ALL dirty assets, not just the one you modified.

**Solution**: Use `AssetDatabase.SaveAssetIfDirty(asset)` (Unity 2020.3+) to save only the specific asset.

### 8. Thread Safety

**Problem**: All Unity API calls must happen on the main thread.

**Solution**: Never call graph creation/manipulation code from background threads. All `UnityEngine` and `UnityEditor` API calls must run on the main Unity thread.

### 9. Graph Variable Type Safety

**Problem**: Variables are not strongly typed; manual casting is required.

**Solution**: Always cast variable values when retrieving them:

```csharp
int health = (int)Variables.Object(player).Get("health");
```

### 10. Internal API Stability

**Problem**: Some programmatic graph creation APIs are marked as internal (`#if VISUAL_SCRIPT_INTERNAL`) and may change between versions.

**Solution**: Pin your Visual Scripting package version and test thoroughly after upgrades. Prefer using the public API surface where possible.

---

## 14. Complete Code Examples

### Example 1: Create a "Hello World" Graph

Creates a ScriptGraphAsset with a Start event connected to Debug.Log("Hello World"):

```csharp
using Unity.VisualScripting;
using UnityEditor;
using UnityEngine;

public static class HelloWorldGraphCreator
{
    [MenuItem("Tools/VS/Create Hello World Graph")]
    public static void Create()
    {
        // Create asset
        var asset = ScriptableObject.CreateInstance<ScriptGraphAsset>();
        var graph = new FlowGraph();

        // Create units
        var start = new Start()
        {
            position = new Vector2(0, 0)
        };

        var debugLog = new InvokeMember(
            new Member(typeof(Debug), nameof(Debug.Log), new[] { typeof(object) })
        )
        {
            position = new Vector2(300, 0)
        };

        var literal = new Literal(typeof(string), "Hello World!")
        {
            position = new Vector2(100, 150)
        };

        // Add units to graph
        graph.units.Add(start);
        graph.units.Add(debugLog);
        graph.units.Add(literal);

        // Connect Start -> Debug.Log (control flow)
        // Port keys depend on actual unit definitions
        // start.controlOutputs["trigger"] -> debugLog.controlInputs["enter"]

        // Connect Literal -> Debug.Log message parameter (value flow)
        // literal.valueOutputs["output"] -> debugLog.valueInputs["%message"]

        // Assign graph to asset
        asset.graph = graph;

        // Save
        AssetDatabase.CreateAsset(asset, "Assets/HelloWorld.asset");
        EditorUtility.SetDirty(asset);
        AssetDatabase.SaveAssets();

        Debug.Log("Hello World graph created at Assets/HelloWorld.asset");
    }
}
```

### Example 2: Create a Graph with Variables

```csharp
using Unity.VisualScripting;
using UnityEditor;
using UnityEngine;

public static class VariableGraphCreator
{
    [MenuItem("Tools/VS/Create Variable Graph")]
    public static void Create()
    {
        var asset = ScriptableObject.CreateInstance<ScriptGraphAsset>();
        var graph = new FlowGraph();

        // Declare graph variables with default values
        graph.variables.Set("health", 100);
        graph.variables.Set("maxHealth", 100);
        graph.variables.Set("playerName", "Hero");
        graph.variables.Set("isAlive", true);
        graph.variables.Set("moveSpeed", 5.0f);

        // Add Start and Update events
        graph.units.Add(new Start() { position = new Vector2(-200, -100) });
        graph.units.Add(new Update() { position = new Vector2(-200, 100) });

        asset.graph = graph;

        AssetDatabase.CreateAsset(asset, "Assets/VariableGraph.asset");
        EditorUtility.SetDirty(asset);
        AssetDatabase.SaveAssets();
    }
}
```

### Example 3: Attach Graph to GameObject

```csharp
using Unity.VisualScripting;
using UnityEditor;
using UnityEngine;

public static class GraphAttacher
{
    [MenuItem("Tools/VS/Create Object With Graph")]
    public static void CreateObjectWithGraph()
    {
        // Create a graph asset
        var asset = ScriptableObject.CreateInstance<ScriptGraphAsset>();
        asset.graph = FlowGraph.WithStartUpdate();

        string path = "Assets/Graphs/AutoGraph.asset";
        AssetDatabase.CreateAsset(asset, path);

        // Create a GameObject and attach ScriptMachine
        GameObject go = new GameObject("VS_Object");
        ScriptMachine sm = go.AddComponent<ScriptMachine>();
        sm.nest.source = GraphSource.Macro;
        sm.nest.macro = asset;

        // Mark scene as dirty
        UnityEditor.SceneManagement.EditorSceneManager.MarkSceneDirty(
            go.scene
        );

        AssetDatabase.SaveAssets();
        Selection.activeGameObject = go;
    }
}
```

### Example 4: Create a Subgraph

```csharp
using Unity.VisualScripting;
using UnityEditor;
using UnityEngine;

public static class SubgraphCreator
{
    [MenuItem("Tools/VS/Create Graph With Subgraph")]
    public static void Create()
    {
        // Create the subgraph asset
        var subAsset = ScriptableObject.CreateInstance<ScriptGraphAsset>();
        subAsset.graph = FlowGraph.WithInputOutput();
        AssetDatabase.CreateAsset(subAsset, "Assets/Graphs/SubGraph.asset");

        // Create the main graph asset
        var mainAsset = ScriptableObject.CreateInstance<ScriptGraphAsset>();
        var mainGraph = new FlowGraph();

        var start = new Start() { position = new Vector2(0, 0) };

        // Create SubgraphUnit referencing the subgraph asset
        var subgraphUnit = new SubgraphUnit(subAsset);
        subgraphUnit.position = new Vector2(300, 0);

        mainGraph.units.Add(start);
        mainGraph.units.Add(subgraphUnit);

        mainAsset.graph = mainGraph;
        AssetDatabase.CreateAsset(mainAsset, "Assets/Graphs/MainGraph.asset");

        EditorUtility.SetDirty(mainAsset);
        EditorUtility.SetDirty(subAsset);
        AssetDatabase.SaveAssets();
    }
}
```

### Example 5: Conditional Branch Graph

```csharp
using Unity.VisualScripting;
using UnityEditor;
using UnityEngine;

public static class BranchGraphCreator
{
    [MenuItem("Tools/VS/Create Branch Graph")]
    public static void Create()
    {
        var asset = ScriptableObject.CreateInstance<ScriptGraphAsset>();
        var graph = new FlowGraph();

        // Declare graph variable
        graph.variables.Set("shouldLog", true);

        // Create units
        var start = new Start() { position = new Vector2(0, 0) };
        var ifUnit = new If() { position = new Vector2(250, 0) };

        var debugLogTrue = new InvokeMember(
            new Member(typeof(Debug), nameof(Debug.Log), new[] { typeof(object) })
        ) { position = new Vector2(500, -100) };

        var debugLogFalse = new InvokeMember(
            new Member(typeof(Debug), nameof(Debug.Log), new[] { typeof(object) })
        ) { position = new Vector2(500, 100) };

        var literalTrue = new Literal(typeof(string), "Condition is TRUE")
        {
            position = new Vector2(300, -200)
        };
        var literalFalse = new Literal(typeof(string), "Condition is FALSE")
        {
            position = new Vector2(300, 200)
        };

        // Add all units
        graph.units.Add(start);
        graph.units.Add(ifUnit);
        graph.units.Add(debugLogTrue);
        graph.units.Add(debugLogFalse);
        graph.units.Add(literalTrue);
        graph.units.Add(literalFalse);

        // Connections would be created here using the patterns from Section 6
        // start -> ifUnit (control)
        // ifUnit.ifTrue -> debugLogTrue (control)
        // ifUnit.ifFalse -> debugLogFalse (control)
        // literalTrue -> debugLogTrue message (value)
        // literalFalse -> debugLogFalse message (value)

        asset.graph = graph;
        AssetDatabase.CreateAsset(asset, "Assets/Graphs/BranchGraph.asset");
        EditorUtility.SetDirty(asset);
        AssetDatabase.SaveAssets();
    }
}
```

---

## 15. Sources and References

### Official Documentation

- [Visual Scripting Overview](https://unity.com/features/unity-visual-scripting)
- [FlowGraph API (v1.8)](https://docs.unity3d.com/Packages/com.unity.visualscripting@1.8/api/Unity.VisualScripting.FlowGraph.html)
- [ScriptGraphAsset API (v1.8)](https://docs.unity3d.com/Packages/com.unity.visualscripting@1.8/api/Unity.VisualScripting.ScriptGraphAsset.html)
- [ScriptGraphAsset API (v1.9)](https://docs.unity3d.com/Packages/com.unity.visualscripting@1.9/api/Unity.VisualScripting.ScriptGraphAsset.html)
- [StateMachine API (v1.8)](https://docs.unity3d.com/Packages/com.unity.visualscripting@1.8/api/Unity.VisualScripting.StateMachine.html)
- [Variables Documentation (v1.8)](https://docs.unity3d.com/Packages/com.unity.visualscripting@1.8/manual/vs-variables.html)
- [Variables Documentation (v1.7)](https://docs.unity3d.com/Packages/com.unity.visualscripting@1.7/manual/vs-variables.html)
- [Script Machines and State Machines (v1.8)](https://docs.unity3d.com/Packages/com.unity.visualscripting@1.8/manual/vs-graph-machine-types.html)
- [Subgraphs and State Units (v1.7)](https://docs.unity3d.com/Packages/com.unity.visualscripting@1.7/manual/vs-nesting-subgraphs-state-units.html)
- [Custom Node Ports (v1.9)](https://docs.unity3d.com/Packages/com.unity.visualscripting@1.9/manual/vs-create-custom-node-add-ports.html)
- [Creating Visual Script Graph Units (v1.6)](https://docs.unity3d.com/Packages/com.unity.visualscripting@1.6/manual/vs-creating-visual-script-graph-unit.html)
- [Variables API (Bolt 1.4 legacy)](https://docs.unity3d.com/bolt/1.4/manual/bolt-variables-api.html)
- [Known Issues: Editor Script Functions (v1.9)](https://docs.unity3d.com/Packages/com.unity.visualscripting@1.9/manual/vs-editor-script-issues.html)
- [Connecting Nodes (v1.9)](https://docs.unity3d.com/Packages/com.unity.visualscripting@1.9/manual/vs-creating-connections.html)
- [InvokeMember API (v1.8)](https://docs.unity3d.com/Packages/com.unity.visualscripting@1.8/api/Unity.VisualScripting.InvokeMember.html)
- [GetMember API (v1.7)](https://docs.unity3d.com/Packages/com.unity.visualscripting@1.7/api/Unity.VisualScripting.GetMember.html)
- [SetMember API (v1.9)](https://docs.unity3d.com/Packages/com.unity.visualscripting@1.9/api/Unity.VisualScripting.SetMember.html)
- [MemberUnit API (v1.6)](https://docs.unity3d.com/Packages/com.unity.visualscripting@1.6/api/Unity.VisualScripting.MemberUnit.html)

### Unity Discussions / Forums

- [Is there a scriptable way to automate adding Visual Scripting nodes?](https://discussions.unity.com/t/is-there-a-scriptable-way-to-automate-adding-visual-scripting-nodes-to-a-script-graph/908134)
- [Create graph from Asset Data](https://discussions.unity.com/t/create-graph-from-asset-data/939298)
- [Add Visual Script component at runtime using C#](https://discussions.unity.com/t/add-visual-script-component-at-runtime-using-c/917855)
- [Running ScriptGraphAsset with Script](https://discussions.unity.com/t/running-scriptgraphasset-with-script/248139)

### Source Code Reference

- [needle-mirror/com.unity.visualscripting (GitHub mirror)](https://github.com/needle-mirror/com.unity.visualscripting)
  - `Runtime/VisualScripting.Flow/Framework/Nesting/GraphInput.cs`
  - `Runtime/VisualScripting.Flow/Framework/Nesting/GraphOutput.cs`
  - `Editor/VisualScripting.Flow/EmptyGraphWindow.cs` (CreateScriptGraphAsset, CreateStateGraphAsset)
  - `Runtime/VisualScripting.Core/Graphs/Graph.cs`
  - `Runtime/VisualScripting.Flow/FlowGraph.cs`

### Editor Scripting Best Practices

- [EditorUtility.SetDirty API](https://docs.unity3d.com/ScriptReference/EditorUtility.SetDirty.html)
- [AssetDatabase.SaveAssets API](https://docs.unity3d.com/ScriptReference/AssetDatabase.SaveAssets.html)
- [AssetDatabase.SaveAssetIfDirty API](https://docs.unity3d.com/ScriptReference/AssetDatabase.SaveAssetIfDirty.html)
- [AssetDatabase.CreateAsset API](https://docs.unity3d.com/6000.1/Documentation/ScriptReference/AssetDatabase.CreateAsset.html)

---

*Report generated: 2026-02-28*
*Based on Unity Visual Scripting package versions 1.5 through 1.9*
