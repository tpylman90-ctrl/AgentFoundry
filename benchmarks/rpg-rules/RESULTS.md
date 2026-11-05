# RPG rules benchmark — first real model baseline

**Date:** 2026-11-05 (UTC)  
**Model:** Qwen2.5-Coder-1.5B-Instruct-GGUF, Q4_K_M, served locally with llama.cpp on an Ubuntu GitHub-hosted CPU.  
**Run:** https://github.com/tpylman90-ctrl/AgentFoundry/actions/runs/42127527184  
**Run ID:** 42127527184  
**Commit:** `30c1aff7ce71d7299dfde01f8a00bbca84cdab97`  
**Seed:** 20261105  
**Temperature:** 0  
**Repetitions:** 1  
**Status:** Verified independent model baseline. NO paired skill comparison yet.

| Condition | Exact-state passes | Accuracy |
|---|---:|---:|
| Without specialized skill | 7 / 13 | 53.8% |
| With specialized skill | Not run | Not established |
| Improvement | Not measured | Not established |

Results by case, as logged in the actual inference step:

| Case | Topic | Baseline |
|---|---|---|
| C01 | Two-handed weapon/shield incompatibility | FAIL |
| C02 | Legal one-handed weapon change | PASS |
| C03 | Two-handed spear with free offhand | FAIL |
| C04 | Unowned item rejected | PASS |
| C05 | Legal shield equip | PASS |
| C06 | Insufficient MP rejection | FAIL |
| C07 | Resource cost and HP cap | FAIL |
| C08 | Invalid heal on knocked-out target | PASS |
| C09 | Full-health potion rejection | FAIL |
| C10 | Successful atomic crafting | PASS |
| C11 | Insufficient crafting materials | PASS |
| C12 | Duplicate one-time reward rejection | PASS |
| C13 | First-time reward claim | FAIL |

**Interpretation:** This demonstrates that the open-source model endpoint ran and the independent baseline was graded. It does **not** demonstrate any skill advantage. A small rules-reasoning puzzle set is also not a substitute for Godot project code edits, unit tests, visual tests or a commercial product evaluation.

**Next gate:** Add the candidate skill's `SKILL.md` to GitHub Actions secret `AGENTFOUNDRY_SKILL_B64` (base64-encoded UTF-8). Trigger **Actions → Rules pilot (real local inference) → Run workflow → paired**. Audit paired outputs and repeat with seeds and Godot coding tasks before making marketplace performance claims.

Note that public benchmark cases are visible in this repository. They are not a secure held-out dataset, and the model label is supplied by the inference endpoint rather than cryptographically attested. The completed GitHub Actions log and seven-day results artifact contain primary scoring evidence.


## Repeated baseline — real model, three passes

**Run:** https://github.com/tpylman90-ctrl/AgentFoundry/actions/runs/42130943045  
**Run ID:** 42130943045  
**Commit:** `714cb14b89cf581f44fde1a2bf40ee527071ef8f`  
**Repetitions:** 3, each scenario independently asked three times.

| Condition | Correct decisions and exact states | Accuracy |
|---|---:|---:|
| Baseline without skill | 21 / 39 | 53.8% |
| Candidate skill | Not run — GitHub secret absent | Not measured |

The logged scorer reported the same seven case successes and six failures in each of the three repetitions. This is an observed deterministic response pattern on this runner with temperature 0, **not** proof that the same score will hold on other prompts, model versions or random seeds.

The workflow's auto mode explicitly selected `baseline`, confirming that `AGENTFOUNDRY_SKILL_B64` was not configured in this run. No private candidate content was passed to the model.

The private-skill comparison is not complete. Treat a with/without delta as **unknown**, not zero or positive, until a genuine paired job succeeds.

Security-hardening follow-up is documented in [SECURITY.md](../../SECURITY.md). Later runs will use a network-isolated container, pinned GitHub Actions revisions, and a pinned image digest; the two baseline runs above used the initial non-isolated local container. Both were **baseline only** and did not include private skill text.
