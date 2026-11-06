# Controlled private skill revision trials

**No commercial SKILL.md content is stored in this public repository.** The original `AGENTFOUNDRY_SKILL_B64` secret remains the v0.2 treatment. The v0.3 treatment must use a distinct secret, `AGENTFOUNDRY_SKILL_V03_B64`, containing base64-encoded UTF-8 bytes of the current v0.3 SKILL.md. Base64 is not encryption; only store the value in GitHub Actions encrypted repository secrets, not a file or workflow input.

## Revisions and provenance

| Revision | Source location | Status |
|---|---|---|
| v0.2 | Existing encrypted Actions secret | Previously measured: rules 27/39; Godot code 4/26 |
| v0.3 | Encrypted Actions secret, exact candidate digest verified | Rules pilot completed: 18/39 vs 21/39 baseline; Godot coding evaluation pending |

v0.3 SHA-256 of `SKILL.md`: `36dc36213804a1b06f82c5f9c20267b0216ecaf228a8344903bbaacd597e760f`. The private skill text itself is not in Git.

## Running controlled comparisons

Both **Rules pilot** and **Godot code pilot** workflows now support the optional `skill_revision` input. For each task family, use `paired` mode, one v0.2 run and one v0.3 run, with the same model, seed, task briefs, tools, decoding settings and acceptance tests. The baseline control is rerun in each paired run. The runner logs the *selected revision label* and public manifest retains the skill SHA-256 digest; it must match the expected revision before a score is trusted.

For a future assistant-initiated v0.3 launch via a safe public commit, update the appropriate launcher file and use the commit marker `[AF-V03-TRIAL]`:
- `benchmarks/rpg-rules/v03-run-now.txt`
- `benchmarks/godot-code/v03-run-now.txt`

Do **not** create these trigger files until the new Actions secret is installed. A missing v0.3 secret in `paired` mode must fail; it must **never silently fall back** to the v0.2 secret. In `auto` mode with no selected secret, the workflow runs baseline only.

## Measurement guardrails

Observed previous pilot effects (+15.4 points in two different *small* experiments) describe v0.2 only. They are not a validated v0.3 improvement. The public case sets are already disclosed; add new tasks and a fair bounded repair loop before any marketplace claims. Never call repeated temperature-zero samples independent tasks. Keep generated source, private skill instructions, raw model output and confidential host-game code off public CI artifacts.

See [coding results](godot-code/RESULTS.md), [rules results](rpg-rules/RESULTS.md) and [security controls](../SECURITY.md).

## First verified v0.3 rules trial (2026-11-06 UTC)

Run: https://github.com/tpylman90-ctrl/AgentFoundry/actions/runs/42147661242

The runner printed the selected **v0.3** revision and successfully validated the candidate SHA-256 before inference. The completed, isolated model benchmark scored **21/39 (53.8%) baseline** against **18/39 (46.2%) with v0.3**, a **-7.7 percentage-point** treatment-minus-baseline difference. This is a regression on the original 13 disclosed rules scenarios. Gains: C01 (two-handed incompatibility). Losses: C02 (legal weapon change) and C11 (insufficient crafting materials rejection). All three deterministic repetitions produced the same pattern for each case.

For perspective, the latest v0.2 revision smoke run [42145156239](https://github.com/tpylman90-ctrl/AgentFoundry/actions/runs/42145156239) scored 21/39 baseline versus 24/39 with v0.2 (+7.7 points). An earlier run scored 27/39 with v0.2; that variance reinforces the need for more seeds and independent tasks. **Do not promote v0.3 as a demonstrated performance improvement.** The Godot coding assessment is a separate benchmark and should be reported separately.
