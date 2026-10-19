Close out epic $ARGUMENTS:
1. Confirm you're on the epic/$ARGUMENTS-* branch; if not, stop and say so.
2. Reconcile the design doc matching docs/design/epic-$ARGUMENTS-*.md
   (glob match on the epic number) against what was actually built.
3. Update docs/deployment/metadata-component-log.md for every changed component.
4. Run automated Apex tests, LWC Jest tests, and the code analyzer; if coverage
   < target or new high-severity findings, stop and report.
5. Run the epic's smoke path via chrome-devtools; save screenshots.
6. Add the epic's critical paths to docs/testing/regression-suite.md.
7. Update the epic status in docs/design/_master-design.md.
8. Commit to the epic branch referencing the epic; show me the diff.
9. After my OK: push the branch and open a PR with gh pr create
   (title "Epic $ARGUMENTS: <name>", body = design-doc summary + component list).
   Do NOT merge — a human reviews and merges.
