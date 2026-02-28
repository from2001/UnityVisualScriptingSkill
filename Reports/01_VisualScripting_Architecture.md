# Unity Visual Scripting Architecture Report

## 1. Overview

Unity Visual Scripting (formerly "Bolt") is a node-based visual programming system integrated into the Unity Editor. It enables developers to create gameplay logic, state machines, and event-driven systems using a graphical node editor rather than writing C# code. The system compiles to executable code and supports both runtime execution and AOT (Ahead-of-Time) compilation for platforms like IL2CPP.

**Primary Namespace:** `Unity.VisualScripting`

**Key Assemblies:**
| Assembly | Purpose |
|----------|---------|
| `Unity.VisualScripting.Core` | Foundation types, interfaces, base classes |
| `Unity.VisualScripting.Flow` | Flow graph execution engine, runtime |
| `Unity.VisualScripting.Tests.Editor` | Testing infrastructure |

---

## 2. Core Architecture

### 2.1 Dual-Graph Architecture

Unity Visual Scripting supports two distinct graph paradigms:

| Graph Type | Asset Type | Machine Component | Purpose |
|------------|-----------|-------------------|---------|
| **Script Graph** (Flow Graph) | `ScriptGraphAsset` | `ScriptMachine` | Sequential flow-based logic (like a flowchart) |
| **State Graph** | `StateGraphAsset` | `StateMachine` | State machine logic with states and transitions |

Both graph types share common serialization, migration, and variable infrastructure.

### 2.2 Class Hierarchy

```
IGraphElementWithDebugData
  └── IUnit
        └── Unit (abstract base class)
              ├── EventUnit (base for event-driven units)
              ├── NesterUnit<TGraph, TMacro> (for subgraphs)
              │     └── StateUnit (embeds StateGraph in FlowGraph)
              ├── GraphInput (subgraph interface: inputs)
              ├── GraphOutput (subgraph interface: outputs)
              ├── GetGraph<TGraph, TGraphAsset, TMachine>
              ├── SetGraph<TGraph, TMacro, TMachine>
              ├── HasGraph<TGraph, TMacro, TMachine>
              └── GetGraphs<TGraph, TGraphAsset, TMachine>

GraphElement<TGraph>
  └── UnitConnection<TSourcePort, TDestinationPort>
        ├── ControlConnection
        └── ValueConnection

Macro<TGraph> (ScriptableObject)
  ├── ScriptGraphAsset (holds a FlowGraph)
  └── StateGraphAsset (holds a StateGraph)

Machine<TGraph, TGraphAsset> (MonoBehaviour component)
  ├── ScriptMachine (executes FlowGraphs)
  └── StateMachine (executes StateGraphs)
```

### 2.3 Naming Evolution (Bolt to Unity Visual Scripting)

Since its transition from Bolt, several terms were renamed:
| Old Term (Bolt / pre-1.7) | New Term (Unity VS) |
|---------------------------|---------------------|
| Flow Graph | Script Graph |
| Flow Machine | Script Machine |
| SuperUnit | Subgraph |
| Units | Nodes (UI term, but `Unit` remains in code) |
| Control Input/Output | Trigger Input/Output (UI term) |
| Value Input/Output | Data Input/Output (UI term) |

> **Note:** In the C# API, the original names (`Unit`, `ControlInput`, `ControlOutput`, `ValueInput`, `ValueOutput`) are still used.

---

## 3. Graph Structure Internals

### 3.1 FlowGraph (Script Graph)

A `FlowGraph` is the internal graph object held by a `ScriptGraphAsset`. It contains:

- **`units`** - Collection of `IUnit` instances (the nodes)
- **`controlConnections`** - Collection of `ControlConnection` objects (execution flow wires)
- **`valueConnections`** - Collection of `ValueConnection` objects (data wires)
- **Graph variables** - Local variables scoped to this graph

### 3.2 Units (Nodes)

Every node in a graph is a `Unit`. Each unit exposes **ports** for connections:

| Port Type | Class | Direction | Purpose |
|-----------|-------|-----------|---------|
| **ControlInput** | `ControlInput` | Incoming | Receives execution flow (when to execute) |
| **ControlOutput** | `ControlOutput` | Outgoing | Emits execution flow (what to execute next) |
| **ValueInput** | `ValueInput` | Incoming | Receives data values |
| **ValueOutput** | `ValueOutput` | Outgoing | Provides data values |

Units access their ports via collections:
- `unit.controlInputs` - All control input ports
- `unit.controlOutputs` - All control output ports
- `unit.valueInputs` - All value input ports
- `unit.valueOutputs` - All value output ports

### 3.3 Connections

Two connection types link units together:

**ControlConnection** - Links a `ControlOutput` to a `ControlInput`:
```csharp
graph.controlConnections.Add(new ControlConnection(sourceUnit.trigger, destUnit.enter));
```
- A `ControlOutput` can only have **one** outgoing control connection.

**ValueConnection** - Links a `ValueOutput` to a `ValueInput`:
```csharp
graph.valueConnections.Add(new ValueConnection(sourceUnit.output, destUnit.input));
```
- A `ValueInput` can only have **one** incoming value connection.
- Type compatibility is checked between source and destination ports.

### 3.4 Unit Definition Lifecycle

Each unit has a definition lifecycle:
1. `canDefine` - Whether the unit can be defined in its current state
2. `Define()` - Sets up the unit's ports and connections
3. `EnsureDefined()` - Ensures the unit has been defined
4. `isDefined` / `failedToDefine` / `definitionException` - Status properties

---

## 4. Key Unit Types and Port APIs

### 4.1 Event Units

Event units trigger execution based on Unity lifecycle events or custom events.

| Unit Class | Description | Key Ports |
|------------|-------------|-----------|
| `Start` | Unity Start event | `trigger` (ControlOutput) |
| `Update` | Unity Update event | `trigger` (ControlOutput) |
| `FixedUpdate` | Unity FixedUpdate | `trigger` (ControlOutput) |
| `LateUpdate` | Unity LateUpdate | `trigger` (ControlOutput) |
| `OnCollisionEnter` | Physics collision | `trigger` (ControlOutput), collision data ports |
| `OnCollisionExit` | Physics collision end | `trigger` (ControlOutput) |
| `OnTriggerEnter` | Trigger zone enter | `trigger` (ControlOutput) |
| `OnTriggerExit` | Trigger zone exit | `trigger` (ControlOutput) |

**Usage:**
```csharp
var onUpdate = new Update();
graph.units.Add(onUpdate);
// Connect: onUpdate.trigger -> someUnit.enter
```

### 4.2 Member Access Units

These units access C# members (fields, properties, methods) via reflection.

#### Member Class Construction

The `Member` class describes which C# member to access:
```csharp
// Property access
new Member(typeof(Time), nameof(Time.deltaTime))

// Method with specific parameter types
new Member(typeof(Transform), "Rotate", new[] { typeof(float), typeof(float), typeof(float) })
```

Member types: `Field`, `Property`, `Method`, `Constructor`

#### GetMember

Reads a field or property value.

| Port | Type | Description |
|------|------|-------------|
| `target` | ValueInput | Object instance (omitted for static members) |
| `value` | ValueOutput | The retrieved value |

```csharp
var getDeltaTime = new GetMember(new Member(typeof(Time), nameof(Time.deltaTime)));
graph.units.Add(getDeltaTime);
// Access: getDeltaTime.value (ValueOutput)
```

#### SetMember

Writes a field or property value.

| Port | Type | Description |
|------|------|-------------|
| `enter` | ControlInput | Execution trigger |
| `exit` | ControlOutput | Execution continuation |
| `target` | ValueInput | Object instance (omitted for static) |
| `input` | ValueInput | Value to assign |
| `output` | ValueOutput | The assigned value (pass-through) |

#### InvokeMember

Calls a method or constructor.

| Port | Type | Description |
|------|------|-------------|
| `enter` | ControlInput | Execution trigger |
| `exit` | ControlOutput | Execution continuation |
| `target` | ValueInput | Object instance (omitted for static) |
| `result` | ValueOutput | Method return value (if any) |
| `inputParameters[n]` | ValueInput | Method parameter at index n |
| `outputParameters[n]` | ValueOutput | Out/ref parameter at index n |

```csharp
var rotateMember = new Member(typeof(Transform), "Rotate",
    new[] { typeof(float), typeof(float), typeof(float) });
var rotate = new InvokeMember(rotateMember);
graph.units.Add(rotate);

// Ports:
//   rotate.enter           - ControlInput
//   rotate.exit            - ControlOutput (implicit, flows after invoke)
//   rotate.inputParameters[0] - ValueInput (xAngle)
//   rotate.inputParameters[1] - ValueInput (yAngle)
//   rotate.inputParameters[2] - ValueInput (zAngle)
```

### 4.3 Literal Units

Represent constant values in the graph.

```csharp
var speed = new Literal(typeof(float), 10f);
graph.units.Add(speed);
// Port: speed.output (ValueOutput)
```

### 4.4 Math Units

Perform mathematical operations.

| Unit Class | Ports |
|------------|-------|
| `ScalarAdd` | `a` (ValueInput), `b` (ValueInput), `sum` (ValueOutput) |
| `ScalarMultiply` | `a` (ValueInput), `b` (ValueInput), `product` (ValueOutput) |
| `ScalarSubtract` | `a` (ValueInput), `b` (ValueInput), `difference` (ValueOutput) |
| `ScalarDivide` | `a` (ValueInput), `b` (ValueInput), `quotient` (ValueOutput) |
| `GenericAdd` | Generic addition |
| `GenericSubtract` | Generic subtraction |
| `GenericMultiply` | Generic multiplication |
| `GenericDivide` | Generic division |

Additional math categories: Vector2, Vector3, Vector4 operations, Mathf members.

```csharp
var multiply = new ScalarMultiply();
graph.units.Add(multiply);
// multiply.a       - ValueInput
// multiply.b       - ValueInput
// multiply.product - ValueOutput
```

### 4.5 Flow Control Units

Control execution flow in the graph.

| Unit Class | Description | Key Ports |
|------------|-------------|-----------|
| `If` (Branch) | Conditional branch | `enter`, `condition`, `ifTrue`, `ifFalse` |
| `SelectOnFlow` | Select value by flow | Dynamic control inputs, value inputs |
| `SelectOnString` | Select by string match | String-based branching |
| `While` | While loop | `enter`, `condition`, `body`, `exit` |
| `For` | For loop | `enter`, `firstIndex`, `lastIndex`, `body`, `exit`, `index` |
| `ForEach` | Iterate collection | `enter`, `collection`, `body`, `exit`, `item` |
| `Sequence` | Execute multiple paths | `enter`, multiple outputs |

### 4.6 Variable Units

Access Visual Scripting variables across different scopes.

| Unit Class | Description |
|------------|-------------|
| `GetVariable` | Retrieves a variable value |
| `SetVariable` | Assigns a variable value |
| `IsVariableDefined` | Checks if a variable exists |

Variable scopes (via `VariableKind` enum):
- **Flow** - Exists only during current flow execution
- **Graph** - Scoped to the current graph
- **Object** - Scoped to the GameObject
- **Scene** - Shared across the scene
- **Application** - Persists across scenes
- **Saved** - Persists across sessions (PlayerPrefs)

### 4.7 Logic Units

| Unit Class | Description |
|------------|-------------|
| `And` | Logical AND |
| `Or` | Logical OR |
| `Not` / `Negate` | Logical negation |
| `Equal` | Equality comparison |
| `NotEqual` | Inequality comparison |
| `Greater` | Greater than |
| `Less` | Less than |
| `GreaterOrEqual` | Greater than or equal |
| `LessOrEqual` | Less than or equal |

### 4.8 Other Unit Categories

- **Collections** - List and Dictionary operations
- **String** - String manipulation units
- **Conversion** - Type conversion units
- **Time** - Time-related units
- **Enum** - Enum literal units
- **This** - Represents the current GameObject

---

## 5. ScriptGraphAsset vs. StateGraphAsset

### 5.1 ScriptGraphAsset (Flow-Based Programming)

A `ScriptGraphAsset` is a `ScriptableObject` (inheriting from `Macro<FlowGraph>`) that stores a `FlowGraph`. It represents sequential, flow-based logic similar to a flowchart.

**Key characteristics:**
- Contains a `FlowGraph` accessible via the `graph` property
- Executed by the `ScriptMachine` component
- Units connected by control connections define execution order
- Value connections pass data between units
- Supports subgraphs for modular design

**Creation:**
```csharp
var graphAsset = ScriptableObject.CreateInstance<ScriptGraphAsset>();
var graph = graphAsset.graph; // Access the FlowGraph
// Add units, connections...
AssetDatabase.CreateAsset(graphAsset, "Assets/MyGraph.asset");
```

### 5.2 StateGraphAsset (State Machine Programming)

A `StateGraphAsset` is a `ScriptableObject` (inheriting from `Macro<StateGraph>`) that stores a `StateGraph`. It represents a finite state machine with states and transitions.

**Key characteristics:**
- Contains a `StateGraph` accessible via the `graph` property
- Executed by the `StateMachine` component
- Each state can contain its own embedded `FlowGraph` (with Enter, Update, Exit events)
- Transitions between states are driven by conditions

**State types within a StateGraph:**
| State Type | Description |
|------------|-------------|
| `FlowState` | A state containing an embedded FlowGraph with Enter/Update/Exit events |
| `SuperState` | A state containing an embedded StateGraph (hierarchical state machine) |
| `AnyState` | Special state that can transition to any other state regardless of current state |

**Transitions:**
- `StateTransition` objects define connections between states
- `FlowStateTransition` is the concrete transition type with a trigger condition
- `AnyState` cannot be a destination (only a source)

### 5.3 Comparison Table

| Feature | ScriptGraphAsset | StateGraphAsset |
|---------|-----------------|-----------------|
| Internal Graph | `FlowGraph` | `StateGraph` |
| Machine Component | `ScriptMachine` | `StateMachine` |
| Programming Model | Sequential flow | State machine |
| Contains | Units + Connections | States + Transitions |
| Use Case | Linear logic, calculations, event responses | AI behaviors, game states, animation states |

---

## 6. Machine Components and Runtime Execution

### 6.1 ScriptMachine

`ScriptMachine` is a `MonoBehaviour` component attached to a `GameObject` that executes a `FlowGraph`.

```csharp
var machine = gameObject.AddComponent<ScriptMachine>();
machine.nest.source = GraphSource.Macro;
machine.nest.macro = graphAsset; // ScriptGraphAsset reference
```

### 6.2 StateMachine

`StateMachine` is a `MonoBehaviour` component that executes a `StateGraph`.

```csharp
var machine = gameObject.AddComponent<StateMachine>();
machine.nest.source = GraphSource.Macro;
machine.nest.macro = stateGraphAsset; // StateGraphAsset reference
```

### 6.3 GraphSource and GraphNest

The `GraphNest<TGraph, TMacro>` class manages graph assignment on machines:

| Property | Description |
|----------|-------------|
| `nest.source` | `GraphSource.Macro` (external asset) or `GraphSource.Embed` (embedded in component) |
| `nest.macro` | Reference to the graph asset (when source is Macro) |
| `nest.embed` | The embedded graph (when source is Embed) |

### 6.4 Variables Component

The `Variables` component provides runtime variable access on GameObjects:

```csharp
var vars = gameObject.GetComponent<Variables>();
var decl = vars.declarations.GetDeclaration("velocity");
float vel = (float)decl.value;
decl.value = vel * 2f;
```

---

## 7. Subgraphs (SuperUnits)

Subgraphs allow nesting one graph inside another for modular design.

### 7.1 NesterUnit

`NesterUnit<TGraph, TMacro>` is the abstract base class for units that contain a nested graph. The `StateUnit` is a concrete example that nests a `StateGraph` inside a `FlowGraph`.

**StateUnit ports:**
- Control inputs for `Start` and `Stop`
- Control outputs for `Started` and `Stopped`

### 7.2 GraphInput and GraphOutput

Inside a subgraph, `GraphInput` and `GraphOutput` special units define the interface with the parent graph:
- `GraphInput` fetches values from the parent `NesterUnit`
- `GraphOutput` passes values back to the parent

---

## 8. Event Bus System

The Event Bus provides decoupled communication between C# code and Visual Scripting graphs.

### 8.1 Core API

```csharp
// Register a handler
EventHook hook = new EventHook("MyEvent");
Action<EmptyEventArgs> handler = _ => DoSomething();
EventBus.Register(hook, handler);

// Trigger globally
EventBus.Trigger("MyEvent");

// Trigger targeted at a specific machine
EventBus.Trigger(new EventHook("MyEvent", scriptMachine));

// Unregister
EventBus.Unregister(hook, handler);
```

### 8.2 Custom Event Units

Create custom event nodes by extending `MachineEventUnit<T>`:

```csharp
[UnitTitle("On My Custom Event")]
public class MyCustomEvent : MachineEventUnit<EmptyEventArgs>
{
    protected override string hookName => "MyCustomEventName";
}
```

---

## 9. Programmatic Graph Creation Pattern

The complete pattern for creating and assigning a graph via editor scripts:

```csharp
#if UNITY_EDITOR
using UnityEditor;
using UnityEngine;
using Unity.VisualScripting;

public static class GraphCreator
{
    [MenuItem("Tools/Create My Graph")]
    public static void Create()
    {
        // 1. Create the asset
        var graphAsset = ScriptableObject.CreateInstance<ScriptGraphAsset>();
        var graph = graphAsset.graph;

        // 2. Create units (nodes)
        var onUpdate = new Update();
        graph.units.Add(onUpdate);
        onUpdate.position = new Vector2(-300, 0);

        var getDeltaTime = new GetMember(new Member(typeof(Time), nameof(Time.deltaTime)));
        graph.units.Add(getDeltaTime);

        var speed = new Literal(typeof(float), 10f);
        graph.units.Add(speed);

        var multiply = new ScalarMultiply();
        graph.units.Add(multiply);

        var rotateMember = new Member(typeof(Transform), "Rotate",
            new[] { typeof(float), typeof(float), typeof(float) });
        var rotate = new InvokeMember(rotateMember);
        graph.units.Add(rotate);

        // 3. Connect control flow
        graph.controlConnections.Add(new ControlConnection(onUpdate.trigger, rotate.enter));

        // 4. Connect data flow
        graph.valueConnections.Add(new ValueConnection(speed.output, multiply.a));
        graph.valueConnections.Add(new ValueConnection(getDeltaTime.value, multiply.b));
        graph.valueConnections.Add(new ValueConnection(multiply.product, rotate.inputParameters[0]));

        // 5. Save the asset
        AssetDatabase.CreateAsset(graphAsset, "Assets/MyGraph.asset");
        AssetDatabase.SaveAssets();

        // 6. Optionally assign to a GameObject
        var go = GameObject.Find("MyObject");
        if (go != null)
        {
            var machine = go.GetComponent<ScriptMachine>();
            if (machine == null)
                machine = go.AddComponent<ScriptMachine>();
            machine.nest.source = GraphSource.Macro;
            machine.nest.macro = graphAsset;
            EditorUtility.SetDirty(go);
        }
    }
}
#endif
```

**Key steps:**
1. `ScriptableObject.CreateInstance<ScriptGraphAsset>()` - Create the asset
2. `graphAsset.graph` - Access the `FlowGraph`
3. `graph.units.Add(unit)` - Add units to the graph
4. `graph.controlConnections.Add(new ControlConnection(...))` - Wire control flow
5. `graph.valueConnections.Add(new ValueConnection(...))` - Wire data flow
6. `AssetDatabase.CreateAsset(...)` - Persist to disk
7. `machine.nest.source = GraphSource.Macro` + `machine.nest.macro = graphAsset` - Assign to a machine

---

## 10. Build Pipeline and AOT Support

Unity Visual Scripting includes AOT compilation support for platforms that require it (IL2CPP, iOS, WebGL, etc.):

- **AOT Stub Generation** - Automatically generates stubs for all nodes used in graphs
- **link.xml Generation** - Prevents managed code stripping from removing needed types
- **Platform Support** - iOS, Android, WebGL, VisionOS, consoles
- **Performance** - String data unloading after deserialization, domain reload cost < 1ms when not in use
