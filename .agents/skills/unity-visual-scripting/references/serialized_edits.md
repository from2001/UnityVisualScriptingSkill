# Editing serialized Visual Scripting graphs

Use direct editing for small, understood changes in an existing asset. Prefer Unity
editor APIs for new graphs, topology changes involving nested/shared objects, or object
reference changes. A template is not a substitute for the target asset's schema.

## Preserve the container

Keep the asset's Unity YAML header, `m_Script` GUID, `_objectReferences` list and order,
unknown fields, file IDs, and `.meta` file. `_objectReferences` can hold live asset or
scene references; it is not generally empty. Do not replace the asset with a template
that hard-codes a ScriptGraphAsset GUID, particularly for a StateGraphAsset.

For the observed single-quoted `_data._json` format, decode doubled YAML single quotes
(`''` becomes `'`), then parse the JSON. Change only the requested values. Serialize the
JSON on one line and double its single quotes when putting it back. Detect the actual
YAML scalar style; do not apply a single-line regex to folded, wrapped, or differently
quoted data. Use Unity serialization when the format cannot be safely round-tripped.

## Preserve the object graph

- Keep existing `$id`, `$ref`, element `guid`, `$version`, and nested objects intact.
  New IDs must be unused throughout the serialized graph, not just in the top array.
- Preserve reference indexes into `_objectReferences` and all unaffected bindings.
- Check connection endpoint IDs and actual port keys; `%parameterName` is distinct
  from a C# accessor. Changing a member's overload may change its ports.
- Do not impose the example's element ordering or renumber existing IDs. Review the
  diff to ensure unrelated nodes, variables, states, and transitions stayed intact.

The [API reference](api_reference.md#9-yamljson-format-reference-for-modification)
contains sample field shapes, not universal serialization rules. Reimport and reopen
the edited asset in Unity; exercise the affected behavior and inspect missing units,
connections, and object references. Without an editor, report serialization/runtime
validation as pending even when JSON parses correctly.
