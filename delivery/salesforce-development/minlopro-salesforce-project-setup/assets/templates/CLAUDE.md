# Acme Delivery — Project Memory

## What this is
Salesforce build, managed by epic. Source-tracked, deployed via SF CLI,
source control on GitHub. (Note any vendor/managed package in play here.)

## Orgs (prod deploys are GATED — require explicit human approval + preconditions)
- Default / build target: `acme-sandbox` (test.salesforce.com)
- UAT: `acme-uat`
- Production (deploy-only, gated): `acme-prod`
Always run `sf org list` and confirm the default before any deploy.

A `PreToolUse` hook (`.claude/hooks/block-prod-deploy.sh`) gates prod deploys/deletes.
It no longer hard-blocks: on a real prod promote it DENIES if the release
preconditions are missing (an explicit `--manifest`/`--metadata`, a deployment doc,
and a completed rollback strategy in docs/deployment/deployment-strategy.md), and
otherwise forces an explicit human approval prompt before the deploy runs. Always
promote an explicit manifest; validate with `--dry-run` first. (Fail-closed: without
`jq` the hook degrades to a hard block. It does NOT cover anonymous Apex or MCP tool
calls, so keep the default org a sandbox.)

## Operating rules
- Work one epic at a time, on its branch: epic/0X-<name>. NEVER commit to main;
  main only moves via reviewed PRs (branch protection enforces this).
- Every metadata component you add/change/delete MUST be logged in
  docs/deployment/metadata-component-log.md in the same change.
- Commit per logical unit; reference the epic ID in the commit message.
- Never edit force-app and leave a plan stale — plans and code change together.
- Never write tokens, auth URLs, or credentials into the repo. Secrets live in
  org Named Credentials. .sf/ and .sfdx/ stay ignored.
- Use the installed sf-skills (Apex, Flow, LWC, SOQL, objects/fields) when
  generating metadata — don't hand-roll what a skill covers.

## Living documents (keep these current)
@docs/design/_master-design.md
@docs/deployment/deployment-strategy.md
@docs/deployment/metadata-component-log.md
@docs/testing/test-plan.md

## Conventions
- Apex test coverage target: 90%+ on touched classes (75% required to deploy).
- Every new/modified LWC ships with Jest tests; Code Analyzer stays clean.
- Naming: <ClientPrefix>_<Epic prefix>_<Object/Feature>__...
- Definition of done per epic: code built, component log updated, PR reviewed &
  merged, smoke green, regression suite re-run, UAT signed off (for release),
  design doc reconciled.

## Key contacts (fill in roles)
- Delivery lead / prod approver: <name>
- UAT owner (client): <name>
