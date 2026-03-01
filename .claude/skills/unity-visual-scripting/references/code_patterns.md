# Unity Visual Scripting - Code Pattern Templates

Complete working C# editor script patterns. All patterns require:

```csharp
#if UNITY_EDITOR
using UnityEditor;
using UnityEngine;
using Unity.VisualScripting;
#endif
```

## Table of Contents

1. [Full Graph Creation + Assignment](#1-full-graph-creation--assignment)
2. [Event Handling](#2-event-handling)
3. [Input Handling](#3-input-handling)
4. [Transform Manipulation](#4-transform-manipulation)
5. [Physics](#5-physics)
6. [Variables](#6-variables)
7. [Flow Control](#7-flow-control)
8. [Component Access](#8-component-access)
9. [Coroutine-Like Patterns](#9-coroutine-like-patterns)
10. [UI Interactions](#10-ui-interactions)
11. [Animation](#11-animation)
12. [Audio](#12-audio)
13. [Debug Logging](#13-debug-logging)
14. [Graph Assignment](#14-graph-assignment)

---

## 1. Full Graph Creation + Assignment

### Rotation Graph (proven working example)

```csharp
public static class CreateRotateGraph
{
    [MenuItem("Tools/Create Rotate Graph")]
    public static void Create()
    {
        var graphAsset = ScriptableObject.CreateInstance<ScriptGraphAsset>();
        var graph = graphAsset.graph;

        // On Update event
        var onUpdate = new Update();
        graph.units.Add(onUpdate);
        onUpdate.position = new Vector2(-300, 0);

        // Get Time.deltaTime
        var getDeltaTime = new GetMember(new Member(typeof(Time), nameof(Time.deltaTime)));
        graph.units.Add(getDeltaTime);
        getDeltaTime.position = new Vector2(-500, 200);

        // Speed literals (degrees per second)
        var xSpeed = new Literal(typeof(float), 10f);
        graph.units.Add(xSpeed);
        xSpeed.position = new Vector2(-500, 100);

        var ySpeed = new Literal(typeof(float), 20f);
        graph.units.Add(ySpeed);
        ySpeed.position = new Vector2(-500, 300);

        var zSpeed = new Literal(typeof(float), 5f);
        graph.units.Add(zSpeed);
        zSpeed.position = new Vector2(-500, 400);

        // Multiply: speed * deltaTime for each axis
        var multiplyX = new ScalarMultiply();
        graph.units.Add(multiplyX);
        multiplyX.position = new Vector2(-200, 100);

        var multiplyY = new ScalarMultiply();
        graph.units.Add(multiplyY);
        multiplyY.position = new Vector2(-200, 300);

        var multiplyZ = new ScalarMultiply();
        graph.units.Add(multiplyZ);
        multiplyZ.position = new Vector2(-200, 400);

        // Transform.Rotate(float, float, float)
        var rotateMember = new Member(typeof(Transform), "Rotate",
            new[] { typeof(float), typeof(float), typeof(float) });
        var rotate = new InvokeMember(rotateMember);
        graph.units.Add(rotate);
        rotate.position = new Vector2(150, 0);

        // Control: Update -> Rotate
        graph.controlConnections.Add(new ControlConnection(onUpdate.trigger, rotate.enter));

        // Value: speed * deltaTime -> Rotate parameters
        graph.valueConnections.Add(new ValueConnection(xSpeed.output, multiplyX.a));
        graph.valueConnections.Add(new ValueConnection(getDeltaTime.value, multiplyX.b));
        graph.valueConnections.Add(new ValueConnection(ySpeed.output, multiplyY.a));
        graph.valueConnections.Add(new ValueConnection(getDeltaTime.value, multiplyY.b));
        graph.valueConnections.Add(new ValueConnection(zSpeed.output, multiplyZ.a));
        graph.valueConnections.Add(new ValueConnection(getDeltaTime.value, multiplyZ.b));
        graph.valueConnections.Add(new ValueConnection(multiplyX.product, rotate.inputParameters[0]));
        graph.valueConnections.Add(new ValueConnection(multiplyY.product, rotate.inputParameters[1]));
        graph.valueConnections.Add(new ValueConnection(multiplyZ.product, rotate.inputParameters[2]));

        // Save
        if (!AssetDatabase.IsValidFolder("Assets/VisualScripting"))
            AssetDatabase.CreateFolder("Assets", "VisualScripting");
        AssetDatabase.CreateAsset(graphAsset, "Assets/VisualScripting/RotateCube.asset");
        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();

        // Assign to object
        var cube = GameObject.Find("RotatingCube");
        if (cube != null)
        {
            var machine = cube.GetComponent<ScriptMachine>();
            if (machine == null)
                machine = cube.AddComponent<ScriptMachine>();
            machine.nest.source = GraphSource.Macro;
            machine.nest.macro = graphAsset;
            EditorUtility.SetDirty(cube);
        }
    }
}
```

---

## 2. Event Handling

### Start -> Debug.Log

```csharp
var start = new Start();
graph.units.Add(start);
start.position = new Vector2(0, 0);

var debugLog = new InvokeMember(new Member(typeof(Debug), "Log", new[] { typeof(object) }));
graph.units.Add(debugLog);
debugLog.position = new Vector2(300, 0);

var message = new Literal(typeof(string), "Game Started!");
graph.units.Add(message);
message.position = new Vector2(100, 150);

graph.controlConnections.Add(new ControlConnection(start.trigger, debugLog.enter));
graph.valueConnections.Add(new ValueConnection(message.output, debugLog.inputParameters[0]));
```

### OnEnable / OnDisable pair

```csharp
var onEnable = new OnEnable();
graph.units.Add(onEnable);
onEnable.position = new Vector2(0, 0);

var onDisable = new OnDisable();
graph.units.Add(onDisable);
onDisable.position = new Vector2(0, 300);
// Connect triggers to desired actions
```

---

## 3. Input Handling

### GetKeyDown with Branch

```csharp
var update = new Update();
graph.units.Add(update);
update.position = new Vector2(0, 0);

var getKeyDown = new InvokeMember(
    new Member(typeof(Input), "GetKeyDown", new[] { typeof(KeyCode) })
);
graph.units.Add(getKeyDown);
getKeyDown.position = new Vector2(300, 0);

var keyCode = new Literal(typeof(KeyCode), KeyCode.Space);
graph.units.Add(keyCode);
keyCode.position = new Vector2(100, 150);

var ifUnit = new If();
graph.units.Add(ifUnit);
ifUnit.position = new Vector2(550, 0);

graph.controlConnections.Add(new ControlConnection(update.trigger, getKeyDown.enter));
graph.controlConnections.Add(new ControlConnection(getKeyDown.exit, ifUnit.enter));
graph.valueConnections.Add(new ValueConnection(keyCode.output, getKeyDown.inputParameters[0]));
graph.valueConnections.Add(new ValueConnection(getKeyDown.result, ifUnit.condition));
// ifUnit.ifTrue -> action
```

### GetAxis (movement)

```csharp
var getAxis = new InvokeMember(
    new Member(typeof(Input), "GetAxis", new[] { typeof(string) })
);
graph.units.Add(getAxis);

var axisName = new Literal(typeof(string), "Horizontal");
graph.units.Add(axisName);

graph.valueConnections.Add(new ValueConnection(axisName.output, getAxis.inputParameters[0]));
// getAxis.result -> float value
```

---

## 4. Transform Manipulation

### Translate (move forward)

```csharp
var translate = new InvokeMember(
    new Member(typeof(Transform), "Translate", new[] { typeof(Vector3) })
);
graph.units.Add(translate);

var direction = new Literal(typeof(Vector3), new Vector3(0, 0, 1));
graph.units.Add(direction);

graph.valueConnections.Add(new ValueConnection(direction.output, translate.inputParameters[0]));
```

### Get/Set Position

```csharp
// Get position
var getPos = new GetMember(new Member(typeof(Transform), "position"));
graph.units.Add(getPos);
// getPos.value -> Vector3

// Set position
var setPos = new SetMember(new Member(typeof(Transform), "position"));
graph.units.Add(setPos);
// setPos.assign (ControlInput), setPos.input (ValueInput for Vector3)
```

### LookAt

```csharp
var lookAt = new InvokeMember(
    new Member(typeof(Transform), "LookAt", new[] { typeof(Transform) })
);
graph.units.Add(lookAt);
```

---

## 5. Physics

### OnTriggerEnter -> Debug.Log

```csharp
var onTrigger = new OnTriggerEnter();
graph.units.Add(onTrigger);
onTrigger.position = new Vector2(0, 0);

var debugLog = new InvokeMember(new Member(typeof(Debug), "Log", new[] { typeof(object) }));
graph.units.Add(debugLog);
debugLog.position = new Vector2(300, 0);

var msg = new Literal(typeof(string), "Trigger entered!");
graph.units.Add(msg);
msg.position = new Vector2(100, 150);

graph.controlConnections.Add(new ControlConnection(onTrigger.trigger, debugLog.enter));
graph.valueConnections.Add(new ValueConnection(msg.output, debugLog.inputParameters[0]));
```

### AddForce

```csharp
var addForce = new InvokeMember(
    new Member(typeof(Rigidbody), "AddForce", new[] { typeof(Vector3) })
);
graph.units.Add(addForce);

var force = new Literal(typeof(Vector3), new Vector3(0, 500, 0));
graph.units.Add(force);

graph.valueConnections.Add(new ValueConnection(force.output, addForce.inputParameters[0]));
```

---

## 6. Variables

### Declare + Get + Set graph variables

```csharp
// Declare
graph.variables.Set("score", 0);

// GetVariable unit
var getScore = new GetVariable() { kind = VariableKind.Graph };
graph.units.Add(getScore);
getScore.defaultValues["name"] = "score";
// getScore.value -> int

// SetVariable unit
var setScore = new SetVariable() { kind = VariableKind.Graph };
graph.units.Add(setScore);
setScore.defaultValues["name"] = "score";
// control: setScore.assign -> setScore.assigned
// value: newValue -> setScore.input
```

### Increment variable pattern

```csharp
graph.variables.Set("counter", 0);

var getVar = new GetVariable() { kind = VariableKind.Graph };
graph.units.Add(getVar);
getVar.defaultValues["name"] = "counter";

var addOne = new ScalarSum();
graph.units.Add(addOne);

var one = new Literal(typeof(int), 1);
graph.units.Add(one);

var setVar = new SetVariable() { kind = VariableKind.Graph };
graph.units.Add(setVar);
setVar.defaultValues["name"] = "counter";

graph.valueConnections.Add(new ValueConnection(getVar.value, addOne.multiInputs[0]));
graph.valueConnections.Add(new ValueConnection(one.output, addOne.multiInputs[1]));
graph.valueConnections.Add(new ValueConnection(addOne.sum, setVar.input));
// Wire control: trigger -> setVar.assign
```

---

## 7. Flow Control

### If/Else branch

```csharp
var ifUnit = new If();
graph.units.Add(ifUnit);

// Wire: condition source -> ifUnit.condition
// Wire: ifUnit.ifTrue -> true action
// Wire: ifUnit.ifFalse -> false action
```

### Sequence (multiple actions)

```csharp
var seq = new Sequence();
seq.outputCount = 3;
graph.units.Add(seq);

graph.controlConnections.Add(new ControlConnection(trigger.exit, seq.enter));
graph.controlConnections.Add(new ControlConnection(seq.multiOutputs[0], action1.enter));
graph.controlConnections.Add(new ControlConnection(seq.multiOutputs[1], action2.enter));
graph.controlConnections.Add(new ControlConnection(seq.multiOutputs[2], action3.enter));
```

### For loop

```csharp
var forLoop = new For();
graph.units.Add(forLoop);

var first = new Literal(typeof(int), 0);
graph.units.Add(first);
var last = new Literal(typeof(int), 10);
graph.units.Add(last);
var step = new Literal(typeof(int), 1);
graph.units.Add(step);

graph.valueConnections.Add(new ValueConnection(first.output, forLoop.firstIndex));
graph.valueConnections.Add(new ValueConnection(last.output, forLoop.lastIndex));
graph.valueConnections.Add(new ValueConnection(step.output, forLoop.step));
// forLoop.body -> loop body, forLoop.exit -> after loop
// forLoop.currentIndex -> current i
```

### While loop

```csharp
var whileLoop = new While();
graph.units.Add(whileLoop);
// Wire: condition -> whileLoop.condition
// Wire: whileLoop.body -> loop actions
// Wire: whileLoop.exit -> after loop
```

---

## 8. Component Access

### GetComponent pattern

```csharp
var getComponent = new InvokeMember(
    new Member(typeof(GameObject), "GetComponent",
        new[] { typeof(string) })
);
graph.units.Add(getComponent);
// Or use GetMember on a known component type property
```

### SetActive

```csharp
var setActive = new InvokeMember(
    new Member(typeof(GameObject), "SetActive", new[] { typeof(bool) })
);
graph.units.Add(setActive);

var active = new Literal(typeof(bool), false);
graph.units.Add(active);

graph.valueConnections.Add(new ValueConnection(active.output, setActive.inputParameters[0]));
```

### Instantiate

```csharp
var instantiate = new InvokeMember(
    new Member(typeof(Object), "Instantiate", new[] { typeof(Object) })
);
graph.units.Add(instantiate);
// Wire prefab reference to instantiate.inputParameters[0]
```

### Destroy

```csharp
var destroy = new InvokeMember(
    new Member(typeof(Object), "Destroy", new[] { typeof(Object) })
);
graph.units.Add(destroy);
```

---

## 9. Coroutine-Like Patterns

### WaitForSeconds

```csharp
var wait = new WaitForSecondsUnit();
graph.units.Add(wait);

var seconds = new Literal(typeof(float), 2.0f);
graph.units.Add(seconds);

graph.valueConnections.Add(new ValueConnection(seconds.output, wait.seconds));
// Control: trigger -> wait.enter, wait.exit -> next action
```

### WaitUntil

```csharp
var waitUntil = new WaitUntilUnit();
graph.units.Add(waitUntil);
// Wire condition -> waitUntil.condition
// Control: trigger -> waitUntil.enter, waitUntil.exit -> next action
```

---

## 10. UI Interactions

### OnButtonClick

```csharp
var onClick = new OnButtonClick();
graph.units.Add(onClick);
onClick.position = new Vector2(0, 0);
// onClick.trigger -> action
```

### OnSliderValueChanged

```csharp
var onSlider = new OnSliderValueChanged();
graph.units.Add(onSlider);
// onSlider.trigger, onSlider.value outputs
```

---

## 11. Animation

### Animator.SetTrigger

```csharp
var setTrigger = new InvokeMember(
    new Member(typeof(Animator), "SetTrigger", new[] { typeof(string) })
);
graph.units.Add(setTrigger);

var triggerName = new Literal(typeof(string), "Jump");
graph.units.Add(triggerName);

graph.valueConnections.Add(new ValueConnection(triggerName.output, setTrigger.inputParameters[0]));
```

### Animator.SetBool

```csharp
var setBool = new InvokeMember(
    new Member(typeof(Animator), "SetBool", new[] { typeof(string), typeof(bool) })
);
graph.units.Add(setBool);
```

### Animator.SetFloat

```csharp
var setFloat = new InvokeMember(
    new Member(typeof(Animator), "SetFloat", new[] { typeof(string), typeof(float) })
);
graph.units.Add(setFloat);
```

---

## 12. Audio

### AudioSource.Play

```csharp
var play = new InvokeMember(
    new Member(typeof(AudioSource), "Play")
);
graph.units.Add(play);
```

### AudioSource.PlayOneShot

```csharp
var playOneShot = new InvokeMember(
    new Member(typeof(AudioSource), "PlayOneShot", new[] { typeof(AudioClip) })
);
graph.units.Add(playOneShot);
```

---

## 13. Debug Logging

### Debug.Log

```csharp
var debugLog = new InvokeMember(
    new Member(typeof(Debug), "Log", new[] { typeof(object) })
);
graph.units.Add(debugLog);

var msg = new Literal(typeof(string), "Message");
graph.units.Add(msg);

graph.valueConnections.Add(new ValueConnection(msg.output, debugLog.inputParameters[0]));
```

### Debug.LogWarning / Debug.LogError

```csharp
var logWarning = new InvokeMember(
    new Member(typeof(Debug), "LogWarning", new[] { typeof(object) })
);
var logError = new InvokeMember(
    new Member(typeof(Debug), "LogError", new[] { typeof(object) })
);
```

---

## 14. Graph Assignment

### Assign existing asset to GameObject

```csharp
public static void AssignGraph()
{
    var go = GameObject.Find("TargetObject");
    if (go == null) { Debug.LogError("Object not found."); return; }

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
```

### Assign to selected GameObject (editor selection)

```csharp
public static void AssignToSelected()
{
    var go = Selection.activeGameObject;
    if (go == null) { Debug.LogError("No GameObject selected."); return; }

    var graphAsset = AssetDatabase.LoadAssetAtPath<ScriptGraphAsset>(
        "Assets/VisualScripting/MyGraph.asset");
    if (graphAsset == null) { Debug.LogError("Graph asset not found."); return; }

    var machine = go.GetComponent<ScriptMachine>();
    if (machine == null)
        machine = go.AddComponent<ScriptMachine>();

    machine.nest.source = GraphSource.Macro;
    machine.nest.macro = graphAsset;
    EditorUtility.SetDirty(go);
    Selection.activeGameObject = go;
}
```

### Assign StateGraph to GameObject

```csharp
public static void AssignStateGraph()
{
    var go = GameObject.Find("TargetObject");
    if (go == null) { Debug.LogError("Object not found."); return; }

    var stateAsset = AssetDatabase.LoadAssetAtPath<StateGraphAsset>(
        "Assets/VisualScripting/MyStateGraph.asset");
    if (stateAsset == null) { Debug.LogError("State graph asset not found."); return; }

    var machine = go.GetComponent<StateMachine>();
    if (machine == null)
        machine = go.AddComponent<StateMachine>();

    machine.nest.source = GraphSource.Macro;
    machine.nest.macro = stateAsset;
    EditorUtility.SetDirty(go);
}
```

### Embed graph directly in component

```csharp
var machine = go.AddComponent<ScriptMachine>();
machine.nest.source = GraphSource.Embed;
machine.nest.embed = FlowGraph.WithStartUpdate();
EditorUtility.SetDirty(go);
```
