#!/usr/bin/env python3
"""
check_port_keys.py - Static analysis for Unity Visual Scripting C# port accessor errors.

Catches VS-specific errors that Roslyn cannot detect because they involve runtime semantics:
  VS-PORT-001: equal.equal / notEqual.notEqual (wrong accessor - should be .comparison)
  VS-PORT-002: .result port wiring on void method InvokeMember units
  VS-PORT-003: ScalarSum/GenericSum using .a/.b instead of .multiInputs[n]

Usage:
    python3 check_port_keys.py <path_to_cs_file>
"""

import re
import sys
from pathlib import Path

# Known void methods by type (subset of most commonly used)
KNOWN_VOID_METHODS = {
    "Transform": {"Rotate", "Translate", "LookAt", "SetParent", "SetPositionAndRotation",
                   "DetachChildren", "SetAsFirstSibling", "SetAsLastSibling"},
    "GameObject": {"SetActive", "BroadcastMessage", "SendMessage", "SendMessageUpwards"},
    "Rigidbody": {"AddForce", "AddTorque", "MovePosition", "MoveRotation",
                  "AddExplosionForce", "AddRelativeForce", "AddRelativeTorque",
                  "Sleep", "WakeUp", "ResetCenterOfMass", "ResetInertiaTensor"},
    "Rigidbody2D": {"AddForce", "AddTorque", "MovePosition", "MoveRotation"},
    "AudioSource": {"Play", "Stop", "Pause", "UnPause", "PlayOneShot", "PlayDelayed"},
    "Animator": {"SetTrigger", "ResetTrigger", "SetBool", "SetFloat", "SetInteger",
                 "Play", "CrossFade", "CrossFadeInFixedTime", "Rebind"},
    "Debug": {"Log", "LogWarning", "LogError", "LogException", "DrawLine", "DrawRay",
              "Assert", "Break"},
    "Object": {"Destroy", "DestroyImmediate", "DontDestroyOnLoad"},
    "MonoBehaviour": {"StartCoroutine", "StopCoroutine", "StopAllCoroutines",
                      "CancelInvoke", "Invoke", "InvokeRepeating"},
    "ParticleSystem": {"Play", "Stop", "Pause", "Clear", "Emit", "Simulate"},
    "Collider": {"ClosestPoint", "ClosestPointOnBounds"},
    "NavMeshAgent": {"SetDestination", "Move", "Stop", "Resume", "ResetPath", "Warp"},
    "Camera": {"Render", "ResetProjectionMatrix", "ResetWorldToCameraMatrix"},
}

# Multi-input unit types that use multiInputs[n], NOT a/b
MULTI_INPUT_UNITS = {"ScalarSum", "GenericSum", "ScalarSubtract", "GenericSubtract"}


def check_file(path):
    """Run all VS-specific checks on a C# file. Returns list of issue dicts."""
    issues = []
    source = Path(path).read_text(encoding="utf-8")

    issues.extend(_check_comparison_accessors(source))
    issues.extend(_check_void_result(source))
    issues.extend(_check_multi_input_accessors(source))

    return issues


def _check_comparison_accessors(source):
    """VS-PORT-001: Detect equal.equal / notEqual.notEqual wrong accessor usage."""
    issues = []

    # Find variables declared as Equal or NotEqual
    type_pattern = re.compile(
        r'(?:var|Equal|NotEqual)\s+(\w+)\s*=\s*new\s+(Equal|NotEqual)\s*\(',
        re.MULTILINE
    )
    comparison_vars = {}
    for m in type_pattern.finditer(source):
        comparison_vars[m.group(1)] = m.group(2)

    # Check for .equal or .notEqual accessor usage on those variables
    accessor_pattern = re.compile(r'\b(\w+)\.(equal|notEqual)\b')
    for m in accessor_pattern.finditer(source):
        var_name = m.group(1)
        accessor = m.group(2)
        if var_name in comparison_vars:
            line_no = source[:m.start()].count('\n') + 1
            issues.append({
                "line": line_no,
                "severity": "Error",
                "code": "VS-PORT-001",
                "message": (
                    f"'{var_name}.{accessor}' is wrong. "
                    f"BinaryComparisonUnit C# accessor is '.comparison'. "
                    f"Use '{var_name}.comparison' instead."
                )
            })

    return issues


def _check_void_result(source):
    """VS-PORT-002: Detect .result usage on void method InvokeMember units."""
    issues = []

    # Find InvokeMember variables with their Member types
    invoke_pattern = re.compile(
        r'(?:var|InvokeMember)\s+(\w+)\s*=\s*new\s+InvokeMember\s*\(\s*'
        r'new\s+Member\s*\(\s*typeof\s*\(\s*(\w+)\s*\)\s*,\s*'
        r'(?:nameof\s*\(\s*\w+\.(\w+)\s*\)|"(\w+)")',
        re.MULTILINE
    )
    invoke_vars = {}
    for m in invoke_pattern.finditer(source):
        var_name = m.group(1)
        type_name = m.group(2)
        method_name = m.group(3) or m.group(4)
        void_methods = KNOWN_VOID_METHODS.get(type_name, set())
        invoke_vars[var_name] = {
            "type": type_name,
            "method": method_name,
            "is_void": method_name in void_methods
        }

    # Find .result usage on those variables
    result_pattern = re.compile(r'\b(\w+)\.result\b')
    for m in result_pattern.finditer(source):
        var_name = m.group(1)
        if var_name in invoke_vars and invoke_vars[var_name]["is_void"]:
            info = invoke_vars[var_name]
            line_no = source[:m.start()].count('\n') + 1
            issues.append({
                "line": line_no,
                "severity": "Error",
                "code": "VS-PORT-002",
                "message": (
                    f"'{var_name}.result' is invalid: "
                    f"{info['type']}.{info['method']}() is void and has no result port. "
                    f"Remove this connection."
                )
            })

    return issues


def _check_multi_input_accessors(source):
    """VS-PORT-003: Detect .a/.b usage on multi-input units (ScalarSum, GenericSum)."""
    issues = []

    # Find multi-input unit variables
    unit_pattern = re.compile(
        r'(?:var|\w+)\s+(\w+)\s*=\s*new\s+(' + '|'.join(MULTI_INPUT_UNITS) + r')\s*\(',
        re.MULTILINE
    )
    multi_vars = {}
    for m in unit_pattern.finditer(source):
        multi_vars[m.group(1)] = m.group(2)

    # Check for .a or .b accessor usage
    ab_pattern = re.compile(r'\b(\w+)\.(a|b)\b')
    for m in ab_pattern.finditer(source):
        var_name = m.group(1)
        accessor = m.group(2)
        if var_name in multi_vars:
            unit_type = multi_vars[var_name]
            line_no = source[:m.start()].count('\n') + 1
            idx = 0 if accessor == "a" else 1
            issues.append({
                "line": line_no,
                "severity": "Error",
                "code": "VS-PORT-003",
                "message": (
                    f"'{var_name}.{accessor}' is wrong. "
                    f"{unit_type} is a MultiInputUnit and uses "
                    f"'.multiInputs[{idx}]' (C#) or '\"{idx}\"' (JSON key), "
                    f"not '.{accessor}'. Use '{var_name}.multiInputs[{idx}]' instead."
                )
            })

    return issues


def main():
    if len(sys.argv) < 2:
        print("Usage: check_port_keys.py <cs_file>", file=sys.stderr)
        sys.exit(2)

    cs_file = sys.argv[1]
    if not Path(cs_file).exists():
        print(f"ERROR: File not found: {cs_file}", file=sys.stderr)
        sys.exit(2)

    issues = check_file(cs_file)
    errors = [i for i in issues if i["severity"] == "Error"]
    warnings = [i for i in issues if i["severity"] == "Warning"]

    if not issues:
        print("Port key check PASSED: No issues found.")
        sys.exit(0)

    for i in errors:
        print(f"  ERROR {i['code']} (line {i['line']}): {i['message']}")
    for i in warnings:
        print(f"  WARNING {i['code']} (line {i['line']}): {i['message']}")

    print(f"\nTotal: {len(errors)} error(s), {len(warnings)} warning(s)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
