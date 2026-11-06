import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("staged",ROOT/"tools"/"run_staged_godot.py")
s=importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)

class StagedPromptTests(unittest.TestCase):
    def test_extraction_rejects_explanations(self):
        self.assertEqual(s.extract("extends RefCounted\nfunc go():\n\tpass"),"extends RefCounted\nfunc go():\n\tpass\n")
        self.assertEqual(s.extract("here is the answer"),"")
        self.assertEqual(s.extract("extends Node\nfunc go():\n\tpass"),"")
        self.assertEqual(s.extract(""),"")
    def test_cards_are_unique_and_bounded(self):
        text="<!-- AF_STAGE:code:start -->\n"+("do this " * 20)+"\n<!-- AF_STAGE:code:end -->"
        self.assertEqual(len(s.card(text,"STAGE","code").split()),40)
        with self.assertRaises(ValueError):
            s.card(text,"STAGE","repair")
        with self.assertRaises(ValueError):
            s.card(text,"STAGE","../x")
    def test_reproducible_two_arms(self):
        one=[(x["id"],arm) for x,arm in s.plan_order(s.tasks(),"paired",8)]
        two=[(x["id"],arm) for x,arm in s.plan_order(s.tasks(),"paired",8)]
        self.assertEqual(one,two)
        self.assertEqual(len(set(one)),6)
        self.assertEqual(len(s.plan_order(s.tasks(),"baseline",8)),3)
    def test_requires_exact_new_secret(self):
        self.assertEqual(s.skill("baseline","/not-used"),"")
        with self.assertRaises(ValueError):
            s.skill("paired",None)

    def test_closed_schema_compiler_feedback_rejects_raw_text(self):
        import json, tempfile
        with tempfile.TemporaryDirectory() as temp:
            from pathlib import Path
            path = Path(temp) / "sanitized.json"
            rows = [
                {"task": task, "condition": arm,
                 "diagnostic": {"category": "parse_token", "line": 21, "method": None}}
                for task in ("equipment", "forge", "abilities")
                for arm in ("baseline", "skill")
            ]
            payload = {"mode": "paired", "diagnostic_schema": 1, "cases": rows}
            path.write_text(json.dumps(payload))
            self.assertEqual(len(s.load_diagnostics(str(path), "paired")), 6)
            payload["cases"][0]["diagnostic"]["raw"] = "LEAK_PRIVATE_SKILL"
            path.write_text(json.dumps(payload))
            with self.assertRaises(ValueError):
                s.load_diagnostics(str(path), "paired")
            payload["cases"][0]["diagnostic"].pop("raw")
            payload["cases"][0]["diagnostic"]["line"] = "21; LEAK_PRIVATE_SKILL"
            path.write_text(json.dumps(payload))
            with self.assertRaises(ValueError):
                s.load_diagnostics(str(path), "paired")
            payload["cases"][0]["diagnostic"]["line"] = 21
            payload["cases"].append(payload["cases"][0])
            path.write_text(json.dumps(payload))
            with self.assertRaises(ValueError):
                s.load_diagnostics(str(path), "paired")

    def test_no_remote_endpoint(self):
        self.assertEqual(s.ENDPOINT,"http://af-model:8080/v1/chat/completions")
