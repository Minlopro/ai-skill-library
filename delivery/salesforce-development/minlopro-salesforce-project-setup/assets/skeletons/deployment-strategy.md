# Acme Deployment Strategy

## Environments & promotion path
sandbox (build) -> UAT -> production
Aliases: acme-sandbox -> acme-uat -> acme-prod

## Deploy mechanics
- Build/validate in sandbox: sf project deploy start --target-org acme-sandbox
- Delta validate-only vs prod (no commit):
  sf project deploy start --dry-run --manifest delta/package/package.xml \
    --target-org acme-prod --test-level RunLocalTests
- Promote to prod (the prod-deploy hook gates this — see below). ALWAYS deploy an
  explicit manifest, never a blanket source-dir push:
  sf project deploy start --manifest delta/package/package.xml \
    --target-org acme-prod --test-level RunLocalTests

## Prod-deploy gate (how the hook behaves)
The .claude/hooks/block-prod-deploy.sh hook no longer hard-blocks prod deploys. On a
real prod deploy/delete it checks three preconditions and then:
- DENIES (with a message on what to add) if any of these are missing: (1) an explicit
  --manifest/--metadata on the command, (2) this deployment doc exists, (3) the
  Rollback strategy below is completed (no unfilled placeholders);
- otherwise returns "ask", which forces an explicit human approval prompt before the
  promote runs. --dry-run and non-prod deploys pass through untouched.
Fail-closed: without jq the hook degrades to a hard block. Default org must stay a
sandbox; anonymous Apex and MCP tool calls do not pass through this hook.

## Per-epic deploy gate (definition of "deployable")
- [ ] Component log updated
- [ ] Apex tests pass, coverage >= target; LWC Jest green; Code Analyzer clean
- [ ] Smoke test green in sandbox
- [ ] PR reviewed & merged to main
- [ ] Regression suite re-run, no new failures
- [ ] UAT signed off (for release)
- [ ] Delta manifest built and validated vs prod with --dry-run
- [ ] Rollback strategy below completed for this release
- [ ] Named human release owner approved the prod promote

## Rollback
Complete every item below before any prod promote — replace each placeholder with
real content. The hook treats an unfilled placeholder as "not done" and denies the
deploy until this section is finished.
- Rollback package: <fill: the reverse sfdx-git-delta between the prior release tag
  and this one — name the tags, e.g. from rel-2024.11 back to rel-2024.10>
- Destructive changes: <fill: path to manifest/destructiveChanges.xml for this
  release, and confirmation it was validated in sandbox>
- Pre-deploy snapshot: <fill: how the current prod state of the touched components
  was captured (retrieve into a tagged branch / backup) so it can be restored>
- Data considerations: <fill: any data migration/backfill that must be reversed, or
  "none">
- Verification after rollback: <fill: the smoke check that proves prod is back to a
  good state>

## Production deploy approval record (append one block per promote)
- Release tag: <fill>
- Manifest deployed: <fill: path>
- Approved by (named release owner): <fill>   Date/time: <fill>
- Dry-run result reviewed: <fill: link / summary>
- Post-deploy smoke result: <fill>
