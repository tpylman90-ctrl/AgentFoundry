# AgentFoundry

**AI-agent skills engineering, reproducible evaluations, and honest release gates.**

AgentFoundry is the experimental development home for reusable skills that help AI coding agents build software. The first candidate is **Godot RPG Systems Architect**, derived from general methods developed during RPG production.

## What this public repository contains

- `benchmarks/rpg-rules/` — a small exact-state RPG rules-reasoning benchmark (equipment, skills, crafting and loot).
- `tools/run_rules_pilot.py` — independent-model endpoint runner, with fresh conversations and randomized condition order.
- `.github/workflows/checks.yml` — offline validation tests.
- `.github/workflows/rules-pilot.yml` — opt-in local-model runner on a GitHub-hosted CPU.

**This repository does not publish the commercial skill, Shattered Realms source, game art, signing keys, or private agent prompts.** Store skill text in a GitHub Actions secret named `AGENTFOUNDRY_SKILL_B64` for a private skill-vs-baseline evaluation. The benchmark strips the skill text from exported evidence.

## Reproducible first evaluation

Two conditions get the same model, input, decoding budget, scoring and new conversation per question:

1. **Baseline:** generic engineering instructions only.
2. **With skill:** identical instructions plus the privately supplied skill text.

The pilot's exact-state results **do not** measure autonomous Godot code editing or Claude Code performance. In particular, a small local model is an inexpensive diagnostic, not a substitute for a strong coding-agent assessment. Public test questions can also be contaminated through training or retrieval, so benchmark conclusions must be limited.

Run the no-cost local check with `python3 -m unittest discover -s tests -v`.
Use `Actions → Rules pilot → Run workflow` to request hosted inference; see [pilot setup](benchmarks/rpg-rules/README.md) first. The workflow never calls a paid inference API.

## Product gates

- [x] Independent repository established.
- [x] Public benchmark tooling separated from commercial skill content.
- [ ] Independent same-model baseline/skill pair executed and transcripts audited.
- [ ] Larger Godot coding-agent patch trial completed with GUT/engine validation.
- [ ] Android verification where relevant.
- [ ] Marketplace rights and license reviewed; product approval requested before publishing.

**Status convention:** PASS means an executed check with retained evidence; PLANNED means unrun. No synthetic or mock test is an independent model benchmark.

Repository source distribution terms have not yet been selected. Do not assume that publicly readable means freely relicensable.
