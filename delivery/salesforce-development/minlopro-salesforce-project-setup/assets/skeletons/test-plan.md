# Acme Test Plan

## 1. Automated testing (every build / pre-deploy, and before every PR)
- Apex unit tests: sf apex run test --target-org acme-sandbox --code-coverage \
    --result-format human --wait 10
- LWC Jest: npm run test:unit
- Static analysis: sf code-analyzer run --workspace ./force-app --view detail
- Coverage gate: 90%+ on touched classes (75% hard floor to deploy)
- Run locally before opening the PR; paste the results into the PR description

## 2. Smoke testing (per epic, fast happy-path)
- Driven by the Chrome DevTools MCP against the sandbox UI
- Per epic: log in, exercise the primary flow end-to-end, assert key records/UI
- Output: pass/fail + screenshots saved to docs/testing/smoke-runs/

## 3. Full regression testing (before any prod promotion)
- Re-run the cumulative suite in docs/testing/regression-suite.md
- Each new epic ADDS its critical paths (the suite only grows)
