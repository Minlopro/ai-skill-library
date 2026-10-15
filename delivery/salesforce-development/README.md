# Delivery / Salesforce Development

Skills for building on the Salesforce platform: Apex, Lightning Web Components,
triggers, flows, metadata and object modeling, SFDX/CLI, and deployment workflows.

## Skills

- **apex-coding-standard** — enforce and apply Salesforce Apex coding standards (review existing code + generate compliant new code). Class-name prefix is project-configurable.
- **apex-test-authoring** — write meaningful Apex tests: real assertions, realistic data, bulk/negative/edge coverage, mocking, and the production coverage gate (generate + review).
- **lwc-coding-standard** — enforce and apply Lightning Web Component coding standards (review + generate).
- **flow-coding-standard** — build reliable, bulk-safe, maintainable Flows and know when a Flow is the wrong tool: before/after-save, fault paths, no DML-in-loops (generate + review).
- **agentforce-agent-builder** — build, edit, debug, and ship an Agentforce agent the source-first way: Agent Script `.agent` bundle + Apex invocable actions, publish/activate, MIAW gotchas.
- **deployment-workbook** — the sprint-by-sprint deploy-log workbook format and the commit convention that goes with it.
- **design-doc-standard** — standards for design docs, dev/test plans, ERDs, security matrices, and the project orientation file (CLAUDE.md/README).
- **product-library-search** — find reusable assets in the Minlopro product library (`Minlopro/minlopro-product-library`) before building anything new: turn a story into search terms, rank assets (`scripts/search.py`), judge the fit, and report what to reuse, configure, and still build. Never reads client delivery repos.
- **product-library-sanitize** — the strip-down procedure for every product library contribution: client terms, neutral API names (no client prefix, no `MLP_`), client values to configuration, obviously synthetic `TEST` data in contributed assets, a masked client-detail scan (`scripts/scan.py`, zero findings), check-only deploy, and the PR.
