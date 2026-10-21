---
name: minlopro-devhub-setup
description: Set up Minlopro's production org (alias minlopro-prod) as your Salesforce CLI Dev Hub so you can create scratch orgs, check your access and the firm's shared scratch-org limits, and keep the guardrails that come with logging the CLI in to Minlopro production. Use when someone asks to set up the Dev Hub, connect minlopro-prod, create or get scratch orgs, fix "no Dev Hub" or scratch org errors, or onboard to scratch-org work at Minlopro, even if they don't name the skill.
---

# Minlopro Dev Hub setup (minlopro-prod)

Minlopro creates scratch orgs from its **production org's Dev Hub**. This skill connects your Salesforce CLI to it, checks that you can create scratch orgs, and sets the guardrails.

**Read this first.** `minlopro-prod` is Minlopro production: the same org as Proto, with real client and project data. Logging the CLI in gives your terminal (and any AI agent running in it) API access as you. The org is a **Dev Hub only**: you create scratch orgs *from* it, and you never deploy to it, load data into it, run Apex in it, or query client data from it through the CLI.

## What you need

- Salesforce CLI (`sf`) installed: `sf --version` shows 2.x. Install from https://developer.salesforce.com/tools/salesforcecli if not.
- A Minlopro production login with permission to create scratch orgs ("Create and Delete Scratch Orgs" plus access to Active Scratch Org and Scratch Org Info). System Administrators already have it. If you aren't one and step 3 fails, ask a Proto admin in #ai-leaders to grant it. An admin can grant it with a permission set that has that system permission and those two objects (Read, Create, Edit, Delete).

## Steps

1. **Get the login domain, then log in as a Dev Hub only.** Ask the user for Minlopro's production login domain: the My Domain URL they use to sign in to Minlopro production (Proto), in the form `https://<domain>.my.salesforce.com`. Don't guess it, and don't write it into files or commits. If they don't know it, they can copy it from the browser address bar while logged in to Proto, or ask in #ai-leaders. Then:

   ```sh
   sf org login web --alias minlopro-prod --instance-url https://<domain>.my.salesforce.com --set-default-dev-hub
   ```

   Use `--set-default-dev-hub` and **never** `--set-default` (that makes production the default target for deploys and data commands).

2. **Run the check script.** It is read-only:

   ```sh
   sh <this skill's folder>/scripts/check-devhub.sh minlopro-prod https://<domain>.my.salesforce.com
   ```

   It confirms the CLI is logged in to that domain, that `minlopro-prod` is a Dev Hub and your default Dev Hub, that it is **not** your default target org, and prints the firm's remaining scratch-org capacity.

3. **Create a scratch org** from your project (it needs `config/project-scratch-def.json`; a starter is in `templates/project-scratch-def.json`):

   ```sh
   sf org create scratch --definition-file config/project-scratch-def.json --alias my-feature --duration-days 7 --target-dev-hub minlopro-prod --wait 20
   ```

   Point commands at the scratch org with `--target-org my-feature`, or `sf config set target-org my-feature` inside the project folder.

4. **Delete it when you're done:** `sf org delete scratch --target-org my-feature --no-prompt`. Scratch orgs also expire on their own after `--duration-days`.

## Rules (firm policy)

- **minlopro-prod is never a target.** Only ever pass it as `--target-dev-hub`. Never use it with `--target-org` for deploy, retrieve, data, apex, or query commands. If a command or an AI agent proposes that, stop.
- **Shared limits.** The whole firm shares one quota of active scratch orgs and new orgs a day (the check script shows what's left). Keep `--duration-days` short (7 is plenty for most work), delete orgs you're finished with, and don't create orgs in loops.
- **Synthetic data only.** Never load client data, real client records, or PHI into a scratch org. Use made-up records (names like "Test Patient 01", IDs like "R-1001").
- **Keep the login private.** Don't paste output of `sf org display --verbose` or any "auth URL" anywhere: it contains a token that logs in as you to Minlopro production. Don't commit `.sf/` or `.sfdx/` folders.
- **AI agents.** If you run Claude Code or another agent, tell it minlopro-prod is a Dev Hub only. HELM enforces this in policy and refuses both Dev Hubs and Proto as targets.
- **Leaving or rotating.** To remove the login: `sf org logout --target-org minlopro-prod --no-prompt`.

## Troubleshooting

| You see | Do this |
|---|---|
| `No default dev hub found` or `NoDefaultDevHubError` | Rerun step 1 with `--set-default-dev-hub`, or pass `--target-dev-hub minlopro-prod` |
| `You do not have the required permissions` or `INSUFFICIENT_ACCESS` when creating | You lack the scratch-org permission: ask a Proto admin (see "What you need") |
| `The request to create a scratch org failed... LIMIT_EXCEEDED` | The firm hit its active or daily limit. Delete your old orgs (`sf org list --clean` removes expired ones from your list) and try later |
| `expired access/refresh token` or `RefreshTokenAuthError` | Log in again with step 1 |
| A feature you need (for example Contacts to Multiple Accounts, Person Accounts) is missing in the org | Add it to the scratch definition's `features` or `settings` **before** creating the org; some settings only take effect at creation |
| The check script says minlopro-prod is your default target org | Run `sf config unset target-org --global` and set the target in each project instead |

## When you're helping someone else run this

Walk them through steps 1 to 3 in order, run the check script and read its output with them, and stop at any FAIL line. Never run deploy, data, or apex commands against minlopro-prod, and never ask them to paste tokens or auth URLs.
