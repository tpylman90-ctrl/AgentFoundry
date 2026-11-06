# Godot 4.5.2 GDScript code-generation pilot — first verified result

**Benchmark type:** independent single-shot code generation plus real-engine behavioral tests, **not** full autonomous coding-agent patch development.  
**Date:** 2026-11-06 UTC (November 5, Eastern US).  
**Model:** Qwen2.5-Coder-1.5B-Instruct Q4_K_M via isolated localhost-only Docker model service.  
**Generation conditions:** same three public task briefs, token budget (1,100 tokens), temperature 0, reproducible randomized order; private `SKILL.md` supplied only to treatment.
**Evaluation:** Godot 4.5.2 headless, separate Docker containers with `--network none`, reduced privileges, bounded timeouts, independent engine assertions.  
**Scoring run:** https://github.com/tpylman90-ctrl/AgentFoundry/actions/runs/42141247988  
**Run ID:** `42141247988`; source commit `db629c697f8c0895c1ce1ca7f1c33cd4bf618e6d`.  
**Artifact:** `agentfoundry-godot-code-42141247988` (public scores only; raw code and model output not included).

## A/B outcome

| Task | Generic baseline | With private skill | Notes |
|---|---:|---:|---|
| Equipment compatibility | 0/9 | **4/9** | Treatment script loaded in Godot; 4 checks passed |
| Transactional forging | 0/8 | 0/8 | Neither produced working tested behavior |
| Battle abilities | 0/9 | 0/9 | Neither produced working tested behavior |
| **Total** | **0/26 (0%)** | **4/26 (15.4%)** | **+4 checks, +15.4 percentage points observed** |

This was **one generated implementation per task per condition**, not 26 independent trial runs. The observed difference is preliminary, with a high failure rate. A valid public commercial performance claim would require many independent prompts, held-out tests, stronger models and implementation review. The small coding model may not be strong enough for these Godot 4.5 APIs in a one-shot coding setting.

The preceding **rules-only** pilot was a separate experiment: `21/39` baseline versus `27/39` with skill on deterministic rules puzzles. Do not merge that score with this code-generation result or imply that +15.4 percentage points generalizes.

## Independent benchmark validity check

The reference suite at `benchmarks/godot-code/reference/` contains three explicitly correct baseline implementations authored to the public task contracts and run through the exact same test scripts and sandbox:
- Equipment: **9/9 passed**
- Forge: **8/8 passed**
- Abilities: **9/9 passed**
- **Reference total: 26/26 passed**

Verified GitHub Actions run: https://github.com/tpylman90-ctrl/AgentFoundry/actions/runs/42142018642 (workflow **Godot benchmark reference verification**). The engine reported an actual PASS line for all 26 assertions. This confirms the test harness can recognize valid implementations; it does not prove that all edge cases in production are covered.

## Confidentiality and cost

- The encrypted GitHub Actions secret was loaded into the ephemeral benchmark evaluator only. The private skill text is not in public Git history, generated scripts are not uploaded, and the raw engine logs are private ephemeral files removed at job cleanup.
- The model and evaluator communicate only inside a Docker `--internal` bridge. Generated GDScript is executed separately with `--network none`, read-only mounts, reduced Linux capabilities, memory and CPU limits.
- No paid inference APIs or private game repositories were involved. The workflow uses public standard GitHub-hosted runners and free/open-source software (subject to GitHub platform limits).

## What we can say

**Supported:** On this narrow model, these three coding tasks, and this fixed benchmark, the specialized skill improved the number of Godot engine assertions passed from zero to four, and the single treatment equipment script ran successfully enough to complete all nine checks (passing four).

**Not supported:** The skill makes Claude/Claude Code better; that the generated RPG systems are production-ready; that the percentage improvement will persist on different models, tasks or seeds; that this tests an autonomous coding agent with tools and feedback; or that code quality improved outside these assertions.

## Next engineering gates

1. Add a reference-suite preflight to all future Godot coding benchmark workflows.
2. Add a *bounded repair loop* that feeds model-safe compiler/test failure diagnostics to both conditions with identical iteration and token budgets, then rerun.
3. Evaluate with a stronger free open-source coding model on the same fixed tasks plus new held-out tasks.
4. Only after tests pass, perform more realistic multi-file Godot/GUT integration work, Android validation where appropriate, and eventual marketplace licensing review.

The earlier initial run https://github.com/tpylman90-ctrl/AgentFoundry/actions/runs/42139957503 used a soft timeout and stalled in script execution; the completed hard-timeout run above supersedes it for result claims.
