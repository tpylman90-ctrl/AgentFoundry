"""Offline safety and scoring tests. The stub is NOT an independent model."""
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("rules_pilot", ROOT / "tools" / "run_rules_pilot.py")
pilot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pilot)


class RulePilotTests(unittest.TestCase):
    def test_exact_score_requires_boolean_and_exact_state(self):
        expected = {"allowed": False, "state": {"hp": 20, "mp": 6}}
        self.assertEqual(pilot.exact_score(expected, expected), 1)
        self.assertEqual(pilot.exact_score(expected, {"allowed": 0, "state": {"hp": 20, "mp": 6}}), 0)
        self.assertEqual(pilot.exact_score(expected, {"allowed": False, "state": {"hp": "20", "mp": 6}}), 0)
        self.assertEqual(pilot.exact_score(expected, {"allowed": False, "state": {"hp": 20}}), 0)
        self.assertEqual(pilot.exact_score(expected, {"allowed": False, "state": {"hp": 20, "mp": 6, "foo": 0}}), 0)

    def test_json_code_fence(self):
        self.assertEqual(pilot.parse_reply('```json\n{"allowed":false,"state":{}}\n```'),
                         {"allowed": False, "state": {}})

    def test_cases_have_stable_contract(self):
        cases = json.loads(pilot.CASE_PATH.read_text())
        pilot.validate_cases(cases)
        self.assertEqual(len(cases), 13)
        self.assertEqual(len(set(c["id"] for c in cases)), 13)

    def test_remote_endpoint_rejects_http(self):
        with self.assertRaisesRegex(ValueError, "HTTPS"):
            pilot.check_endpoint("http://example.com/v1/chat/completions", "")
        with self.assertRaisesRegex(ValueError, "LLM_API_KEY"):
            pilot.check_endpoint("https://example.com/v1/chat/completions", "")
        self.assertEqual(pilot.check_endpoint("http://127.0.0.1:8080/v1/chat/completions", "").hostname,
                         "127.0.0.1")

    def test_paired_run_does_not_export_private_skill(self):
        secret = "TOP_SECRET_SKILL_TEXT_NEVER_EXPORT "
        calls = []

        def fake_completion(endpoint, model, prompt, system, timeout, max_tokens, key):
            calls.append((prompt, system))
            return '{"allowed": false, "state": {}}'

        with tempfile.TemporaryDirectory() as temp:
            d = Path(temp)
            skill = d / "private_skill.md"
            skill.write_text(secret * 6)
            args = SimpleNamespace(endpoint="http://127.0.0.1:8080/v1/chat/completions",
                                   model="mock-only", mode="paired", skill_file=str(skill),
                                   output=str(d / "results"), seed=3, repetitions=1,
                                   timeout=5, max_tokens=220)
            with mock.patch.object(pilot, "completion", side_effect=fake_completion):
                status = pilot.run(args)
            self.assertEqual(status, "paired_rules_pilot")
            self.assertEqual(len(calls), 26)
            baseline = [system for _, system in calls if secret not in system]
            treatment = [system for _, system in calls if secret in system]
            self.assertEqual(len(baseline), 13)
            self.assertEqual(len(treatment), 13)
            manifest = (d / "results" / "results.json").read_text()
            report = (d / "results" / "REPORT.md").read_text()
            self.assertNotIn(secret, manifest + report)
            self.assertIn("skill_sha256", manifest)
            self.assertIn("mock-only", report)

    def test_baseline_run_cannot_claim_delta(self):
        def fake_completion(*_args):
            return '{"allowed":false,"state":{}}'

        with tempfile.TemporaryDirectory() as temp:
            d = Path(temp)
            args = SimpleNamespace(endpoint="http://localhost:8080/v1/chat/completions",
                                   model="mock-only", mode="baseline", skill_file=None,
                                   output=str(d / "results"), seed=4, repetitions=1,
                                   timeout=5, max_tokens=220)
            with mock.patch.object(pilot, "completion", side_effect=fake_completion):
                status = pilot.run(args)
            self.assertEqual(status, "baseline_diagnostic")
            report = (d / "results" / "REPORT.md").read_text()
            self.assertNotIn("Difference (skill minus baseline)", report)

    def test_private_skill_never_uses_remote_endpoint(self):
        with tempfile.TemporaryDirectory() as temp:
            args = SimpleNamespace(endpoint="https://example.com/v1/chat/completions",
                                   model="mock-only", mode="paired", skill_file=None,
                                   output=str(Path(temp) / "results"), seed=4, repetitions=1,
                                   timeout=5, max_tokens=220)
            with mock.patch.dict("os.environ", {"LLM_API_KEY": "not_a_real_key"}):
                with self.assertRaisesRegex(ValueError, "loopback model"):
                    pilot.run(args)

    def test_paired_requires_skill_file(self):
        with tempfile.TemporaryDirectory() as temp:
            args = SimpleNamespace(endpoint="http://localhost:8080/v1/chat/completions",
                                   model="mock-only", mode="paired", skill_file=None,
                                   output=str(Path(temp) / "results"), seed=4, repetitions=1,
                                   timeout=5, max_tokens=220)
            with self.assertRaisesRegex(ValueError, "requires --skill-file"):
                pilot.run(args)


if __name__ == "__main__":
    unittest.main()
