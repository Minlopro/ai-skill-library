---
name: coe-mlp-project-bootstrap
description: Bootstrap a new Minlopro client project from a Proto project name or link — creates the GitHub repo from the firm project template, fills README/CLAUDE.md from Proto, sets up branches, org auth, and optional prod/dev metadata baselines. TRIGGER when the user asks to set up, scaffold, bootstrap, or kick off a project repo, hands over a Proto project link/name for setup, or asks to "create the boilerplate" for an engagement. DO NOT TRIGGER for feature work inside an existing project repo, or for Proto reporting/timecards.
---

# Minlopro Project Bootstrap

Turn a Proto project (name or lightning link) into a ready-to-work repo: created from the firm template, documented, branched, org-authorized, and optionally baselined with prod/dev metadata.

**Input:** a Proto project name or lightning URL.

**Prime directive: search first → present findings as options → ask ONE question. Confirm every decision gate with the user BEFORE acting. Never assume, never invent, never argue from memory — re-run the enumerating command instead.**

## Step 0 — Prerequisites

Check and report all of these before anything else; stop and tell the user what's missing:

- `git --version`, `node --version`, `npm --version`
- `gh --version` and `gh auth status` (needs `repo` scope + Minlopro org access)
- `sf --version`
- Template access: `gh repo view Minlopro/MLP-project-template --json name,defaultBranchRef,isPrivate` (repo is private — unauthenticated access fails)
- Proto access via the Salesforce MCP connector (read-only suffices until the write-back step)
- Git identity: `git config user.name` / `user.email` — must be the human's Minlopro identity

## Step 1 — Pull project facts from Proto

- From a link, take the record Id directly. From a name, search Proto projects by name — if more than one match, present Id + account + status and have the user pick. Never guess the record.
- Query the Proto project record for: account/client, project manager and partner, account exec, primary customer contact, stage/status/type, products, start and estimated completion dates, estimated hours, SOW link, objectives, methodology, and the customer production org ID.
- Query the project's resource records for the team. **Gotcha:** the role field is often blank — the role is usually embedded in the record's Name as `LastName | Role`; parse it from there.
- Expect gaps (no Technical Strategist role, no SOW link, blank dates). Mark them TBD and ask the user — never invent names, hours, dates, or links.

## Step 2 — Duplicate-asset pre-flight (MANDATORY)

**Repo:** search BEFORE asking:
- `gh search repos --owner Minlopro "<client>"` and `"<project keyword>"` (index can lag), AND
- `gh api /orgs/Minlopro/repos --paginate --jq '.[].name' | grep -iE "<client>|<keywords>"` (authoritative; paginated so it survives org growth).
- Grep for the CLIENT name, not just the project — a broader client repo may already contain this work.

Then ONE question with findings as options: matches → "use existing <x>" per candidate / "create new anyway" / "other — here's a link"; no matches → "create new (nothing found)" / "there's one you can't see — link" / "park as open item".

**If an existing repo is chosen → AUDIT mode, not create mode.** Clone it and check what's already done before doing anything: branches present? README/CLAUDE.md filled or placeholders? template fixes applied? source dir populated? backup branch exists? org status documented? Report a done/missing checklist and confirm which gaps to fill. Never redo a completed step.

**Local folder:** check the target folder doesn't already exist. If it does, stop and ask — never overwrite.

## Step 3 — Decision gates (confirm ALL before creating anything)

1. Folder name (can match the Proto project name verbatim, spaces OK locally).
2. Repo name (no spaces on GitHub; confirm the current firm naming convention with the user — conventions have drifted between the rules doc and practice, so do not assume).
3. Technical Strategist if absent from Proto (offer: a team member / TBD / the user).
4. Git scope: local only vs create the GitHub repo now.
5. sf org aliases are personal per machine — docs may only SUGGEST aliases, never mandate.

## Step 4 — Create the repo (per the firm's GitHub rules)

Repos are created via GitHub's template feature — never a clone-copy or empty repo:

```bash
gh repo create Minlopro/<repo-name> --template Minlopro/MLP-project-template --private --include-all-branches
```

- `--include-all-branches` is REQUIRED: the template ships long-lived branches plus a `blank` branch (pristine-template reference), all at one commit. Without the flag only the default branch copies, silently.
- Template generation is async — retry the clone a few times with short sleeps.
- **Verify immediately after creation:** `gh repo view Minlopro/<repo> --json isPrivate,name` (must be private — fix instantly if not) and `gh api repos/Minlopro/<repo>/branches --jq '.[].name'` diffed against the template's branch list.
- Branch naming may differ between the firm rules doc and the template's actual branches — enumerate the template's branches, confirm with the user which naming wins, and make the repo docs match the choice.

## Step 5 — Fill placeholders + fix known template gaps

Placeholder files: `README.md`, `CLAUDE.md`, `sfdx-project.json` (name), `package.json` (name/description), scratch-org definition (orgName), and the feature `_TEMPLATE` manifest/README (example component names). Fill from Proto facts; keep TBDs visible. Record in README: client, project, TS/FS, team, Proto link, summary with cited numbers, org status, branch table with *suggested* aliases.

Template gaps to check for and fix in the new repo (flag upstream to the template owners if still present):
1. The default package directory may not exist in a fresh clone (git can't track empty dirs; sf commands fail) → add `<dir>/main/default/.gitkeep`.
2. The scratch-org definition's orgName may carry a leftover placeholder value → set it to the project name.
3. A `prepare`/husky setup without an actual `.husky/pre-commit` hook file → add one running `npx lint-staged`.
4. Prettier plugins for XML/Apex installed but undeclared (prettier v3 doesn't auto-load plugins) → add a `.prettierrc.json` declaring them, with lwc/html parser overrides.

Then `npm install` (registers husky hooks; must run after clone), and sweep for leftover placeholders with a case-insensitive grep before committing.

## Step 6 — Branches

All boilerplate commits land on the default branch first (Conventional Commits, under the human's identity). Then fast-forward the other long-lived branches to that commit so they share the starting point. The `blank` branch stays at the pristine-template commit FOREVER — never touch it. Push everything with `-u` (branches without upstream break later `git pull` chains silently). Leave the working copy on the integrated-development branch.

After this point: no direct commits to shared branches — even docs tweaks go via `feature/*` → merge. The promotion order defined in the repo's README is fixed; only the TS promotes to the production branch.

## Step 7 — Org authentication (no IDE needed)

Org auth is machine-global (`~/.sf` + keychain); the browser login is the only human step. Never use stored SFDX auth URLs for this (they're secrets).

1. Pre-flight: `sf org list` — show rows plausibly belonging to this client, then ONE question: "reuse alias <x>" per match / "log in fresh" / "my alias is named differently". Never create a second auth/alias for the same org.
2. Ask which orgs EXIST (prod/dev/qa/uat) — do not assume all four.
3. Login one org at a time, user completes in browser: prod → `--instance-url https://login.salesforce.com`, sandboxes → `https://test.salesforce.com`.
4. In the project folder: `sf config set target-org <dev-alias>` (project-local `.sf/config.json`, gitignored). Never default to prod.
5. Verify `sf org list`; the username suffix reveals the sandbox name — surface it to the user as a sanity check.
6. **Org-ID cross-check:** compare the prod org's ID (`sf org display --json`) against the customer production org ID recorded in Proto. Mismatch → STOP (possible wrong client's org). Proto blank → offer a confirmed write-back.
7. Record org status (which orgs exist, which sandbox is dev) in README + CLAUDE.md.

## Step 8 — Baselines (optional; ask the user)

Retrieves are read-only — safe for prod. **Prod is retrieve-only, EVER: never deploy/delete against a prod alias; hand the command to the TS instead.**

Confirm BOTH before retrieving: (a) backup branch name/cut point (no spaces; e.g. `prod-backup` from the default branch, outside the promotion flow, never merged); (b) scope vs `.forceignore` (the template excludes org-specific items — a FULL backup lifts them; comment them out ON that branch only, after checkout — the file reverts on branch switch).

Per org:
1. `sf project generate manifest --from-org <alias> --output-dir manifest --name <org>-full` — never use the repo's code-types-only manifest for a backup.
2. `sf project retrieve start --manifest manifest/<org>-full.xml --target-org <alias> --ignore-conflicts --wait 30` — run in background; takes minutes. Exit code 0 even with partial-retrieve warnings (permission-blocked layouts, private-folder documents, ConnectedApp load errors, ExperienceBundle API disabled, WorkflowFlowAutomation naming quirks) — record the gaps in the commit message.
3. Before pushing: `find <pkg-dir> -type f -size +40M` (GitHub hard limit 100MB).
4. Commit with `HUSKY=0 git commit --no-verify` (bulk-only exception; say so in the message). Prod snapshot → backup branch; dev baseline → `feature/*` merged into the integrated-development branch.
5. Record baseline state in README.

## Step 9 — Write-back to Proto

Offer (confirmed writes, never silent): store the GitHub repo URL on the Proto project record, and backfill the customer production org ID field if it was blank and the org is verified.

## Hard rules (each traces to a real mistake)

1. Never claim "X doesn't exist" without enumerating the source in the same step. If the user says they can see X, STOP and re-verify — never argue from memory.
2. After creating any asset, verify the result (`git branch -r`, `gh repo view`, `sf org list`) — don't trust the creating command's silence.
3. After template creation, diff the repo against the template (branches AND files).
4. Search first → findings as options → one question. Never make the user answer from memory what a command can enumerate.
5. Confirm decision gates BEFORE acting. Announcing a choice mid-action is not confirmation.
6. Before every retrieve/deploy, print the target alias + username + org ID and confirm it belongs to THIS client — other clients' orgs are one typo away.
7. `HUSKY=0`/`--no-verify` only for bulk baseline commits, stated in the message.
8. Branch-specific file edits only after `git branch --show-current` confirms the branch.
9. `&&` chains fail silently mid-chain — verify end state after any multi-step chain.
10. Hours, budgets, dates, scope come from Proto/SOW or are marked TBD. Cite sources.
11. No client specifics in reusable assets. No PHI anywhere, ever (firm rule, applies beyond this skill).
