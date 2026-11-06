#!/usr/bin/env python3
"""Generate single-file Godot 4.5 implementations, baseline vs private skill.

Runs only inside the Docker --internal af-code-private network. The output
GDScript is untrusted and must only run in a separate no-network sandbox.
No private prompt or raw model output is printed or uploaded to GitHub.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import time
import urllib.request

ENDPOINT = "http://af-model:8080/v1/chat/completions"
SYSTEM = (
    "You are an experienced Godot 4.5 GDScript engineer implementing an RPG "
    "feature in a new, isolated project. Follow the requested API precisely. "
    "Return only the complete standalone GDScript file; no explanations, "
    "diff markers, test cases, or Markdown commentary."
)
TASKS = Path(__file__).resolve().parents[1] / "benchmarks" / "godot-code" / "tasks.json"


def extract_script(raw):
    """Convert a model's response into ONE source file without rewriting it."""
    if not isinstance(raw, str):
        return ""
    s = raw.strip()
    if s.startswith("```"):
        pos = s.find("\n")
        if pos < 0:
            return ""
        s = s[pos + 1:]
        if "```" in s:
            s = s.split("```", 1)[0]
    if not s.lstrip().startswith("extends RefCounted"):
        return ""  # no repair or cherry-picking a better answer
    s = s.strip()
    if not s or "\x00" in s or len(s.encode("utf-8")) > 80000:
        return ""
    return s + "\n"


def create_plan(tasks, mode, seed):
    if mode not in ("baseline", "paired"):
        raise ValueError("invalid mode")
    ids = [x["id"] for x in tasks]
    if len(ids) != len(set(ids)) or len(ids) != 3:
        raise ValueError("expected 3 unique task IDs")
    arms = ("baseline", "skill") if mode == "paired" else ("baseline",)
    plan = [(task, arm) for task in tasks for arm in arms]
    random.Random(seed).shuffle(plan)
    return plan


def infer(task_prompt, system, max_tokens, timeout):
    payload = {
        "model": "qwen-coder-1.5b",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": task_prompt},
        ],
        "temperature": 0,
        "max_tokens": max_tokens,
        "stream": False,
    }
    request = urllib.request.Request(
        ENDPOINT, json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = json.load(response)
    return data["choices"][0]["message"]["content"]


def run(mode, skill_file, output, seed, timeout, max_tokens):
    if os.getenv("AGENTFOUNDRY_ISOLATED_DOCKER") != "af-code-private":
        raise ValueError("private inference requires isolated agentfoundry Docker execution")
    skill = ""
    if mode == "paired":
        if not skill_file:
            raise ValueError("paired test requires private skill file")
        skill = Path(skill_file).read_text(encoding="utf-8")
        if len(skill.strip()) < 100:
            raise ValueError("private skill is missing or too short")
    tasks = json.loads(TASKS.read_text(encoding="utf-8"))
    plan = create_plan(tasks, mode, seed)
    root = Path(output).resolve()
    if root.exists() and any(root.iterdir()):
        raise ValueError("output directory must be empty")
    root.mkdir(parents=True, exist_ok=True)
    meta = {
        "type": "single-shot-godot-code-generation",
        "mode": mode, "seed": seed, "temperature": 0,
        "max_tokens": max_tokens, "model_label": "qwen-coder-1.5b",
        "skill_sha256": hashlib.sha256(skill.encode()).hexdigest() if skill else None,
        "attempts": [],
    }
    for task, arm in plan:
        folder = root / task["id"] / arm
        folder.mkdir(parents=True)
        system = SYSTEM + ("\n\nApply the following confidential specialized skill:\n" + skill if arm == "skill" else "")
        raw = ""
        err = ""
        started = time.monotonic()
        try:
            raw = infer(task["brief"], system, max_tokens, timeout)
            source = extract_script(raw)
            if not source:
                err = "not_standalone_gdscript"
            else:
                (folder / "generated.gd").write_text(source, encoding="utf-8")
        except (OSError, KeyError, ValueError, TypeError, IndexError) as exc:
            err = "generation_error_" + type(exc).__name__
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        meta["attempts"].append({
            "task": task["id"], "condition": arm, "generation_status": err or "generated",
            "source_sha256": hashlib.sha256(
                (folder / "generated.gd").read_bytes()
            ).hexdigest() if (folder / "generated.gd").exists() else None,
            "raw_response_sha256": digest, "elapsed_seconds": round(time.monotonic() - started, 2),
        })
        # No source and no system prompt in CI logs.
        print("AF_GENERATED", task["id"], arm, err or "OK", flush=True)
    (root / "generation.json").write_text(json.dumps(meta, indent=2) + "\n")
    return len(meta["attempts"])


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=("baseline", "paired"), required=True)
    p.add_argument("--skill-file")
    p.add_argument("--output", required=True)
    p.add_argument("--seed", type=int, default=20261105)
    p.add_argument("--timeout", type=int, default=240)
    p.add_argument("--max-tokens", type=int, default=1100)
    args = p.parse_args()
    if args.max_tokens < 100 or args.max_tokens > 2200:
        p.error("unsupported token budget")
    try:
        count = run(args.mode, args.skill_file, args.output, args.seed, args.timeout, args.max_tokens)
    except (OSError, ValueError) as e:
        p.error(str(e))
    print("Code generation attempts completed:", count)


if __name__ == "__main__":
    main()
