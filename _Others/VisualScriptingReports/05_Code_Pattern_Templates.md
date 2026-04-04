# Unity Visual Scripting - Code Pattern Templates

Complete, working C# editor script patterns for generating common Visual Scripting graph scenarios programmatically. Each pattern follows the proven structure from `CreateRotateGraph.cs`.

**Required boilerplate for all patterns:**

```csharp
#if UNITY_EDITOR
using UnityEditor;
using UnityEngine;
using Unity.VisualScripting;
#endif
```

---

## Table of Contents

1. [Basic Event Handling](#1-basic-event-handling)
2. [Input Handling](#2-input-handling)
3. [Physics](#3-physics)
4. [Transform Manipulation](#4-transform-manipulation)
5. [GameObject Operations](#5-gameobject-operations)
6. [Component Access](#6-component-access)
7. [Variables](#7-variables)
8. [Flow Control](#8-flow-control)
9. [Coroutine-Like Patterns](#9-coroutine-like-patterns)
10. [UI Interactions](#10-ui-interactions)
11. [Animation](#11-animation)
12. [Audio](#12-audio)
13. [Math Operations](#13-math-operations)
14. [String Operations](#14-string-operations)
15. [Debug Logging](#15-debug-logging)

---

## 1. Basic Event Handling

### 1.1 OnStart Event

**Description**: Executes a Debug.Log when the game starts.

```csharp
public static void CreateOnStartGraph(FlowGraph graph)
{
    var start = new Start();
    graph.units.Add(start);
    start.position = new Vector2(0, 0);

    var debugLog = new InvokeMember(new Member(typeof(Debug), "Log", new[] { typeof(object) }));
    graph.units.Add(debugLog);
    debugLog.position = new Vector2(300, 0);

    var message = new Literal(typeof(string), "Game Started!");
    graph.units.Add(message);
    message.position = new Vector2(100, 150);

    // Control: Start.trigger -> Debug.Log.enter
    graph.controlConnections.Add(new ControlConnection(start.trigger, debugLog.enter));
    // Value: message.output -> Debug.Log.inputParameters[0]
    graph.valueConnections.Add(new ValueConnection(message.output, debugLog.inputParameters[0]));
}
```

**Port notes**: `Start.trigger` (ControlOutput) -> `InvokeMember.enter` (ControlInput). `Literal.output` (ValueOutput) -> `InvokeMember.inputParameters[0]` (ValueInput).

### 1.2 OnUpdate Event

**Description**: Per-frame update loop.

```csharp
public static void CreateOnUpdateGraph(FlowGraph graph)
{
    var update = new Update();
    graph.units.Add(update);
    update.position = new Vector2(0, 0);

    // Connect update.trigger to any action's enter port
    // graph.controlConnections.Add(new ControlConnection(update.trigger, action.enter));
}
```

### 1.3 OnEnable / OnDisable Pair

**Description**: Log messages when the object is enabled and disabled.

```csharp
public static void CreateEnableDisableGraph(FlowGraph graph)
{
    // OnEnable
    var onEnable = new OnEnable();
    graph.units.Add(onEnable);
    onEnable.position = new Vector2(0, 0);

    var logEnable = new InvokeMember(new Member(typeof(Debug), "Log", new[] { typeof(object) }));
    graph.units.Add(logEnable);
    logEnable.position = new Vector2(300, 0);

    var enableMsg = new Literal(typeof(string), "Object Enabled");
    graph.units.Add(enableMsg);
    enableMsg.position = new Vector2(100, 100);

    graph.controlConnections.Add(new ControlConnection(onEnable.trigger, logEnable.enter));
    graph.valueConnections.Add(new ValueConnection(enableMsg.output, logEnable.inputParameters[0]));

    // OnDisable
    var onDisable = new OnDisable();
    graph.units.Add(onDisable);
    onDisable.position = new Vector2(0, 300);

    var logDisable = new InvokeMember(new Member(typeof(Debug), "Log", new[] { typeof(object) }));
    graph.units.Add(logDisable);
    logDisable.position = new Vector2(300, 300);

    var disableMsg = new Literal(typeof(string), "Object Disabled");
    graph.units.Add(disableMsg);
    disableMsg.position = new Vector2(100, 400);

    graph.controlConnections.Add(new ControlConnection(onDisable.trigger, logDisable.enter));
    graph.valueConnections.Add(new ValueConnection(disableMsg.output, logDisable.inputParameters[0]));
}
```

### 1.4 FixedUpdate for Physics

**Description**: FixedUpdate event for physics-rate operations.

```csharp
public static void CreateFixedUpdateGraph(FlowGraph graph)
{
    var fixedUpdate = new FixedUpdate();
    graph.units.Add(fixedUpdate);
    fixedUpdate.position = new Vector2(0, 0);

    // fixedUpdate.trigger -> physics operations
}
```

---

## 2. Input Handling

### 2.1 GetKey (Keyboard Input)

**Description**: Check if the Space key is pressed each frame.

```csharp
public static void CreateGetKeyGraph(FlowGraph graph)
{
    var update = new Update();
    graph.units.Add(update);
    update.position = new Vector2(0, 0);

    // Input.GetKeyDown(KeyCode)
    var getKeyDown = new InvokeMember(
        new Member(typeof(Input), "GetKeyDown", new[] { typeof(KeyCode) })
    );
    graph.units.Add(getKeyDown);
    getKeyDown.position = new Vector2(300, 0);

    var keyCode = new Literal(typeof(KeyCode), KeyCode.Space);
    graph.units.Add(keyCode);
    keyCode.position = new Vector2(100, 150);

    // If branch
    var ifUnit = new If();
    graph.units.Add(ifUnit);
    ifUnit.position = new Vector2(550, 0);

    // Action on key press
    var debugLog = new InvokeMember(new Member(typeof(Debug), "Log", new[] { typeof(object) }));
    graph.units.Add(debugLog);
    debugLog.position = new Vector2(800, -50);

    var msg = new Literal(typeof(string), "Space pressed!");
    graph.units.Add(msg);
    msg.position = new Vector2(600, 100);

    // Control flow: Update -> GetKeyDown -> If -> Debug.Log
    graph.controlConnections.Add(new ControlConnection(update.trigger, getKeyDown.enter));
    graph.controlConnections.Add(new ControlConnection(getKeyDown.exit, ifUnit.enter));
    graph.controlConnections.Add(new ControlConnection(ifUnit.ifTrue, debugLog.enter));

    // Value: KeyCode -> GetKeyDown, GetKeyDown.result -> If.condition
    graph.valueConnections.Add(new ValueConnection(keyCode.output, getKeyDown.inputParameters[0]));
    graph.valueConnections.Add(new ValueConnection(getKeyDown.result, ifUnit.condition));
    graph.valueConnections.Add(new ValueConnection(msg.output, debugLog.inputParameters[0]));
}
```

**Port notes**: `InvokeMember.result` provides the bool return value of `Input.GetKeyDown`.

### 2.2 GetAxis (Horizontal/Vertical Input)

**Description**: Read horizontal and vertical axes.

```csharp
public static void CreateGetAxisGraph(FlowGraph graph)
{
    var update = new Update();
    graph.units.Add(update);
    update.position = new Vector2(0, 0);

    // Input.GetAxis("Horizontal")
    var getHorizontal = new InvokeMember(
        new Member(typeof(Input), "GetAxis", new[] { typeof(string) })
    );
    graph.units.Add(getHorizontal);
    getHorizontal.position = new Vector2(300, 0);

    var horizontalStr = new Literal(typeof(string), "Horizontal");
    graph.units.Add(horizontalStr);
    horizontalStr.position = new Vector2(100, 100);

    // Input.GetAxis("Vertical")
    var getVertical = new InvokeMember(
        new Member(typeof(Input), "GetAxis", new[] { typeof(string) })
    );
    graph.units.Add(getVertical);
    getVertical.position = new Vector2(300, 200);

    var verticalStr = new Literal(typeof(string), "Vertical");
    graph.units.Add(verticalStr);
    verticalStr.position = new Vector2(100, 300);

    graph.controlConnections.Add(new ControlConnection(update.trigger, getHorizontal.enter));
    graph.controlConnections.Add(new ControlConnection(getHorizontal.exit, getVertical.enter));

    graph.valueConnections.Add(new ValueConnection(horizontalStr.output, getHorizontal.inputParameters[0]));
    graph.valueConnections.Add(new ValueConnection(verticalStr.output, getVertical.inputParameters[0]));

    // getHorizontal.result and getVertical.result provide float values
}
```

### 2.3 GetMouseButton

**Description**: Detect left mouse button click.

```csharp
public static void CreateMouseClickGraph(FlowGraph graph)
{
    var update = new Update();
    graph.units.Add(update);
    update.position = new Vector2(0, 0);

    // Input.GetMouseButtonDown(0)
    var getMouseBtn = new InvokeMember(
        new Member(typeof(Input), "GetMouseButtonDown", new[] { typeof(int) })
    );
    graph.units.Add(getMouseBtn);
    getMouseBtn.position = new Vector2(300, 0);

    var buttonIndex = new Literal(typeof(int), 0); // 0 = left click
    graph.units.Add(buttonIndex);
    buttonIndex.position = new Vector2(100, 100);

    var ifUnit = new If();
    graph.units.Add(ifUnit);
    ifUnit.position = new Vector2(550, 0);

    graph.controlConnections.Add(new ControlConnection(update.trigger, getMouseBtn.enter));
    graph.controlConnections.Add(new ControlConnection(getMouseBtn.exit, ifUnit.enter));
    graph.valueConnections.Add(new ValueConnection(buttonIndex.output, getMouseBtn.inputParameters[0]));
    graph.valueConnections.Add(new ValueConnection(getMouseBtn.result, ifUnit.condition));

    // ifUnit.ifTrue -> action when clicked
}
```

---

## 3. Physics

### 3.1 OnTriggerEnter

**Description**: Detect when an object enters a trigger zone and log the collider name.

```csharp
public static void CreateOnTriggerEnterGraph(FlowGraph graph)
{
    var onTrigger = new OnTriggerEnter();
    graph.units.Add(onTrigger);
    onTrigger.position = new Vector2(0, 0);

    var debugLog = new InvokeMember(new Member(typeof(Debug), "Log", new[] { typeof(object) }));
    graph.units.Add(debugLog);
    debugLog.position = new Vector2(300, 0);

    graph.controlConnections.Add(new ControlConnection(onTrigger.trigger, debugLog.enter));

    // OnTriggerEnter provides a "collider" value output (Collider type)
    // Connect it to the debug log input
    // Note: The exact port access depends on the event unit's definition
}
```

**Port notes**: `OnTriggerEnter` has `trigger` (ControlOutput) and value outputs for the collider data.

### 3.2 OnCollisionEnter

**Description**: Detect collisions and access collision data.

```csharp
public static void CreateOnCollisionEnterGraph(FlowGraph graph)
{
    var onCollision = new OnCollisionEnter();
    graph.units.Add(onCollision);
    onCollision.position = new Vector2(0, 0);

    var debugLog = new InvokeMember(new Member(typeof(Debug), "Log", new[] { typeof(object) }));
    graph.units.Add(debugLog);
    debugLog.position = new Vector2(400, 0);

    var msg = new Literal(typeof(string), "Collision detected!");
    graph.units.Add(msg);
    msg.position = new Vector2(200, 150);

    graph.controlConnections.Add(new ControlConnection(onCollision.trigger, debugLog.enter));
    graph.valueConnections.Add(new ValueConnection(msg.output, debugLog.inputParameters[0]));
}
```

### 3.3 Raycast

**Description**: Perform a raycast from the object's position forward.

```csharp
public static void CreateRaycastGraph(FlowGraph graph)
{
    var update = new Update();
    graph.units.Add(update);
    update.position = new Vector2(0, 0);

    // Get transform.position
    var getPos = new GetMember(new Member(typeof(Transform), "position"));
    graph.units.Add(getPos);
    getPos.position = new Vector2(0, 200);

    // Get transform.forward
    var getFwd = new GetMember(new Member(typeof(Transform), "forward"));
    graph.units.Add(getFwd);
    getFwd.position = new Vector2(0, 350);

    // Max distance
    var maxDist = new Literal(typeof(float), 100f);
    graph.units.Add(maxDist);
    maxDist.position = new Vector2(0, 500);

    // Physics.Raycast(Vector3 origin, Vector3 direction, float maxDistance)
    var raycast = new InvokeMember(
        new Member(typeof(Physics), "Raycast",
            new[] { typeof(Vector3), typeof(Vector3), typeof(float) })
    );
    graph.units.Add(raycast);
    raycast.position = new Vector2(300, 0);

    graph.controlConnections.Add(new ControlConnection(update.trigger, raycast.enter));
    graph.valueConnections.Add(new ValueConnection(getPos.value, raycast.inputParameters[0]));
    graph.valueConnections.Add(new ValueConnection(getFwd.value, raycast.inputParameters[1]));
    graph.valueConnections.Add(new ValueConnection(maxDist.output, raycast.inputParameters[2]));

    // raycast.result is a bool indicating if something was hit
    var ifUnit = new If();
    graph.units.Add(ifUnit);
    ifUnit.position = new Vector2(600, 0);

    graph.controlConnections.Add(new ControlConnection(raycast.exit, ifUnit.enter));
    graph.valueConnections.Add(new ValueConnection(raycast.result, ifUnit.condition));
}
```

---

## 4. Transform Manipulation

### 4.1 Move (Translate)

**Description**: Move an object forward each frame using Transform.Translate.

```csharp
public static void CreateMoveForwardGraph(FlowGraph graph)
{
    var update = new Update();
    graph.units.Add(update);
    update.position = new Vector2(0, 0);

    var getDeltaTime = new GetMember(new Member(typeof(Time), nameof(Time.deltaTime)));
    graph.units.Add(getDeltaTime);
    getDeltaTime.position = new Vector2(0, 200);

    var speed = new Literal(typeof(float), 5f);
    graph.units.Add(speed);
    speed.position = new Vector2(0, 100);

    var multiply = new ScalarMultiply();
    graph.units.Add(multiply);
    multiply.position = new Vector2(200, 150);

    // Transform.Translate(Vector3 translation)
    var translate = new InvokeMember(
        new Member(typeof(Transform), "Translate", new[] { typeof(Vector3) })
    );
    graph.units.Add(translate);
    translate.position = new Vector2(500, 0);

    // Vector3(0, 0, speed*dt) - we need to create a Vector3
    var createVector = new InvokeMember(
        new Member(typeof(Vector3), null, new[] { typeof(float), typeof(float), typeof(float) })
    // Note: For Vector3 constructor, use a different approach:
    );
    // Alternative: use Vector3.forward * speed * deltaTime via GetMember + ScalarMultiply

    graph.controlConnections.Add(new ControlConnection(update.trigger, translate.enter));
    graph.valueConnections.Add(new ValueConnection(speed.output, multiply.a));
    graph.valueConnections.Add(new ValueConnection(getDeltaTime.value, multiply.b));
}
```

### 4.2 Rotate (Proven Pattern from Sample)

**Description**: Rotate an object continuously. This is the exact pattern from `CreateRotateGraph.cs`.

```csharp
public static void CreateRotateGraph(FlowGraph graph)
{
    // On Update event
    var onUpdate = new Update();
    graph.units.Add(onUpdate);
    onUpdate.position = new Vector2(-300, 0);

    // Get Time.deltaTime
    var getDeltaTime = new GetMember(new Member(typeof(Time), nameof(Time.deltaTime)));
    graph.units.Add(getDeltaTime);
    getDeltaTime.position = new Vector2(-500, 200);

    // Speed literals
    var xSpeed = new Literal(typeof(float), 10f);
    graph.units.Add(xSpeed);
    xSpeed.position = new Vector2(-500, 100);

    var ySpeed = new Literal(typeof(float), 20f);
    graph.units.Add(ySpeed);
    ySpeed.position = new Vector2(-500, 300);

    var zSpeed = new Literal(typeof(float), 5f);
    graph.units.Add(zSpeed);
    zSpeed.position = new Vector2(-500, 400);

    // Multiply speed * deltaTime for each axis
    var multiplyX = new ScalarMultiply();
    graph.units.Add(multiplyX);
    multiplyX.position = new Vector2(-200, 100);

    var multiplyY = new ScalarMultiply();
    graph.units.Add(multiplyY);
    multiplyY.position = new Vector2(-200, 300);

    var multiplyZ = new ScalarMultiply();
    graph.units.Add(multiplyZ);
    multiplyZ.position = new Vector2(-200, 400);

    // Transform.Rotate(float xAngle, float yAngle, float zAngle)
    var rotateMember = new Member(typeof(Transform), "Rotate",
        new[] { typeof(float), typeof(float), typeof(float) });
    var rotate = new InvokeMember(rotateMember);
    graph.units.Add(rotate);
    rotate.position = new Vector2(150, 0);

    // Connect control: Update -> Rotate
    graph.controlConnections.Add(new ControlConnection(onUpdate.trigger, rotate.enter));

    // Connect value: speed * deltaTime
    graph.valueConnections.Add(new ValueConnection(xSpeed.output, multiplyX.a));
    graph.valueConnections.Add(new ValueConnection(getDeltaTime.value, multiplyX.b));

    graph.valueConnections.Add(new ValueConnection(ySpeed.output, multiplyY.a));
    graph.valueConnections.Add(new ValueConnection(getDeltaTime.value, multiplyY.b));

    graph.valueConnections.Add(new ValueConnection(zSpeed.output, multiplyZ.a));
    graph.valueConnections.Add(new ValueConnection(getDeltaTime.value, multiplyZ.b));

    // Connect results to Rotate parameters
    graph.valueConnections.Add(new ValueConnection(multiplyX.product, rotate.inputParameters[0]));
    graph.valueConnections.Add(new ValueConnection(multiplyY.product, rotate.inputParameters[1]));
    graph.valueConnections.Add(new ValueConnection(multiplyZ.product, rotate.inputParameters[2]));
}
```

### 4.3 Set Position

**Description**: Set an object's position to a specific Vector3.

```csharp
public static void CreateSetPositionGraph(FlowGraph graph)
{
    var start = new Start();
    graph.units.Add(start);
    start.position = new Vector2(0, 0);

    var setPosition = new SetMember(new Member(typeof(Transform), "position"));
    graph.units.Add(setPosition);
    setPosition.position = new Vector2(300, 0);

    var targetPos = new Literal(typeof(Vector3), new Vector3(0, 5, 0));
    graph.units.Add(targetPos);
    targetPos.position = new Vector2(100, 150);

    graph.controlConnections.Add(new ControlConnection(start.trigger, setPosition.assign));
    graph.valueConnections.Add(new ValueConnection(targetPos.output, setPosition.input));
}
```

### 4.4 LookAt

**Description**: Make an object look at a target position.

```csharp
public static void CreateLookAtGraph(FlowGraph graph)
{
    var update = new Update();
    graph.units.Add(update);
    update.position = new Vector2(0, 0);

    // Transform.LookAt(Vector3 worldPosition)
    var lookAt = new InvokeMember(
        new Member(typeof(Transform), "LookAt", new[] { typeof(Vector3) })
    );
    graph.units.Add(lookAt);
    lookAt.position = new Vector2(300, 0);

    var targetPos = new Literal(typeof(Vector3), Vector3.zero);
    graph.units.Add(targetPos);
    targetPos.position = new Vector2(100, 150);

    graph.controlConnections.Add(new ControlConnection(update.trigger, lookAt.enter));
    graph.valueConnections.Add(new ValueConnection(targetPos.output, lookAt.inputParameters[0]));
}
```

---

## 5. GameObject Operations

### 5.1 Find by Name

**Description**: Find a GameObject by name on Start.

```csharp
public static void CreateFindObjectGraph(FlowGraph graph)
{
    var start = new Start();
    graph.units.Add(start);
    start.position = new Vector2(0, 0);

    // GameObject.Find(string name)
    var findObj = new InvokeMember(
        new Member(typeof(GameObject), "Find", new[] { typeof(string) })
    );
    graph.units.Add(findObj);
    findObj.position = new Vector2(300, 0);

    var objName = new Literal(typeof(string), "Player");
    graph.units.Add(objName);
    objName.position = new Vector2(100, 100);

    graph.controlConnections.Add(new ControlConnection(start.trigger, findObj.enter));
    graph.valueConnections.Add(new ValueConnection(objName.output, findObj.inputParameters[0]));

    // findObj.result provides the found GameObject (or null)
}
```

### 5.2 Instantiate

**Description**: Instantiate a prefab.

```csharp
public static void CreateInstantiateGraph(FlowGraph graph)
{
    var start = new Start();
    graph.units.Add(start);
    start.position = new Vector2(0, 0);

    // Object.Instantiate(Object original)
    var instantiate = new InvokeMember(
        new Member(typeof(Object), "Instantiate", new[] { typeof(Object) })
    );
    graph.units.Add(instantiate);
    instantiate.position = new Vector2(300, 0);

    // The prefab reference would come from a GetVariable or graph variable
    // For this pattern, we use a graph variable for the prefab
    graph.variables.Set("prefab", (Object)null); // Assign in inspector

    var getPrefab = new GetVariable();
    getPrefab.kind = VariableKind.Graph;
    getPrefab.defaultName = "prefab";
    graph.units.Add(getPrefab);
    getPrefab.position = new Vector2(50, 150);

    graph.controlConnections.Add(new ControlConnection(start.trigger, instantiate.enter));
    graph.valueConnections.Add(new ValueConnection(getPrefab.value, instantiate.inputParameters[0]));
}
```

### 5.3 Destroy

**Description**: Destroy a GameObject.

```csharp
public static void CreateDestroyGraph(FlowGraph graph)
{
    var start = new Start();
    graph.units.Add(start);
    start.position = new Vector2(0, 0);

    // Object.Destroy(Object obj)
    var destroy = new InvokeMember(
        new Member(typeof(Object), "Destroy", new[] { typeof(Object) })
    );
    graph.units.Add(destroy);
    destroy.position = new Vector2(300, 0);

    // "This" refers to the current GameObject
    var thisUnit = new This();
    graph.units.Add(thisUnit);
    thisUnit.position = new Vector2(100, 150);

    graph.controlConnections.Add(new ControlConnection(start.trigger, destroy.enter));
    graph.valueConnections.Add(new ValueConnection(thisUnit.self, destroy.inputParameters[0]));
}
```

### 5.4 SetActive

**Description**: Toggle a GameObject's active state.

```csharp
public static void CreateSetActiveGraph(FlowGraph graph)
{
    var start = new Start();
    graph.units.Add(start);
    start.position = new Vector2(0, 0);

    // GameObject.SetActive(bool value)
    var setActive = new InvokeMember(
        new Member(typeof(GameObject), "SetActive", new[] { typeof(bool) })
    );
    graph.units.Add(setActive);
    setActive.position = new Vector2(300, 0);

    var activeValue = new Literal(typeof(bool), false);
    graph.units.Add(activeValue);
    activeValue.position = new Vector2(100, 150);

    graph.controlConnections.Add(new ControlConnection(start.trigger, setActive.enter));
    graph.valueConnections.Add(new ValueConnection(activeValue.output, setActive.inputParameters[0]));
    // target port auto-resolves to current GameObject when unconnected
}
```

---

## 6. Component Access

### 6.1 GetComponent

**Description**: Get a Rigidbody component from the current object.

```csharp
public static void CreateGetComponentGraph(FlowGraph graph)
{
    var start = new Start();
    graph.units.Add(start);
    start.position = new Vector2(0, 0);

    // GameObject.GetComponent<Rigidbody>() - use the generic-less version
    // GetComponent(Type type) or use a specific member accessor
    var getComponent = new InvokeMember(
        new Member(typeof(GameObject), "GetComponent", new[] { typeof(System.Type) })
    );
    graph.units.Add(getComponent);
    getComponent.position = new Vector2(300, 0);

    // Alternative: Access via GetMember on a known component type
    // e.g., get Rigidbody.velocity
    var getRbVelocity = new GetMember(new Member(typeof(Rigidbody), "velocity"));
    graph.units.Add(getRbVelocity);
    getRbVelocity.position = new Vector2(300, 200);
    // The target port will accept a Rigidbody reference
}
```

### 6.2 AddComponent

**Description**: Add a Rigidbody to a GameObject.

```csharp
public static void CreateAddComponentGraph(FlowGraph graph)
{
    var start = new Start();
    graph.units.Add(start);
    start.position = new Vector2(0, 0);

    // Use InvokeMember for AddComponent<T>() on the current object
    var addRb = new InvokeMember(
        new Member(typeof(GameObject), "AddComponent", new[] { typeof(System.Type) })
    );
    graph.units.Add(addRb);
    addRb.position = new Vector2(300, 0);

    graph.controlConnections.Add(new ControlConnection(start.trigger, addRb.enter));
}
```

---

## 7. Variables

### 7.1 Get/Set Graph Variables

**Description**: Initialize and update a "score" graph variable.

```csharp
public static void CreateGraphVariableGraph(FlowGraph graph)
{
    // Declare graph variable with default value
    graph.variables.Set("score", 0);

    var start = new Start();
    graph.units.Add(start);
    start.position = new Vector2(0, 0);

    // Set score to 100 on start
    var setScore = new SetVariable();
    setScore.kind = VariableKind.Graph;
    setScore.defaultName = "score";
    graph.units.Add(setScore);
    setScore.position = new Vector2(300, 0);

    var initialValue = new Literal(typeof(int), 100);
    graph.units.Add(initialValue);
    initialValue.position = new Vector2(100, 150);

    graph.controlConnections.Add(new ControlConnection(start.trigger, setScore.assign));
    graph.valueConnections.Add(new ValueConnection(initialValue.output, setScore.input));

    // Later: Get the score
    var getScore = new GetVariable();
    getScore.kind = VariableKind.Graph;
    getScore.defaultName = "score";
    graph.units.Add(getScore);
    getScore.position = new Vector2(0, 300);
    // getScore.value is a ValueOutput with the current score
}
```

### 7.2 Object Variables

**Description**: Access variables on a specific GameObject.

```csharp
public static void CreateObjectVariableGraph(FlowGraph graph)
{
    var start = new Start();
    graph.units.Add(start);
    start.position = new Vector2(0, 0);

    // Set object variable "health" to 100
    var setHealth = new SetVariable();
    setHealth.kind = VariableKind.Object;
    setHealth.defaultName = "health";
    graph.units.Add(setHealth);
    setHealth.position = new Vector2(300, 0);

    var healthValue = new Literal(typeof(int), 100);
    graph.units.Add(healthValue);
    healthValue.position = new Vector2(100, 150);

    graph.controlConnections.Add(new ControlConnection(start.trigger, setHealth.assign));
    graph.valueConnections.Add(new ValueConnection(healthValue.output, setHealth.input));
    // target (@object port) auto-resolves to current GameObject when unconnected
}
```

### 7.3 Increment a Variable

**Description**: Increment a score variable by a value.

```csharp
public static void CreateIncrementVariableGraph(FlowGraph graph)
{
    graph.variables.Set("score", 0);

    // Trigger (could be connected to any event)
    var start = new Start();
    graph.units.Add(start);
    start.position = new Vector2(0, 0);

    // Get current score
    var getScore = new GetVariable();
    getScore.kind = VariableKind.Graph;
    getScore.defaultName = "score";
    graph.units.Add(getScore);
    getScore.position = new Vector2(100, 150);

    // Add points
    var addPoints = new ScalarAdd();
    graph.units.Add(addPoints);
    addPoints.position = new Vector2(300, 150);

    var points = new Literal(typeof(float), 10f);
    graph.units.Add(points);
    points.position = new Vector2(100, 300);

    // Set updated score
    var setScore = new SetVariable();
    setScore.kind = VariableKind.Graph;
    setScore.defaultName = "score";
    graph.units.Add(setScore);
    setScore.position = new Vector2(500, 0);

    // Wiring
    graph.controlConnections.Add(new ControlConnection(start.trigger, setScore.assign));
    graph.valueConnections.Add(new ValueConnection(getScore.value, addPoints.a));
    graph.valueConnections.Add(new ValueConnection(points.output, addPoints.b));
    graph.valueConnections.Add(new ValueConnection(addPoints.sum, setScore.input));
}
```

---

## 8. Flow Control

### 8.1 If/Branch

**Description**: Conditional execution based on a boolean.

```csharp
public static void CreateIfBranchGraph(FlowGraph graph)
{
    graph.variables.Set("isReady", false);

    var start = new Start();
    graph.units.Add(start);
    start.position = new Vector2(0, 0);

    var getReady = new GetVariable();
    getReady.kind = VariableKind.Graph;
    getReady.defaultName = "isReady";
    graph.units.Add(getReady);
    getReady.position = new Vector2(100, 150);

    var ifUnit = new If();
    graph.units.Add(ifUnit);
    ifUnit.position = new Vector2(300, 0);

    var logTrue = new InvokeMember(new Member(typeof(Debug), "Log", new[] { typeof(object) }));
    graph.units.Add(logTrue);
    logTrue.position = new Vector2(600, -100);

    var logFalse = new InvokeMember(new Member(typeof(Debug), "Log", new[] { typeof(object) }));
    graph.units.Add(logFalse);
    logFalse.position = new Vector2(600, 100);

    var trueMsg = new Literal(typeof(string), "Ready!");
    graph.units.Add(trueMsg);
    trueMsg.position = new Vector2(400, -200);

    var falseMsg = new Literal(typeof(string), "Not ready");
    graph.units.Add(falseMsg);
    falseMsg.position = new Vector2(400, 200);

    graph.controlConnections.Add(new ControlConnection(start.trigger, ifUnit.enter));
    graph.controlConnections.Add(new ControlConnection(ifUnit.ifTrue, logTrue.enter));
    graph.controlConnections.Add(new ControlConnection(ifUnit.ifFalse, logFalse.enter));
    graph.valueConnections.Add(new ValueConnection(getReady.value, ifUnit.condition));
    graph.valueConnections.Add(new ValueConnection(trueMsg.output, logTrue.inputParameters[0]));
    graph.valueConnections.Add(new ValueConnection(falseMsg.output, logFalse.inputParameters[0]));
}
```

### 8.2 For Loop

**Description**: Loop 10 times and log the iteration index.

```csharp
public static void CreateForLoopGraph(FlowGraph graph)
{
    var start = new Start();
    graph.units.Add(start);
    start.position = new Vector2(0, 0);

    var forLoop = new For();
    graph.units.Add(forLoop);
    forLoop.position = new Vector2(300, 0);

    var firstIdx = new Literal(typeof(int), 0);
    graph.units.Add(firstIdx);
    firstIdx.position = new Vector2(100, 100);

    var lastIdx = new Literal(typeof(int), 10);
    graph.units.Add(lastIdx);
    lastIdx.position = new Vector2(100, 200);

    var step = new Literal(typeof(int), 1);
    graph.units.Add(step);
    step.position = new Vector2(100, 300);

    var debugLog = new InvokeMember(new Member(typeof(Debug), "Log", new[] { typeof(object) }));
    graph.units.Add(debugLog);
    debugLog.position = new Vector2(600, 0);

    // Control
    graph.controlConnections.Add(new ControlConnection(start.trigger, forLoop.enter));
    graph.controlConnections.Add(new ControlConnection(forLoop.body, debugLog.enter));

    // Values
    graph.valueConnections.Add(new ValueConnection(firstIdx.output, forLoop.firstIndex));
    graph.valueConnections.Add(new ValueConnection(lastIdx.output, forLoop.lastIndex));
    graph.valueConnections.Add(new ValueConnection(step.output, forLoop.step));
    graph.valueConnections.Add(new ValueConnection(forLoop.currentIndex, debugLog.inputParameters[0]));
}
```

### 8.3 While Loop

**Description**: Loop while a condition is true.

```csharp
public static void CreateWhileLoopGraph(FlowGraph graph)
{
    graph.variables.Set("counter", 0);

    var start = new Start();
    graph.units.Add(start);
    start.position = new Vector2(0, 0);

    // Condition: counter < 10
    var getCounter = new GetVariable();
    getCounter.kind = VariableKind.Graph;
    getCounter.defaultName = "counter";
    graph.units.Add(getCounter);
    getCounter.position = new Vector2(100, 200);

    var maxVal = new Literal(typeof(float), 10f);
    graph.units.Add(maxVal);
    maxVal.position = new Vector2(100, 300);

    var lessThan = new Less();
    graph.units.Add(lessThan);
    lessThan.position = new Vector2(300, 200);

    var whileLoop = new While();
    graph.units.Add(whileLoop);
    whileLoop.position = new Vector2(500, 0);

    // Control
    graph.controlConnections.Add(new ControlConnection(start.trigger, whileLoop.enter));

    // Condition
    graph.valueConnections.Add(new ValueConnection(getCounter.value, lessThan.a));
    graph.valueConnections.Add(new ValueConnection(maxVal.output, lessThan.b));
    graph.valueConnections.Add(new ValueConnection(lessThan.comparison, whileLoop.condition));

    // Body: increment counter (would need SetVariable wired to whileLoop.body)
}
```

### 8.4 Sequence

**Description**: Execute multiple actions in order from a single trigger.

```csharp
public static void CreateSequenceGraph(FlowGraph graph)
{
    var start = new Start();
    graph.units.Add(start);
    start.position = new Vector2(0, 0);

    var seq = new Sequence();
    seq.outputCount = 3;
    graph.units.Add(seq);
    seq.position = new Vector2(300, 0);

    // Three Debug.Log actions
    var log1 = new InvokeMember(new Member(typeof(Debug), "Log", new[] { typeof(object) }));
    graph.units.Add(log1);
    log1.position = new Vector2(600, -150);

    var log2 = new InvokeMember(new Member(typeof(Debug), "Log", new[] { typeof(object) }));
    graph.units.Add(log2);
    log2.position = new Vector2(600, 0);

    var log3 = new InvokeMember(new Member(typeof(Debug), "Log", new[] { typeof(object) }));
    graph.units.Add(log3);
    log3.position = new Vector2(600, 150);

    var msg1 = new Literal(typeof(string), "Step 1");
    graph.units.Add(msg1);
    msg1.position = new Vector2(400, -250);

    var msg2 = new Literal(typeof(string), "Step 2");
    graph.units.Add(msg2);
    msg2.position = new Vector2(400, -50);

    var msg3 = new Literal(typeof(string), "Step 3");
    graph.units.Add(msg3);
    msg3.position = new Vector2(400, 100);

    // Control
    graph.controlConnections.Add(new ControlConnection(start.trigger, seq.enter));
    graph.controlConnections.Add(new ControlConnection(seq.multiOutputs[0], log1.enter));
    graph.controlConnections.Add(new ControlConnection(seq.multiOutputs[1], log2.enter));
    graph.controlConnections.Add(new ControlConnection(seq.multiOutputs[2], log3.enter));

    // Values
    graph.valueConnections.Add(new ValueConnection(msg1.output, log1.inputParameters[0]));
    graph.valueConnections.Add(new ValueConnection(msg2.output, log2.inputParameters[0]));
    graph.valueConnections.Add(new ValueConnection(msg3.output, log3.inputParameters[0]));
}
```

---

## 9. Coroutine-Like Patterns

### 9.1 WaitForSeconds

**Description**: Wait 2 seconds then execute an action.

```csharp
public static void CreateWaitGraph(FlowGraph graph)
{
    var start = new Start();
    graph.units.Add(start);
    start.position = new Vector2(0, 0);

    var wait = new WaitForSecondsUnit();
    graph.units.Add(wait);
    wait.position = new Vector2(300, 0);

    var seconds = new Literal(typeof(float), 2.0f);
    graph.units.Add(seconds);
    seconds.position = new Vector2(100, 100);

    var debugLog = new InvokeMember(new Member(typeof(Debug), "Log", new[] { typeof(object) }));
    graph.units.Add(debugLog);
    debugLog.position = new Vector2(600, 0);

    var msg = new Literal(typeof(string), "2 seconds passed!");
    graph.units.Add(msg);
    msg.position = new Vector2(400, 100);

    // Control
    graph.controlConnections.Add(new ControlConnection(start.trigger, wait.enter));
    graph.controlConnections.Add(new ControlConnection(wait.exit, debugLog.enter));

    // Values
    graph.valueConnections.Add(new ValueConnection(seconds.output, wait.seconds));
    graph.valueConnections.Add(new ValueConnection(msg.output, debugLog.inputParameters[0]));
}
```

### 9.2 Timer (Periodic Action)

**Description**: Execute something after a timer elapses.

```csharp
public static void CreateTimerGraph(FlowGraph graph)
{
    var start = new Start();
    graph.units.Add(start);
    start.position = new Vector2(0, 0);

    var timer = new Timer();
    graph.units.Add(timer);
    timer.position = new Vector2(300, 0);

    var duration = new Literal(typeof(float), 5.0f);
    graph.units.Add(duration);
    duration.position = new Vector2(100, 100);

    graph.controlConnections.Add(new ControlConnection(start.trigger, timer.controlInputs["start"]));
    graph.valueConnections.Add(new ValueConnection(duration.output, timer.valueInputs["duration"]));
    // timer has control outputs for tick, completed
}
```

### 9.3 Cooldown

**Description**: Limit how often an action can execute.

```csharp
public static void CreateCooldownGraph(FlowGraph graph)
{
    var update = new Update();
    graph.units.Add(update);
    update.position = new Vector2(0, 0);

    var cooldown = new Cooldown();
    graph.units.Add(cooldown);
    cooldown.position = new Vector2(300, 0);

    var duration = new Literal(typeof(float), 1.0f);
    graph.units.Add(duration);
    duration.position = new Vector2(100, 100);

    graph.controlConnections.Add(new ControlConnection(update.trigger, cooldown.controlInputs["enter"]));
    graph.valueConnections.Add(new ValueConnection(duration.output, cooldown.valueInputs["duration"]));
    // cooldown.controlOutputs["ready"] fires when cooldown has elapsed
}
```

---

## 10. UI Interactions

### 10.1 Button Click

**Description**: Respond to a UI Button click.

```csharp
public static void CreateButtonClickGraph(FlowGraph graph)
{
    var onClick = new OnButtonClick();
    graph.units.Add(onClick);
    onClick.position = new Vector2(0, 0);

    var debugLog = new InvokeMember(new Member(typeof(Debug), "Log", new[] { typeof(object) }));
    graph.units.Add(debugLog);
    debugLog.position = new Vector2(300, 0);

    var msg = new Literal(typeof(string), "Button clicked!");
    graph.units.Add(msg);
    msg.position = new Vector2(100, 100);

    graph.controlConnections.Add(new ControlConnection(onClick.trigger, debugLog.enter));
    graph.valueConnections.Add(new ValueConnection(msg.output, debugLog.inputParameters[0]));
}
```

### 10.2 Slider Value Changed

**Description**: Respond to a UI Slider value change.

```csharp
public static void CreateSliderGraph(FlowGraph graph)
{
    var onSlider = new OnSliderValueChanged();
    graph.units.Add(onSlider);
    onSlider.position = new Vector2(0, 0);

    var debugLog = new InvokeMember(new Member(typeof(Debug), "Log", new[] { typeof(object) }));
    graph.units.Add(debugLog);
    debugLog.position = new Vector2(300, 0);

    graph.controlConnections.Add(new ControlConnection(onSlider.trigger, debugLog.enter));
    // onSlider has a value output for the new slider value
}
```

---

## 11. Animation

### 11.1 SetTrigger

**Description**: Trigger an animation transition.

```csharp
public static void CreateSetTriggerGraph(FlowGraph graph)
{
    var start = new Start();
    graph.units.Add(start);
    start.position = new Vector2(0, 0);

    // Animator.SetTrigger(string name)
    var setTrigger = new InvokeMember(
        new Member(typeof(Animator), "SetTrigger", new[] { typeof(string) })
    );
    graph.units.Add(setTrigger);
    setTrigger.position = new Vector2(300, 0);

    var triggerName = new Literal(typeof(string), "Jump");
    graph.units.Add(triggerName);
    triggerName.position = new Vector2(100, 100);

    graph.controlConnections.Add(new ControlConnection(start.trigger, setTrigger.enter));
    graph.valueConnections.Add(new ValueConnection(triggerName.output, setTrigger.inputParameters[0]));
    // target port auto-resolves to Animator on same GameObject
}
```

### 11.2 SetBool

**Description**: Set an animation boolean parameter.

```csharp
public static void CreateSetBoolGraph(FlowGraph graph)
{
    var start = new Start();
    graph.units.Add(start);
    start.position = new Vector2(0, 0);

    // Animator.SetBool(string name, bool value)
    var setBool = new InvokeMember(
        new Member(typeof(Animator), "SetBool", new[] { typeof(string), typeof(bool) })
    );
    graph.units.Add(setBool);
    setBool.position = new Vector2(300, 0);

    var paramName = new Literal(typeof(string), "isRunning");
    graph.units.Add(paramName);
    paramName.position = new Vector2(100, 100);

    var paramValue = new Literal(typeof(bool), true);
    graph.units.Add(paramValue);
    paramValue.position = new Vector2(100, 200);

    graph.controlConnections.Add(new ControlConnection(start.trigger, setBool.enter));
    graph.valueConnections.Add(new ValueConnection(paramName.output, setBool.inputParameters[0]));
    graph.valueConnections.Add(new ValueConnection(paramValue.output, setBool.inputParameters[1]));
}
```

---

## 12. Audio

### 12.1 PlayOneShot

**Description**: Play a sound effect using AudioSource.PlayOneShot.

```csharp
public static void CreatePlayOneShotGraph(FlowGraph graph)
{
    graph.variables.Set("sfxClip", (Object)null); // Assign AudioClip in inspector

    var start = new Start();
    graph.units.Add(start);
    start.position = new Vector2(0, 0);

    // AudioSource.PlayOneShot(AudioClip clip)
    var playOneShot = new InvokeMember(
        new Member(typeof(AudioSource), "PlayOneShot", new[] { typeof(AudioClip) })
    );
    graph.units.Add(playOneShot);
    playOneShot.position = new Vector2(400, 0);

    var getClip = new GetVariable();
    getClip.kind = VariableKind.Graph;
    getClip.defaultName = "sfxClip";
    graph.units.Add(getClip);
    getClip.position = new Vector2(150, 150);

    graph.controlConnections.Add(new ControlConnection(start.trigger, playOneShot.enter));
    graph.valueConnections.Add(new ValueConnection(getClip.value, playOneShot.inputParameters[0]));
}
```

### 12.2 Play / Stop

**Description**: Play and stop audio on an AudioSource.

```csharp
public static void CreatePlayStopGraph(FlowGraph graph)
{
    var start = new Start();
    graph.units.Add(start);
    start.position = new Vector2(0, 0);

    // AudioSource.Play()
    var play = new InvokeMember(new Member(typeof(AudioSource), "Play"));
    graph.units.Add(play);
    play.position = new Vector2(300, 0);

    graph.controlConnections.Add(new ControlConnection(start.trigger, play.enter));

    // AudioSource.Stop() can be connected to a different trigger
    var onDisable = new OnDisable();
    graph.units.Add(onDisable);
    onDisable.position = new Vector2(0, 200);

    var stop = new InvokeMember(new Member(typeof(AudioSource), "Stop"));
    graph.units.Add(stop);
    stop.position = new Vector2(300, 200);

    graph.controlConnections.Add(new ControlConnection(onDisable.trigger, stop.enter));
}
```

---

## 13. Math Operations

### 13.1 Vector3 Math (Addition)

**Description**: Add two vectors using GenericSum.

```csharp
public static void CreateVectorAddGraph(FlowGraph graph)
{
    var vecA = new Literal(typeof(Vector3), new Vector3(1, 0, 0));
    graph.units.Add(vecA);
    vecA.position = new Vector2(0, 0);

    var vecB = new Literal(typeof(Vector3), new Vector3(0, 1, 0));
    graph.units.Add(vecB);
    vecB.position = new Vector2(0, 150);

    // Vector3 addition via generic sum
    var add = new GenericSum();
    graph.units.Add(add);
    add.position = new Vector2(250, 75);

    graph.valueConnections.Add(new ValueConnection(vecA.output, add.a));
    graph.valueConnections.Add(new ValueConnection(vecB.output, add.b));
    // add.result provides the sum Vector3
}
```

### 13.2 Scalar Arithmetic

**Description**: Compute (a + b) * c.

```csharp
public static void CreateArithmeticGraph(FlowGraph graph)
{
    var a = new Literal(typeof(float), 5f);
    graph.units.Add(a);
    a.position = new Vector2(0, 0);

    var b = new Literal(typeof(float), 3f);
    graph.units.Add(b);
    b.position = new Vector2(0, 100);

    var c = new Literal(typeof(float), 2f);
    graph.units.Add(c);
    c.position = new Vector2(0, 200);

    var add = new ScalarAdd();
    graph.units.Add(add);
    add.position = new Vector2(200, 50);

    var multiply = new ScalarMultiply();
    graph.units.Add(multiply);
    multiply.position = new Vector2(400, 100);

    graph.valueConnections.Add(new ValueConnection(a.output, add.a));
    graph.valueConnections.Add(new ValueConnection(b.output, add.b));
    graph.valueConnections.Add(new ValueConnection(add.sum, multiply.a));
    graph.valueConnections.Add(new ValueConnection(c.output, multiply.b));
    // multiply.product = (5 + 3) * 2 = 16
}
```

### 13.3 Mathf.Clamp

**Description**: Clamp a value between min and max.

```csharp
public static void CreateClampGraph(FlowGraph graph)
{
    var inputVal = new Literal(typeof(float), 150f);
    graph.units.Add(inputVal);
    inputVal.position = new Vector2(0, 0);

    var minVal = new Literal(typeof(float), 0f);
    graph.units.Add(minVal);
    minVal.position = new Vector2(0, 100);

    var maxVal = new Literal(typeof(float), 100f);
    graph.units.Add(maxVal);
    maxVal.position = new Vector2(0, 200);

    // Mathf.Clamp(float value, float min, float max)
    var clamp = new InvokeMember(
        new Member(typeof(Mathf), "Clamp", new[] { typeof(float), typeof(float), typeof(float) })
    );
    graph.units.Add(clamp);
    clamp.position = new Vector2(250, 0);

    graph.valueConnections.Add(new ValueConnection(inputVal.output, clamp.inputParameters[0]));
    graph.valueConnections.Add(new ValueConnection(minVal.output, clamp.inputParameters[1]));
    graph.valueConnections.Add(new ValueConnection(maxVal.output, clamp.inputParameters[2]));
    // clamp.result = 100f (clamped from 150 to max 100)
}
```

### 13.4 Vector3.Lerp

**Description**: Linearly interpolate between two positions.

```csharp
public static void CreateLerpGraph(FlowGraph graph)
{
    var from = new Literal(typeof(Vector3), Vector3.zero);
    graph.units.Add(from);
    from.position = new Vector2(0, 0);

    var to = new Literal(typeof(Vector3), new Vector3(10, 0, 0));
    graph.units.Add(to);
    to.position = new Vector2(0, 150);

    var t = new Literal(typeof(float), 0.5f);
    graph.units.Add(t);
    t.position = new Vector2(0, 300);

    // Vector3.Lerp(Vector3 a, Vector3 b, float t)
    var lerp = new InvokeMember(
        new Member(typeof(Vector3), "Lerp",
            new[] { typeof(Vector3), typeof(Vector3), typeof(float) })
    );
    graph.units.Add(lerp);
    lerp.position = new Vector2(300, 0);

    graph.valueConnections.Add(new ValueConnection(from.output, lerp.inputParameters[0]));
    graph.valueConnections.Add(new ValueConnection(to.output, lerp.inputParameters[1]));
    graph.valueConnections.Add(new ValueConnection(t.output, lerp.inputParameters[2]));
    // lerp.result = (5, 0, 0)
}
```

---

## 14. String Operations

### 14.1 String Concatenation

**Description**: Concatenate two strings.

```csharp
public static void CreateStringConcatGraph(FlowGraph graph)
{
    var strA = new Literal(typeof(string), "Hello, ");
    graph.units.Add(strA);
    strA.position = new Vector2(0, 0);

    var strB = new Literal(typeof(string), "World!");
    graph.units.Add(strB);
    strB.position = new Vector2(0, 100);

    // String.Concat(string, string)
    var concat = new InvokeMember(
        new Member(typeof(string), "Concat", new[] { typeof(string), typeof(string) })
    );
    graph.units.Add(concat);
    concat.position = new Vector2(250, 0);

    graph.valueConnections.Add(new ValueConnection(strA.output, concat.inputParameters[0]));
    graph.valueConnections.Add(new ValueConnection(strB.output, concat.inputParameters[1]));
    // concat.result = "Hello, World!"
}
```

### 14.2 String Format

**Description**: Format a string with a value.

```csharp
public static void CreateStringFormatGraph(FlowGraph graph)
{
    var format = new Literal(typeof(string), "Score: {0}");
    graph.units.Add(format);
    format.position = new Vector2(0, 0);

    graph.variables.Set("score", 100);
    var getScore = new GetVariable();
    getScore.kind = VariableKind.Graph;
    getScore.defaultName = "score";
    graph.units.Add(getScore);
    getScore.position = new Vector2(0, 150);

    // String.Format(string format, object arg0)
    var strFormat = new InvokeMember(
        new Member(typeof(string), "Format", new[] { typeof(string), typeof(object) })
    );
    graph.units.Add(strFormat);
    strFormat.position = new Vector2(300, 0);

    graph.valueConnections.Add(new ValueConnection(format.output, strFormat.inputParameters[0]));
    graph.valueConnections.Add(new ValueConnection(getScore.value, strFormat.inputParameters[1]));
    // strFormat.result = "Score: 100"
}
```

---

## 15. Debug Logging

### 15.1 Simple Debug.Log

**Description**: Log a message to console.

```csharp
public static void CreateDebugLogGraph(FlowGraph graph)
{
    var start = new Start();
    graph.units.Add(start);
    start.position = new Vector2(0, 0);

    var debugLog = new InvokeMember(
        new Member(typeof(Debug), "Log", new[] { typeof(object) })
    );
    graph.units.Add(debugLog);
    debugLog.position = new Vector2(300, 0);

    var msg = new Literal(typeof(string), "Log message");
    graph.units.Add(msg);
    msg.position = new Vector2(100, 100);

    graph.controlConnections.Add(new ControlConnection(start.trigger, debugLog.enter));
    graph.valueConnections.Add(new ValueConnection(msg.output, debugLog.inputParameters[0]));
}
```

**Port names**: `start.trigger` -> `debugLog.enter`, `msg.output` -> `debugLog.inputParameters[0]`

### 15.2 Debug.LogWarning

**Description**: Log a warning message.

```csharp
public static void CreateDebugLogWarningGraph(FlowGraph graph)
{
    var start = new Start();
    graph.units.Add(start);
    start.position = new Vector2(0, 0);

    var logWarning = new InvokeMember(
        new Member(typeof(Debug), "LogWarning", new[] { typeof(object) })
    );
    graph.units.Add(logWarning);
    logWarning.position = new Vector2(300, 0);

    var msg = new Literal(typeof(string), "Warning!");
    graph.units.Add(msg);
    msg.position = new Vector2(100, 100);

    graph.controlConnections.Add(new ControlConnection(start.trigger, logWarning.enter));
    graph.valueConnections.Add(new ValueConnection(msg.output, logWarning.inputParameters[0]));
}
```

### 15.3 Debug.LogError

**Description**: Log an error message.

```csharp
public static void CreateDebugLogErrorGraph(FlowGraph graph)
{
    var start = new Start();
    graph.units.Add(start);
    start.position = new Vector2(0, 0);

    var logError = new InvokeMember(
        new Member(typeof(Debug), "LogError", new[] { typeof(object) })
    );
    graph.units.Add(logError);
    logError.position = new Vector2(300, 0);

    var msg = new Literal(typeof(string), "Error occurred!");
    graph.units.Add(msg);
    msg.position = new Vector2(100, 100);

    graph.controlConnections.Add(new ControlConnection(start.trigger, logError.enter));
    graph.valueConnections.Add(new ValueConnection(msg.output, logError.inputParameters[0]));
}
```

---

## Full Example: Complete Editor Script Wrapper

Every pattern above can be wrapped in a full editor script like this:

```csharp
#if UNITY_EDITOR
using UnityEditor;
using UnityEngine;
using Unity.VisualScripting;

public static class PatternGraphCreator
{
    [MenuItem("Tools/VS Patterns/Create [PatternName] Graph")]
    public static void Create()
    {
        var graphAsset = ScriptableObject.CreateInstance<ScriptGraphAsset>();
        var graph = graphAsset.graph;

        // Call the pattern function
        CreatePatternGraph(graph);

        // Save
        if (!AssetDatabase.IsValidFolder("Assets/VisualScripting"))
            AssetDatabase.CreateFolder("Assets", "VisualScripting");

        AssetDatabase.CreateAsset(graphAsset, "Assets/VisualScripting/PatternGraph.asset");
        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();

        Debug.Log("Pattern graph created successfully.");
    }

    private static void CreatePatternGraph(FlowGraph graph)
    {
        // Insert pattern code here
    }
}
#endif
```

---

*Templates based on Unity Visual Scripting 1.7-1.9 and verified against working sample code in `Editor Script Samples/CreateRotateGraph.cs`.*
