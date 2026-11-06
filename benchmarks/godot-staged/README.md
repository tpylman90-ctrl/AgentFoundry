# Staged Godot code pilot (experimental)

This runs the **same three public RPG coding tasks** as the original Godot 4.5.2 pilot, but changes the protocol from a single large prompt to a sequence of smaller model requests.

1. **Contract extraction:** 220 completion tokens for a compact public-API checklist, no code.
2. **Implementation:** 1,700 completion tokens to output a complete standalone GDScript file.
3. **Engine feedback:** headless Godot 4.5.2 executes the original independent assertions in a no-network container. The evaluator records failures privately and creates a score-only result.
4. **One repair attempt:** a separate model call gets the task contract, its current code, and only *sanitized failing assertion IDs and status*. It has an equal 1,700-token cap in baseline and treatment.
5. **Re-execute and score:** the corrected code runs the same tests; report both before and after scores.

The paired treatment uses compact task-relevant cards extracted from the **private** v0.3.1 SKILL.md. The baseline receives the same phase structure, tasks, token budgets, model version and engine feedback without those commercial instructions. This isolates instruction content **within this staged protocol**. It does not support a clean direct percentage comparison against the old *one-shot* pilot, which had fewer inference calls and a smaller output budget.

## Privacy, security and free tooling

Commercial package bytes are **not committed** here. The staged candidate is loaded only from `AGENTFOUNDRY_SKILL_V031_B64` in encrypted GitHub Actions repository secrets, with the candidate SHA-256 checked before paired inference. Its SHA-256 is `f038c76d78ed4ea2c33f1472c313881ebf27ab74f9c065440439f649a0800ee9`.

The model and isolated evaluator use a private Docker `--internal` network without published ports; the Godot engine is separately executed with `--network none`. No paid model API. The runner saves generated scripts and raw Godot logs only in temporary working files and deletes them during cleanup. Only **aggregate test results, assertion IDs, code hashes, and revision hashes** may appear in public artifacts.

The Godot self-test uses known-correct reference implementations, and must pass all 26 independent checks before any private skill is loaded. A broken reference gate invalidates the benchmark.

## Run instructions

- The public launcher `benchmarks/godot-staged/launch.txt` starts a **baseline-only** smoke test by default; no private secret is required.
- For a full paired test, add the new `AGENTFOUNDRY_SKILL_V031_B64` Actions secret (do not overwrite the older v0.2/v0.3 secrets), and choose **Actions → Godot staged code pilot (real engine) → Run workflow → paired**.
- You can alternatively update `benchmarks/godot-staged/run-paired.txt` with a commit message containing the exact marker `[AF-V031-TRIAL]`. The workflow will **fail closed** if the secret is missing or has a different digest, rather than silently running a baseline.
- The output artifact has **before** and **after repair** score files; generated code and commercial prompt content are excluded.

## Diagnostic-guided repair extension

The separate [diagnostic experiment](DIAGNOSTIC_EXPERIMENT.md) added closed-schema Godot parser/runtime categories and optional bounded generated-file line numbers to the repair input, without altering the v0.3.1 skill package. Its first paired run completed successfully: **4/26 baseline before and after repair; 3/26 v0.3.1 before, 4/26 after repair**. This is a successful *integration test*, but **not** a measured final accuracy uplift over baseline.

The original staged workflow and earlier result remain unchanged for reproducibility.

## Interpretation

This is a narrow diagnostic on Qwen2.5-Coder-1.5B Q4_K_M, not proof of commercial coding-agent capability or autonomous multi-file Godot engineering. Holdout tasks, stronger free models and more runs are necessary. The v0.3.0 one-shot regression remains recorded separately, and the experimental v0.3.1 package is **not promoted** without empirical improvement.

See [the original coding results](../godot-code/RESULTS.md), [revision comparison](../V03_RESULTS.md), and [security safeguards](../../SECURITY.md).
