# Unity Visual Scripting - Unit Types Catalog

Comprehensive catalog of all important Unit types available for programmatic Visual Scripting graph creation. All classes are in the `Unity.VisualScripting` namespace unless stated otherwise.

---

## Table of Contents

1. [Event Units](#1-event-units)
2. [Flow Control Units](#2-flow-control-units)
3. [Variable Units](#3-variable-units)
4. [Math and Logic Units](#4-math-and-logic-units)
5. [Member Access Units](#5-member-access-units)
6. [Literal Units](#6-literal-units)
7. [Type Conversion](#7-type-conversion)
8. [Special Units (SubGraph, StateUnit)](#8-special-units)
9. [Time-Related Units](#9-time-related-units)
10. [Null and Comparison Units](#10-null-and-comparison-units)
11. [String Units](#11-string-units)
12. [Collection/List Units](#12-collectionlist-units)
13. [Vector Math Units](#13-vector-math-units)
14. [Port System and Connections](#14-port-system-and-connections)

---

## 1. Event Units

Event units inherit from `GameObjectEventUnit<T>` or `MachineEventUnit<T>` and define a `hookName` constant from the `EventHooks` class. All event units have at least a `ControlOutput` named `trigger`.

### 1.1 Lifecycle Events

| Class Name | Hook Name | Description |
|---|---|---|
| `Start` | `EventHooks.Start` | Called once when the script starts |
| `Update` | `EventHooks.Update` | Called every frame |
| `FixedUpdate` | `EventHooks.FixedUpdate` | Called on fixed timestep |
| `LateUpdate` | `EventHooks.LateUpdate` | Called after all Update calls |
| `OnEnable` | `EventHooks.OnEnable` | Called when the object becomes enabled |
| `OnDisable` | `EventHooks.OnDisable` | Called when the object becomes disabled |
| `OnDestroy` | `EventHooks.OnDestroy` | Called when the object is destroyed |

**Common Ports:**
- `trigger` (ControlOutput) - Fires when the event occurs

**Code Example:**
```csharp
var startEvent = new Start();
graph.units.Add(startEvent);
```

### 1.2 Physics Events (3D)

| Class Name | Hook Name | Key Value Outputs |
|---|---|---|
| `OnTriggerEnter` | `EventHooks.OnTriggerEnter` | `collider` (Collider) |
| `OnTriggerExit` | `EventHooks.OnTriggerExit` | `collider` (Collider) |
| `OnTriggerStay` | `EventHooks.OnTriggerStay` | `collider` (Collider) |
| `OnCollisionEnter` | `EventHooks.OnCollisionEnter` | `collider`, `contacts`, `impulse`, `relativeVelocity`, `data` (Collision) |
| `OnCollisionExit` | `EventHooks.OnCollisionExit` | `collider`, `data` (Collision) |
| `OnCollisionStay` | `EventHooks.OnCollisionStay` | `collider`, `data` (Collision) |
| `OnControllerColliderHit` | `EventHooks.OnControllerColliderHit` | hit data |
| `OnJointBreak` | `EventHooks.OnJointBreak` | `breakForce` (float) |
| `OnParticleCollision` | `EventHooks.OnParticleCollision` | `other` (GameObject), `collisionEvents` (List) |

Collision event units inherit from `CollisionEventUnit` (abstract base class).

### 1.3 Physics Events (2D)

| Class Name | Hook Name |
|---|---|
| `OnTriggerEnter2D` | `EventHooks.OnTriggerEnter2D` |
| `OnTriggerExit2D` | `EventHooks.OnTriggerExit2D` |
| `OnTriggerStay2D` | `EventHooks.OnTriggerStay2D` |
| `OnCollisionEnter2D` | `EventHooks.OnCollisionEnter2D` |
| `OnCollisionExit2D` | `EventHooks.OnCollisionExit2D` |
| `OnCollisionStay2D` | `EventHooks.OnCollisionStay2D` |
| `OnJointBreak2D` | `EventHooks.OnJointBreak2D` |

2D collision units inherit from `CollisionEvent2DUnit`.

### 1.4 Input Events

#### OnKeyboardInput
- **Class:** `OnKeyboardInput`
- **Value Inputs:**
  - `key` (KeyCode, default: `KeyCode.Space`)
  - `action` (PressState, default: `PressState.Down`)
- **Control Output:** `trigger`

#### OnMouseDown / OnMouseUp / OnMouseEnter / OnMouseExit
- Triggered by `UnityMessageListener` via `EventBus.Trigger(EventHooks.OnMouseDown, gameObject)`

#### OnInputSystemEvent (New Input System)
- **Namespace:** `Unity.VisualScripting.InputSystem`
- **Class:** `OnInputSystemEvent` (abstract base)
- **Value Inputs:**
  - `InputAction` - the input action asset to monitor
  - `InputActionChangeType` - enum: `OnPressed`, `OnHold`, `OnReleased`

### 1.5 Custom Events

#### CustomEvent
- **Class:** `CustomEvent`
- **Properties:**
  - `argumentCount` (int) - number of dynamic argument output ports
- **Value Inputs:**
  - `name` (string) - event name
- **Value Outputs:**
  - `argumentPorts` - dynamically created based on `argumentCount` (named `arg_0`, `arg_1`, etc.)
- **Control Output:** `trigger`

**Code Example:**
```csharp
var customEvent = new CustomEvent();
customEvent.argumentCount = 2;
graph.units.Add(customEvent);
```

#### TriggerCustomEvent
- **Class:** `TriggerCustomEvent`
- **Properties:**
  - `argumentCount` (int)
- **Control Input:** `enter`
- **Value Inputs:**
  - `name` (string) - name of the custom event to trigger
  - `target` (GameObject) - target object
  - `arguments` - dynamically created ValueInput ports
- **Control Output:** `exit`

**Code Example:**
```csharp
var trigger = new TriggerCustomEvent();
trigger.argumentCount = 2;
graph.units.Add(trigger);
```

### 1.6 Application Events

| Class Name | Hook Name |
|---|---|
| `OnApplicationQuit` | `EventHooks.OnApplicationQuit` |
| `OnApplicationPause` | `EventHooks.OnApplicationPause` |
| `OnApplicationFocus` | `EventHooks.OnApplicationFocus` |

Managed by `GlobalMessageListener` (not per-GameObject).

### 1.7 Animation Events

| Class Name | Hook Name |
|---|---|
| `AnimationEvent` | `EventHooks.AnimationEvent` |
| `OnAnimatorMove` | `EventHooks.OnAnimatorMove` |
| `OnAnimatorIK` | `EventHooks.OnAnimatorIK` |

### 1.8 GUI / UI Events

| Class Name | Hook Name |
|---|---|
| `OnGUI` | `EventHooks.OnGUI` |
| `OnButtonClick` | `EventHooks.OnButtonClick` |
| `OnToggleValueChanged` | `EventHooks.OnToggleValueChanged` |
| `OnSliderValueChanged` | `EventHooks.OnSliderValueChanged` |
| `OnDropdownValueChanged` | `EventHooks.OnDropdownValueChanged` |
| `OnInputFieldValueChanged` | `EventHooks.OnInputFieldValueChanged` |
| `OnInputFieldEndEdit` | `EventHooks.OnInputFieldEndEdit` |

### 1.9 BoltUnityEvent
- **Class:** `BoltUnityEvent`
- Triggered when a UnityEvent points to `TriggerUnityEvent`

---

## 2. Flow Control Units

### 2.1 If (Branch)

- **Class:** `If`
- **Control Input:** `enter`
- **Value Input:** `condition` (bool)
- **Control Outputs:** `ifTrue`, `ifFalse`

**Code Example:**
```csharp
var ifUnit = new If();
graph.units.Add(ifUnit);
```

### 2.2 Sequence

- **Class:** `Sequence`
- **Properties:**
  - `outputCount` (int, default: 2, range: 1-10)
- **Control Input:** `enter`
- **Control Outputs:** Dynamically created (e.g., `0`, `1`, `2`, ...)

Executes each output port sequentially in order.

**Code Example:**
```csharp
var seq = new Sequence();
seq.outputCount = 3;
graph.units.Add(seq);
```

### 2.3 For Loop

- **Class:** `For`
- **Control Input:** `enter`
- **Value Inputs:**
  - `firstIndex` (int) - starting index (inclusive)
  - `lastIndex` (int) - ending index (exclusive)
  - `step` (int) - increment value
- **Value Output:** `currentIndex` (int)
- **Control Outputs:** `body`, `exit`

### 2.4 For Each Loop

- **Class:** `ForEach`
- **Control Input:** `enter`
- **Value Input:** `collection` (IEnumerable)
- **Value Outputs:**
  - `currentIndex` (int)
  - `currentKey` (object) - for dictionaries
  - `currentItem` (object)
- **Control Outputs:** `body`, `exit`

### 2.5 While Loop

- **Class:** `While`
- **Control Input:** `enter`
- **Value Input:** `condition` (bool)
- **Control Outputs:** `body`, `exit`

### 2.6 Switch On Enum

- **Class:** `SwitchOnEnum`
- **Control Input:** `enter`
- **Value Input:** `enum` (Enum)
- **Control Outputs:** Dynamically created for each enum value (`branches`)

### 2.7 Select (Ternary)

- **Class:** `SelectUnit`
- **Value Inputs:** `condition` (bool), `ifTrue` (object), `ifFalse` (object)
- **Value Output:** `selection`

### 2.8 Select On Enum

- **Class:** `SelectOnEnum`
- **Value Inputs:** `selector` (Enum), `branches` (dynamically created per enum value)
- **Value Output:** `selection`

### 2.9 Select On Flow

- **Class:** `SelectOnFlow`
- **Control Inputs:** Dynamically created `branches`
- **Value Inputs:** Corresponding value inputs per branch
- **Control Output:** `exit`
- **Value Output:** `selection`

### 2.10 Once

- **Class:** `Once`
- **Control Inputs:** `enter`, `reset`
- **Control Outputs:** `once`, `after`

Executes `once` only on first trigger; subsequent calls go to `after`. `reset` makes it fire `once` again.

### 2.11 Toggle Value

- **Class:** `ToggleValue`
- **Properties:** `startOn` (bool)
- **Control Inputs:** `turnOn`, `turnOff`, `toggle`
- **Value Inputs:** `onValue`, `offValue`
- **Value Output:** (returns on/off value based on state)

### 2.12 Toggle Flow

- **Class:** `ToggleFlow`
- Switches flow on/off based on toggle state

---

## 3. Variable Units

All variable units inherit from `UnifiedVariableUnit`. The `kind` property uses the `VariableKind` enum, and `name` specifies the variable name.

### 3.1 VariableKind Enum

| Value | Scope | Description |
|---|---|---|
| `VariableKind.Flow` | Flow | Temporary, local to execution flow |
| `VariableKind.Graph` | Graph | Local to current graph |
| `VariableKind.Object` | Object | Shared across a GameObject |
| `VariableKind.Scene` | Scene | Shared across the current scene |
| `VariableKind.Application` | Application | Shared across scenes, reset on quit |
| `VariableKind.Saved` | Saved | Persists after quit (no Unity object refs) |

### 3.2 GetVariable

- **Class:** `GetVariable`
- **Properties:**
  - `kind` (VariableKind)
  - `defaultName` (string) - initial name for the variable
  - `specifyFallback` (bool) - if true, adds fallback port
- **Value Inputs:**
  - `name` (string) - variable name
  - `@object` (GameObject) - only when `kind == VariableKind.Object`
  - `fallback` (object) - only when `specifyFallback == true`
- **Value Output:** `value` (object)

**Code Example:**
```csharp
var getVar = new GetVariable();
getVar.kind = VariableKind.Graph;
getVar.defaultName = "health";
graph.units.Add(getVar);
```

### 3.3 SetVariable

- **Class:** `SetVariable`
- **Properties:**
  - `kind` (VariableKind)
  - `defaultName` (string)
- **Control Input:** `assign`
- **Value Inputs:**
  - `name` (string) - variable name
  - `input` (object) - value to assign
  - `@object` (GameObject) - only when `kind == VariableKind.Object`
- **Control Output:** `assigned`
- **Value Output:** `output` (object) - the assigned value

**Code Example:**
```csharp
var setVar = new SetVariable();
setVar.kind = VariableKind.Graph;
setVar.defaultName = "health";
graph.units.Add(setVar);
```

### 3.4 IsVariableDefined

- **Class:** `IsVariableDefined`
- **Properties:** `kind` (VariableKind), `defaultName` (string)
- **Value Inputs:** `name` (string), `@object` (GameObject, Object scope only)
- **Value Output:** `isVariableDefined` (bool)

---

## 4. Math and Logic Units

### 4.1 Generic Arithmetic

These support multiple types via `OperatorUtility`.

| Class Name | Operation | Input Ports | Output Port |
|---|---|---|---|
| `GenericSum` | Addition | `a`, `b` (or `values` for multi-input) | `result` |
| `GenericSubtract` | Subtraction | `minuend` (A), `subtrahend` (B) | `difference` |
| `GenericMultiply` | Multiplication | `a`, `b` | `result` |
| `GenericDivide` | Division | `dividend` (A), `divisor` (B) | `quotient` |
| `GenericModulo` | Modulo | `dividend` (A), `divisor` (B) | `remainder` |

Base classes: `Sum<T>`, `Subtract<T>`, `Divide<T>`, `Modulo<T>`

### 4.2 Scalar Math

| Class Name | Operation | Input Ports | Output Port |
|---|---|---|---|
| `ScalarSum` | Addition | `values` (multi-input) | `sum` |
| `ScalarSubtract` | Subtraction | `minuend`, `subtrahend` | `difference` |
| `ScalarMultiply` | Multiplication | `values` (multi-input) | `product` |
| `ScalarDivide` | Division | `dividend`, `divisor` | `quotient` |
| `ScalarModulo` | Modulo | `dividend`, `divisor` | `remainder` |
| `ScalarExponentiate` | Power | `base` (x), `exponent` (n) | `power` |
| `ScalarMaximum` | Max | `values` (multi-input) | `maximum` |
| `ScalarMinimum` | Min | `values` (multi-input) | `minimum` |
| `ScalarAbsolute` | Abs | `input` | `output` |
| `ScalarRound` | Round | `input` | `output` |

### 4.3 Comparison Units

#### General Comparison (multi-output)
- **Class:** `Comparison`
- **Properties:** `numeric` (bool) - if true, does float comparison
- **Value Inputs:** `a`, `b`
- **Value Outputs:**
  - `aLessThanB` (bool)
  - `aLessThanOrEqualToB` (bool)
  - `aEqualToB` (bool)
  - `aNotEqualToB` (bool)
  - `aGreaterThanOrEqualToB` (bool)
  - `aGreatherThanB` (bool)

#### Individual Comparison Units (inherit from `BinaryComparisonUnit`)

| Class Name | Operation | Input Ports | Output Port |
|---|---|---|---|
| `Equal` | A == B | `a`, `b` | `comparison` (bool) |
| `NotEqual` | A != B | `a`, `b` | `comparison` (bool) |
| `Greater` | A > B | `a`, `b` | `comparison` (bool) |
| `GreaterOrEqual` | A >= B | `a`, `b` | `comparison` (bool) |
| `Less` | A < B | `a`, `b` | `comparison` (bool) |
| `LessOrEqual` | A <= B | `a`, `b` | `comparison` (bool) |

### 4.4 Boolean Logic Units

| Class Name | Operation | Input Ports | Output Port |
|---|---|---|---|
| `And` | Logical AND | `a`, `b` | `result` (bool) |
| `Or` | Logical OR | `a`, `b` | `result` (bool) |
| `Negate` (Not) | Logical NOT | `input` | `output` (bool) |
| `ExclusiveOr` | XOR | `a`, `b` | `result` (bool) |

---

## 5. Member Access Units

### 5.1 Member Class

The `Member` class represents a reflected member (field, property, method, or constructor).

**Constructors:**
```csharp
// Field or property
new Member(typeof(Transform), "position")

// Method (no overloads)
new Member(typeof(Debug), "Log")

// Method with overload disambiguation
new Member(typeof(Mathf), "Clamp", new Type[] { typeof(float), typeof(float), typeof(float) })
```

**Properties:**
- `targetType` (Type) - the owning type
- `name` (string) - member name
- `parameterTypes` (Type[]) - for method overload disambiguation
- `Reflect()` - resolves the MemberInfo
- `ToUniqueString()` - generates unique string representation

### 5.2 GetMember

- **Class:** `GetMember` (inherits from `MemberUnit`)
- **Constructor:** `new GetMember(member)` or default + set `member` property
- **Value Inputs:**
  - `target` (object) - only for instance members (not static)
- **Value Output:** `value` (object) - the retrieved value

**Code Example:**
```csharp
var getMember = new GetMember(new Member(typeof(Transform), "position"));
graph.units.Add(getMember);
```

### 5.3 SetMember

- **Class:** `SetMember` (inherits from `MemberUnit`)
- **Constructor:** `new SetMember(member)` or default + set `member` property
- **Control Input:** `assign`
- **Value Inputs:**
  - `target` (object) - only for instance members
  - `input` (object) - value to assign
- **Control Output:** `assigned`
- **Value Outputs:**
  - `output` (object) - the value that was set
  - `targetOutput` (object) - for chaining (if `chainable` is true)

**Code Example:**
```csharp
var setMember = new SetMember(new Member(typeof(Transform), "position"));
graph.units.Add(setMember);
```

### 5.4 InvokeMember

- **Class:** `InvokeMember` (inherits from `MemberUnit`)
- **Constructor:** `new InvokeMember(member)` or default + set `member` property
- **Control Input:** `enter`
- **Value Inputs:**
  - `target` (object) - only for instance methods
  - Per-parameter value inputs (dynamically created per method parameter)
- **Control Output:** `exit`
- **Value Outputs:**
  - `result` (object) - method return value (if non-void)
  - `targetOutput` (object) - for chaining

**Code Example:**
```csharp
// Instance method: Transform.Translate(Vector3)
var invoke = new InvokeMember(new Member(typeof(Transform), "Translate", new[] { typeof(Vector3) }));
graph.units.Add(invoke);

// Static method: Debug.Log(object)
var debugLog = new InvokeMember(new Member(typeof(Debug), "Log", new[] { typeof(object) }));
graph.units.Add(debugLog);
```

---

## 6. Literal Units

### 6.1 Literal Class

- **Class:** `Literal` (inherits from `SpecialUnit`)
- **Constructors:**
  - `new Literal(Type type)` - creates literal with pseudo-default value
  - `new Literal(Type type, object value)` - creates literal with specific value
- **Value Output:** `output` (object) - the constant value

**Code Examples:**
```csharp
var floatLit = new Literal(typeof(float), 3.14f);
var stringLit = new Literal(typeof(string), "Hello");
var boolLit = new Literal(typeof(bool), true);
var intLit = new Literal(typeof(int), 42);
var vec3Lit = new Literal(typeof(Vector3), new Vector3(1, 2, 3));
var colorLit = new Literal(typeof(Color), Color.red);
```

### 6.2 Supported Literal Types

**Primitives:**
- `bool`, `int`, `float`, `string`

**Unity Structs:**
- `Vector2`, `Vector3`, `Vector4`
- `Quaternion`, `Matrix4x4`
- `Rect`, `Bounds`
- `Color`
- `AnimationCurve`
- `LayerMask`
- `Ray`, `Ray2D`
- `RaycastHit`, `RaycastHit2D`
- `ContactPoint`, `ContactPoint2D`
- `ParticleCollisionEvent`
- `Scene`

**Other:**
- Any `Enum` type
- The available type list is managed by `BoltCoreConfiguration.typeOptions`

---

## 7. Type Conversion

### 7.1 ConversionUtility

The `ConversionUtility` class provides methods for type checking and conversion:

- `ConversionUtility.IsConvertibleTo(Type source, Type destination)` - checks convertibility
- `ConversionUtility.ConvertTo(object value, Type type)` - performs conversion

**Supported ConversionTypes:**
- `Identity` - same type, no conversion needed
- `Upcast` / `Downcast` - inheritance hierarchy casts
- `ToString` - object to string representation
- `NumericImplicit` / `NumericExplicit` - between numeric types
- `UserDefinedImplicit` / `UserDefinedExplicit` - custom conversions
- `EnumerableToArray` / `EnumerableToList` - collection conversions
- `UnityHierarchy` - Component <-> GameObject conversions

### 7.2 Expose Unit

- **Class:** `Expose` (inherits from `SpecialUnit`)
- Exposes all members of a specified type as value outputs
- Can expose instance or static members
- Dynamically creates `ValueOutput` ports for each member

---

## 8. Special Units

### 8.1 SubgraphUnit (formerly SuperUnit)

- **Class:** `SubgraphUnit` (inherits from `NesterUnit<FlowGraph, ScriptGraphAsset>`)
- **Constructor:** `new SubgraphUnit(ScriptGraphAsset macro)`
- Used to nest a `ScriptGraphAsset` inside another flow graph
- The term "SuperUnit" was renamed to "Subgraph" in v1.7.1

### 8.2 GraphInput

- **Class:** `GraphInput`
- Fetches input values from the parent `SubgraphUnit` into the nested graph
- Dynamically creates `ControlOutput` and `ValueOutput` ports based on parent definitions
- Only one `GraphInput` per nested graph

### 8.3 GraphOutput

- **Class:** `GraphOutput`
- Passes output values from the nested graph back to the parent `SubgraphUnit`
- Dynamically creates `ControlInput` and `ValueInput` ports based on parent definitions
- Multiple `GraphOutput` nodes can exist, but only one executes

### 8.4 StateUnit

- **Class:** `StateUnit`
- **Constructors:**
  - `new StateUnit()` - embedded state graph
  - `new StateUnit(StateGraphAsset macro)` - reference macro state graph
- **Control Inputs:** `start`, `stop`
- **Control Outputs:** `started`, `stopped`

### 8.5 Formula Unit

- **Class:** `Formula` (extends `MultiInputUnit<object>`)
- **Properties:**
  - `formula` (string) - the mathematical/logical expression
  - `cacheArguments` (bool) - whether to cache input values
- **Value Output:** `result`
- Supports `Vector2`, `Vector3`, `Vector4` creation in formulas

---

## 9. Time-Related Units

All time units inherit from the abstract `WaitUnit` class.

### 9.1 WaitUnit (Base Class)

- **Class:** `WaitUnit` (abstract)
- **Control Input:** `enter`
- **Control Output:** `exit`

### 9.2 WaitForSecondsUnit

- **Class:** `WaitForSecondsUnit` (inherits from `WaitUnit`)
- **Value Inputs:**
  - `seconds` (float, default: 0f)
  - `unscaledTime` (bool, default: false) - ignore Time.timeScale
- Uses `UnityEngine.WaitForSeconds` or `WaitForSecondsRealtime` internally

**Code Example:**
```csharp
var wait = new WaitForSecondsUnit();
graph.units.Add(wait);
// Connect a Literal(typeof(float), 2.0f) to the "seconds" port
```

### 9.3 WaitUntilUnit

- **Class:** `WaitUntilUnit` (inherits from `WaitUnit`)
- **Value Input:** `condition` (bool)
- Uses `UnityEngine.WaitUntil` internally

### 9.4 Timer

- **Class:** `Timer`
- Has input for `seconds` and `unscaledTime`
- Provides elapsed time tracking
- Note: `OnTimerElapsed` is obsolete, use `Timer` instead

### 9.5 Cooldown

- **Class:** `Cooldown`
- Has a `Reset` control input port
- Provides a "ready" state tracking
- Used for rate-limiting execution flow

---

## 10. Null and Comparison Units

### 10.1 Null Literal

Use a `Literal` with null value or create inline null references.

### 10.2 NullCheck

- **Class:** `NullCheck`
- **Control Input:** `enter`
- **Value Input:** `input` (object, allows null)
- **Control Outputs:** `ifNotNull`, `ifNull`
- Handles `UnityEngine.Object` types specially (custom equality operator)

**Code Example:**
```csharp
var nullCheck = new NullCheck();
graph.units.Add(nullCheck);
```

### 10.3 NullCoalesce

- **Class:** `NullCoalesce`
- **Value Inputs:**
  - `input` (object, allows null)
  - `fallback` (object)
- **Value Output:** `result` - returns `input` if non-null, else `fallback`
- Handles `UnityEngine.Object` types specially

---

## 11. String Units

String operations are primarily accessed via `InvokeMember` on `string` type or through the `StringUtility` class. The following string-related operations exist:

### Available via InvokeMember

```csharp
// String.Concat
new InvokeMember(new Member(typeof(string), "Concat", new[] { typeof(string), typeof(string) }))

// String.Contains
new InvokeMember(new Member(typeof(string), "Contains", new[] { typeof(string) }))

// String.Format
new InvokeMember(new Member(typeof(string), "Format", new[] { typeof(string), typeof(object) }))
```

### StringUtility Methods (internal use)

- `IsNullOrWhiteSpace(string)` - null/empty/whitespace check
- `FallbackEmpty(string, string)` - fallback if empty
- `FallbackWhitespace(string, string)` - fallback if whitespace
- `ToSeparatedString(IEnumerable, string)` - join with separator

---

## 12. Collection/List Units

### 12.1 ListContainsItem

- **Class:** `ListContainsItem`
- **Value Inputs:**
  - `list` (IList)
  - `item` (object)
- **Value Output:** `contains` (bool)

### 12.2 Other Collection Units

The `UnitOptionTree` organizes units under "Collections/Lists" and "Collections/Dictionaries" categories. Common operations include:

- `CreateList` - creates a new list
- `AddListItem` - adds item to list
- `GetListItem` - retrieves item by index
- `RemoveListItem` - removes item from list
- `CountItems` - gets collection count
- `MergeDictionaries` - merges two dictionaries (extends `MultiInputUnit`)
- `CreateDictionary` - creates a new dictionary

These are accessed via member invocation or dedicated unit classes in the Collections category.

---

## 13. Vector Math Units

### 13.1 Vector3 Units

| Class Name | Operation | Input Ports | Output Port |
|---|---|---|---|
| `Vector3Sum` | Vector addition | `values` (multi-input) | `sum` |
| `Vector3Average` | Average | `values` (multi-input) | `average` |
| `Vector3Maximum` | Component-wise max | `values` (multi-input) | `maximum` |
| `Vector3Minimum` | Component-wise min | `values` (multi-input) | `minimum` |
| `Vector3Round` | Round components | `input` | `output` |

Categories: "Math/Vector 2", "Math/Vector 3", "Math/Vector 4"

### 13.2 Vector Access via GetMember

```csharp
// Get Vector3.x component
new GetMember(new Member(typeof(Vector3), "x"))

// Get Vector3.magnitude
new GetMember(new Member(typeof(Vector3), "magnitude"))

// Vector3.Distance static method
new InvokeMember(new Member(typeof(Vector3), "Distance", new[] { typeof(Vector3), typeof(Vector3) }))

// Vector3.Lerp static method
new InvokeMember(new Member(typeof(Vector3), "Lerp", new[] { typeof(Vector3), typeof(Vector3), typeof(float) }))
```

---

## 14. Port System and Connections

### 14.1 Port Types

| Port Class | Direction | Type | Purpose |
|---|---|---|---|
| `ControlInput` | Input | Flow | Receives execution flow |
| `ControlOutput` | Output | Flow | Emits execution flow |
| `ValueInput` | Input | Data | Receives a value |
| `ValueOutput` | Output | Data | Provides a value |

All port types inherit from `UnitPort<TValidOther, TInvalidOther, TConnection>`.

**Port Properties:**
- `ControlInput` has `action` or `coroutineAction` delegate
- `ControlOutput` allows only single connection
- `ValueInput` allows only single connection, supports default values
- `ValueOutput` has `type` property and `getValue` delegate

### 14.2 Connection Classes

| Class | Source | Destination |
|---|---|---|
| `ControlConnection` | `ControlOutput` | `ControlInput` |
| `ValueConnection` | `ValueOutput` | `ValueInput` |

Both inherit from `UnitConnection<TSourcePort, TDestinationPort>`.

### 14.3 Creating Connections Programmatically

**Method 1: Using graph connection collections directly**
```csharp
// Control connection
source.controlOutputs["exit"].ConnectToValid(destination.controlInputs["enter"]);

// Value connection
source.valueOutputs["value"].ConnectToValid(destination.valueInputs["input"]);
```

**Method 2: Accessing FlowGraph connection collections**
```csharp
// graph.controlConnections stores ControlConnection instances
// graph.valueConnections stores ValueConnection instances
```

**Connection Rules:**
- `ControlOutput` can only have a single connection (one-to-one)
- `ValueInput` can only have a single connection (one-to-one)
- `ValueOutput` can connect to multiple `ValueInput` ports (one-to-many)
- `ControlInput` can receive from multiple `ControlOutput` ports (many-to-one)
- Value connections check type compatibility via `ConversionUtility`

### 14.4 Complete Wiring Example

```csharp
// Create a simple graph: Start -> SetVariable("health", 100)
var graph = new FlowGraph();

// Create units
var start = new Start();
var setVar = new SetVariable();
setVar.kind = VariableKind.Graph;
setVar.defaultName = "health";

var literal = new Literal(typeof(int), 100);

// Add units to graph
graph.units.Add(start);
graph.units.Add(setVar);
graph.units.Add(literal);

// Wire control flow: Start.trigger -> SetVariable.assign
start.controlOutputs["trigger"].ConnectToValid(setVar.controlInputs["assign"]);

// Wire value: Literal.output -> SetVariable.input
literal.valueOutputs["output"].ConnectToValid(setVar.valueInputs["input"]);
```

---

## Appendix: Unit Category Summary

| Category Path | Example Units |
|---|---|
| Events/Lifecycle | Start, Update, FixedUpdate, OnEnable, OnDestroy |
| Events/Physics | OnTriggerEnter, OnCollisionEnter, OnJointBreak |
| Events/Input | OnKeyboardInput, OnMouseDown |
| Events/Editor | CustomEvent, TriggerCustomEvent |
| Control | If, Sequence, Once, ToggleValue, ToggleFlow |
| Control/Looping | For, ForEach, While |
| Control/Branching | SwitchOnEnum, SwitchOnString, SwitchOnInteger |
| Control/Selection | SelectUnit, SelectOnEnum, SelectOnFlow |
| Variables | GetVariable, SetVariable, IsVariableDefined |
| Logic | And, Or, Negate, ExclusiveOr, Equal, NotEqual, Comparison |
| Math/Generic | GenericSum, GenericSubtract, GenericMultiply, GenericDivide |
| Math/Scalar | ScalarSum, ScalarSubtract, ScalarExponentiate |
| Math/Vector 2 | Vector2 operations |
| Math/Vector 3 | Vector3Sum, Vector3Average, Vector3Maximum, Vector3Round |
| Math/Vector 4 | Vector4 operations |
| Nulls | NullCheck, NullCoalesce |
| Time | WaitForSecondsUnit, WaitUntilUnit, Timer, Cooldown |
| Nesting | SubgraphUnit, StateUnit, GraphInput, GraphOutput |
| Codebase | GetMember, SetMember, InvokeMember |
| Collections/Lists | ListContainsItem, CreateList, AddListItem |
| Collections/Dictionaries | MergeDictionaries, CreateDictionary |

---

## Key Takeaways for Programmatic Graph Creation

1. **All units** are added to a graph via `graph.units.Add(unit)`.
2. **Event units** are entry points with no control inputs, only control outputs (`trigger`).
3. **Member units** (Get/Set/InvokeMember) are the most flexible - they can access any .NET member via the `Member` class.
4. **Variable units** use `VariableKind` enum and `defaultName` to configure scope and name.
5. **Connections** are made via `port.ConnectToValid(otherPort)` using the port collections on each unit.
6. **Literals** provide constant values and are created with `new Literal(type, value)`.
7. **Flow control** units like `If`, `Sequence`, and loops manage execution order.
8. **Port names** are string keys used to access ports: `unit.controlInputs["enter"]`, `unit.valueOutputs["value"]`, etc.
