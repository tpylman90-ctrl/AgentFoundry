# Diagnostic-guided staged Godot coding experiment

**Status:** paired evaluation launched; do not infer improvement before reading the completed score artifact.

## Motivation

The prior staged v0.3.1 trial scored **4/26** Godot assertions for both baseline and private-skill conditions, unchanged after one repair. Both conditions received failed assertion IDs and a boolean engine-exit status, but no useful compiler diagnostic. In particular, a script that fails during parsing gives the model no clue whether its issue is syntax, typing, a missing method or a resource timeout.

## Fixed paired experiment

- **Control:** original compact contract → complete GDScript → Godot tests → one repair → retest; no private skill.
- **Treatment:** exact same phases, tasks, open model, generation temperature, completion token caps and engine tests, with v0.3.1 task-specific confidential cards as the *only additional guidance*.
- **Common change:** both arms now receive *identical schema* of typed compiler feedback derived from their **own** Godot logs during repair.
- **Model:** free Qwen2.5-Coder-1.5B-Instruct Q4_K_M, served by pinned llama.cpp inside an outbound-network-isolated Docker network.
- **Runtime:** Godot 4.5.2 stable in a separate `--network none` sandbox; reference implementations must pass all **26/26** checks before any private skill is loaded.
- **Scoring:** report engine assertions per arm **before** and **after** the single bounded repair call. No per-arm manual intervention or selective retries.

## Strict diagnostic declassification

The file `tools/sanitize_godot_feedback.py` reads raw Godot error logs locally and exports only:
- a category chosen from a **closed, code-defined allowlist**, such as `parse_token`, `parse_type`, `parse_indentation`, `missing_method`, `invalid_call`, `script_load`, `resource_timeout`, or `engine_failure`;
- an optional positive line number (at most 4000), referring only to the generated script;
- an optional method name chosen from the public benchmark's fixed known API, e.g. `equip` or `craft`.

The diagnostic JSON **never includes free-form error messages, source lines, raw model output, secrets, or stack traces**. All received diagnostic fields are validated a second time inside the isolated model client. Malformed or extra JSON fields fail closed.

The diagnostic feedback JSON remains **private to the ephemeral runner**, and **is not an Actions artifact**. Only the score-only reports and source-content hashes are uploaded. The production candidate `SKILL.md` stays in the GitHub Actions secret and is never committed.

## Interpretation

This is a three-task public pilot, so even a positive result is only preliminary. More repetitions with varied tasks and a stronger free coding model would be needed before a commercial claim. A zero delta is not proof of equivalence, and a result from a repaired-script pipeline must not be compared numerically to a single-shot result without noting the protocol difference.

## Execution record

Workflow: `.github/workflows/godot-staged-diagnostics.yml`.

Initial paired run: https://github.com/tpylman90-ctrl/AgentFoundry/actions/runs/42267940387

Earlier staged pair (no compiler-category feedback): https://github.com/tpylman90-ctrl/AgentFoundry/actions/runs/42259382783

Private-staged-skill SHA-256 remains unchanged from the earlier v0.3.1 evaluation; the candidate package was **not revised** for this diagnostic experiment.
