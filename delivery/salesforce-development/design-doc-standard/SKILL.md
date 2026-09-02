---
name: design-doc-standard
description: "Enforce and apply standards for structural project documentation — design docs, dev plans, test plans, security matrices, data-model/ERD diagrams, gap analyses, the project orientation file (often CLAUDE.md or README.md), and any requirements documents. Use this skill whenever the user asks to write or update a design doc, security matrix, dev plan, test plan, ERD, gap analysis, project orientation file, or any structural reference document. Always trigger this skill when the work would touch the project orientation file (overview, gap table, object/entity relationships, permission model). This skill covers both REVIEW MODE (audit an existing doc) and GENERATE MODE (produce a compliant new doc). For deployment workbooks (sprint-by-sprint deploy logs) use the deployment-workbook skill instead — it has its own append-only rules."
---

# Design Doc Standard Skill

This skill governs the structural documentation in the repo — the docs that describe what the system IS, not what was deployed when. Deploy logs use the [`deployment-workbook`](./deployment-workbook-SKILL.md) skill.

Two modes:
1. **REVIEW MODE** — Audit an existing structural doc and flag violations.
2. **GENERATE MODE** — Write a new doc that is compliant from the start.

Detect from context.

---

## THE STANDARD

### 1. Doc Taxonomy + Location

Documentation is organized **by feature**. The docs root (here: `technical-design/`) holds one folder per feature, a `_platform/` folder for cross-cutting docs, and master roll-ups at the root.

```
technical-design/
├── README.md                      ← feature catalog / map
├── MASTER_TECHNICAL_DESIGN.md     ← architecture + per-feature design roll-up
├── MASTER_DEPLOYMENT_WORKBOOK.md  ← chronological release roll-up
├── _platform/                     ← cross-cutting (span all features)
└── <feature>/                     ← one folder per feature; files drop the feature prefix
```

**The standard triad — every feature folder MUST carry these three:**

| File (in `<feature>/`) | Purpose |
|---|---|
| `DESIGN.md` | The design spec — what + why, data model, components, decisions |
| `DEPLOYMENT_WORKBOOK.md` | Sprint-by-sprint deploy log (see `deployment-workbook` skill) |
| `TEST_GUIDE.md` | Test plan / verification guide |

**Optional add-ons** live alongside in the same folder when the feature needs them: `DEV_PLAN.md` (sprint sequence), `SECURITY.md` (per-feature security), `GUIDE.md` (operator/admin instructions).

**Cross-cutting + master docs:**

| Doc | Location | Naming | Purpose |
|---|---|---|---|
| Project orientation (AI/dev) | repo root | `CLAUDE.md`, `AGENTS.md` | Loaded every AI session; keep concise |
| Human README | repo root | `README.md` | Customer/contributor onboarding |
| Feature catalog / map | docs root | `README.md` | Index of features + links to each triad |
| Master technical design | docs root | `MASTER_TECHNICAL_DESIGN.md` | Architecture + per-feature design roll-up |
| Master deployment workbook | docs root | `MASTER_DEPLOYMENT_WORKBOOK.md` | Chronological release roll-up |
| Cross-system security | `_platform/` | `SECURITY_MATRIX.md` | Canonical persona × resource × action matrix |
| Data model | `_platform/` | `DATA_MODEL_DIAGRAM.md` | Canonical ERD + relationship narrative |
| Gap / persona analysis | `_platform/` | `<X>_GAP_ANALYSIS.md`, `PERSONA_GAP_ANALYSIS.md` | Cross-cutting holes + remediation |
| Requirements / epics | `_platform/` or `requirements/` | `EPIC_REQUIREMENTS.md`, `user_stories.csv` | Requirements backbone |
| Process flows | `requirements/` | `PROCESS_FLOWS.md` | Process diagrams + story tables |

**Rules:**
- Never create a structural doc outside a feature folder, `_platform/`, or the docs root.
- One canonical doc per concept — `SECURITY_MATRIX.md` is THE security map; `DATA_MODEL_DIAGRAM.md` is THE ERD. Don't split.
- **Roll-up is mandatory.** When you create or materially change a feature `DESIGN.md`, refresh its summary in `MASTER_TECHNICAL_DESIGN.md` and its row in `README.md`. New feature → create the full triad folder, then register it in `README.md`, `MASTER_TECHNICAL_DESIGN.md`, and `MASTER_DEPLOYMENT_WORKBOOK.md`.
- A small feature may collapse `DEV_PLAN`/`TEST_GUIDE` detail into `DESIGN.md` — but the triad's `DESIGN.md` + `DEPLOYMENT_WORKBOOK.md` are never optional, and a missing `TEST_GUIDE.md` is a tracked gap, not a silent omission.

---

### 2. Required Front Matter

Every structural doc opens with:

```markdown
# <Doc Title>

## Document Control
| Field | Value |
|---|---|
| Version | X.Y |
| Date | YYYY-MM-DD |
| Status | Draft / In Review / Approved / Active / Superseded |
| Owner | <role / person> |

## Changelog
| Date | Version | Author | Summary |
|---|---|---|---|
| YYYY-MM-DD | X.Y | <name> | What changed |
```

Exceptions:
- The project orientation file (`CLAUDE.md`, `README.md`, etc.) and the human README don't have Document Control — they're living orientation files. But the orientation file must have a changelog footer or "Last meaningful update: YYYY-MM-DD" footer.
- Pure data files (CSVs, JSON, YAML) are not prose — they're controlled by their own ingestion/sync process, not by this skill.

---

### 3. Status Markers + Deprecation

Documents and their sections have explicit lifecycle markers:

| Status | Meaning | Action on read |
|---|---|---|
| **Draft** | In active authoring; not yet reviewed | Don't cite as authoritative |
| **In Review** | Awaiting approval | Don't deploy from |
| **Approved** | Reviewed + signed off, not yet shipped | Deploy ready |
| **Active** | Shipped + current | Authoritative |
| **Superseded** | Replaced by another doc | Read for history only |

**Deprecation in-doc:**
Never delete superseded content. Mark it inline:

```markdown
> **DEPRECATED YYYY-MM-DD** — superseded by [`NEW_DOC.md`](NEW_DOC.md). Retained for historical reference. Do not implement against this section.
```

Same for deprecated entities/fields mentioned in tables:

```markdown
| `<Old_Resource>` (DEPRECATED YYYY-MM-DD) | <type> | See `<New_Resource>` |
```

---

### 4. Dates — Always Absolute

- **`YYYY-MM-DD` only.** No "today", "yesterday", "last week", "this sprint", "recently".
- Today's date comes from the session context, not memory.
- If a date is genuinely unknown (back-filling old work), use `YYYY-MM-DD (approx)` with the marker.
- 🔴 Critical violation: any relative date in a structural doc.

---

### 5. The Project Orientation File — Special Rules

The project's orientation file (commonly `CLAUDE.md` for AI-loaded projects, `AGENTS.md`, or a similar single-file overview) is loaded into context **every session**. Every paragraph costs tokens forever. Different rules apply:

**Update triggers** (when the orientation file MUST be updated):
1. A new subsystem ships → add to Architecture diagram + Core Subsystems section.
2. A core entity, table, or field is deprecated → mark in the relationships table + add inline deprecation note.
3. A permission set, role, or capability is added/removed/renamed → update the Permission Model section.
4. A row in the Known Critical Gaps table flips from `Pending` to `Shipped YYYY-MM-DD (Sprint X)`.
5. A new design doc or workbook is created → add to Documentation References.
6. A "source of truth" callout from a workbook session is now repo-wide → fold it into the relevant subsystem section.

**Editorial rules:**
- **Brevity is a feature.** If a section can be a 5-row table instead of 3 paragraphs, use the table.
- Link to the deep doc instead of duplicating its content. The orientation file is an index, not a textbook.
- Every claim must be verifiable in code or in a linked doc within 1 click — no stale narrative.
- When editing, also touch the gap table / relationships table / permission model if your change crosses those domains. Don't leave one section consistent and the others outdated.

**The Known Critical Gaps table** is the project's open-question ledger. Every row:

```markdown
| Gap | Impact | Component Needed | Status |
|---|---|---|---|
| <description> | <regulatory or operational impact> | <what's missing> | Pending / **Shipped YYYY-MM-DD (Sprint X)** / Deferred — see <doc> / Won't fix — see <doc> |
```

Status conventions:
- `Pending` — known gap, not started
- `**Shipped YYYY-MM-DD (Sprint X)**` — closed; bold; date + sprint reference required
- `Deferred — see <doc>` — postponed with a written rationale somewhere
- `Won't fix — see <doc>` — explicit decision not to do it

When a gap closes, also add a one-line summary of HOW it closed in the row.

---

### 6. Cross-linking Discipline

- Every subsystem design doc links UP to the project orientation file and DOWN to its deployment workbook.
- Every doc has a `## See also` section at the bottom listing related docs.
- Use relative paths.
- Story / requirement IDs are written as plain text — link only when a published URL exists.
- Code entities (objects, classes, fields, components, services, tables) use code spans: `MyClass`, `my_table.id`, `customer.balance`.
- The first time a class / module / component is referenced, include its repo path: `MyService` (`src/services/my_service.py`).

---

### 7. Source of Truth Callouts

When a doc establishes or confirms a "single source of truth", call it out with a blockquote:

```markdown
> **Source of truth:** `<canonical artifact>` is the single canonical list of `<thing>`. `<consumer>` reads it dynamically; there is no hardcoded list anywhere in the service layer.
```

Use these any time a config table replaces inline values, a service centralizes logic, or a doc supersedes an ad-hoc convention. They make the codebase searchable for "where is the canonical X?".

---

### 8. Tables Over Prose

If structure exists in the data — personas, entities, fields, statuses, sprints — use a markdown pipe table. Reserve prose for the *why* and the non-obvious *how*.

A 6-row prose paragraph describing 6 personas is a 🟡 Standard violation; the same content as a 4-column table is the standard.

---

### 9. Diagrams

- **Mermaid** for ERDs, sequence diagrams, flow charts (GitHub and most renderers handle it natively).
- **ASCII tables** for matrices (permission matrices, capability matrices) — they survive grep, line-diff cleanly, and don't require a renderer.
- **Pipe tables** for everything else.
- **Never embed PNG / JPG** of diagrams that could be Mermaid — they don't version-control well, can't be diffed, and rot silently.
- One exception: hand-drawn whiteboard photos from discovery sessions are OK in `requirements/` if explicitly captioned as historical artifacts.

---

### 10. Regulatory / Compliance Framing

For any doc touching regulated or compliance-relevant topics (FDA, HIPAA, GDPR, PCI-DSS, SOC 2, ISO 27001, industry-specific standards):

- Cite the specific standard / section / clause the design satisfies.
- Explain *why* this design satisfies it (one sentence is fine).
- If there's a gap, file it in the orientation file's Known Critical Gaps table — never just mention it in prose.
- Use canonical reference phrasing for whatever standard applies (e.g. `<framework> §<section>` or the standard's own citation format).

---

### 11. Versioning

| Change | Bump |
|---|---|
| Typo, link fix, formatting | No bump |
| Section addition or clarification | Minor (1.0 → 1.1) |
| Substantive rewrite, model change, new design approach | Major (1.0 → 2.0) |
| Doc fully superseded by another doc | Mark Superseded, don't bump |

Every bump adds a changelog row. The Document Control table reflects the latest version.

---

### 12. Commit Messages

When committing changes to structural docs, follow the same commit-message convention as deployment workbooks — see [`deployment-workbook-SKILL.md`](./deployment-workbook-SKILL.md) §11.

Specific to design-doc commits:
- Use prefix `docs:` if the commit is doc-only (no code changes).
- Use prefix `<subsystem>:` if doc + code shipped together (the workbook update is the source of truth then; design doc update is a side effect).
- For orientation-file updates, the subject line should name the section that changed (`docs: update <orientation-file> gap table — close <row> row`).
- For versioned baseline doc bumps, the commit subject must include the new version (`docs: <STANDARD>-<ID> v<n> — <summary of change>`).

---

### 13. Versioned Baseline Files Are Special

Some projects maintain versioned regulatory or specification baselines (URS, RFC drafts, API specs, public schemas) where the version is part of the filename (`<NAME>_v<n>.md`).

- **Never edit a published version in place.** When a new version is needed, copy the file to `<NAME>_v<n+1>.md` and edit the new copy.
- The old version stays in the repo as the historical record.
- Document the version bump in `## Changelog` at the top of the new version, and in the project orientation file's Documentation References section.
- Requirement / clause IDs never change once published — adding new requirements appends new IDs.

---

## REVIEW MODE — How to conduct a review

```
## Design Doc Review — <Doc Name>

### 🔴 Critical Violations
- [Section §X] <violation> — <fix>

### 🟡 Standard Violations
- [Section §X] <violation> — <fix>

### 🟢 Suggestions
- <suggestion>

### Summary
X critical, Y standard, Z suggestions.
[Verdict: PASS / FAIL]
```

PASS requires zero critical AND zero standard violations.

---

## GENERATE MODE — How to write a compliant doc

When generating new structural docs:

1. Confirm the doc kind + location from §1 — ask if unclear.
2. Scaffold the Document Control + Changelog front matter from §2 with today's date and Version 1.0.
3. Apply §3 status markers (`Draft` for fresh authoring, `Active` only after review).
4. Use absolute dates throughout (§4).
5. If the work would touch the project orientation file (§5 triggers), generate those edits alongside the new doc — don't ship a new subsystem doc without updating the project overview.
6. Cross-link UP and DOWN (§6) and add a `## See also` footer.
7. Add source-of-truth callouts (§7) for any new canonical thing the doc introduces.
8. Prefer tables (§8) — only use prose for the why/how.
9. Use Mermaid / ASCII tables / pipe tables per §9.
10. For regulated/compliance topics, frame per §10.
11. For versioned baseline files, follow §13's version-as-file-copy rule.

---

## Quick Reference — Common Violations Checklist

| # | Violation | Severity |
|---|---|---|
| 1 | Editing a published versioned baseline in place instead of copying to v<n+1> | 🔴 Critical |
| 2 | Deleting deprecated content instead of marking `DEPRECATED YYYY-MM-DD` | 🔴 Critical |
| 3 | Relative date ("today", "last week", "this sprint") | 🔴 Critical |
| 4 | Creating a structural doc outside the project's documentation directories | 🔴 Critical |
| 5 | New subsystem shipped without updating the project orientation file's Core Subsystems section | 🔴 Critical |
| 6 | Entity/field deprecated in code but the orientation file's relationships table not updated | 🔴 Critical |
| 7 | Permission/role added/removed/renamed but the Permission Model section not updated | 🔴 Critical |
| 8 | Gap closed in code but the orientation file's gap table still says Pending | 🔴 Critical |
| 9 | New design doc created with no link from the orientation file's Documentation References | 🔴 Critical |
| 10 | Embedding a PNG/JPG diagram that could be Mermaid | 🟡 Standard |
| 11 | Missing Document Control / Changelog front matter | 🟡 Standard |
| 12 | Missing Status field in Document Control | 🟡 Standard |
| 13 | No `## See also` cross-link section | 🟡 Standard |
| 14 | Prose where a table would be clearer | 🟡 Standard |
| 15 | Splitting a canonical concept across multiple docs (two security matrices, two ERDs) | 🟡 Standard |
| 16 | Source-of-truth callout missing when one is introduced | 🟡 Standard |
| 17 | Regulatory topic discussed without citing the specific standard / section | 🟡 Standard |
| 18 | Version bump without a changelog row | 🟡 Standard |
| 19 | Plain code-entity names not in code spans (e.g. `MyClass` instead of `MyClass`) | 🟢 Suggestion |
| 20 | Orientation-file section grown to 3+ paragraphs where a table would suffice (brevity is a feature) | 🟢 Suggestion |
| 21 | Doc lacks a clear "what is this for" sentence in the first paragraph | 🟢 Suggestion |
