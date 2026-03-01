# Unity Visual Scripting - JSON Graph Patterns

Complete `.asset` file patterns for generating Unity Visual Scripting graphs directly. Each pattern shows the JSON `elements` array content (units + connections).

## YAML Boilerplate Template

Every `.asset` file uses this exact template. Replace `GRAPH_NAME` and `JSON_CONTENT`:

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

**Rules:**
- `m_Script` guid `95e66c6366d904e98bc83428217d4fd7` = `ScriptGraphAsset` (never changes)
- `JSON_CONTENT` is the entire graph JSON on a **single line**, wrapped in YAML single quotes
- Single quotes inside JSON string values must be escaped as `''` (YAML 1.1 rule)
- `m_Name` should match the filename (without `.asset`)

## JSON Root Structure

```json
{"graph":{"variables":{"Kind":"Flow","collection":{"$content":[],"$version":"A"},"$version":"A"},"controlInputDefinitions":[],"controlOutputDefinitions":[],"valueInputDefinitions":[],"valueOutputDefinitions":[],"title":null,"summary":null,"pan":{"x":0.0,"y":0.0},"zoom":1.0,"elements":[...],"$version":"A"}}
```

The `elements` array contains ALL units and connections in a flat list. Units come first, connections after.

## Table of Contents

1. [Start to Debug.Log (simplest)](#1-start-to-debuglog)
2. [Update to Rotation (full working example)](#2-update-to-rotation)
3. [OnTriggerEnter to Action](#3-ontriggerenter-to-action)
4. [Get/Set Variable and Increment](#4-getset-variable-and-increment)
5. [If/Else Branch](#5-ifelse-branch)
6. [Sequence (fan-out)](#6-sequence-fan-out)
7. [InvokeMember Patterns](#7-invokemember-patterns)
8. [GetMember / SetMember](#8-getmember--setmember)
9. [Literal Value Types](#9-literal-value-types)

---

## 1. Start to Debug.Log

The simplest possible graph: Start event fires Debug.Log with a string literal.

### Elements

```json
[
  {
    "coroutine": false,
    "defaultValues": {},
    "position": {"x": 0.0, "y": 0.0},
    "guid": "a1b2c3d4-e5f6-4a7b-8c9d-000000000001",
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
    "guid": "a1b2c3d4-e5f6-4a7b-8c9d-000000000002",
    "$version": "A",
    "$type": "Unity.VisualScripting.InvokeMember",
    "$id": "2"
  },
  {
    "type": "System.String",
    "value": {"$content": "Game Started!", "$type": "System.String"},
    "defaultValues": {},
    "position": {"x": 100.0, "y": 150.0},
    "guid": "a1b2c3d4-e5f6-4a7b-8c9d-000000000003",
    "$version": "A",
    "$type": "Unity.VisualScripting.Literal",
    "$id": "3"
  },
  {
    "sourceUnit": {"$ref": "1"},
    "sourceKey": "trigger",
    "destinationUnit": {"$ref": "2"},
    "destinationKey": "enter",
    "guid": "a1b2c3d4-e5f6-4a7b-8c9d-000000000004",
    "$type": "Unity.VisualScripting.ControlConnection"
  },
  {
    "sourceUnit": {"$ref": "3"},
    "sourceKey": "output",
    "destinationUnit": {"$ref": "2"},
    "destinationKey": "%message",
    "guid": "a1b2c3d4-e5f6-4a7b-8c9d-000000000005",
    "$type": "Unity.VisualScripting.ValueConnection"
  }
]
```

**Key observations:**
- Start event: `coroutine: false`, `defaultValues: {}`
- Debug.Log (static): no `target` in defaultValues, `parameterNames: ["message"]`
- InvokeMember parameter port key: `%message` (prefixed with `%`)
- Literal `output` port key: `"output"`
- Connections reference units by `$ref` matching the unit's `$id`

---

## 2. Update to Rotation

Full working graph: Update every frame → multiply speeds by deltaTime → Transform.Rotate.

### Elements

```json
[
  {
    "coroutine": false,
    "defaultValues": {},
    "position": {"x": -300.0, "y": 0.0},
    "guid": "b2c3d4e5-f6a7-4b8c-9d0e-000000000001",
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
    "guid": "b2c3d4e5-f6a7-4b8c-9d0e-000000000002",
    "$version": "A",
    "$type": "Unity.VisualScripting.GetMember",
    "$id": "2"
  },
  {
    "type": "System.Single",
    "value": {"$content": 10.0, "$type": "System.Single"},
    "defaultValues": {},
    "position": {"x": -500.0, "y": 100.0},
    "guid": "b2c3d4e5-f6a7-4b8c-9d0e-000000000003",
    "$version": "A",
    "$type": "Unity.VisualScripting.Literal",
    "$id": "3"
  },
  {
    "type": "System.Single",
    "value": {"$content": 20.0, "$type": "System.Single"},
    "defaultValues": {},
    "position": {"x": -500.0, "y": 300.0},
    "guid": "b2c3d4e5-f6a7-4b8c-9d0e-000000000004",
    "$version": "A",
    "$type": "Unity.VisualScripting.Literal",
    "$id": "4"
  },
  {
    "type": "System.Single",
    "value": {"$content": 5.0, "$type": "System.Single"},
    "defaultValues": {},
    "position": {"x": -500.0, "y": 400.0},
    "guid": "b2c3d4e5-f6a7-4b8c-9d0e-000000000005",
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
    "guid": "b2c3d4e5-f6a7-4b8c-9d0e-000000000006",
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
    "guid": "b2c3d4e5-f6a7-4b8c-9d0e-000000000007",
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
    "guid": "b2c3d4e5-f6a7-4b8c-9d0e-000000000008",
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
    "guid": "b2c3d4e5-f6a7-4b8c-9d0e-000000000009",
    "$version": "A",
    "$type": "Unity.VisualScripting.InvokeMember",
    "$id": "9"
  },
  {
    "sourceUnit": {"$ref": "1"},
    "sourceKey": "trigger",
    "destinationUnit": {"$ref": "9"},
    "destinationKey": "enter",
    "guid": "b2c3d4e5-f6a7-4b8c-9d0e-000000000010",
    "$type": "Unity.VisualScripting.ControlConnection"
  },
  {
    "sourceUnit": {"$ref": "3"},
    "sourceKey": "output",
    "destinationUnit": {"$ref": "6"},
    "destinationKey": "a",
    "guid": "b2c3d4e5-f6a7-4b8c-9d0e-000000000011",
    "$type": "Unity.VisualScripting.ValueConnection"
  },
  {
    "sourceUnit": {"$ref": "2"},
    "sourceKey": "value",
    "destinationUnit": {"$ref": "6"},
    "destinationKey": "b",
    "guid": "b2c3d4e5-f6a7-4b8c-9d0e-000000000012",
    "$type": "Unity.VisualScripting.ValueConnection"
  },
  {
    "sourceUnit": {"$ref": "4"},
    "sourceKey": "output",
    "destinationUnit": {"$ref": "7"},
    "destinationKey": "a",
    "guid": "b2c3d4e5-f6a7-4b8c-9d0e-000000000013",
    "$type": "Unity.VisualScripting.ValueConnection"
  },
  {
    "sourceUnit": {"$ref": "2"},
    "sourceKey": "value",
    "destinationUnit": {"$ref": "7"},
    "destinationKey": "b",
    "guid": "b2c3d4e5-f6a7-4b8c-9d0e-000000000014",
    "$type": "Unity.VisualScripting.ValueConnection"
  },
  {
    "sourceUnit": {"$ref": "5"},
    "sourceKey": "output",
    "destinationUnit": {"$ref": "8"},
    "destinationKey": "a",
    "guid": "b2c3d4e5-f6a7-4b8c-9d0e-000000000015",
    "$type": "Unity.VisualScripting.ValueConnection"
  },
  {
    "sourceUnit": {"$ref": "2"},
    "sourceKey": "value",
    "destinationUnit": {"$ref": "8"},
    "destinationKey": "b",
    "guid": "b2c3d4e5-f6a7-4b8c-9d0e-000000000016",
    "$type": "Unity.VisualScripting.ValueConnection"
  },
  {
    "sourceUnit": {"$ref": "6"},
    "sourceKey": "product",
    "destinationUnit": {"$ref": "9"},
    "destinationKey": "%xAngle",
    "guid": "b2c3d4e5-f6a7-4b8c-9d0e-000000000017",
    "$type": "Unity.VisualScripting.ValueConnection"
  },
  {
    "sourceUnit": {"$ref": "7"},
    "sourceKey": "product",
    "destinationUnit": {"$ref": "9"},
    "destinationKey": "%yAngle",
    "guid": "b2c3d4e5-f6a7-4b8c-9d0e-000000000018",
    "$type": "Unity.VisualScripting.ValueConnection"
  },
  {
    "sourceUnit": {"$ref": "8"},
    "sourceKey": "product",
    "destinationUnit": {"$ref": "9"},
    "destinationKey": "%zAngle",
    "guid": "b2c3d4e5-f6a7-4b8c-9d0e-000000000019",
    "$type": "Unity.VisualScripting.ValueConnection"
  }
]
```

**Key observations:**
- `Update` event: same shape as `Start` — `coroutine: false`, `defaultValues: {}`
- `GetMember` for static property (Time.deltaTime): `parameterTypes: null`, `defaultValues: {}`
- `ScalarMultiply`: ports `a`, `b` (input), `product` (output)
- `InvokeMember` for instance method: `"target": null` in defaultValues (auto-resolves to attached Transform)
- Parameter port keys: `%xAngle`, `%yAngle`, `%zAngle` (matching `parameterNames`)

---

## 3. OnTriggerEnter to Action

OnTriggerEnter → Debug.Log with the collider name.

### Elements

```json
[
  {
    "coroutine": false,
    "defaultValues": {"target": null},
    "position": {"x": 0.0, "y": 0.0},
    "guid": "c3d4e5f6-a7b8-4c9d-0e1f-000000000001",
    "$version": "A",
    "$type": "Unity.VisualScripting.OnTriggerEnter",
    "$id": "1"
  },
  {
    "member": {
      "name": "gameObject",
      "parameterTypes": null,
      "targetType": "UnityEngine.Collider",
      "targetTypeName": "UnityEngine.Collider",
      "$version": "A"
    },
    "defaultValues": {"target": null},
    "position": {"x": 0.0, "y": 200.0},
    "guid": "c3d4e5f6-a7b8-4c9d-0e1f-000000000002",
    "$version": "A",
    "$type": "Unity.VisualScripting.GetMember",
    "$id": "2"
  },
  {
    "member": {
      "name": "name",
      "parameterTypes": null,
      "targetType": "UnityEngine.GameObject",
      "targetTypeName": "UnityEngine.GameObject",
      "$version": "A"
    },
    "defaultValues": {"target": null},
    "position": {"x": 250.0, "y": 200.0},
    "guid": "c3d4e5f6-a7b8-4c9d-0e1f-000000000003",
    "$version": "A",
    "$type": "Unity.VisualScripting.GetMember",
    "$id": "3"
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
    "guid": "c3d4e5f6-a7b8-4c9d-0e1f-000000000004",
    "$version": "A",
    "$type": "Unity.VisualScripting.InvokeMember",
    "$id": "4"
  },
  {
    "sourceUnit": {"$ref": "1"},
    "sourceKey": "trigger",
    "destinationUnit": {"$ref": "4"},
    "destinationKey": "enter",
    "guid": "c3d4e5f6-a7b8-4c9d-0e1f-000000000005",
    "$type": "Unity.VisualScripting.ControlConnection"
  },
  {
    "sourceUnit": {"$ref": "1"},
    "sourceKey": "collider",
    "destinationUnit": {"$ref": "2"},
    "destinationKey": "target",
    "guid": "c3d4e5f6-a7b8-4c9d-0e1f-000000000006",
    "$type": "Unity.VisualScripting.ValueConnection"
  },
  {
    "sourceUnit": {"$ref": "2"},
    "sourceKey": "value",
    "destinationUnit": {"$ref": "3"},
    "destinationKey": "target",
    "guid": "c3d4e5f6-a7b8-4c9d-0e1f-000000000007",
    "$type": "Unity.VisualScripting.ValueConnection"
  },
  {
    "sourceUnit": {"$ref": "3"},
    "sourceKey": "value",
    "destinationUnit": {"$ref": "4"},
    "destinationKey": "%message",
    "guid": "c3d4e5f6-a7b8-4c9d-0e1f-000000000008",
    "$type": "Unity.VisualScripting.ValueConnection"
  }
]
```

**Key observations:**
- `OnTriggerEnter`: has `defaultValues: {"target": null}` (target filter port)
- Event ValueOutput port: `collider` (used as sourceKey)
- Chain: collider → GetMember(gameObject) → GetMember(name) → Debug.Log
- GetMember instance: `defaultValues: {"target": null}`

---

## 4. Get/Set Variable and Increment

Graph variable "counter" + increment pattern: GetVariable → ScalarSum (+1) → SetVariable.

### Graph Variables Declaration

When declaring graph variables, add them to the `collection.$content` array:

```json
"variables": {
  "Kind": "Flow",
  "collection": {
    "$content": [
      {"name": "counter", "value": {"$content": 0, "$type": "System.Int32"}, "$version": "A"}
    ],
    "$version": "A"
  },
  "$version": "A"
}
```

### Elements

```json
[
  {
    "coroutine": false,
    "defaultValues": {},
    "position": {"x": 0.0, "y": 0.0},
    "guid": "d4e5f6a7-b8c9-4d0e-1f2a-000000000001",
    "$version": "A",
    "$type": "Unity.VisualScripting.Start",
    "$id": "1"
  },
  {
    "kind": "Graph",
    "defaultValues": {
      "name": {"$content": "counter", "$type": "System.String"}
    },
    "position": {"x": 200.0, "y": 150.0},
    "guid": "d4e5f6a7-b8c9-4d0e-1f2a-000000000002",
    "$version": "A",
    "$type": "Unity.VisualScripting.GetVariable",
    "$id": "2"
  },
  {
    "inputCount": 2,
    "defaultValues": {
      "1": {"$content": 1.0, "$type": "System.Single"}
    },
    "position": {"x": 400.0, "y": 150.0},
    "guid": "d4e5f6a7-b8c9-4d0e-1f2a-000000000003",
    "$version": "A",
    "$type": "Unity.VisualScripting.ScalarSum",
    "$id": "3"
  },
  {
    "kind": "Graph",
    "defaultValues": {
      "name": {"$content": "counter", "$type": "System.String"}
    },
    "position": {"x": 250.0, "y": 0.0},
    "guid": "d4e5f6a7-b8c9-4d0e-1f2a-000000000004",
    "$version": "A",
    "$type": "Unity.VisualScripting.SetVariable",
    "$id": "4"
  },
  {
    "sourceUnit": {"$ref": "1"},
    "sourceKey": "trigger",
    "destinationUnit": {"$ref": "4"},
    "destinationKey": "assign",
    "guid": "d4e5f6a7-b8c9-4d0e-1f2a-000000000005",
    "$type": "Unity.VisualScripting.ControlConnection"
  },
  {
    "sourceUnit": {"$ref": "2"},
    "sourceKey": "value",
    "destinationUnit": {"$ref": "3"},
    "destinationKey": "0",
    "guid": "d4e5f6a7-b8c9-4d0e-1f2a-000000000006",
    "$type": "Unity.VisualScripting.ValueConnection"
  },
  {
    "sourceUnit": {"$ref": "3"},
    "sourceKey": "sum",
    "destinationUnit": {"$ref": "4"},
    "destinationKey": "input",
    "guid": "d4e5f6a7-b8c9-4d0e-1f2a-000000000007",
    "$type": "Unity.VisualScripting.ValueConnection"
  }
]
```

**Key observations:**
- `GetVariable`/`SetVariable`: `kind` field (string: `"Graph"`, `"Object"`, `"Scene"`, `"Application"`, `"Saved"`, `"Flow"`)
- Variable name in `defaultValues.name` as typed value: `{"$content": "counter", "$type": "System.String"}`
- `ScalarSum`: `inputCount: 2`, input port keys are `"0"`, `"1"` (NOT `multiInputs[0]`), output is `"sum"`
- `ScalarSum` defaultValues use index string keys: `{"1": {"$content": 1.0, "$type": "System.Single"}}`
- `SetVariable` control ports: `assign` (in), `assigned` (out); value ports: `input` (in), `output` (out)

---

## 5. If/Else Branch

Update → GetKeyDown(Space) → If → branch to two Debug.Log actions.

### Elements

```json
[
  {
    "coroutine": false,
    "defaultValues": {},
    "position": {"x": 0.0, "y": 0.0},
    "guid": "e5f6a7b8-c9d0-4e1f-2a3b-000000000001",
    "$version": "A",
    "$type": "Unity.VisualScripting.Update",
    "$id": "1"
  },
  {
    "chainable": false,
    "parameterNames": ["key"],
    "member": {
      "name": "GetKeyDown",
      "parameterTypes": ["UnityEngine.KeyCode"],
      "targetType": "UnityEngine.Input",
      "targetTypeName": "UnityEngine.Input",
      "$version": "A"
    },
    "defaultValues": {
      "%key": {"$content": 32, "$type": "UnityEngine.KeyCode"}
    },
    "position": {"x": 250.0, "y": 0.0},
    "guid": "e5f6a7b8-c9d0-4e1f-2a3b-000000000002",
    "$version": "A",
    "$type": "Unity.VisualScripting.InvokeMember",
    "$id": "2"
  },
  {
    "defaultValues": {
      "condition": {"$content": false, "$type": "System.Boolean"}
    },
    "position": {"x": 500.0, "y": 0.0},
    "guid": "e5f6a7b8-c9d0-4e1f-2a3b-000000000003",
    "$version": "A",
    "$type": "Unity.VisualScripting.If",
    "$id": "3"
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
    "position": {"x": 750.0, "y": -50.0},
    "guid": "e5f6a7b8-c9d0-4e1f-2a3b-000000000004",
    "$version": "A",
    "$type": "Unity.VisualScripting.InvokeMember",
    "$id": "4"
  },
  {
    "type": "System.String",
    "value": {"$content": "Space pressed!", "$type": "System.String"},
    "defaultValues": {},
    "position": {"x": 550.0, "y": -150.0},
    "guid": "e5f6a7b8-c9d0-4e1f-2a3b-000000000005",
    "$version": "A",
    "$type": "Unity.VisualScripting.Literal",
    "$id": "5"
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
    "position": {"x": 750.0, "y": 150.0},
    "guid": "e5f6a7b8-c9d0-4e1f-2a3b-000000000006",
    "$version": "A",
    "$type": "Unity.VisualScripting.InvokeMember",
    "$id": "6"
  },
  {
    "type": "System.String",
    "value": {"$content": "Not pressed", "$type": "System.String"},
    "defaultValues": {},
    "position": {"x": 550.0, "y": 250.0},
    "guid": "e5f6a7b8-c9d0-4e1f-2a3b-000000000007",
    "$version": "A",
    "$type": "Unity.VisualScripting.Literal",
    "$id": "7"
  },
  {
    "sourceUnit": {"$ref": "1"},
    "sourceKey": "trigger",
    "destinationUnit": {"$ref": "2"},
    "destinationKey": "enter",
    "guid": "e5f6a7b8-c9d0-4e1f-2a3b-000000000008",
    "$type": "Unity.VisualScripting.ControlConnection"
  },
  {
    "sourceUnit": {"$ref": "2"},
    "sourceKey": "exit",
    "destinationUnit": {"$ref": "3"},
    "destinationKey": "enter",
    "guid": "e5f6a7b8-c9d0-4e1f-2a3b-000000000009",
    "$type": "Unity.VisualScripting.ControlConnection"
  },
  {
    "sourceUnit": {"$ref": "2"},
    "sourceKey": "result",
    "destinationUnit": {"$ref": "3"},
    "destinationKey": "condition",
    "guid": "e5f6a7b8-c9d0-4e1f-2a3b-000000000010",
    "$type": "Unity.VisualScripting.ValueConnection"
  },
  {
    "sourceUnit": {"$ref": "3"},
    "sourceKey": "ifTrue",
    "destinationUnit": {"$ref": "4"},
    "destinationKey": "enter",
    "guid": "e5f6a7b8-c9d0-4e1f-2a3b-000000000011",
    "$type": "Unity.VisualScripting.ControlConnection"
  },
  {
    "sourceUnit": {"$ref": "3"},
    "sourceKey": "ifFalse",
    "destinationUnit": {"$ref": "6"},
    "destinationKey": "enter",
    "guid": "e5f6a7b8-c9d0-4e1f-2a3b-000000000012",
    "$type": "Unity.VisualScripting.ControlConnection"
  },
  {
    "sourceUnit": {"$ref": "5"},
    "sourceKey": "output",
    "destinationUnit": {"$ref": "4"},
    "destinationKey": "%message",
    "guid": "e5f6a7b8-c9d0-4e1f-2a3b-000000000013",
    "$type": "Unity.VisualScripting.ValueConnection"
  },
  {
    "sourceUnit": {"$ref": "7"},
    "sourceKey": "output",
    "destinationUnit": {"$ref": "6"},
    "destinationKey": "%message",
    "guid": "e5f6a7b8-c9d0-4e1f-2a3b-000000000014",
    "$type": "Unity.VisualScripting.ValueConnection"
  }
]
```

**Key observations:**
- `If` unit: `defaultValues: {"condition": {...}}`, ports: `enter`, `ifTrue`, `ifFalse`, `condition`
- Enum values (KeyCode.Space = 32): serialized as integer with enum type: `{"$content": 32, "$type": "UnityEngine.KeyCode"}`
- InvokeMember result port: `"result"` (ValueOutput)

---

## 6. Sequence (fan-out)

Start → Sequence with 3 outputs → three Debug.Log actions.

### Elements

```json
[
  {
    "coroutine": false,
    "defaultValues": {},
    "position": {"x": 0.0, "y": 0.0},
    "guid": "f6a7b8c9-d0e1-4f2a-3b4c-000000000001",
    "$version": "A",
    "$type": "Unity.VisualScripting.Start",
    "$id": "1"
  },
  {
    "outputCount": 3,
    "defaultValues": {},
    "position": {"x": 250.0, "y": 0.0},
    "guid": "f6a7b8c9-d0e1-4f2a-3b4c-000000000002",
    "$version": "A",
    "$type": "Unity.VisualScripting.Sequence",
    "$id": "2"
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
    "position": {"x": 500.0, "y": -150.0},
    "guid": "f6a7b8c9-d0e1-4f2a-3b4c-000000000003",
    "$version": "A",
    "$type": "Unity.VisualScripting.InvokeMember",
    "$id": "3"
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
    "position": {"x": 500.0, "y": 0.0},
    "guid": "f6a7b8c9-d0e1-4f2a-3b4c-000000000004",
    "$version": "A",
    "$type": "Unity.VisualScripting.InvokeMember",
    "$id": "4"
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
    "position": {"x": 500.0, "y": 150.0},
    "guid": "f6a7b8c9-d0e1-4f2a-3b4c-000000000005",
    "$version": "A",
    "$type": "Unity.VisualScripting.InvokeMember",
    "$id": "5"
  },
  {
    "sourceUnit": {"$ref": "1"},
    "sourceKey": "trigger",
    "destinationUnit": {"$ref": "2"},
    "destinationKey": "enter",
    "guid": "f6a7b8c9-d0e1-4f2a-3b4c-000000000006",
    "$type": "Unity.VisualScripting.ControlConnection"
  },
  {
    "sourceUnit": {"$ref": "2"},
    "sourceKey": "0",
    "destinationUnit": {"$ref": "3"},
    "destinationKey": "enter",
    "guid": "f6a7b8c9-d0e1-4f2a-3b4c-000000000007",
    "$type": "Unity.VisualScripting.ControlConnection"
  },
  {
    "sourceUnit": {"$ref": "2"},
    "sourceKey": "1",
    "destinationUnit": {"$ref": "4"},
    "destinationKey": "enter",
    "guid": "f6a7b8c9-d0e1-4f2a-3b4c-000000000008",
    "$type": "Unity.VisualScripting.ControlConnection"
  },
  {
    "sourceUnit": {"$ref": "2"},
    "sourceKey": "2",
    "destinationUnit": {"$ref": "5"},
    "destinationKey": "enter",
    "guid": "f6a7b8c9-d0e1-4f2a-3b4c-000000000009",
    "$type": "Unity.VisualScripting.ControlConnection"
  }
]
```

**Key observations:**
- `Sequence`: `outputCount` property, `defaultValues: {}`
- Sequence output port keys: `"0"`, `"1"`, `"2"` (index strings, same as multiOutputs)
- Input port: `"enter"`

---

## 7. InvokeMember Patterns

### Static Method (Debug.Log)

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
  "position": {"x": 0.0, "y": 0.0},
  "guid": "UUID_HERE",
  "$version": "A",
  "$type": "Unity.VisualScripting.InvokeMember",
  "$id": "N"
}
```

- No `target` in defaultValues (static method)
- Ports: `enter`, `exit` (control), `%message` (value in), `result` (value out — but Log returns void, no `result` port)

### Instance Method (Transform.Rotate)

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
  "position": {"x": 0.0, "y": 0.0},
  "guid": "UUID_HERE",
  "$version": "A",
  "$type": "Unity.VisualScripting.InvokeMember",
  "$id": "N"
}
```

- `"target": null` in defaultValues (auto-resolves to attached component)
- Parameter defaults prefixed with `%`

### Void Instance Method (GameObject.SetActive)

```json
{
  "chainable": false,
  "parameterNames": ["value"],
  "member": {
    "name": "SetActive",
    "parameterTypes": ["System.Boolean"],
    "targetType": "UnityEngine.GameObject",
    "targetTypeName": "UnityEngine.GameObject",
    "$version": "A"
  },
  "defaultValues": {
    "target": null,
    "%value": {"$content": false, "$type": "System.Boolean"}
  },
  "position": {"x": 0.0, "y": 0.0},
  "guid": "UUID_HERE",
  "$version": "A",
  "$type": "Unity.VisualScripting.InvokeMember",
  "$id": "N"
}
```

- Void methods: no `result` port available. Do NOT wire `result` from void InvokeMember.
- `targetOutput` is also null for void instance methods.

### No-Parameter Method (AudioSource.Play)

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
  "guid": "UUID_HERE",
  "$version": "A",
  "$type": "Unity.VisualScripting.InvokeMember",
  "$id": "N"
}
```

---

## 8. GetMember / SetMember

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
  "position": {"x": 0.0, "y": 0.0},
  "guid": "UUID_HERE",
  "$version": "A",
  "$type": "Unity.VisualScripting.GetMember",
  "$id": "N"
}
```

- Static: no `target` in defaultValues
- Output port: `"value"`

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
  "guid": "UUID_HERE",
  "$version": "A",
  "$type": "Unity.VisualScripting.GetMember",
  "$id": "N"
}
```

- Instance: `"target": null` in defaultValues (auto-resolves)

### SetMember — Instance Property (Transform.position)

```json
{
  "member": {
    "name": "position",
    "parameterTypes": null,
    "targetType": "UnityEngine.Transform",
    "targetTypeName": "UnityEngine.Transform",
    "$version": "A"
  },
  "defaultValues": {
    "target": null,
    "input": {"x": 0.0, "y": 0.0, "z": 0.0, "$type": "UnityEngine.Vector3"}
  },
  "position": {"x": 0.0, "y": 0.0},
  "guid": "UUID_HERE",
  "$version": "A",
  "$type": "Unity.VisualScripting.SetMember",
  "$id": "N"
}
```

- Control ports: `assign` (in), `assigned` (out)
- Value ports: `target`, `input` (in), `output` (out)

---

## 9. Literal Value Types

### String

```json
{
  "type": "System.String",
  "value": {"$content": "Hello World", "$type": "System.String"},
  "defaultValues": {},
  "position": {"x": 0.0, "y": 0.0},
  "guid": "UUID_HERE",
  "$version": "A",
  "$type": "Unity.VisualScripting.Literal",
  "$id": "N"
}
```

### Int

```json
{
  "type": "System.Int32",
  "value": {"$content": 42, "$type": "System.Int32"},
  "defaultValues": {},
  "position": {"x": 0.0, "y": 0.0},
  "guid": "UUID_HERE",
  "$version": "A",
  "$type": "Unity.VisualScripting.Literal",
  "$id": "N"
}
```

### Float

```json
{
  "type": "System.Single",
  "value": {"$content": 3.14, "$type": "System.Single"},
  "defaultValues": {},
  "position": {"x": 0.0, "y": 0.0},
  "guid": "UUID_HERE",
  "$version": "A",
  "$type": "Unity.VisualScripting.Literal",
  "$id": "N"
}
```

### Bool

```json
{
  "type": "System.Boolean",
  "value": {"$content": true, "$type": "System.Boolean"},
  "defaultValues": {},
  "position": {"x": 0.0, "y": 0.0},
  "guid": "UUID_HERE",
  "$version": "A",
  "$type": "Unity.VisualScripting.Literal",
  "$id": "N"
}
```

### Vector3

```json
{
  "type": "UnityEngine.Vector3",
  "value": {"x": 1.0, "y": 2.0, "z": 3.0, "$type": "UnityEngine.Vector3"},
  "defaultValues": {},
  "position": {"x": 0.0, "y": 0.0},
  "guid": "UUID_HERE",
  "$version": "A",
  "$type": "Unity.VisualScripting.Literal",
  "$id": "N"
}
```

### Color

```json
{
  "type": "UnityEngine.Color",
  "value": {"r": 1.0, "g": 0.0, "b": 0.0, "a": 1.0, "$type": "UnityEngine.Color"},
  "defaultValues": {},
  "position": {"x": 0.0, "y": 0.0},
  "guid": "UUID_HERE",
  "$version": "A",
  "$type": "Unity.VisualScripting.Literal",
  "$id": "N"
}
```

### Enum (KeyCode)

```json
{
  "type": "UnityEngine.KeyCode",
  "value": {"$content": 32, "$type": "UnityEngine.KeyCode"},
  "defaultValues": {},
  "position": {"x": 0.0, "y": 0.0},
  "guid": "UUID_HERE",
  "$version": "A",
  "$type": "Unity.VisualScripting.Literal",
  "$id": "N"
}
```

Enums are serialized as their integer value (e.g., `KeyCode.Space` = 32).

---

## JSON Serialization Quick Reference

| Concept | Format |
|---------|--------|
| Unit $id | Sequential string integers: `"1"`, `"2"`, ... |
| Unit reference | `{"$ref": "1"}` |
| UUID | `uuidgen \| tr '[:upper:]' '[:lower:]'` for each element |
| $version | Always `"A"` |
| Position | `{"x": 0.0, "y": 0.0}` (pixels, ~250px horizontal spacing) |
| Typed value | `{"$content": VALUE, "$type": "Full.Type.Name"}` |
| Struct value | Direct fields + `$type`: `{"x": 1.0, "y": 2.0, "z": 3.0, "$type": "UnityEngine.Vector3"}` |
| Null | `null` |
| Member | `{"name": "...", "parameterTypes": [...], "targetType": "...", "targetTypeName": "...", "$version": "A"}` |
| Param port key | `%paramName` (e.g., `%message`, `%xAngle`) |
| ScalarSum input keys | `"0"`, `"1"` (index strings) |
| Sequence output keys | `"0"`, `"1"`, `"2"` (index strings) |
