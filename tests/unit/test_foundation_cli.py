import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from skills.foundation.foundation import markdown_assessment, policy, run_process, scaffold_files


class FoundationCliTests(unittest.TestCase):
    def test_assessment_reports_missing_controls(self):
        with tempfile.TemporaryDirectory() as directory:
            result = markdown_assessment(Path(directory))

        self.assertFalse(result["ready"])
        self.assertIn("AGENTS.md", result["missing_files"])
        self.assertIn("scripts", result["missing_directories"])

    def test_policy_routes_paths(self):
        result = policy(["ai/prompts/example.md", "infrastructure/main.tf", "README.md"])

        self.assertIn("policies/ai/", result)
        self.assertIn("policies/architecture/", result)
        self.assertIn("policies/repository/", result)

    def test_policy_without_paths_lists_domains(self):
        result = policy([])

        self.assertIn("repository: policies/repository/", result)
        self.assertIn("AI: policies/ai/", result)

    def test_minimal_scaffold_has_enforcement_core(self):
        source = Path(__file__).resolve().parents[2]

        files = {path.relative_to(source).as_posix() for path in scaffold_files(source, "minimal")}

        self.assertIn("PROJECT.yaml", files)
        self.assertIn(".plumbline/plumbline.py", files)
        self.assertIn("scripts/plumbline-check.sh", files)

    def test_run_process_forces_utf8_output(self):
        with patch("skills.foundation.foundation.subprocess.run") as run:
            run.return_value.returncode = 0

            self.assertEqual(run_process(["python", "-V"], Path.cwd()), 0)

        environment = run.call_args.kwargs["env"]
        self.assertEqual(environment["PYTHONIOENCODING"], "utf-8")


if __name__ == "__main__":
    unittest.main()
