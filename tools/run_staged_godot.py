#!/usr/bin/env python3
"""Isolated staged Godot benchmark. Do not print prompt/code/skill contents."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import re
import sys
from urllib.request import Request, urlopen

from sanitize_godot_feedback import validate_diagnostic, TASKS, ARMS

ROOT = Path(__file__).resolve().parents[1]
ENDPOINT = "http://af-model:8080/v1/chat/completions"
EXPECTED = "f038c76d78ed4ea2c33f1472c313881ebf27ab74f9c065440439f649a0800ee9"
PLAN = ("Extract the exact Godot 4.5 API contract: class base, signatures, "
        "initial state, success and rejection behavior. Respond with at most "
        "eight short checklist clauses, not code. Do not invent APIs.")
IMPLEMENT = ("Write one complete standalone Godot 4.5 GDScript file that "
             "starts with extends RefCounted, matches all requested methods, "
             "and handles invalid operations without mutation. Return code only.")
REPAIR = ("Correct a Godot 4.5 GDScript implementation against the exact public "
          "API and observed engine feedback. First address any reported compiler "
          "or runtime error category; then fix rejected behavioral assertions. "
          "Do not alter tests or the public API. Return only complete source.")
DOMAIN = {"equipment":"equipment", "forge":"forge", "abilities":"abilities"}

def card(text, category, name):
    if not re.fullmatch("[a-z]+", name):
        raise ValueError("invalid stage card identifier")
    start = "<!-- AF_" + category + ":" + name + ":start -->"
    end = "<!-- AF_" + category + ":" + name + ":end -->"
    if text.count(start) != 1 or text.count(end) != 1:
        raise ValueError("invalid confidential card delimiters")
    a, b = text.index(start) + len(start), text.index(end)
    if b <= a:
        raise ValueError("bad card order")
    snippet = text[a:b].strip()
    if not (15 <= len(snippet.split()) <= 190):
        raise ValueError("card length limit")
    return snippet

def skill(mode, path):
    if mode == "baseline":
        return ""
    if mode != "paired" or not path:
        raise ValueError("paired stage requires encrypted skill")
    text = Path(path).read_text(encoding="utf-8")
    if hashlib.sha256(text.encode()).hexdigest() != EXPECTED:
        raise ValueError("staged private skill SHA-256 mismatch")
    for x in ["contract","code","repair"]:
        card(text, "STAGE", x)
    for x in DOMAIN.values():
        card(text, "DOMAIN", x)
    return text

def extract(raw):
    if not isinstance(raw, str):
        return ""
    raw = raw.strip()
    fence = chr(96) * 3
    if raw.startswith(fence):
        if "\n" not in raw:
            return ""
        raw = raw.split("\n",1)[1].split(fence,1)[0].strip()
    if not raw.startswith("extends RefCounted") or "\x00" in raw:
        return ""
    if len(raw.encode("utf-8")) > 45000:
        return ""
    return raw + "\n"

def call(system, prompt, budget, timeout):
    if os.getenv("AGENTFOUNDRY_ISOLATED_DOCKER") != "af-staged-private":
        raise ValueError("no-egress container required")
    body=json.dumps({"model":"qwen-coder-1.5b",
                     "messages":[{"role":"system","content":system},
                                 {"role":"user","content":prompt}],
                     "temperature":0,"max_tokens":budget,"stream":False}).encode()
    req=Request(ENDPOINT,data=body,headers={"Content-Type":"application/json"},method="POST")
    with urlopen(req,timeout=timeout) as reply:
        return json.load(reply)["choices"][0]["message"]["content"]

def safe_call(system,prompt,budget,timeout):
    try:
        return call(system,prompt,budget,timeout),""
    except (OSError,ValueError,KeyError,IndexError,TypeError):
        return "","inference_error"

def tasks():
    data=json.loads((ROOT/"benchmarks/godot-code/tasks.json").read_text())
    if [x["id"] for x in data]!=["equipment","forge","abilities"]:
        raise ValueError("unexpected task set")
    return data

def plan_order(items,mode,seed):
    arms=("baseline","skill") if mode=="paired" else ("baseline",)
    plan=[(t,arm) for t in items for arm in arms]
    random.Random(seed).shuffle(plan)
    return plan

def overlay(text,stage,domain,arm):
    if arm=="baseline":
        return ""
    return "\n"+card(text,"STAGE",stage)+"\n"+card(text,"DOMAIN",domain)

def load_diagnostics(path, mode):
    """Read only typed allowlisted diagnostics, never free-form engine text."""
    if not path:
        return {}
    raw = Path(path).read_bytes()
    if len(raw) > 12000:
        raise ValueError("diagnostic payload exceeded size cap")
    payload = json.loads(raw)
    if type(payload) is not dict or set(payload) != {"mode", "diagnostic_schema", "cases"}:
        raise ValueError("bad diagnostic envelope")
    if payload["mode"] != mode or type(payload["diagnostic_schema"]) is not int or payload["diagnostic_schema"] != 1:
        raise ValueError("invalid diagnostic protocol")
    rows = payload["cases"]
    if type(rows) is not list:
        raise ValueError("invalid diagnostic cases")
    expected = {(t, a) for t in TASKS for a in (ARMS if mode == "paired" else ("baseline",))}
    if len(rows) != len(expected):
        raise ValueError("incorrect diagnostic count")
    clean = {}
    for row in rows:
        if type(row) is not dict or set(row) != {"task", "condition", "diagnostic"}:
            raise ValueError("untrusted diagnostic row")
        key = (row["task"], row["condition"])
        if key not in expected or key in clean:
            raise ValueError("unexpected or duplicate diagnostic case")
        clean[key] = validate_diagnostic(row["diagnostic"])
    return clean


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--phase",choices=["prepare","repair"],required=True)
    p.add_argument("--mode",choices=["baseline","paired"],required=True)
    p.add_argument("--skill-file")
    p.add_argument("--output",required=True)
    p.add_argument("--feedback")
    p.add_argument("--diagnostics", help="Private closed-schema compiler diagnostics from the same engine pass")
    p.add_argument("--seed",type=int,default=20261105)
    p.add_argument("--timeout",type=int,default=240)
    a=p.parse_args()
    if os.getenv("AGENTFOUNDRY_ISOLATED_DOCKER")!="af-staged-private":
        raise ValueError("isolation missing")
    private=skill(a.mode,a.skill_file)
    root=Path(a.output)
    items=tasks()
    if a.phase=="prepare":
        if root.exists() and any(root.iterdir()):
            raise ValueError("output must start empty")
        root.mkdir(parents=True,exist_ok=True)
        report={"mode":a.mode,"model_label":"qwen-coder-1.5b",
                "seed":a.seed,"temperature":0,"max_tokens":1700,
                "skill_sha256":hashlib.sha256(private.encode()).hexdigest() if private else None,
                "protocol":"contract_then_code","attempts":[]}
        for t,arm in plan_order(items,a.mode,a.seed):
            dest=root/t["id"]/arm
            dest.mkdir(parents=True)
            ptext,perr=safe_call(PLAN+overlay(private,"contract",DOMAIN[t["id"]],arm),
                                 t["brief"],220,a.timeout)
            # Bound model's plan size; never upload plans or raw responses.
            prompt=t["brief"]+"\nCompact contract notes:\n"+ptext[:950]
            raw,err=safe_call(IMPLEMENT+overlay(private,"code",DOMAIN[t["id"]],arm),
                              prompt,1700,a.timeout)
            code=extract(raw)
            if code:
                (dest/"generated.gd").write_text(code)
            status="generated" if code else (err or "invalid_source")
            report["attempts"].append({
                "task":t["id"],"condition":arm,"generation_status":status,
                "plan_status":perr or "planned",
                "source_sha256":hashlib.sha256(code.encode()).hexdigest() if code else None,
                "raw_response_sha256":hashlib.sha256(raw.encode()).hexdigest(),
                "phase":"before_repair",
            })
            print("STAGED_GENERATED",t["id"],arm,status,flush=True)
        (root/"generation.json").write_text(json.dumps(report,indent=2)+"\n")
    else:
        if not a.feedback:
            raise ValueError("feedback required for repair")
        report=json.loads((root/"generation.json").read_text())
        feedback=json.loads(Path(a.feedback).read_text())
        if feedback["mode"]!=a.mode or report["mode"]!=a.mode:
            raise ValueError("condition mismatch")
        rows={(x["task"],x["condition"]):x for x in feedback["cases"]}
        diagnostics=load_diagnostics(a.diagnostics,a.mode)
        for t,arm in plan_order(items,a.mode,a.seed):
            dest=root/t["id"]/arm
            source=dest/"generated.gd"
            prior=source.read_text() if source.exists() else ""
            result=rows[t["id"],arm]
            if result["passed"]==result["total"] and result["engine_exit_zero"]:
                print("STAGED_REPAIR",t["id"],arm,"ALREADY_PASS",flush=True)
                continue
            summary={"failed_assertion_ids":result["failed_checks"][:12],
                     "engine_exited_cleanly":bool(result["engine_exit_zero"]),
                     "all_assertions_reported":bool(result["all_checks_reported"])}
            if diagnostics:
                summary["compiler_diagnostic"]=diagnostics[(t["id"],arm)]
            prompt=t["brief"]+"\nAttempted code:\n"+prior[:16000]+\
                   "\nEngine test feedback:\n"+json.dumps(summary)+\
                   "\nReturn complete revised source."
            raw,err=safe_call(REPAIR+overlay(private,"repair",DOMAIN[t["id"]],arm),
                              prompt,1700,a.timeout)
            code=extract(raw)
            if source.exists():
                source.unlink()
            if code:
                source.write_text(code)
            status="generated" if code else (err or "invalid_repair")
            meta=next(v for v in report["attempts"]
                      if v["task"]==t["id"] and v["condition"]==arm)
            meta.update({"generation_status":status,
                         "source_sha256":hashlib.sha256(code.encode()).hexdigest() if code else None,
                         "raw_response_sha256":hashlib.sha256(raw.encode()).hexdigest(),
                         "phase":"after_repair","repair_attempted":True})
            print("STAGED_REPAIR",t["id"],arm,status,flush=True)
        report["protocol"]="contract_then_code_then_one_repair_with_typed_diagnostics" if diagnostics else "contract_then_code_then_one_repair"
        (root/"generation.json").write_text(json.dumps(report,indent=2)+"\n")

if __name__=="__main__":
    try:
        main()
    except (ValueError,OSError,KeyError,TypeError) as e:
        # Never print exception message: a network exception could echo a prompt.
        print("STAGED_ERROR",type(e).__name__,file=sys.stderr)
        raise SystemExit(1)
