# Validation scope

Run tools using the absolute skill directory when it is installed outside the project.

```sh
python3 <skill-dir>/tools/validate.py <generator.cs> --unity-project <project>
python3 <skill-dir>/tools/validate.py <generator.cs> --static-only
```

The first command compiles a temporary copy of the source using .NET SDK 8+, the exact
Unity version in `ProjectSettings/ProjectVersion.txt`, and the project's existing
`Library/ScriptAssemblies`. Missing imports/assemblies are setup failures; open the
project in Unity to produce them. No project or installed skill files are modified.
The compiler template is shipped with the skill, including on a fresh checkout.

Common Unity Hub installations on macOS, Windows, and Linux are searched for that exact
version. For custom locations, use `--unity-managed-dir` pointing to
`Unity.app/Contents/Managed` (macOS) or `Editor/Data/Managed` (Windows/Linux).
`--unity-version` is useful without a project; if supplied with a project it must match.
The explicit Managed path is an override: the caller must ensure it belongs to the
reported editor. The tool does not silently choose another installed Unity version.

| Exit | Meaning |
| --- | --- |
| 0 | Requested checks completed without detected errors. |
| 1 | A compiler/build or static-check error was detected. |
| 2 | Missing setup, timeout, or an incomplete/crashed check. |

`--static-only` can return 0 for clean heuristic checks while compilation remains
unperformed. Its output states that scope. Regex checks can miss errors or flag valid
custom helpers; inspect their findings rather than changing sound code to satisfy a
spelling pattern. An unexpected subprocess exit never becomes a successful result.

The compilation template uses .NET Standard 2.1 and C# 9, matching the language baseline
of the sample Unity 6.0 projects ([Unity compiler documentation](https://docs.unity3d.com/6000.0/Documentation/Manual/csharp-compiler.html)).
It does not reproduce project asmdefs, all conditional symbols, platform dependencies,
or Unity's complete compilation pipeline. For those cases compile in the target editor.
Reflection member names, generated ports, serialized data, actual execution, and visuals
must be verified in Unity. Do not treat an unavailable check as failure of the artifact
itself or as a reason to withhold otherwise useful work; state the missing evidence.
