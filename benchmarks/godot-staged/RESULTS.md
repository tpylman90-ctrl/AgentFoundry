# First completed staged Godot baseline (no private skill)

**Date:** November 6, 2026 UTC.  
**Workflow:** [GitHub Actions run 42242242194](https://github.com/tpylman90-ctrl/AgentFoundry/actions/runs/42242242194)  
**Commit:** `c1b6f4dcf59643178f9e9cbbc1a46677a1cd170d`  
**Artifact:** `agentfoundry-staged-godot-42242242194`  
**Result:** GitHub workflow completed **successfully**; model inference, engine testing, scoring, bounded repair, re-testing, artifact upload, and cleanup all passed.

The workflow selected **baseline**, so **no private commercial skill was used**. The run used Qwen2.5-Coder-1.5B Q4_K_M, contract extraction (220 completion tokens), full code generation (1700 completion tokens), a real Godot 4.5.2 engine test, and at most one repair call (1700 completion tokens) based on sanitized failure labels.

| Task | Before repair | After repair |
|---|---:|---:|
| Equipment | 4/9 | 4/9 |
| Crafting | 0/8 | 0/8 |
| Battle abilities | 0/9 | 0/9 |
| **Total** | **4/26** | **4/26** |

The reference implementations passed 26/26 in the same engine before inference. Model output was not corrected by the evaluator, and raw scripts, private skill text and raw engine logs were not published. Results and safe source hashes were uploaded as public scoring artifacts.

**Interpretation:** This verifies the staged infrastructure, not the v0.3.1 skill. The repair attempt did not improve the baseline on these three tasks. Earlier one-shot results used a different output budget and fewer calls, so comparing their percentages directly would confound instructions with evaluation protocol.

**Next gate:** Configure the separate encrypted `AGENTFOUNDRY_SKILL_V031_B64` secret and run `paired` with exactly the same tasks, budgets and repair allowance. The expected SKILL.md SHA-256 is `f038c76d78ed4ea2c33f1472c313881ebf27ab74f9c065440439f649a0800ee9`. No private source file belongs in Git.

**Release decision:** Staged v0.3.1 remains private and experimental; no measured performance improvement has yet been established.
