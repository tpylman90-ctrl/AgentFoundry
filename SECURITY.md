# Security and confidentiality policy

AgentFoundry is public **test infrastructure**, not a public warehouse for commercial skills, personal prompts, game assets, user data, or credentials.

## Authorized boundaries

- Free/open-source execution only. Never configure billing, a paid API, third-party agent credits or paid services to run this benchmark.
- Do not publish the Godot RPG Systems Architect candidate or its supporting reference files to public Git, logs, issues, Actions artifacts, or pull requests.
- Do not modify the Shattered Realms, AssetWright, SceneForge, or Forge Core repositories from this project.
- Do not send private skill text to external inference endpoints. The Python runner rejects non-loopback model endpoints in `paired` mode.
- A GitHub Actions secret must be configured by a repository administrator through GitHub settings. **Base64 is encoding, not encryption**; never store its value in source control or public workflow inputs.

## Inference trust boundary

Before the commercial skill can be loaded, the Actions runner downloads *public* GGUF model weights and the public Python evaluator image. **The model and evaluator run as separate containers on one Docker `--internal` bridge network. No container ports are published to the host or public Internet.** Both containers lack normal outbound Internet routing, use read-only filesystems and have Linux capabilities dropped. The public model file is mounted read-only into the model container. The private skill file is held on the ephemeral runner host (mode 0600 via `umask 077`) and mounted read-only into the evaluator container **only**, never into the model's filesystem. The evaluator sends the private instructions to the model's `af-model:8080` service solely over the isolated Docker bridge. The Python runner has an explicit allowlist for this exact internal service in paired mode.

The workflow uses immutable git commit references for its GitHub Actions and a pinned container digest. Published artifacts retain only aggregate scores, case IDs, timings, and output SHA-256 digests; no raw prompts or generated responses. The workflow attempts to delete its ephemeral secret file during cleanup.

**Residual risks:** GitHub's hosted runner, GitHub's secret storage, and the official action/container supply chains remain trust dependencies. A container image or a model implementation could mishandle inputs. A model can intentionally regurgitate parts of supplied instructions; raw responses are therefore not publicly uploaded. Network isolation reduces outbound-exfiltration risk, but is not a formal proof against all side channels. Do not place passwords, API keys, personal secrets, signing keys, or unpublished Shattered Realms intellectual property into an agent skill at all.

## GitHub workflow usage

- `rules-pilot.yml` accepts `baseline`, `paired`, or `auto` from `workflow_dispatch`. The `run-now.txt` push path launches `auto`: choose paired only if `AGENTFOUNDRY_SKILL_B64` is present; otherwise baseline.
- A missing secret never triggers publication of sample skill contents.
- Do not run private-skill jobs on untrusted pull requests, forks, or branches. The benchmark workflow is restricted to main pushes on explicit launcher files or manual dispatch.
- Treat results artifacts in public repositories as **public even when URLs are obscure**. Do not include source code, prompts, raw model output, or personally identifying data.

## Verification gates

1. Automated unit tests pass.
2. Both containers start on the same no-egress network; private-network model health endpoint responds. A failure blocks inference.
3. Real model run completes with no transport errors and emits a signed-by-GitHub Actions run record.
4. Paired mode is used only when the private skill is available through GitHub Secrets, with both arms on the same model under identical settings.
5. No commercial claim of code-quality improvement without external agents making actual Godot code edits and passing engine tests.

When uncertain about confidentiality, default to **not running** rather than exposing private material.
