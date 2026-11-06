#!/usr/bin/env python3
"""Score actual Godot-engine executions, publishing NO model-generated source."""
import argparse
import hashlib
import json
from pathlib import Path
import re

TEST_PATTERN = re.compile(r"^AF_TEST:([EFA][0-9]{2}):(PASS|FAIL)\s*$")


def grade(log_text, expected_prefix, count):
    expected = {f"{expected_prefix}{i:02d}" for i in range(1, count + 1)}
    results = {}
    for line in log_text.splitlines():
        match = TEST_PATTERN.fullmatch(line.strip())
        if match and match.group(1) in expected:
            if match.group(1) in results:  # duplicate result is invalid
                results[match.group(1)] = False
            else:
                results[match.group(1)] = match.group(2) == "PASS"
    return {
        "passed": sum(1 for key in expected if results.get(key) is True),
        "total": count,
        "missing_checks": sorted(expected - set(results)),
        "failed_checks": sorted(key for key in expected if not results.get(key, False)),
    }


def summarize(task_specs, generation, logs_root):
    mode = generation["mode"]
    if mode not in ("baseline", "paired"):
        raise ValueError("invalid mode")
    arms = ["baseline", "skill"] if mode == "paired" else ["baseline"]
    attempts = {(a["task"], a["condition"]): a for a in generation["attempts"]}
    by_task = []
    aggregates = {arm: {"passed": 0, "total": 0, "compilable_tasks": 0} for arm in arms}
    for task in task_specs:
        prefix = {"equipment": "E", "forge": "F", "abilities": "A"}[task["id"]]
        for arm in arms:
            a = attempts.get((task["id"], arm))
            if a is None:
                raise ValueError("missing attempt")
            path = logs_root / task["id"] / arm
            out_log = path / "engine.log"
            code = path / "exit.txt"
            if out_log.exists():
                text = out_log.read_text(encoding="utf-8", errors="replace")
            else:
                text = ""
            report = grade(text, prefix, task["checks"])
            exit_status = int(code.read_text().strip()) if code.exists() else -1
            ok = exit_status == 0 and report["missing_checks"] == []
            row = {
                "task": task["id"], "condition": arm, "passed": report["passed"],
                "total": task["checks"], "failed_checks": report["failed_checks"],
                "all_checks_reported": not report["missing_checks"],
                "engine_exit_zero": exit_status == 0,
                "generation_status": a["generation_status"],
                "source_sha256": a["source_sha256"],
            }
            aggregates[arm]["passed"] += row["passed"]
            aggregates[arm]["total"] += row["total"]
            aggregates[arm]["compilable_tasks"] += int(ok)
            by_task.append(row)
    result = {
        "status": "paired_godot_code_trial" if mode == "paired" else "baseline_only_godot_code_trial",
        "model_label": generation["model_label"],
        "mode": mode, "seed": generation["seed"], "temperature": generation["temperature"],
        "token_budget": generation["max_tokens"], "skill_sha256": generation["skill_sha256"],
        "engine_version": "Godot 4.5.2 stable Linux x86_64",
        "aggregate": aggregates, "cases": by_task,
        "method": "independent single-shot Godot GDScript generation; engine executes behavior assertions",
        "limitations": "one small public test set, one code sample per condition/task, not autonomous agent patch development",
    }
    return result


def markdown(result):
    rows = [
        "# AgentFoundry — real Godot code execution pilot",
        "",
        f"**Status:** {result['status']}",
        f"**Model:** {result['model_label']}; **engine:** {result['engine_version']}.",
        f"**Seed:** {result['seed']}; **sampling temperature:** {result['temperature']}; "
        f"**max completion tokens:** {result['token_budget']}.",
        "",
        "| Condition | Passing Godot assertions | Executed tasks with complete checks |",
        "|---|---:|---:|",
    ]
    for arm, data in result["aggregate"].items():
        rows.append(f"| {arm} | {data['passed']}/{data['total']} | {data['compilable_tasks']}/3 |")
    if result["mode"] == "paired":
        a, b = result["aggregate"]["baseline"], result["aggregate"]["skill"]
        delta = 100 * (b["passed"] - a["passed"]) / a["total"]
        rows.append(f"\n**Observed skill difference:** {delta:+.1f} percentage points "
                    f"({b['passed'] - a['passed']:+d} assertions).")
    rows.extend(["", "| Task | Condition | Passed | Engine exited cleanly |", "|---|---|---:|---|"])
    for x in result["cases"]:
        rows.append(f"| {x['task']} | {x['condition']} | {x['passed']}/{x['total']} | "
                    f"{'yes' if x['engine_exit_zero'] else 'no'} |")
    rows.extend([
        "", "This study tests **single-shot GDScript generation** followed by a real Godot",
        "engine-run behavior check. It is **not** a multi-step autonomous coding-agent",
        "study, production Android validation, or proof of cross-model skill quality.",
        "No model-generated source, private skill instructions, or raw Godot logs",
        "are published in the result artifact.",
        "",
    ])
    return "\n".join(rows)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--tasks", required=True)
    p.add_argument("--generation", required=True)
    p.add_argument("--logs", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    tasks = json.loads(Path(args.tasks).read_text())
    generation = json.loads(Path(args.generation).read_text())
    report = summarize(tasks, generation, Path(args.logs))
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    (output / "results.json").write_text(json.dumps(report, indent=2) + "\n")
    (output / "REPORT.md").write_text(markdown(report))
    print(markdown(report))  # privacy-safe report only


if __name__ == "__main__":
    main()
