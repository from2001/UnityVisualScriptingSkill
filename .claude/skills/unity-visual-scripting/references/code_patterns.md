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
15. [JSON Graph Patterns (for Modification)](#15-json-graph-patterns-for-modification)

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

---

## 15. JSON Graph Patterns (for Modification)

JSON patterns for directly editing `.asset` files. Each example shows the `elements` array content. Wrap in the YAML boilerplate + JSON root structure (see `api_reference.md` Section 9).

### YAML Boilerplate Template

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

### JSON Root Structure

```json
{"graph":{"variables":{"Kind":"Flow","collection":{"$content":[],"$version":"A"},"$version":"A"},"controlInputDefinitions":[],"controlOutputDefinitions":[],"valueInputDefinitions":[],"valueOutputDefinitions":[],"title":null,"summary":null,"pan":{"x":0.0,"y":0.0},"zoom":1.0,"elements":[...ELEMENTS...],"$version":"A"}}
```

### Start -> Debug.Log (simplest pattern)

```json
[
  {
    "coroutine": false,
    "defaultValues": {},
    "position": {"x": 0.0, "y": 0.0},
    "guid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "$version": "A",
    "$type": "Unity.VisualScripting.Start",
    "$id": "1"
  },
  {
    "chainable": false,
    "parameterNames": ["message"],
    "member": {
      "name": "Log",
      "parameterTypes": ["System.Object"],
      "targetType": "UnityEngine.Debug",
      "targetTypeName": "UnityEngine.Debug",
      "$version": "A"
    },
    "defaultValues": {},
    "position": {"x": 300.0, "y": 0.0},
    "guid": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "$version": "A",
    "$type": "Unity.VisualScripting.InvokeMember",
    "$id": "2"
  },
  {
    "type": "System.String",
    "value": {"$content": "Hello from YAML!", "$type": "System.String"},
    "defaultValues": {},
    "position": {"x": 100.0, "y": 150.0},
    "guid": "c3d4e5f6-a7b8-9012-cdef-123456789012",
    "$version": "A",
    "$type": "Unity.VisualScripting.Literal",
    "$id": "3"
  },
  {
    "sourceUnit": {"$ref": "1"},
    "sourceKey": "trigger",
    "destinationUnit": {"$ref": "2"},
    "destinationKey": "enter",
    "guid": "d4e5f6a7-b8c9-0123-defa-234567890123",
    "$type": "Unity.VisualScripting.ControlConnection"
  },
  {
    "sourceUnit": {"$ref": "3"},
    "sourceKey": "output",
    "destinationUnit": {"$ref": "2"},
    "destinationKey": "%message",
    "guid": "e5f6a7b8-c9d0-1234-efab-345678901234",
    "$type": "Unity.VisualScripting.ValueConnection"
  }
]
```

### Update -> Transform.Rotate (full example)

```json
[
  {
    "coroutine": false,
    "defaultValues": {},
    "position": {"x": -300.0, "y": 0.0},
    "guid": "11111111-1111-1111-1111-111111111111",
    "$version": "A",
    "$type": "Unity.VisualScripting.Update",
    "$id": "1"
  },
  {
    "member": {
      "name": "deltaTime",
      "parameterTypes": null,
      "targetType": "UnityEngine.Time",
      "targetTypeName": "UnityEngine.Time",
      "$version": "A"
    },
    "defaultValues": {},
    "position": {"x": -500.0, "y": 200.0},
    "guid": "22222222-2222-2222-2222-222222222222",
    "$version": "A",
    "$type": "Unity.VisualScripting.GetMember",
    "$id": "2"
  },
  {
    "type": "System.Single",
    "value": {"$content": 10.0, "$type": "System.Single"},
    "defaultValues": {},
    "position": {"x": -500.0, "y": 100.0},
    "guid": "33333333-3333-3333-3333-333333333333",
    "$version": "A",
    "$type": "Unity.VisualScripting.Literal",
    "$id": "3"
  },
  {
    "type": "System.Single",
    "value": {"$content": 20.0, "$type": "System.Single"},
    "defaultValues": {},
    "position": {"x": -500.0, "y": 300.0},
    "guid": "44444444-4444-4444-4444-444444444444",
    "$version": "A",
    "$type": "Unity.VisualScripting.Literal",
    "$id": "4"
  },
  {
    "type": "System.Single",
    "value": {"$content": 5.0, "$type": "System.Single"},
    "defaultValues": {},
    "position": {"x": -500.0, "y": 400.0},
    "guid": "55555555-5555-5555-5555-555555555555",
    "$version": "A",
    "$type": "Unity.VisualScripting.Literal",
    "$id": "5"
  },
  {
    "defaultValues": {
      "a": {"$content": 0.0, "$type": "System.Single"},
      "b": {"$content": 0.0, "$type": "System.Single"}
    },
    "position": {"x": -200.0, "y": 100.0},
    "guid": "66666666-6666-6666-6666-666666666666",
    "$version": "A",
    "$type": "Unity.VisualScripting.ScalarMultiply",
    "$id": "6"
  },
  {
    "defaultValues": {
      "a": {"$content": 0.0, "$type": "System.Single"},
      "b": {"$content": 0.0, "$type": "System.Single"}
    },
    "position": {"x": -200.0, "y": 300.0},
    "guid": "77777777-7777-7777-7777-777777777777",
    "$version": "A",
    "$type": "Unity.VisualScripting.ScalarMultiply",
    "$id": "7"
  },
  {
    "defaultValues": {
      "a": {"$content": 0.0, "$type": "System.Single"},
      "b": {"$content": 0.0, "$type": "System.Single"}
    },
    "position": {"x": -200.0, "y": 400.0},
    "guid": "88888888-8888-8888-8888-888888888888",
    "$version": "A",
    "$type": "Unity.VisualScripting.ScalarMultiply",
    "$id": "8"
  },
  {
    "chainable": false,
    "parameterNames": ["xAngle", "yAngle", "zAngle"],
    "member": {
      "name": "Rotate",
      "parameterTypes": ["System.Single", "System.Single", "System.Single"],
      "targetType": "UnityEngine.Transform",
      "targetTypeName": "UnityEngine.Transform",
      "$version": "A"
    },
    "defaultValues": {
      "target": null,
      "%xAngle": {"$content": 0.0, "$type": "System.Single"},
      "%yAngle": {"$content": 0.0, "$type": "System.Single"},
      "%zAngle": {"$content": 0.0, "$type": "System.Single"}
    },
    "position": {"x": 150.0, "y": 0.0},
    "guid": "99999999-9999-9999-9999-999999999999",
    "$version": "A",
    "$type": "Unity.VisualScripting.InvokeMember",
    "$id": "9"
  },
  {"sourceUnit":{"$ref":"1"},"sourceKey":"trigger","destinationUnit":{"$ref":"9"},"destinationKey":"enter","guid":"aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa","$type":"Unity.VisualScripting.ControlConnection"},
  {"sourceUnit":{"$ref":"3"},"sourceKey":"output","destinationUnit":{"$ref":"6"},"destinationKey":"a","guid":"bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb","$type":"Unity.VisualScripting.ValueConnection"},
  {"sourceUnit":{"$ref":"2"},"sourceKey":"value","destinationUnit":{"$ref":"6"},"destinationKey":"b","guid":"cccccccc-cccc-cccc-cccc-cccccccccccc","$type":"Unity.VisualScripting.ValueConnection"},
  {"sourceUnit":{"$ref":"4"},"sourceKey":"output","destinationUnit":{"$ref":"7"},"destinationKey":"a","guid":"dddddddd-dddd-dddd-dddd-dddddddddddd","$type":"Unity.VisualScripting.ValueConnection"},
  {"sourceUnit":{"$ref":"2"},"sourceKey":"value","destinationUnit":{"$ref":"7"},"destinationKey":"b","guid":"eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee","$type":"Unity.VisualScripting.ValueConnection"},
  {"sourceUnit":{"$ref":"5"},"sourceKey":"output","destinationUnit":{"$ref":"8"},"destinationKey":"a","guid":"ffffffff-ffff-ffff-ffff-ffffffffffff","$type":"Unity.VisualScripting.ValueConnection"},
  {"sourceUnit":{"$ref":"2"},"sourceKey":"value","destinationUnit":{"$ref":"8"},"destinationKey":"b","guid":"01010101-0101-0101-0101-010101010101","$type":"Unity.VisualScripting.ValueConnection"},
  {"sourceUnit":{"$ref":"6"},"sourceKey":"product","destinationUnit":{"$ref":"9"},"destinationKey":"%xAngle","guid":"02020202-0202-0202-0202-020202020202","$type":"Unity.VisualScripting.ValueConnection"},
  {"sourceUnit":{"$ref":"7"},"sourceKey":"product","destinationUnit":{"$ref":"9"},"destinationKey":"%yAngle","guid":"03030303-0303-0303-0303-030303030303","$type":"Unity.VisualScripting.ValueConnection"},
  {"sourceUnit":{"$ref":"8"},"sourceKey":"product","destinationUnit":{"$ref":"9"},"destinationKey":"%zAngle","guid":"04040404-0404-0404-0404-040404040404","$type":"Unity.VisualScripting.ValueConnection"}
]
```

### OnTriggerEnter -> Action

```json
[
  {
    "coroutine": false,
    "defaultValues": {"target": null},
    "position": {"x": 0.0, "y": 0.0},
    "guid": "aaa11111-1111-1111-1111-111111111111",
    "$version": "A",
    "$type": "Unity.VisualScripting.OnTriggerEnter",
    "$id": "1"
  },
  {
    "chainable": false,
    "parameterNames": ["message"],
    "member": {
      "name": "Log",
      "parameterTypes": ["System.Object"],
      "targetType": "UnityEngine.Debug",
      "targetTypeName": "UnityEngine.Debug",
      "$version": "A"
    },
    "defaultValues": {},
    "position": {"x": 300.0, "y": 0.0},
    "guid": "aaa22222-2222-2222-2222-222222222222",
    "$version": "A",
    "$type": "Unity.VisualScripting.InvokeMember",
    "$id": "2"
  },
  {
    "type": "System.String",
    "value": {"$content": "Trigger entered!", "$type": "System.String"},
    "defaultValues": {},
    "position": {"x": 100.0, "y": 150.0},
    "guid": "aaa33333-3333-3333-3333-333333333333",
    "$version": "A",
    "$type": "Unity.VisualScripting.Literal",
    "$id": "3"
  },
  {"sourceUnit":{"$ref":"1"},"sourceKey":"trigger","destinationUnit":{"$ref":"2"},"destinationKey":"enter","guid":"aaa44444-4444-4444-4444-444444444444","$type":"Unity.VisualScripting.ControlConnection"},
  {"sourceUnit":{"$ref":"3"},"sourceKey":"output","destinationUnit":{"$ref":"2"},"destinationKey":"%message","guid":"aaa55555-5555-5555-5555-555555555555","$type":"Unity.VisualScripting.ValueConnection"}
]
```

### Get/Set Variable and Increment

```json
[
  {
    "coroutine": false,
    "defaultValues": {},
    "position": {"x": 0.0, "y": 0.0},
    "guid": "bbb11111-1111-1111-1111-111111111111",
    "$version": "A",
    "$type": "Unity.VisualScripting.Start",
    "$id": "1"
  },
  {
    "kind": "Graph",
    "defaultValues": {"name": {"$content": "counter", "$type": "System.String"}},
    "position": {"x": 200.0, "y": 150.0},
    "guid": "bbb22222-2222-2222-2222-222222222222",
    "$version": "A",
    "$type": "Unity.VisualScripting.GetVariable",
    "$id": "2"
  },
  {
    "inputCount": 2,
    "defaultValues": {"1": {"$content": 1, "$type": "System.Int32"}},
    "position": {"x": 400.0, "y": 150.0},
    "guid": "bbb33333-3333-3333-3333-333333333333",
    "$version": "A",
    "$type": "Unity.VisualScripting.ScalarSum",
    "$id": "3"
  },
  {
    "kind": "Graph",
    "defaultValues": {"name": {"$content": "counter", "$type": "System.String"}},
    "position": {"x": 600.0, "y": 0.0},
    "guid": "bbb44444-4444-4444-4444-444444444444",
    "$version": "A",
    "$type": "Unity.VisualScripting.SetVariable",
    "$id": "4"
  },
  {"sourceUnit":{"$ref":"1"},"sourceKey":"trigger","destinationUnit":{"$ref":"4"},"destinationKey":"assign","guid":"bbb55555-5555-5555-5555-555555555555","$type":"Unity.VisualScripting.ControlConnection"},
  {"sourceUnit":{"$ref":"2"},"sourceKey":"value","destinationUnit":{"$ref":"3"},"destinationKey":"0","guid":"bbb66666-6666-6666-6666-666666666666","$type":"Unity.VisualScripting.ValueConnection"},
  {"sourceUnit":{"$ref":"3"},"sourceKey":"sum","destinationUnit":{"$ref":"4"},"destinationKey":"input","guid":"bbb77777-7777-7777-7777-777777777777","$type":"Unity.VisualScripting.ValueConnection"}
]
```

### If/Else Branch

```json
[
  {
    "coroutine": false,
    "defaultValues": {},
    "position": {"x": 0.0, "y": 0.0},
    "guid": "ccc11111-1111-1111-1111-111111111111",
    "$version": "A",
    "$type": "Unity.VisualScripting.Update",
    "$id": "1"
  },
  {
    "defaultValues": {"condition": {"$content": false, "$type": "System.Boolean"}},
    "position": {"x": 300.0, "y": 0.0},
    "guid": "ccc22222-2222-2222-2222-222222222222",
    "$version": "A",
    "$type": "Unity.VisualScripting.If",
    "$id": "2"
  },
  {"sourceUnit":{"$ref":"1"},"sourceKey":"trigger","destinationUnit":{"$ref":"2"},"destinationKey":"enter","guid":"ccc33333-3333-3333-3333-333333333333","$type":"Unity.VisualScripting.ControlConnection"}
]
```

Wire `condition` (ValueInput), `ifTrue`/`ifFalse` (ControlOutput) to additional units as needed.

### Sequence (fan-out)

```json
[
  {
    "coroutine": false,
    "defaultValues": {},
    "position": {"x": 0.0, "y": 0.0},
    "guid": "ddd11111-1111-1111-1111-111111111111",
    "$version": "A",
    "$type": "Unity.VisualScripting.Start",
    "$id": "1"
  },
  {
    "outputCount": 3,
    "defaultValues": {},
    "position": {"x": 250.0, "y": 0.0},
    "guid": "ddd22222-2222-2222-2222-222222222222",
    "$version": "A",
    "$type": "Unity.VisualScripting.Sequence",
    "$id": "2"
  },
  {"sourceUnit":{"$ref":"1"},"sourceKey":"trigger","destinationUnit":{"$ref":"2"},"destinationKey":"enter","guid":"ddd33333-3333-3333-3333-333333333333","$type":"Unity.VisualScripting.ControlConnection"}
]
```

Output keys: `"0"`, `"1"`, `"2"`. Connect each to separate action units.

### InvokeMember — Static Void Method (Debug.Log)

```json
{
  "chainable": false,
  "parameterNames": ["message"],
  "member": {
    "name": "Log",
    "parameterTypes": ["System.Object"],
    "targetType": "UnityEngine.Debug",
    "targetTypeName": "UnityEngine.Debug",
    "$version": "A"
  },
  "defaultValues": {},
  "position": {"x": 300.0, "y": 0.0},
  "guid": "eee11111-1111-1111-1111-111111111111",
  "$version": "A",
  "$type": "Unity.VisualScripting.InvokeMember",
  "$id": "N"
}
```

Static: no `target` in defaultValues. Void: no `result` port.

### InvokeMember — Instance Method (Transform.Rotate)

```json
{
  "chainable": false,
  "parameterNames": ["xAngle", "yAngle", "zAngle"],
  "member": {
    "name": "Rotate",
    "parameterTypes": ["System.Single", "System.Single", "System.Single"],
    "targetType": "UnityEngine.Transform",
    "targetTypeName": "UnityEngine.Transform",
    "$version": "A"
  },
  "defaultValues": {
    "target": null,
    "%xAngle": {"$content": 0.0, "$type": "System.Single"},
    "%yAngle": {"$content": 0.0, "$type": "System.Single"},
    "%zAngle": {"$content": 0.0, "$type": "System.Single"}
  },
  "position": {"x": 150.0, "y": 0.0},
  "guid": "eee22222-2222-2222-2222-222222222222",
  "$version": "A",
  "$type": "Unity.VisualScripting.InvokeMember",
  "$id": "N"
}
```

Instance: `"target": null` in defaultValues. Parameter defaults: `%`-prefixed.

### InvokeMember — No-Parameter Instance Method (AudioSource.Play)

```json
{
  "chainable": false,
  "parameterNames": [],
  "member": {
    "name": "Play",
    "parameterTypes": [],
    "targetType": "UnityEngine.AudioSource",
    "targetTypeName": "UnityEngine.AudioSource",
    "$version": "A"
  },
  "defaultValues": {"target": null},
  "position": {"x": 0.0, "y": 0.0},
  "guid": "eee33333-3333-3333-3333-333333333333",
  "$version": "A",
  "$type": "Unity.VisualScripting.InvokeMember",
  "$id": "N"
}
```

### GetMember — Static Property (Time.deltaTime)

```json
{
  "member": {
    "name": "deltaTime",
    "parameterTypes": null,
    "targetType": "UnityEngine.Time",
    "targetTypeName": "UnityEngine.Time",
    "$version": "A"
  },
  "defaultValues": {},
  "position": {"x": -500.0, "y": 200.0},
  "guid": "fff11111-1111-1111-1111-111111111111",
  "$version": "A",
  "$type": "Unity.VisualScripting.GetMember",
  "$id": "N"
}
```

Static: `"defaultValues": {}`. `parameterTypes` is `null` for properties.

### GetMember — Instance Property (Transform.position)

```json
{
  "member": {
    "name": "position",
    "parameterTypes": null,
    "targetType": "UnityEngine.Transform",
    "targetTypeName": "UnityEngine.Transform",
    "$version": "A"
  },
  "defaultValues": {"target": null},
  "position": {"x": 0.0, "y": 0.0},
  "guid": "fff22222-2222-2222-2222-222222222222",
  "$version": "A",
  "$type": "Unity.VisualScripting.GetMember",
  "$id": "N"
}
```

Instance: `"target": null` in defaultValues.

### SetMember — Instance Property (Material.color)

```json
{
  "chainable": false,
  "member": {
    "name": "color",
    "parameterTypes": null,
    "targetType": "UnityEngine.Material",
    "targetTypeName": "UnityEngine.Material",
    "$version": "A"
  },
  "defaultValues": {
    "target": null,
    "input": {"r": 1.0, "g": 0.0, "b": 0.0, "a": 1.0, "$type": "UnityEngine.Color"}
  },
  "position": {"x": 0.0, "y": 0.0},
  "guid": "fff33333-3333-3333-3333-333333333333",
  "$version": "A",
  "$type": "Unity.VisualScripting.SetMember",
  "$id": "N"
}
```

### Literal Value Types

```json
// String
{"type":"System.String","value":{"$content":"Hello","$type":"System.String"},"defaultValues":{},"position":{"x":0.0,"y":0.0},"guid":"...","$version":"A","$type":"Unity.VisualScripting.Literal","$id":"N"}

// Float
{"type":"System.Single","value":{"$content":3.14,"$type":"System.Single"},"defaultValues":{},"position":{"x":0.0,"y":0.0},"guid":"...","$version":"A","$type":"Unity.VisualScripting.Literal","$id":"N"}

// Int
{"type":"System.Int32","value":{"$content":42,"$type":"System.Int32"},"defaultValues":{},"position":{"x":0.0,"y":0.0},"guid":"...","$version":"A","$type":"Unity.VisualScripting.Literal","$id":"N"}

// Bool
{"type":"System.Boolean","value":{"$content":true,"$type":"System.Boolean"},"defaultValues":{},"position":{"x":0.0,"y":0.0},"guid":"...","$version":"A","$type":"Unity.VisualScripting.Literal","$id":"N"}

// Vector3
{"type":"UnityEngine.Vector3","value":{"x":1.0,"y":2.0,"z":3.0,"$type":"UnityEngine.Vector3"},"defaultValues":{},"position":{"x":0.0,"y":0.0},"guid":"...","$version":"A","$type":"Unity.VisualScripting.Literal","$id":"N"}

// Color
{"type":"UnityEngine.Color","value":{"r":1.0,"g":0.0,"b":0.0,"a":1.0,"$type":"UnityEngine.Color"},"defaultValues":{},"position":{"x":0.0,"y":0.0},"guid":"...","$version":"A","$type":"Unity.VisualScripting.Literal","$id":"N"}

// Enum (KeyCode.Space = 32)
{"type":"UnityEngine.KeyCode","value":{"$content":32,"$type":"UnityEngine.KeyCode"},"defaultValues":{},"position":{"x":0.0,"y":0.0},"guid":"...","$version":"A","$type":"Unity.VisualScripting.Literal","$id":"N"}
```
