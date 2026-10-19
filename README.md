# Minlopro AI Skill Library

A shared library of AI skills (Claude skills) that Minlopro employees can leverage
across their work. Skills are reusable, self-contained instructions the assistant
loads on demand for a specific kind of task.

## Use it in Claude Code

This repo doubles as a **Claude Code plugin marketplace**. **Each skill is published
as its own plugin**, so it shows up as a separate item in the catalog and you can
install exactly the ones you want.

```bash
# add the marketplace (once)
claude plugin marketplace add Minlopro/ai-skill-library

# browse the catalog (one entry per skill)
claude plugin marketplace info minlopro-skill-library

# install the skills you want (each skill is its own plugin)
claude plugin install apex-coding-standard@minlopro-skill-library
claude plugin install browser-qa@minlopro-skill-library

# later: pull the latest
claude plugin marketplace update minlopro-skill-library
```

Every skill is its own entry in `.claude-plugin/marketplace.json` (a `git-subdir`
plugin pointing at that skill's folder in this repo), which is what makes each one a
separate marketplace item.

## Skill catalog

| Skill | Discipline | What it does |
| --- | --- | --- |
| `data-migration-runbook` | data-management | Plan and execute a Salesforce data migration/transformation safely: profile, map, transform, load, validate, reconcile. |
| `browser-qa` | quality-assurance | Drive a real Chrome browser (chrome-devtools MCP) to QA a web app's UI, reproduce bugs, and cross-check the data layer. |
| `agentforce-agent-builder` | salesforce-development | Build, edit, debug, and ship a Salesforce Agentforce agent the source-first way (Agent Script + Apex). |
| `minlopro-salesforce-project-setup` | salesforce-development | Stand up a complete agentic Salesforce delivery project from scratch: toolchain, org/GitHub auth, SFDX scaffold with CLAUDE.md memory and a prod-deploy guardrail hook, then the per-epic delivery loop. |
| `apex-coding-standard` | salesforce-development | Enforce and apply Salesforce Apex coding standards when reviewing or writing Apex. |
| `apex-test-authoring` | salesforce-development | Write meaningful Apex test classes with real assertions and realistic data. |
| `deployment-workbook` | salesforce-development | Enforce the sprint-by-sprint deployment workbook format and its commit convention. |
| `design-doc-standard` | salesforce-development | Enforce standards for design docs, dev/test plans, security matrices, ERDs, and orientation files. |
| `flow-coding-standard` | salesforce-development | Enforce Salesforce Flow best practices and know when a Flow is the wrong tool. |
| `lwc-coding-standard` | salesforce-development | Enforce and apply Salesforce LWC coding standards when reviewing or writing components. |
| `product-library-sanitize` | salesforce-development | Strip client details from Salesforce metadata and package it as a reusable product-library asset. |
| `product-library-search` | salesforce-development | Find reusable, client-free Salesforce assets in the product library before building anything new. |
| `proto-academy-authoring` | internal | Author Proto Academy (internal LMS) content directly in the live org via the Create/Edit/Read MCP connection, as a content creator: permission-gated, no-delete record writes, draft-and-confirm. |

## How it's organized

Skills are grouped by **department**, and `delivery` is broken down further by
**discipline**:

```
sales/                          Sales: prospecting, proposals, estimation, deal support
delivery/                       Client delivery work, by discipline:
  salesforce-development/         Apex, LWC, triggers, flows, metadata, deployments
  data-management/                Data modeling, migration, cleansing, ETL, data quality
  project-management/             Planning, status, scope control, risk, PMO tooling
  salesforce-consulting/          Solution design, requirements, business analysis, advisory
  quality-assurance/              Test strategy, test design, UAT, regression, QA automation
  integrations/                   APIs, MuleSoft/middleware, external systems, auth patterns
operations/                     Internal ops: finance, people, IT/admin, reporting
internal/                       Minlopro's own tools and initiatives (Proto, Academy, etc.)
```

Put a skill in the folder that best matches who owns the task. If it's genuinely
cross-department, prefer the department that most often runs it.

## Adding a skill

Two steps: create the skill folder, then register it as its own marketplace entry.

**1. Create the skill folder** under the relevant department/discipline, containing a
`SKILL.md` plus any supporting files:

```
delivery/salesforce-development/apex-test-scaffolding/
  SKILL.md
  scripts/            (optional)
  references/         (optional)
```

`SKILL.md` starts with YAML frontmatter, then the instructions:

```markdown
---
name: apex-test-scaffolding
description: Scaffold Apex test classes for a given class - use when writing or fixing Salesforce tests.
---

# Apex Test Scaffolding

Step-by-step instructions the assistant follows when this skill is invoked...
```

Conventions:
- `name` is **kebab-case**, unique across the library, and matches the folder name.
- `description` is one line that makes it clear **what it does and when to use it** -
  this is what the assistant reads to decide relevance, so be specific.
- Keep supporting files next to the `SKILL.md` and reference them by relative path.

**2. Register it in the marketplace** so it becomes its own catalog item. Add an
object to `plugins` in `.claude-plugin/marketplace.json`:

```json
{
  "name": "apex-test-scaffolding",
  "displayName": "Apex Test Scaffolding",
  "description": "Scaffold Apex test classes - use when writing or fixing Salesforce tests.",
  "version": "1.0.0",
  "category": "salesforce-development",
  "source": {
    "source": "git-subdir",
    "url": "https://github.com/Minlopro/ai-skill-library.git",
    "path": "delivery/salesforce-development/apex-test-scaffolding"
  }
}
```

The `path` is the skill folder relative to the repo root. A skill folder with a
`SKILL.md` and no `plugin.json` loads as that single skill, so no per-skill
`plugin.json` is needed. Validate before pushing:

```bash
claude plugin validate .
```

## Contributing

Use a branch + PR for review, or push small scaffolding changes directly. Keep each
skill focused - one job per skill, and add its marketplace entry in the same change.
