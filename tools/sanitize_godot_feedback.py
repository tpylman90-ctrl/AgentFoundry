#!/usr/bin/env python3
"""Declassify Godot errors to a tiny, fixed vocabulary for private repair.

Engine logs, generated scripts and skill text are UNTRUSTED. This module
never copies log substrings into the output. The public workflow must NOT
upload the input logs or the private diagnostics file.
"""
import argparse
import json
from pathlib import Path
import re

TASKS = ("equipment", "forge", "abilities")
ARMS = ("baseline", "skill")
CATEGORIES = frozenset({
    "no_source", "parse_indentation", "parse_type", "parse_token",
    "parse_other", "missing_method", "invalid_call",
    "invalid_access", "runtime_type", "script_load", "runtime_other",
    "resource_timeout", "engine_failure", "no_error"
})
METHODS = frozenset({
    "configure", "equip", "unequip", "snapshot", "craft", "inventory", "cast"
})
SOURCE_LINE = re.compile(r"res://generated\.gd:(\d{1,5})(?!\d)", re.I)
GDSCRIPT_RELOAD_LINE = re.compile(r"^\s*at:\s*GDScript::reload\s*\(res://generated\.gd:(\d{1,5})\)", re.I)
MISSING_METHOD = re.compile(
    r"(?:nonexistent|non-existent|unknown)\s+(?:function|method)\s+['\"]"
    r"(configure|equip|unequip|snapshot|craft|inventory|cast)['\"]", re.I
)
ERROR_LINE = re.compile(
    r"^\s*(?:SCRIPT ERROR:|ERROR:|E\s+\d+:\d+:\d+:)", re.I
)


def diagnostic(raw_log: str, exit_code: int) -> dict:
    """Produce only literals selected by code, never user-controlled strings."""
    if not isinstance(raw_log, str) or type(exit_code) is not int:
        raise ValueError("bad diagnostic input")
    text = raw_log[:65536]
    category = "no_error" if exit_code == 0 else "engine_failure"
    method = None
    line_number = None
    if exit_code in (124, 137):
        category = "resource_timeout"
    elif text.strip() == "source_not_generated":
        category = "no_source"
    else:
        # Do not look at unbounded logs; ignore raw stack traces and raw quotes.
        error_lines = [line[:900] for line in text.splitlines()[:250]
                       if ERROR_LINE.match(line)]
        if error_lines:
            first = error_lines[0]
            low = first.lower()
            if "parse error" in low:
                if "indent" in low or "tab" in low or "whitespace" in low:
                    category = "parse_indentation"
                elif any(word in low for word in ("type", "cast", "annotation")):
                    category = "parse_type"
                elif any(word in low for word in (
                        "expected", "unexpected", "token", "identifier",
                        "expression", "statement", "symbol")):
                    category = "parse_token"
                else:
                    category = "parse_other"
            elif "invalid call" in low or "nonexistent function" in low:
                found = MISSING_METHOD.search(first)
                if found:
                    category = "missing_method"
                    method = found.group(1).lower()
                else:
                    category = "invalid_call"
            elif "invalid get index" in low or "invalid access" in low:
                category = "invalid_access"
            elif any(word in low for word in ("type error", "invalid type", "type mismatch")):
                category = "runtime_type"
            elif "failed to load script" in low or "cannot load script" in low:
                category = "script_load"
            elif "error" in low:
                category = "runtime_other"
            loc = SOURCE_LINE.search(first)
            if not loc:
                for followup in error_lines[1:4]:
                    loc = SOURCE_LINE.search(followup)
                    if loc:
                        break
            if not loc:
                for trace in text.splitlines()[:250]:
                    loc = GDSCRIPT_RELOAD_LINE.search(trace)
                    if loc:
                        break
            if loc:
                candidate = int(loc.group(1))
                if 1 <= candidate <= 4000:
                    line_number = candidate
    # Closed schema: names/categories come only from code-defined allowlists.
    output = {"category": category, "line": line_number, "method": method}
    assert output["category"] in CATEGORIES
    assert output["method"] is None or output["method"] in METHODS
    return output


def validate_diagnostic(obj: dict) -> dict:
    """Treat diagnostics as hostile JSON when reading inside the model client."""
    if type(obj) is not dict or set(obj) != {"category", "line", "method"}:
        raise ValueError("unexpected diagnostic fields")
    category, line, method = obj["category"], obj["line"], obj["method"]
    if type(category) is not str or category not in CATEGORIES:
        raise ValueError("unknown category")
    if line is not None and (type(line) is not int or not 1 <= line <= 4000):
        raise ValueError("invalid source line")
    if method is not None and (type(method) is not str or method not in METHODS):
        raise ValueError("untrusted method name")
    return {"category": category, "line": line, "method": method}


def sanitize_run(mode: str, log_dir: Path) -> dict:
    if mode not in ("baseline", "paired"):
        raise ValueError("invalid mode")
    rows = []
    for task in TASKS:
        for arm in (ARMS if mode == "paired" else ("baseline",)):
            source = log_dir / task / arm
            raw = (source / "engine.log").read_text(
                encoding="utf-8", errors="replace"
            ) if (source / "engine.log").exists() else ""
            try:
                code = int((source / "exit.txt").read_text().strip())
            except (OSError, ValueError):
                code = -1
            rows.append({"task": task, "condition": arm,
                         "diagnostic": diagnostic(raw, code)})
    return {"mode": mode, "diagnostic_schema": 1, "cases": rows}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["baseline", "paired"], required=True)
    parser.add_argument("--logs", required=True)
    parser.add_argument("--output", required=True)
    opts = parser.parse_args()
    payload = sanitize_run(opts.mode, Path(opts.logs))
    output = Path(opts.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    # Deliberately no raw log contents or diagnostic details in stdout.
    print("AF_SANITIZER_OK", opts.mode, len(payload["cases"]))


if __name__ == "__main__":
    main()
