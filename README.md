# AgentFoundry

**AI-agent skills engineering, reproducible evaluations, and honest release gates.**

AgentFoundry is the experimental development home for reusable skills that help AI coding agents build software. The first candidate is **Godot RPG Systems Architect**, derived from general methods developed during RPG production.

## What this public repository contains

- `benchmarks/rpg-rules/` — a small exact-state RPG rules-reasoning benchmark (equipment, skills, crafting and loot).
- `benchmarks/godot-code/` — three independent coding briefs and actual Godot 4.5.2 engine-run behavior tests, in networkless sandboxes.
- `tools/run_rules_pilot.py` — independent-model endpoint runner, with fresh conversations and randomized condition order.
- `.github/workflows/checks.yml` — offline validation tests.
- `.github/workflows/godot-code-pilot.yml` — privacy-protected code-generation comparisons using a CPU model and real Godot execution.
- `.github/workflows/network-smoke.yml` — confidentiality-oriented Docker network verification.
- `.github/workflows/rules-pilot.yml` — opt-in local-model runner on a GitHub-hosted CPU.

**See [security policy](SECURITY.md) and [verified experimental results](benchmarks/rpg-rules/RESULTS.md).** A baseline test of the open-source Qwen coding model scored 7/13 and a second run scored 21/39 over three identical repetitions. A confidential paired *rules-reasoning* test scored 21/39 baseline versus 27/39 with the configured private skill (+15.4 percentage points). Separately, the **real-engine single-shot Godot coding pilot** scored 0/26 baseline versus 4/26 with the private skill, while known-correct reference implementations passed 26/26. Both are small model-specific diagnostics, not proof of a production-ready skill. The public case set is a rules diagnostic, not a coding-agent patch benchmark.

**This repository does not publish the commercial skill, Shattered Realms source, game art, signing keys, or private agent prompts.** Store skill text in a GitHub Actions secret named `AGENTFOUNDRY_SKILL_B64` for a private skill-vs-baseline evaluation. The benchmark strips the skill text from exported evidence.

## Reproducible first evaluation

Two conditions get the same model, input, decoding budget, scoring and new conversation per question:

1. **Baseline:** generic engineering instructions only.
2. **With skill:** identical instructions plus the privately supplied skill text.

The pilot's exact-state results **do not** measure autonomous Godot code editing or Claude Code performance. In particular, a small local model is an inexpensive diagnostic, not a substitute for a strong coding-agent assessment. Public test questions can also be contaminated through training or retrieval, so benchmark conclusions must be limited.

Run the no-cost local check with `python3 -m unittest discover -s tests -v`.
Use `Actions → Rules pilot (real local inference) → Run workflow` with baseline, paired or auto to request hosted inference; see [pilot setup](benchmarks/rpg-rules/README.md) first. The workflow never calls a paid inference API.

## Private revision testing

The v0.3 instruction package is retained outside public Git history. Our two independent test workflows now accept a private version selector (`v0.2` or `v0.3`) and separate encrypted Actions secrets. See [the revision comparison protocol](benchmarks/REVISION_COMPARISON.md) for installation, SHA-256 evidence and honest reporting. **No v0.3 independent performance gain has yet been measured.**

**v0.3 test result:** The precision-sweep candidate did **not** improve the first rules or Godot coding trials. It remains experimental and is not promoted. See [v0.3 evaluation](benchmarks/V03_RESULTS.md) for verified scores and limitations.

## Product gates

- [x] Independent repository established.
- [x] Public benchmark tooling separated from commercial skill content.
- [x] Real baseline model inference verified; 7/13 then 21/39 on repeat.
- [x] Independent same-model baseline/skill paired rules test executed, with privacy-safe score evidence (+15.4 percentage points, 13 unique scenarios).
- [ ] Independently review private raw responses and verify skill version against the recorded digest.
- [x] Initial single-file Godot 4.5.2 code-generation benchmark completed: 0/26 baseline, 4/26 with skill; reference validation 26/26. See [coding results](benchmarks/godot-code/RESULTS.md).
- [ ] Broader agentic tool-use and iterative code repair evaluation on fresh tasks.
- [ ] Larger autonomous coding-agent patch trial completed with GUT/engine validation.
- [ ] Android verification where relevant.
- [ ] Marketplace rights and license reviewed; product approval requested before publishing.

**Status convention:** PASS means an executed check with retained evidence; PLANNED means unrun. No synthetic or mock test is an independent model benchmark.

Repository source distribution terms have not yet been selected. Do not assume that publicly readable means freely relicensable.
