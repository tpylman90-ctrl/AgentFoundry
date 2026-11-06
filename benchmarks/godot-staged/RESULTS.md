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


## First verified paired v0.3.1 staged pilot — no observed uplift

**Date:** November 6, 2026 UTC.  
**Workflow:** https://github.com/tpylman90-ctrl/AgentFoundry/actions/runs/42259382783  
**Commit:** `2ac83e9dfc89a1946a388af0593f609aebb342b1`.  
**Public scoring artifact:** `agentfoundry-staged-godot-42259382783`.

The workflow explicitly selected **paired** mode and validated the configured v0.3.1 private skill's exact SHA-256. The three known-correct reference implementations passed 26/26 checks **before** any private model inference. All six code-generation attempts and six bounded repair calls completed; Godot executed the generated code with network access disabled.

| Task | Baseline, before | v0.3.1, before | Baseline, after repair | v0.3.1, after repair |
|---|---:|---:|---:|---:|
| Equipment | 4/9 | 4/9 | 4/9 | 4/9 |
| Crafting | 0/8 | 0/8 | 0/8 | 0/8 |
| Battle abilities | 0/9 | 0/9 | 0/9 | 0/9 |
| **Total** | **4/26** | **4/26** | **4/26** | **4/26** |

The observed treatment-minus-baseline difference was **0/26 (+0.0 percentage points)** before and after repair. One equipment implementation per condition ran and completed the test sequence while passing 4 of its 9 assertions; crafting and abilities did not complete successfully. The repair attempt did not change this result in either condition.

**Interpretation and decision:** This confirms that staged instruction delivery is technically operational, **not** that v0.3.1 improves coding. With only three public tasks and one attempt per task/condition, the result is inconclusive about effectiveness in other settings. Keep the staged candidate experimental; do not replace the previously retained v0.2 candidate or claim marketplace readiness.

**Next controlled experiment:** Give *both* conditions a fixed-size, scrubbed **first compiler/error diagnostic** (e.g. Godot parser error category and safe file-local line number, without source excerpts, private prompts, or raw engine logs). The current repair message contains failing assertion IDs plus engine exit status but no explanatory error for scripts that fail to load, meaning the repair instruction can be detailed yet blind to the actual syntax error. Hold task suite, model, token budgets, private-skill handling and repair allowance constant. Validate that the scrubber cannot emit generated source or commercial instruction text before enabling any public artifact logging. A stronger free open-weights coding model and held-out tasks would then be appropriate.

**Privacy:** The commercial skill and generated scripts were not committed to Git and raw Godot logs were not uploaded. The public artifact contains only numerical scores and safe hashes.
