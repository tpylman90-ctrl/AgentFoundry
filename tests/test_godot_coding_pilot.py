import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

BASE = Path(__file__).resolve().parents[1]


def loadmod(filename, name):
    spec = importlib.util.spec_from_file_location(name, BASE / "tools" / filename)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


gen = loadmod("run_godot_coding_pilot.py", "gen")
score = loadmod("score_godot_coding.py", "score")


class GodotCodingPilotTests(unittest.TestCase):
    def test_script_extraction_only_standalone(self):
        self.assertEqual(gen.extract_script("extends RefCounted\nfunc a():\n\tpass"),
                         "extends RefCounted\nfunc a():\n\tpass\n")
        self.assertEqual(gen.extract_script("```gdscript\nextends RefCounted\n```"),
                         "extends RefCounted\n")
        self.assertEqual(gen.extract_script("Here is the code:\nextends RefCounted"), "")
        self.assertEqual(gen.extract_script("extends Node\npass"), "")

    def test_same_seed_is_reproducible_and_balanced(self):
        tasks = json.loads(gen.TASKS.read_text())
        p1 = [(x["id"], arm) for x, arm in gen.create_plan(tasks, "paired", 77)]
        p2 = [(x["id"], arm) for x, arm in gen.create_plan(tasks, "paired", 77)]
        self.assertEqual(p1, p2)
        self.assertEqual(len(p1), 6)
        self.assertEqual(len({(task, arm) for task, arm in p1}), 6)
        self.assertEqual(len(gen.create_plan(tasks, "baseline", 77)), 3)

    def test_grade_counts_missing_and_rejects_duplicate(self):
        r = score.grade("AF_TEST:E01:PASS\nAF_TEST:E02:FAIL\nAF_TEST:E03:PASS", "E", 3)
        self.assertEqual(r["passed"], 2)
        self.assertEqual(r["total"], 3)
        self.assertEqual(r["failed_checks"], ["E02"])
        r = score.grade("AF_TEST:E01:PASS\nAF_TEST:E01:PASS", "E", 2)
        self.assertEqual(r["passed"], 0)
        self.assertEqual(r["failed_checks"], ["E01", "E02"])

    def test_no_skill_text_in_public_report(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            specs = json.loads(gen.TASKS.read_text())
            generation = {
                "mode":"paired", "seed":4, "temperature":0, "max_tokens":1100,
                "model_label":"stub", "skill_sha256":"a"*64,
                "attempts":[{"task":t["id"],"condition":arm,"generation_status":"generated","source_sha256":"f"*64}
                    for t in specs for arm in ("baseline","skill")],
            }
            for t in specs:
                for arm in ("baseline","skill"):
                    d = root / t["id"] / arm
                    d.mkdir(parents=True)
                    (d/"engine.log").write_text("AF_TEST:E01:PASS\n")
                    (d/"exit.txt").write_text("1")
            summary = score.summarize(specs, generation, root)
            text = score.markdown(summary)
            self.assertIn("Observed skill difference", text)
            self.assertNotIn("TOP_SECRET_SKILL", text)
            self.assertEqual(summary["mode"], "paired")


if __name__ == "__main__":
    unittest.main()
