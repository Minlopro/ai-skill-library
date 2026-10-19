---
name: minlopro-salesforce-project-setup
description: >-
  Set up a complete agentic Salesforce delivery project from scratch in Claude Code:
  install the toolchain (auto-detecting admin vs no-admin machines), authenticate the
  Salesforce orgs and GitHub, scaffold an SFDX repo with the standard CLAUDE.md memory
  system, a production-deploy guardrail hook, and living planning docs, then hand off
  to the per-epic delivery loop. Use this skill whenever the user wants to start,
  bootstrap, scaffold, stand up, or initialize a new Salesforce project, client
  implementation, or delivery environment — including phrasing like "new Salesforce
  project", "set up a delivery repo", "scaffold an SFDX project", or kicking off a
  new Agentforce / Service Cloud / Data Cloud engagement — even if they don't say
  "skill" or name every component. Runs in Claude Code (terminal or Antigravity).
---

# Minlopro Salesforce Project Setup

This skill stands up a ready-to-use agentic Salesforce delivery project in the current
folder: toolchain, authenticated orgs, a source-tracked SFDX repo with the standard
memory and guardrail wiring, and the per-epic delivery loop. It is the delegated path —
the human has already installed and authenticated Claude Code; you (the agent) do the
rest, pausing only when a step genuinely needs their password, `sudo`, or a browser
OAuth/MFA consent screen. Plan on ~15 minutes of light human babysitting on the first run.

`acme` is the placeholder project slug throughout the bundled templates. Ask the user for
their slug and substitute it everywhere `acme` / `Acme` appears (angle-bracket tokens like
`<name>` and `<ClientPrefix>` are intentional and stay).

## Guardrails — read first, never bypass

These are load-bearing. They are enforced in the repo (a hook and branch protection), but
you must also honor them directly:

- **The default org must always be a sandbox.** Run `sf org list` and confirm the default
  before any deploy.
- **Production deploys are gated, not hard-blocked.** The `PreToolUse` hook lets a prod
  deploy/delete proceed only after (a) the release preconditions are in place — an explicit
  `--manifest`/`--metadata`, a deployment doc, and a completed rollback strategy in
  `docs/deployment/deployment-strategy.md` — and (b) a human explicitly approves the prompt
  the hook raises. If any precondition is missing the hook denies and tells you what to add;
  `--dry-run` and non-prod deploys pass through. Validate with `--dry-run` first, and never
  route a prod deploy around the hook (e.g. anonymous Apex or an MCP call) to dodge the
  approval. (Fail-closed: without `jq` the hook degrades to the original hard block.)
- **Never commit to `main`.** Work on `epic/0X-<name>` branches; `main` moves only via
  reviewed PRs.
- **Never write tokens, auth URLs, or credentials into the repo.** They live in org Named
  Credentials. Keep `.sf/` and `.sfdx/` gitignored.
- **On no-admin machines, never use `sudo` and never write to `/usr/local`.** Home-directory
  installs only.
- **Pause for the human** whenever a step needs their macOS password, `sudo`, or a browser
  login/consent. Tell them exactly what to do and wait for confirmation before continuing.
- **Do not create the GitHub repo or commit until the human approves the staged diff.**

## Before you start

Confirm Claude Code is running and authenticated (it is, if you're reading this). Then ask
the user for:
1. **Project slug** (e.g. `acme`) — replaces `acme` in every template.
2. **Org path** — client work (`sandbox` → `uat` → `prod`) or a demo Developer/Dev Hub org.
3. **git `user.name` and `user.email`** (needed in Phase 1).

Work Phases 1–4 in order. Print a one-line status after each phase.

## Phase 1 — Toolchain (install only what's missing)

Check each tool with `command -v` before installing. Detect the machine's capability and
branch accordingly — **read `references/toolchain-install.md`** for the exact command
sequences for both the Admin/Homebrew branch and the no-admin fallback, plus the common
steps (plugins, `sf-skills`, GitHub auth, org logins, Chrome remote debugging).

Summary of what Phase 1 ends with, regardless of branch:
- Node 20+, GitHub CLI (authenticated, `gh auth setup-git`, git identity set), Salesforce
  CLI with the `sfdx-git-delta` and `code-analyzer` plugins, and the `sf-skills` agent skills.
- **`jq`** — required by the prod-deploy guardrail hook and NOT preinstalled on macOS. The
  hook falls back to scanning its raw payload if `jq` is absent (so it still fails closed),
  but install `jq` so the precise parse path is used.
- Orgs authenticated: `acme-sandbox` (default), `acme-uat`, `acme-prod` (NOT default) — or a
  demo org. Confirm with `sf org list`.
- Chrome remote debugging enabled by the user (one-click consent, dedicated test profile).

Pause at every browser/MFA/password step.

## Phase 2 — Scaffold the project (no pauses needed)

Substitute the slug for `acme`/`Acme` as you write each templated file.

1. `sf project generate --name acme-delivery --default-package-dir force-app`; arrange so
   `force-app/`, `manifest/`, `config/`, `sfdx-project.json`, and `.gitignore` sit at the repo root.
2. **Harden `.gitignore`**: ensure it covers `.sf/`, `.sfdx/`, `.env`, `*.key`, and auth-URL files.
3. Create directories: `docs/intake/`, `docs/design/`, `docs/deployment/`,
   `docs/testing/smoke-runs/`, `.claude/commands/`, `.claude/hooks/`.
4. Copy `assets/delivery-guide.md` → `docs/intake/delivery-guide.md` (the per-epic workflow).
5. Install the Salesforce agent skills if not already done: `npx skills add forcedotcom/sf-skills`.
6. Write the templated files from `assets/templates/` (substituting the slug):
   - `CLAUDE.md` → repo root
   - `block-prod-deploy.sh` → `.claude/hooks/` then `chmod +x` it
   - `settings.json` → `.claude/settings.json`
   - `close-epic.md` → `.claude/commands/close-epic.md`
   - `mcp.json` → `.mcp.json` (repo root)
7. Create the skeleton planning docs from `assets/skeletons/` (substitute the slug):
   `docs/intake/source-docs.md`, `docs/design/_master-design.md`,
   `docs/deployment/deployment-strategy.md`, `docs/deployment/metadata-component-log.md`,
   `docs/testing/test-plan.md`, `docs/testing/regression-suite.md`.
8. Set up LWC testing: `npm init -y`, `npm install --save-dev @salesforce/sfdx-lwc-jest`,
   add script `"test:unit": "sfdx-lwc-jest"`.
9. Generate the manifest: `sf project generate manifest --source-dir force-app --name package.xml`
   into `manifest/`.

Resulting structure:

```
acme-delivery/
├── CLAUDE.md                 # root memory — read every session
├── .mcp.json                 # chrome-devtools MCP
├── sfdx-project.json
├── force-app/                # Salesforce metadata (source format)
├── manifest/package.xml
├── .claude/
│   ├── settings.json         # registers the PreToolUse hook
│   ├── hooks/block-prod-deploy.sh
│   └── commands/close-epic.md
└── docs/
    ├── intake/{delivery-guide.md, source-docs.md}
    ├── design/_master-design.md
    ├── deployment/{deployment-strategy.md, metadata-component-log.md}
    └── testing/{test-plan.md, regression-suite.md, smoke-runs/}
```

## Phase 3 — Source control (needs the human's approvals)

1. `git init -b main`, stage everything, then **show the human the staged diff and a short
   summary and WAIT for their OK.**
2. After approval: commit (`"Scaffold delivery repo + Claude memory"`), then
   `gh repo create acme-delivery --private --source=. --remote=origin --push`.
3. Enable branch protection on `main` (require a PR review) via `gh api`.

No CI is wired. Tests are run locally before the PR is opened, per `docs/testing/test-plan.md`.

## Phase 4 — Verify ready-to-use, then report

1. `sf org list` — confirm the default is the sandbox; flag it if not.
2. **Prove the gate works**: attempt a bare `sf project deploy start --target-org acme-prod`
   (no manifest, fresh deployment doc) and confirm the hook DENIES it, listing the missing
   preconditions (manifest + completed rollback). This denial is expected and good — report
   it as a pass. Note for the user: once the manifest is supplied and the rollback strategy
   in `deployment-strategy.md` is filled in, that same command instead raises an approval
   prompt rather than deploying silently.
3. Remind the user to restart Claude Code so `.mcp.json` and `.claude/settings.json` load, then
   (next session) verify the browser tools with `list_pages`.
4. Print a final checklist: everything created, anything skipped, and open items for the human
   (fill in the **Key contacts** in `CLAUDE.md` — delivery lead / prod approver, UAT owner).

## After setup — the per-epic loop

The project is ready; run delivery per epic. The loop is captured in
`docs/intake/delivery-guide.md`, and `/close-epic 0X` runs the closeout end to end:

```
/clear → pick next epic from _master-design.md → branch epic/0X-<name>
       → build in sandbox (SF CLI + sf-skills) → tests (Apex + Jest + analyzer) + smoke
       → /close-epic 0X (reconciles docs, opens the PR) → human reviews & merges
       → release: UAT sign-off → regression → sgd delta → --dry-run vs prod → human approves the gated promote → tag
```

## Bundled files

- `references/toolchain-install.md` — Phase 1 install commands for both the admin and
  no-admin branches, plus the common auth/plugin/org steps. Read it during Phase 1.
- `assets/templates/` — verbatim files written into the repo (slug-substituted): `CLAUDE.md`,
  `block-prod-deploy.sh`, `settings.json`, `close-epic.md`, `mcp.json`.
- `assets/skeletons/` — starter planning docs (headers + TODO bodies).
- `assets/delivery-guide.md` — the per-epic workflow, copied into `docs/intake/`.
