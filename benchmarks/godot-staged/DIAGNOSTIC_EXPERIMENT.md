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


## Completed first diagnostic A/B result — 2026-11-06 UTC

**Status:** GitHub Actions completed successfully. [Run 42267940387](https://github.com/tpylman90-ctrl/AgentFoundry/actions/runs/42267940387), commit `6c493f0895c23f9f9e911856f1a5066a456ba892`. Score-only artifact: `agentfoundry-staged-godot-42267940387`.

The benchmark reference implementations passed all 26 engine checks. The workflow reported `Staged skill fingerprint: verified`, `Staged evaluation mode: paired`, and `AF_SANITIZER_OK paired 6`; the sanitized diagnostics were mounted read-only into the private repair container. All six repair calls completed, all code was retested, and the public artifact uploaded successfully.

| Task | Baseline initial | v0.3.1 initial | Baseline after one repair | v0.3.1 after one repair |
|---|---:|---:|---:|---:|
| Equipment | 4/9 | 3/9 | 4/9 | 4/9 |
| Crafting | 0/8 | 0/8 | 0/8 | 0/8 |
| Abilities | 0/9 | 0/9 | 0/9 | 0/9 |
| **Total** | **4/26** | **3/26** | **4/26** | **4/26** |

**Observed repair effect:** baseline **+0** assertions, v0.3.1 **+1** assertion. **Observed final treatment effect:** **0/26**, a tie. A one-assertion recovery in this tiny pilot is not evidence that the diagnostic mechanism generally increases success: the earlier, no-diagnostic trial had v0.3.1 at 4/26 both before and after repair, and prompt/runner-level variability is possible.

**Decision:** Keep v0.3.1 experimental. The sanitizer's closed-schema plumbing is validated, but neither treatment produced a working crafting or abilities script. Do not claim commercial coding effectiveness or promote the revision.

**Next investigation:** Capture only aggregate allowlisted error-category counts (no raw logs or source snippets), separately verify that the Godot parser errors are being identified rather than all classified as generic `engine_failure`, and test a more capable **free** coding model or truly smaller implementation steps. Preserve the held-out suite for future changes.
