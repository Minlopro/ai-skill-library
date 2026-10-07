# Minlopro AI Skill Library

A shared library of AI skills (Claude skills) that Minlopro employees can leverage
across their work. Skills are reusable, self-contained instructions the assistant
loads on demand for a specific kind of task.

## Use it in Claude Code

This repo doubles as a **Claude Code plugin marketplace**, so you can install every
skill here and keep it synced.

```bash
# add the marketplace (once)
claude plugin marketplace add trenthilkertmlp/ai-skill-library

# install the skill pack
claude plugin install minlopro-skills@minlopro-skill-library

# later: pull the latest skills
claude plugin marketplace update minlopro-skill-library
```

Skills install from the discipline folders listed under `skills` in
`.claude-plugin/plugin.json`. Adding a skill to an already-listed discipline is
picked up on the next `update`; the first skill in a **new** discipline also needs
that folder appended to that `skills` list.

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

Each skill lives in **its own folder** under the relevant department/discipline and
contains a `SKILL.md`, plus any supporting files it needs:

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

## Contributing

Use a branch + PR for review, or push small scaffolding changes directly. Keep each
skill focused - one job per skill.
