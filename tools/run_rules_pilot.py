#!/usr/bin/env python3
"""Exact-state RPG reasoning pilot over a real OpenAI-compatible model endpoint.

No private skill text is written into exported evidence or logs. It is a narrow
rules task, NOT a Godot coding-agent benchmark.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import time
import urllib.parse
import urllib.request
import urllib.error

SYSTEM = (
    'You are a Godot RPG systems engineer. Apply the scenario rules exactly. '
    'Return ONLY compact JSON: {"allowed":true or false,"state":{...}}. '
    'Include every original state key and do not add new keys.'
)
CASE_PATH = Path(__file__).resolve().parents[1] / "benchmarks" / "rpg-rules" / "cases.json"


def parse_reply(content):
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    return json.loads(content)


def exact_score(expected, response):
    if not isinstance(response, dict) or type(response.get("allowed")) is not bool:
        return 0
    state = response.get("state")
    if not isinstance(state, dict) or set(state) != set(expected["state"]):
        return 0
    if response["allowed"] != expected["allowed"]:
        return 0
    return int(all(type(state[key]) is type(value) and state[key] == value
                   for key, value in expected["state"].items()))


def check_endpoint(endpoint, key):
    parsed = urllib.parse.urlparse(endpoint)
    # The only non-loopback private exception is the hard-coded model service
    # inside the Docker --internal network. It cannot be selected via an API URL.
    local = parsed.hostname in ("localhost", "127.0.0.1", "::1") or (
        parsed.hostname == "af-model" and
        os.getenv("AGENTFOUNDRY_ISOLATED_DOCKER") == "af-private"
    )
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("endpoint must be an http(s) URL")
    if not local and parsed.scheme != "https":
        raise ValueError("remote endpoint requires HTTPS")
    if not local and not key:
        raise ValueError("remote endpoint requires LLM_API_KEY")
    return parsed


def completion(endpoint, model, prompt, system, timeout, max_tokens, key):
    body = json.dumps({
        "model": model, "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0, "max_tokens": max_tokens
    }).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = "Bearer " + key
    request = urllib.request.Request(endpoint, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(request, timeout=timeout) as resp:
        output = json.load(resp)
    return output["choices"][0]["message"]["content"]


def validate_cases(cases):
    if len(cases) < 10 or len({case["id"] for case in cases}) != len(cases):
        raise ValueError("need at least 10 cases with unique IDs")
    for case in cases:
        for key in ("id", "task", "scenario", "action", "state", "expected"):
            if key not in case:
                raise ValueError("missing case field: " + key)
        if case["task"] not in ("E1", "E2", "E3"):
            raise ValueError("unknown task")
        if set(case["state"]) != set(case["expected"]["state"]):
            raise ValueError("state shape changed")


def run(args):
    key = os.getenv("LLM_API_KEY", "")
    parsed = check_endpoint(args.endpoint, key)
    private_safe = parsed.hostname in ("localhost", "127.0.0.1", "::1") or (
        parsed.hostname == "af-model" and
        os.getenv("AGENTFOUNDRY_ISOLATED_DOCKER") == "af-private"
    )
    if args.mode == "paired" and not private_safe:
        raise ValueError("private skill comparisons require a loopback model or isolated Docker service")
    cases = json.loads(CASE_PATH.read_text(encoding="utf-8"))
    validate_cases(cases)
    if args.repetitions not in range(1, 11):
        raise ValueError("repetitions must be 1–10")
    skill = ""
    if args.mode == "paired":
        if not args.skill_file:
            raise ValueError("paired mode requires --skill-file")
        skill = Path(args.skill_file).read_text(encoding="utf-8")
        if len(skill.strip()) < 100:
            raise ValueError("skill text is unexpectedly short")
    output = Path(args.output).resolve()
    if output.exists() and any(output.iterdir()):
        raise ValueError("output directory must be empty")
    output.mkdir(parents=True, exist_ok=True)
    conditions = ("baseline", "skill") if args.mode == "paired" else ("baseline",)
    plan = [(case, rep, arm) for case in cases
            for rep in range(1, args.repetitions + 1) for arm in conditions]
    random.Random(args.seed).shuffle(plan)
    rows = []
    transport_failure = False
    for case, repetition, arm in plan:
        system = SYSTEM + ("\n\nUse this specialized agent skill:\n" + skill if arm == "skill" else "")
        prompt = (
            "Scenario: " + case["scenario"] +
            "\nInitial state: " + json.dumps(case["state"], sort_keys=True) +
            "\nAction: " + case["action"] +
            "\nReturn whether allowed and the complete resulting state."
        )
        started = time.monotonic()
        err = ""
        raw = ""
        try:
            raw = str(completion(args.endpoint, args.model, prompt, system,
                                 args.timeout, args.max_tokens, key))
            try:
                score = exact_score(case["expected"], parse_reply(raw))
            except (ValueError, TypeError, KeyError):
                score = 0
                err = "invalid_json_or_shape"
        except (urllib.error.URLError, TimeoutError, KeyError, ValueError, OSError) as exc:
            score = 0
            err = "transport_error_" + type(exc).__name__
            transport_failure = True
        # Privacy guard: neither the system prompt nor model output is exported.
        # The raw-output digest allows local private transcripts to be checked.
        rows.append({
            "case": case["id"], "task": case["task"], "trial": repetition,
            "condition": arm, "pass": score, "error": err,
            "response_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
            "elapsed_seconds": round(time.monotonic() - started, 3),
        })
        print(case["id"], arm, "PASS" if score else "FAIL", err, flush=True)
    status = "incomplete_transport_error" if transport_failure else (
        "paired_rules_pilot" if args.mode == "paired" else "baseline_diagnostic"
    )
    manifest = {
        "status": status, "model_label": args.model,
        "endpoint_origin": parsed.hostname, "case_count": len(cases),
        "repetitions": args.repetitions, "seed": args.seed,
        "skill_sha256": hashlib.sha256(skill.encode("utf-8")).hexdigest() if skill else None,
        "rows": rows,
    }
    (output / "results.json").write_text(json.dumps(manifest, indent=2) + "\n")
    lines = [
        "# Independent model rules-reasoning pilot",
        "", "**Status:** " + status, "",
        "Model label: `" + args.model + "` (supplied by endpoint, not independently attested).",
        f"Cases: {len(cases)}; repetitions: {args.repetitions}.", "",
        "| Condition | Exact-state accuracy | Count |",
        "|---|---:|---:|",
    ]
    for arm in conditions:
        arm_rows = [row for row in rows if row["condition"] == arm]
        if transport_failure:
            percentage = "N/A — incomplete"
        else:
            percentage = f"{100 * sum(row['pass'] for row in arm_rows) / len(arm_rows):.1f}%"
        lines.append(f"| {arm} | {percentage} | {len(arm_rows)} |")
    if len(conditions) == 2 and not transport_failure:
        lines.extend(["", "| Case | Baseline passes | Skill passes |", "|---|---:|---:|"])
        for case in cases:
            b = sum(row["pass"] for row in rows if row["case"] == case["id"] and row["condition"] == "baseline")
            t = sum(row["pass"] for row in rows if row["case"] == case["id"] and row["condition"] == "skill")
            lines.append(f"| {case['id']} | {b}/{args.repetitions} | {t}/{args.repetitions} |")
        without = [row["pass"] for row in rows if row["condition"] == "baseline"]
        with_skill = [row["pass"] for row in rows if row["condition"] == "skill"]
        delta = 100 * (sum(with_skill) - sum(without)) / len(without)
        lines.append(f"\nDifference (skill minus baseline): **{delta:+.1f} percentage points**.")
    lines.extend([
        "", "This is NOT an autonomous Godot coding-agent evaluation, a Claude",
        "evaluation, or an Android test. Small samples are inconclusive.",
        "Full private skill text and raw responses are deliberately excluded",
        "from public CI artifacts.", "",
    ])
    (output / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    return status


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--mode", choices=("baseline", "paired"), default="baseline")
    parser.add_argument("--skill-file")
    parser.add_argument("--output", default="results")
    parser.add_argument("--seed", type=int, default=20261105)
    parser.add_argument("--repetitions", type=int, default=1)
    parser.add_argument("--max-tokens", type=int, default=220)
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()
    try:
        status = run(args)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    if status == "incomplete_transport_error":
        raise SystemExit(2)
    print("Wrote", args.output)


if __name__ == "__main__":
    main()
