using System;
using System.Linq;
using Newtonsoft.Json;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using Unity.VisualScripting;

// Execute only in a disposable project; CreateFixtures replaces its active scene.
public static class VisualScriptingSkillSmoke
{
    const string Root = "__OUTPUT_ROOT__";

    public static string CreateFixtures()
    {
        EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
        var cube = GameObject.CreatePrimitive(PrimitiveType.Cube);
        cube.name = "RotatingCube";
        cube.transform.position = new Vector3(-11f, -8f, 0f);
        CreateRotateGraph.Create();
        var rotate = AssetDatabase.LoadAssetAtPath<ScriptGraphAsset>(Root + "/RotateCube.asset");
        var guids = rotate.graph.units.Select(u => u.guid).ToArray();
        var assetGuid = AssetDatabase.AssetPathToGUID(Root + "/RotateCube.asset");
        rotate.graph.variables.Set("UserMarker", 42);
        EditorUtility.SetDirty(rotate);
        AssetDatabase.SaveAssets();
        CreateRotateGraph.Create();
        var reused = AssetDatabase.LoadAssetAtPath<ScriptGraphAsset>(Root + "/RotateCube.asset");
        Require(reused.graph.variables.IsDefined("UserMarker"), "Rerun erased user graph variables.");
        Require(guids.SequenceEqual(reused.graph.units.Select(u => u.guid)), "Rerun replaced unit GUIDs.");
        Require(cube.GetComponents<ScriptMachine>().Length == 1, "Rerun duplicated the machine.");
        Require(cube.scene.isDirty, "Assignment must mark the scene dirty.");

        var counterAsset = ScriptableObject.CreateInstance<ScriptGraphAsset>();
        var graph = counterAsset.graph;
        graph.variables.Set("counter", 0f);
        var trigger = new CustomEvent();
        graph.units.Add(trigger);
        trigger.defaultValues["name"] = "Increment";
        var get = new GetVariable { kind = VariableKind.Graph };
        graph.units.Add(get);
        get.defaultValues["name"] = "counter";
        var sum = new ScalarSum();
        graph.units.Add(sum);
        var one = new Literal(typeof(float), 1f);
        graph.units.Add(one);
        var set = new SetVariable { kind = VariableKind.Graph };
        graph.units.Add(set);
        set.defaultValues["name"] = "counter";
        graph.valueConnections.Add(new ValueConnection(get.value, sum.multiInputs[0]));
        graph.valueConnections.Add(new ValueConnection(one.output, sum.multiInputs[1]));
        graph.valueConnections.Add(new ValueConnection(sum.sum, set.input));
        graph.controlConnections.Add(new ControlConnection(trigger.trigger, set.assign));
        AssetDatabase.CreateAsset(counterAsset, Root + "/Counter.asset");
        var counter = new GameObject("CounterFixture").AddComponent<ScriptMachine>();
        counter.nest.source = GraphSource.Macro;
        counter.nest.macro = counterAsset;

        var stateAsset = ScriptableObject.CreateInstance<StateGraphAsset>();
        stateAsset.graph = new StateGraph();
        var idle = FlowState.WithEnterUpdateExit();
        idle.isStart = true;
        idle.nest.graph.title = "Idle";
        var walking = FlowState.WithEnterUpdateExit();
        walking.nest.graph.title = "Walking";
        stateAsset.graph.states.Add(idle);
        stateAsset.graph.states.Add(walking);
        AddTransition(stateAsset.graph, idle, walking, "Walk");
        AddTransition(stateAsset.graph, walking, idle, "Stop");
        AssetDatabase.CreateAsset(stateAsset, Root + "/States.asset");
        var machine = new GameObject("StateFixture").AddComponent<StateMachine>();
        machine.nest.source = GraphSource.Macro;
        machine.nest.macro = stateAsset;
        AssetDatabase.SaveAssets();
        EditorSceneManager.SaveScene(cube.scene, Root + "/Validation.unity");
        EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
        Resources.UnloadAsset(reused);
        EditorSceneManager.OpenScene(Root + "/Validation.unity");
        var loaded = GameObject.Find("RotatingCube").GetComponent<ScriptMachine>().nest.macro;
        Require(loaded != null && loaded.graph.units.Count == 9 && loaded.graph.invalidConnections.Count == 0,
            "Reopened rotation graph lost its units or ports.");
        Require(AssetDatabase.AssetPathToGUID(AssetDatabase.GetAssetPath(loaded)) == assetGuid, "Asset GUID changed.");
        Require(guids.SequenceEqual(loaded.graph.units.Select(u => u.guid)), "Serialized unit GUIDs changed.");
        Require(GameObject.Find("StateFixture").GetComponent<StateMachine>().nest.macro != null, "State assignment was not saved.");
        return Write("vs-editmode", new { passed = true, rotationUnits = loaded.graph.units.Count,
            valueConnections = loaded.graph.valueConnections.Count, marker = loaded.graph.variables.Get("UserMarker"),
            assetGuid, rerunPreserved = true, sceneReopened = true });
    }

    static void AddTransition(StateGraph graph, FlowState from, FlowState to, string eventName)
    {
        var transition = FlowStateTransition.WithDefaultTrigger(from, to);
        graph.transitions.Add(transition);
        var trigger = new CustomEvent();
        transition.nest.graph.units.Add(trigger);
        trigger.defaultValues["name"] = eventName;
        var branch = transition.nest.graph.units.OfType<TriggerStateTransition>().Single();
        transition.nest.graph.controlConnections.Add(new ControlConnection(trigger.trigger, branch.trigger));
    }

    public static string CheckPlayMode()
    {
        Require(Application.isPlaying && Time.time > 0.1f, "Wait for Play Mode frames before checking rotation.");
        var cube = GameObject.Find("RotatingCube");
        float angle = Quaternion.Angle(Quaternion.identity, cube.transform.rotation);
        Require(angle > 0.05f, "Update graph did not rotate its implicit self target.");
        var counter = GameObject.Find("CounterFixture").GetComponent<ScriptMachine>();
        for (int i = 0; i < 3; i++) CustomEvent.Trigger(counter.gameObject, "Increment");
        float count = Convert.ToSingle(Variables.Graph(GraphReference.New(counter, true)).Get("counter"));
        Require(count == 3f, "ScalarSum/multiInputs counter did not execute three times.");
        var machine = GameObject.Find("StateFixture").GetComponent<StateMachine>();
        var states = machine.nest.graph.states.OfType<FlowState>().ToArray();
        var idle = states.Single(s => s.nest.graph.title == "Idle");
        var walking = states.Single(s => s.nest.graph.title == "Walking");
        var reference = GraphReference.New(machine, true);
        Require(reference.GetElementData<State.Data>(idle).isActive, "Idle did not start.");
        CustomEvent.Trigger(machine.gameObject, "Walk");
        Require(!reference.GetElementData<State.Data>(idle).isActive && reference.GetElementData<State.Data>(walking).isActive,
            "Idle to Walking transition failed.");
        CustomEvent.Trigger(machine.gameObject, "Stop");
        Require(reference.GetElementData<State.Data>(idle).isActive && !reference.GetElementData<State.Data>(walking).isActive,
            "Walking to Idle transition failed.");
        return Write("vs-playmode", new { passed = true, angle, elapsed = Time.time, counter = count,
            transitions = new[] { "Idle", "Walking", "Idle" } });
    }

    static void Require(bool condition, string message)
    {
        if (!condition) throw new InvalidOperationException(message);
    }

    static string Write(string name, object result)
    {
        System.IO.Directory.CreateDirectory("ValidationResults");
        var json = JsonConvert.SerializeObject(result, Formatting.Indented);
        System.IO.File.WriteAllText("ValidationResults/" + name + ".json", json);
        return json;
    }
}
