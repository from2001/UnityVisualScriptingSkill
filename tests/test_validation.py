"""Regression checks for truthful, portable C# preflight results."""

import contextlib
import importlib.util
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

TOOLS = Path(__file__).resolve().parents[1] / ".agents/skills/unity-visual-scripting/tools"


def load(name):
    spec = importlib.util.spec_from_file_location(name, TOOLS / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


compiler = load("validate_cs")
combined = load("validate")


class CompilerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="unity skill & test ")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / "Example.cs"
        self.source.write_text("#if UNITY_EDITOR\npublic class Example {}\n#endif\n")
        self.managed = self.root / "Managed"
        self.managed.mkdir()
        (self.managed / "UnityEngine.dll").touch()

    def run_compile(self, result):
        with patch.object(compiler.shutil, "which", return_value="dotnet"), patch.object(
            compiler.subprocess, "run", return_value=result
        ):
            return compiler.validate(self.source, managed_dir=self.managed)

    def test_missing_editor_is_incomplete(self):
        code, _ = compiler.validate(self.source, managed_dir=self.root / "missing")
        self.assertEqual(code, 2)

    def test_missing_sdk_is_incomplete(self):
        with patch.object(compiler.shutil, "which", return_value=None):
            code, _ = compiler.validate(self.source, managed_dir=self.managed)
        self.assertEqual(code, 2)

    def test_no_implicit_version_fallback(self):
        code, _ = compiler.validate(self.source)
        self.assertEqual(code, 2)
        project = self.root / "project"
        (project / "ProjectSettings").mkdir(parents=True)
        (project / "ProjectSettings/ProjectVersion.txt").write_text("m_EditorVersion: 6000.0.70f1\n")
        with patch.object(compiler, "find_unity_managed_dir", return_value=None) as lookup:
            code, _ = compiler.validate(self.source, unity_project=project)
        self.assertEqual(code, 2)
        lookup.assert_called_once_with("6000.0.70f1")
        code, _ = compiler.validate(self.source, "6000.0.68f1", project, self.managed)
        self.assertEqual(code, 2)

    def test_missing_package_assemblies_are_incomplete(self):
        (self.root / "ProjectSettings").mkdir()
        (self.root / "ProjectSettings/ProjectVersion.txt").write_text("m_EditorVersion: 6000.0.70f1\n")
        code, _ = compiler.validate(self.source, unity_project=self.root, managed_dir=self.managed)
        self.assertEqual(code, 2)

    def test_build_failure_without_cs_diagnostic_fails(self):
        code, evidence = self.run_compile(subprocess.CompletedProcess([], 1, "error MSB1009: missing project", ""))
        self.assertEqual(code, 1)
        self.assertIn("MSB1009", evidence)

    def test_build_crash_does_not_pass(self):
        code, _ = self.run_compile(subprocess.CompletedProcess([], -9, "", "terminated"))
        self.assertEqual(code, 1)

    def test_timeout_is_incomplete(self):
        with patch.object(compiler.shutil, "which", return_value="dotnet"), patch.object(
            compiler.subprocess, "run", side_effect=subprocess.TimeoutExpired("dotnet", 45)
        ):
            code, _ = compiler.validate(self.source, managed_dir=self.managed)
        self.assertEqual(code, 2)

    def test_packaged_template_builds_in_disposable_directory(self):
        self.assertTrue(compiler.PROJECT_FILE.is_file())
        observed = []
        def build(args, **kwargs):
            cwd = Path(kwargs["cwd"])
            observed.append(cwd)
            props = ET.parse(cwd / "ValidationProject.csproj").getroot()
            self.assertEqual(props.findtext(".//UnityManagedDir"), str(self.managed.resolve()))
            self.assertEqual((cwd / "Input.cs").read_text(), self.source.read_text())
            self.assertNotEqual(cwd, TOOLS / "validation_project")
            return subprocess.CompletedProcess(args, 0, "Build succeeded", "")
        with patch.object(compiler.shutil, "which", return_value="dotnet"), patch.object(
            compiler.subprocess, "run", side_effect=build
        ):
            code, _ = compiler.validate(self.source, managed_dir=self.managed)
        self.assertEqual(code, 0)
        self.assertFalse(observed[0].exists())


class CombinedTests(unittest.TestCase):
    def run_main(self, results, flags=()):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "Input.cs"
            source.write_text("#if UNITY_EDITOR\n#endif\n")
            stdout, stderr = io.StringIO(), io.StringIO()
            with patch.object(sys, "argv", ["validate.py", str(source), *flags]), patch.object(
                combined, "run_check", side_effect=results
            ) as run, contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as raised:
                    combined.main()
            return raised.exception.code, stdout.getvalue(), stderr.getvalue(), run.call_count

    def test_skipped_or_crashed_layers_never_pass(self):
        for codes in ((2, 0), (0, 2), (37, 0), (0, -9)):
            with self.subTest(codes=codes):
                code, _, stderr, calls = self.run_main([(c, "", "setup detail") for c in codes])
                self.assertEqual(code, 2)
                self.assertEqual(calls, 2)
                self.assertIn("setup detail", stderr)

    def test_detected_error_fails_even_with_other_layer_unavailable(self):
        code, _, _, _ = self.run_main([(2, "", ""), (1, "bad port", "")])
        self.assertEqual(code, 1)

    def test_pass_requires_both_layers(self):
        code, _, _, calls = self.run_main([(0, "", ""), (0, "", "")])
        self.assertEqual((code, calls), (0, 2))

    def test_static_only_has_explicit_scope(self):
        code, stdout, _, calls = self.run_main([(0, "", "")], ["--static-only"])
        self.assertEqual((code, calls), (0, 1))
        self.assertIn("compilation not run", stdout)


if __name__ == "__main__":
    unittest.main()
