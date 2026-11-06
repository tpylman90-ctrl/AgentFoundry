# v0.3 comparison — preliminary

Evaluated on 2026-11-06 UTC using identical Qwen2.5-Coder-1.5B-Instruct Q4_K_M conditions and existing public tests. GitHub Actions verified the expected v0.3 SHA-256 before inference; commercial source stayed outside Git.

| Test | Baseline | v0.3 | Earlier v0.2 |
|---|---:|---:|---:|
| RPG rules (39 checks across 13 cases) | 21/39 | 18/39 | 24/39 in latest regression smoke |
| Godot code (26 engine checks across 3 tasks) | 0/26 | 0/26 | 4/26 in earlier completed pilot |

Rules run: https://github.com/tpylman90-ctrl/AgentFoundry/actions/runs/42147661242
Godot run: https://github.com/tpylman90-ctrl/AgentFoundry/actions/runs/42147762050
Reference Godot tests: all 26/26 passed during the Godot run.

These are small, public, one-model diagnostics. Repeated temperature-zero cases are not independent new tasks. Results do not establish cross-model generalization.

**Decision: do not promote v0.3.** It regressed on RPG rule accuracy and did not improve Godot execution in this trial. Continue using v0.2 as the previous tested candidate while investigating shorter, task-relevant instructions and a fair feedback-and-repair loop. No marketplace release.
