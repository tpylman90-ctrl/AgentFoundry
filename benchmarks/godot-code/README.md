# Real Godot coding challenge (single-shot pilot)

This is a **different benchmark from the 13 RPG rules puzzles**. Qwen2.5-Coder-1.5B generates an original Godot 4.5 GDScript class for each of three neutral, non-proprietary task briefs. The generator submits each brief once with a generic system prompt (baseline), and once with the privately installed commercial skill added (paired treatment). The model and task budget remain constant and the request order is seeded and randomized.

Godot 4.5.2, downloaded from the official release and verified against the release digest, runs **actual scripts in a no-network Docker sandbox**. The test suite invokes methods with inputs, validates changes to equipment state, crafting inventory and abilities, and records pass/fail checks. It does not ask another LLM to rate code aesthetically.

## Confidentiality

Only the public task briefs, public engine tests, runtime scaffolding, score computation and workflow are in Git. All model-generated code, raw responses, and raw Godot logs stay on an ephemeral GitHub runner and are deleted after grading. The private skill is loaded through `AGENTFOUNDRY_SKILL_B64`; it is never published.

Inference uses two containers on an outbound-network-isolated Docker bridge. The model container has no access to the skill file. The generation client reads it and sends the skill to the model over the private bridge only. The separate Godot sandbox has no network and does not receive the skill. The Godot process runs generated code under reduced container privileges, with CPU, memory and process caps. These controls reduce risk, but neither GitHub-hosted runners nor containerization provide perfect protection against a malicious generated program.

**No paid API, no private repository source, no Shattered Realms code or game assets.** Do not place signing keys, passwords or personal data inside the skill.

## What this can and cannot establish

- **Measures:** whether an independently run coding model can generate Godot 4.5 GDScript matching an exact API and passing engine-executed behavioral checks.
- **Does not measure:** full autonomous file-editing agents, multi-file projects, Android performance, Claude Code specifically, or long-term improvement.
- This public test set is a small diagnostic, not a secure held-out benchmark. There is one output per condition per task, so a difference is preliminary rather than a statistically established generalization.
- A model can return invalid code. Those tasks count as zero instead of being omitted.
- The generated code is **not** uploaded as a public Actions artifact because it might echo private instructions. Code hashes are included for reproducibility, but external auditors cannot inspect the raw responses.

## Verified first-run evidence

The first completed private paired coding trial is documented in [RESULTS.md](RESULTS.md): **0/26** assertions without the specialized skill versus **4/26** with it, entirely from the treatment equipment implementation. The known-correct reference scripts passed **26/26** in an independent real Godot run. The score is a small preliminary signal and does not show usable complete RPG features.

To protect against broken tests, subsequent coding pilots run the complete known-correct reference suite **before** the private skill is loaded. Any reference failure aborts the run.

## Running

From Actions, select **Godot code pilot → Run workflow**, choosing `auto` to use the private skill when present or `paired` to require it. Push changes to `benchmarks/godot-code/launch.txt` to invoke the 3-task paired auto workflow. The runner builds the engine sandbox and downloads weights **before** reading any private skill.

Review the resulting `agentfoundry-godot-code-<run-id>` artifact for aggregate and per-task scores. Code-generation responses remain private on the runner, not in the public ZIP.

[Repository security policy](../../SECURITY.md)
