using System.Text.Json;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;

// Parse command-line arguments
string? csFilePath = null;
string? managedDir = null;
string? vsAssembliesDir = null;

for (int i = 0; i < args.Length; i++)
{
    switch (args[i])
    {
        case "--managed" when i + 1 < args.Length:
            managedDir = args[++i];
            break;
        case "--vs-assemblies" when i + 1 < args.Length:
            vsAssembliesDir = args[++i];
            break;
        default:
            if (csFilePath == null && !args[i].StartsWith("--"))
                csFilePath = args[i];
            break;
    }
}

if (csFilePath == null || managedDir == null)
{
    Console.Error.WriteLine("Usage: RoslynValidator <file.cs> --managed <unity-managed-dir> [--vs-assemblies <dir>]");
    return 2;
}

if (!File.Exists(csFilePath))
{
    Console.Error.WriteLine($"File not found: {csFilePath}");
    return 2;
}

if (!Directory.Exists(managedDir))
{
    Console.Error.WriteLine($"Unity managed directory not found: {managedDir}");
    return 2;
}

// Read and parse the C# source with UNITY_EDITOR defined
var sourceText = File.ReadAllText(csFilePath);
var parseOptions = CSharpParseOptions.Default
    .WithLanguageVersion(LanguageVersion.CSharp12)
    .WithPreprocessorSymbols("UNITY_EDITOR");

var syntaxTree = CSharpSyntaxTree.ParseText(sourceText, parseOptions, csFilePath);

// Collect metadata references from Unity DLLs
var references = new List<MetadataReference>();

// .NET runtime references (required for basic type resolution)
var trustedAssemblies = ((string?)AppContext.GetData("TRUSTED_PLATFORM_ASSEMBLIES") ?? "")
    .Split(Path.PathSeparator, StringSplitOptions.RemoveEmptyEntries);
foreach (var asm in trustedAssemblies)
{
    var name = Path.GetFileNameWithoutExtension(asm);
    // Include core runtime assemblies
    if (name.StartsWith("System") || name == "mscorlib" || name == "netstandard")
    {
        references.Add(MetadataReference.CreateFromFile(asm));
    }
}

// Unity DLL loading strategy:
// In Unity 6, managed/UnityEngine/ contains ALL module DLLs for both
// UnityEngine (UnityEngine.CoreModule.dll, etc.) and UnityEditor
// (UnityEditor.CoreModule.dll, etc.). Loading these module DLLs makes
// the facade DLLs (managed/UnityEngine.dll, managed/UnityEditor.dll)
// redundant and would cause CS0433 "type exists in both assemblies".
var unityModulesDir = Path.Combine(managedDir, "UnityEngine");
if (Directory.Exists(unityModulesDir) && Directory.GetFiles(unityModulesDir, "*.dll").Length > 0)
{
    // Load all module DLLs (covers both UnityEngine and UnityEditor types)
    foreach (var dll in Directory.GetFiles(unityModulesDir, "*.dll"))
    {
        references.Add(MetadataReference.CreateFromFile(dll));
    }
    // Do NOT load facade DLLs from managed root to avoid duplicates
}
else
{
    // Fallback: load facade DLLs from managed root
    var unityEngineDll = Path.Combine(managedDir, "UnityEngine.dll");
    if (File.Exists(unityEngineDll))
        references.Add(MetadataReference.CreateFromFile(unityEngineDll));
    var unityEditorDll = Path.Combine(managedDir, "UnityEditor.dll");
    if (File.Exists(unityEditorDll))
        references.Add(MetadataReference.CreateFromFile(unityEditorDll));
}

// Visual Scripting DLLs (optional - from project's Library/ScriptAssemblies)
if (vsAssembliesDir != null && Directory.Exists(vsAssembliesDir))
{
    foreach (var dll in Directory.GetFiles(vsAssembliesDir, "Unity.VisualScripting*.dll"))
    {
        references.Add(MetadataReference.CreateFromFile(dll));
    }
}

// Create compilation
var compilationOptions = new CSharpCompilationOptions(OutputKind.DynamicallyLinkedLibrary)
    .WithNullableContextOptions(NullableContextOptions.Disable);

var compilation = CSharpCompilation.Create(
    "ValidationAssembly",
    syntaxTrees: [syntaxTree],
    references: references,
    options: compilationOptions
);

// Get diagnostics and filter
var diagnostics = compilation.GetDiagnostics()
    .Where(d => d.Severity >= DiagnosticSeverity.Warning)
    .Where(d => !IsIgnoredDiagnostic(d))
    .Select(d =>
    {
        var lineSpan = d.Location.GetMappedLineSpan();
        return new
        {
            severity = d.Severity.ToString(),
            code = d.Id,
            message = d.GetMessage(),
            line = lineSpan.StartLinePosition.Line + 1,
            column = lineSpan.StartLinePosition.Character + 1
        };
    })
    .ToList();

// Output as JSON
var json = JsonSerializer.Serialize(diagnostics, new JsonSerializerOptions { WriteIndented = false });
Console.WriteLine(json);

return diagnostics.Any(d => d.severity == "Error") ? 1 : 0;

// Filter out diagnostics that are expected/irrelevant for editor script snippets
static bool IsIgnoredDiagnostic(Diagnostic d)
{
    return d.Id switch
    {
        // "Assuming assembly reference" warnings from Unity DLL version mismatches
        "CS1701" or "CS1702" => true,
        // "Missing XML comment" warnings
        "CS1591" => true,
        // "The extern alias was not used" - not relevant for validation
        "CS0430" => true,
        _ => false
    };
}
