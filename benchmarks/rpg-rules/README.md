# RPG rules pilot — external-model A/B test

This benchmark measures whether an AI model follows **13 deterministic RPG state-transition rules**. It is a diagnostic for skill usefulness, not a claim about Godot implementation quality.

## Conditions

- Baseline: a neutral Godot RPG engineer system prompt.
- Treatment: the same prompt plus the private Godot RPG Systems Architect `SKILL.md`.

Each trial independently submits the same scenario, initial state, action and response schema. The exact answer is *not* included in the prompt. Conditions are randomly interleaved using a saved seed. Each output is scored on exact allow/deny decision and all resulting state values, not partial credit.

## Run without paid inference

GitHub Actions: **Actions → Rules pilot (real local inference) → Run workflow**, then select:
- `baseline` to check the actual open-source model and hosted runner without disclosing a skill.
- `auto` to choose paired only when the private skill secret is already configured, otherwise collect baseline diagnostics.
- `paired` only after adding repository secret `AGENTFOUNDRY_SKILL_B64`, which must hold the base64-encoded UTF-8 skill text (entire standalone SKILL.md).

The workflow downloads public weights before reading secrets, then uses a pinned CPU `llama.cpp` image on an outbound-network-isolated internal Docker bridge, with a localhost-only API and the public **Qwen2.5-Coder-1.5B-Instruct-GGUF Q4_K_M** model. It uses *no inference API key* or paid external service. The private skill remains on the ephemeral runner, not mounted in Docker. See [SECURITY.md](../../SECURITY.md). GitHub-hosted standard runners for public repositories are subject to GitHub's current policies and limits. This small model may fail many complex cases and is not representative of Claude or a production coding agent.

The main-branch `benchmarks/rpg-rules/run-now.txt` trigger performs a three-repetition `auto` run, regardless of whether you have configured the secret.

Never put the commercial skill contents into public repository files, an Actions input, step logs or a public issue. The workflow checks that the secret is present before a paired run. Artifacts contain scores, model-output hashes, case IDs and timings **only**; private prompts and raw model outputs are excluded.

To create the base64 value on a trusted machine:

```sh
python3 -c "import base64,pathlib; print(base64.b64encode(pathlib.Path('SKILL.md').read_bytes()).decode('ascii'))"
```

Paste that single value into GitHub repository **Settings → Secrets and variables → Actions → New repository secret**, name `AGENTFOUNDRY_SKILL_B64`. Do not share the value in chat or source code. Avoid running untrusted pull-request code alongside this secret.

## Local pilot

```sh
python3 -m unittest discover -s tests -v
python3 tools/run_rules_pilot.py --endpoint http://127.0.0.1:8080/v1/chat/completions \
  --model qwen-coder-1.5b --mode baseline --output results-local
# Paired mode: add --mode paired --skill-file /private/path/SKILL.md
```

Run a fresh output directory each time. `results.json` records all arms, the randomized seed, model label and SHA-256 skill digest. A transport failure invalidates the entire comparison. Output hash is not a substitute for privately retained raw transcripts.

## Limitations and next stage

**Public case disclosure:** the answer keys are in this public repository. A remote coding agent with access to the repo could look them up. The actual API inference calls do not supply expected answers; however, this is a pilot, not a secure held-out benchmark.

**No direct code quality measurement:** our future E1/E2/E3 Godot implementation benchmark needs two fresh, equally provisioned coding agents, identical patch briefs, independent GUT tests, engine import, blind review and Android inspection where appropriate. Do not equate a positive pilot delta with a successful marketplace skill.

**Decision gate:** require several model seeds/repetitions, per-case inspection, and at least one independent code-editing study before advertising measurable performance improvements.
