# Acme — Per-Epic Delivery Guide

The setup produced this repo. From here you run the per-epic loop. Each step writes
to a living document; later steps and future sessions read those documents back.

## The loop at a glance
/clear  ->  pick next epic from docs/design/_master-design.md build sequence
        ->  branch: git checkout -b epic/0X-<name>
        ->  build in sandbox with SF CLI + sf-skills
        ->  tests: Apex + LWC Jest + code-analyzer, then the smoke path
        ->  /close-epic 0X   (reconciles docs, commits to the epic branch, opens a PR)
        ->  human reviews & merges the PR
        ->  at a release boundary: UAT sign-off -> full regression -> sgd delta
            -> --dry-run vs prod -> a HUMAN promotes -> tag the release

## Step 1 — Documentation intake
Drop raw inputs into docs/intake/, then parse them into docs/intake/source-docs.md,
organized by epic: business objective, in-scope objects/automation, integrations,
assumptions, open questions, acceptance criteria. Flag contradictions; list gaps as
open questions. Do not invent scope.

## Step 2 — Technical design (per epic + master roll-up)
One design doc per epic at docs/design/epic-0X-<name>.md, plus the master roll-up at
docs/design/_master-design.md reconciling cross-epic dependencies and build order.

Per-epic design doc template:

    # Epic 0X — <Name>
    ## Objective & acceptance criteria   (pulled from intake)
    ## Solution design
    - Data model: objects, fields, relationships (new vs. modified)
    - Automation: flows, Apex triggers/classes, validation rules
    - UI: Lightning pages, LWCs, record pages, managed-package components touched
    - Integrations: external systems, named credentials, platform events
    - Security: profiles, perm sets, sharing
    ## Metadata components (this epic)
    | Type | API Name | New/Mod/Del | Notes |
    ## Dependencies    (Depends on / Blocks)
    ## Risks / open questions
    ## Test conditions (Smoke: ... ; Regression impact: ...)

## Step 3 — Build, log, test
- Build in sandbox with the SF CLI; use the installed sf-skills for Apex/Flow/LWC/SOQL.
- Log EVERY metadata component in docs/deployment/metadata-component-log.md in the
  same change. Rebuild the manifest from source when needed.
- Run Apex tests + LWC Jest + code-analyzer; then the Chrome DevTools smoke path,
  saving screenshots to docs/testing/smoke-runs/.

## Step 4 — Close the epic
Run /close-epic 0X. It reconciles the design doc, updates the component log, grows the
regression suite, updates epic status, commits to the epic branch, and opens a PR.
It does NOT merge — a human reviews and merges.

## Step 5 — Release
UAT sign-off -> re-run the full regression suite -> build the sgd delta ->
--dry-run validate vs acme-prod -> a HUMAN runs the promote -> tag the release.
Production deploys are human-only; the PreToolUse hook blocks the agent.
