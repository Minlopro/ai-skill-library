---
name: deployment-workbook
description: "Enforce and apply deployment workbook standards — the sprint-by-sprint deploy log format used in a project's `<SUBSYSTEM>_DEPLOYMENT_WORKBOOK.md` files. Use this skill whenever the user asks to log a deploy, append a sprint, write a session entry, document what shipped, update a workbook, or commit a deploy. Also covers the commit-message convention used after each workbook update. Always trigger this skill for any work that involves a deployment workbook or a commit that accompanies a workbook update — even simple requests like \"log this deploy\" or \"add a sprint entry\". This skill covers both REVIEW MODE (audit an existing workbook section) and GENERATE MODE (write a new section that is fully compliant from the start)."
---

# Deployment Workbook Skill

This skill governs two modes:
1. **REVIEW MODE** — Audit an existing workbook section and flag all violations.
2. **GENERATE MODE** — Write a new workbook entry (sprint, session, commit) that is fully compliant from the start.

Detect mode from context: if the user pastes a workbook section or asks "is this ok / review this", use REVIEW MODE. If they ask to log a deploy, append a sprint, or write the commit that accompanies one, use GENERATE MODE.

---

## THE STANDARD

### 1. Naming + Location

Documentation is organized **by feature**. Each feature owns a folder under the docs root (here: `technical-design/<feature>/`), and the workbook is always named:

```
technical-design/<feature>/DEPLOYMENT_WORKBOOK.md
```

The feature folder is the namespace, so the file drops any feature prefix (use `DEPLOYMENT_WORKBOOK.md`, not `<FEATURE>_DEPLOYMENT_WORKBOOK.md`). Cross-cutting deploys that don't belong to one feature (e.g. org-wide security) are logged in the relevant `_platform/` doc.

A single master roll-up — `technical-design/MASTER_DEPLOYMENT_WORKBOOK.md` — indexes every milestone across all features (one row per milestone, newest first, linking to the feature workbook).

**Rules:**
- One workbook per feature, in that feature's folder, appended forever. Never split a feature's deploy history across two workbooks.
- Never create a workbook outside a feature folder (or `_platform/` for cross-cutting work).
- **Roll-up is mandatory.** After appending a sprint/session to a feature workbook, add a corresponding row to `MASTER_DEPLOYMENT_WORKBOOK.md` and refresh the feature's "Latest deploy" in `technical-design/README.md`.
- New feature? Create the folder + the standard triad (`DESIGN.md`, `DEPLOYMENT_WORKBOOK.md`, `TEST_GUIDE.md`), then add it to the `README.md` feature catalog, `MASTER_TECHNICAL_DESIGN.md`, and `MASTER_DEPLOYMENT_WORKBOOK.md`. See the `design-doc-standard` skill for the full triad rules.

---

### 2. Required Front Matter

Every workbook opens with these four sections in this order:

```markdown
# <Subsystem> Deployment Workbook

## Document Control
| Field | Value |
|---|---|
| Version | X.Y |
| Date | YYYY-MM-DD |
| Owner | <role / person> |
| Source environment | <name of dev/source env> |
| Target environment(s) | <names of UAT / staging / production> |

## Related docs
- [`DESIGN.md`](DESIGN.md) — feature design spec (same folder)
- [`TEST_GUIDE.md`](TEST_GUIDE.md) — test approach (same folder)
- [`DEV_PLAN.md`](DEV_PLAN.md) — sprint plan, if present (same folder)
- [`../MASTER_DEPLOYMENT_WORKBOOK.md`](../MASTER_DEPLOYMENT_WORKBOOK.md) — the master roll-up
- [`../_platform/SECURITY_MATRIX.md`](../_platform/SECURITY_MATRIX.md) — cross-cutting refs, as relevant

## Running Changelog
| Date | Version | Summary |
|---|---|---|
| YYYY-MM-DD | X.Y | Short description |

## Naming Convention
Sprints lettered A → Z chronologically. Sub-sprints use `.5`/`.2` decimal suffixes for additive/follow-up work within the same theme (e.g. `K.5`, `J.2`). Letters are never reused.
```

---

### 3. Sprint Section Structure

Each sprint gets a top-level `##` heading and the following sub-sections in this order. Missing sections are a 🟡 Standard violation; missing the heading itself is 🔴 Critical.

```markdown
## Sprint <Letter> — <Concise Title>

**Date shipped:** YYYY-MM-DD
**Stories closed:** <STORY-ID>, <REQUIREMENT-ID>
**Exit criteria:** <one-line statement>

### Phase 1: <First major deliverable>
- Bullet of what changed
- Bullet of what changed

### Phase 2: <Next major deliverable>
- …

### Sprint <Letter> Test Results
- Automated tests: X passed / Y total / Z% coverage
- Manual smoke: <persona/role> on <flow> — PASS/FAIL
- Failures: <explicit list or "none">

### Sprint <Letter> Exit Criteria — All Met
- [x] Criterion 1
- [x] Criterion 2

### Sprint <Letter> Stories Closed
- <STORY-ID> — <title> — <status>

### Sprint <Letter> Deltas from Plan
- What we said we'd do vs. what we shipped — explicit deviations only (no entry needed if zero deltas)

### Sprint <Letter> Gotchas
- Anything non-obvious that future-me/team needs to know — permission surprises, deploy order, post-deploy manual steps

### Sprint <Letter> Follow-ups
- Open items deferred to a later sprint, with sprint target where known
```

After every sprint section, append a **Cumulative Manifest Summary**:

```markdown
## Manifest Summary — Sprints A + B + ... + <Letter> (Cumulative)

| Component | This sprint | Cumulative |
|---|---|---|
| <Component type 1> | N | N |
| <Component type 2> | N | N |
| <Component type N> | N | N |
```

Component types depend on the project (e.g. classes, components, modules, tables, schemas, services, jobs, configs). Pick a stable set per workbook and stick with it.

---

### 4. Session Entries (Non-Sprint Work)

When work isn't sprint-aligned (a one-off fix, a docs refresh, a tooling change), use a dated session heading instead:

```markdown
### Session YYYY-MM-DD — <Concise Title>

**Driver:** <one-line context: what triggered this work>

**What shipped:**
- Bullet
- Bullet

**Why:**
1-2 sentences. Link story IDs / requirements / gap-table rows where applicable.

**Files touched:**
- path/to/file1
- path/to/file2

**Deploy log:**
```
$ <deploy command>
Status: Succeeded
Tests run: X passed / 0 failed
```

**Gotchas:**
- …

**Follow-ups:**
- …
```

Session entries nest under the most recent sprint section. Don't create top-level `##` for sessions — they're additive.

---

### 5. Dates

- **Always absolute, `YYYY-MM-DD`** — never "today", "yesterday", "last week", "this sprint".
- Today's date comes from the session context (or `date` command output), not from memory or guesses.
- When recording a date that's already in the past, double-check it against git log / commit history — don't approximate.
- If a date is genuinely unknown (e.g. an old shipped item being back-filled), write `YYYY-MM-DD (approx)` with the approximation marker.

---

### 6. Append-Only Discipline

- **Old sprint sections are NEVER edited.** They are the historical deploy log.
- If a sprint's work is later corrected/extended, add a new `<Letter>.5 — correction` sub-sprint with a back-reference (`Corrects K.3 §2 — the threshold value should have been 4.0 not 6.5`).
- Exceptions: typo fixes, cross-link corrections, formatting fixes. Anything that changes the substance of a recorded event requires a new section.
- This is a 🔴 Critical rule — silently editing closed sprint sections defeats the purpose of the log.

---

### 7. Test Results

Every sprint must record:
- **Test counts** — passed / total / coverage %. Use exact numbers from test runner output, never round.
- **Manual smoke list** — persona/role + flow + PASS/FAIL.
- **Failures** — if any, list explicitly with the exception message and the disposition (fixed in same sprint / deferred to follow-up).
- **Coverage gaps** — if any module is below the project's threshold, call it out.

"All tests passing" with no numbers is a 🟡 Standard violation.

---

### 8. Cumulative Manifest

Every sprint section must end with an updated cumulative manifest table (see §3). The "Cumulative" column shows the running total across all sprints to date — this lets a reader open any sprint section and see the total deployed footprint of the subsystem.

If a sprint deprecates or removes components, that's a separate `### Removed in Sprint X` sub-section — the manifest reflects the net total.

---

### 9. Cross-linking

- Every workbook links UP to the related design doc, dev plan, test plan in `## Related workbooks`.
- Sprint sections that depend on external work (e.g. data seeded by another team) link to the relevant doc inline.
- Use relative paths for inter-doc links (e.g. `[`<SIBLING>.md`](<SIBLING>.md)`).
- Story / requirement IDs link to the system of record if there's a URL; otherwise just cite the ID.

---

### 10. Source of Truth Callouts

When the work introduces a new "single source of truth" (a config table replacing inline lists, a service centralizing logic, a field deprecating a sibling), call it out explicitly:

```markdown
> **Source of truth:** `<canonical artifact>` is now the single canonical list of `<thing>`. `<consumer>` reads it dynamically; there is no hardcoded list anywhere else.
```

These callouts make the project-overview file's updates easier (it expects them).

---

### 11. Commit Message Convention (when committing alongside a workbook update)

After updating the workbook + shipping code, every commit follows this structure:

```
<area>: <imperative summary, ≤72 chars>

<paragraph: WHAT changed and the user-visible behavior>

<paragraph: WHY — the regulatory/feature/process driver, with story IDs>

<paragraph: side-effects, breaking changes, deploy-order requirements>

<bulleted list of files/objects/classes touched, if non-trivial>

<workbook reference: "Workbook: <SUBSYSTEM> §Sprint <Letter>">

<project-specific attribution footer, if any>
```

**Rules:**
- Subject line: imperative ("Add", "Fix", "Refactor", "Deploy"), ≤72 chars, no trailing period.
- Blank line after subject.
- Multi-paragraph body — never a one-line message for non-trivial work.
- WHAT first, then WHY, then side-effects. Don't merge them.
- Reference the workbook section explicitly (`Workbook: <SUBSYSTEM> §Sprint <Letter>` or `Workbook: <SUBSYSTEM> §Session YYYY-MM-DD`).
- Story / requirement IDs go in the WHY paragraph.
- Project-specific attribution footer (e.g. `Co-Authored-By:` or `Signed-off-by:`) is mandatory if the project uses one.
- Never include local-only artifacts (e.g. `.DS_Store`, IDE caches, machine-local settings) in the commit.

**Subject line prefixes** — pick a stable convention per repo:
- `<subsystem>:` — short subsystem identifier (e.g. `auth:`, `billing:`, `scheduler:`)
- `Add` / `Fix` / `Refactor` / `Deploy` / `Docs` / `Tests` — for cross-cutting work
- `<non-code-area>:` — for non-code artifact areas (e.g. `data-templates:`, `infra:`, `requirements:`)

---

### 12. Manual Post-Deploy Steps

Many deploys require steps the CLI can't do (UI configuration, environment refresh, permission assignment in restricted environments, picklist/enum value updates, third-party integration setup). Every sprint that has any must declare them:

```markdown
### Phase N: Manual Post-Deploy Steps

After the automated deploy succeeds, complete these steps in the target environment:

1. **<Tool / UI>** — <action> (path: <where in the tool>)
2. **<Configuration>** — <action>
3. **<Service / Integration>** — <action>
```

Missing manual-step documentation when manual steps were actually required is a 🔴 Critical violation — the next deployer has no idea.

---

## REVIEW MODE — How to conduct a review

Produce this structured report:

```
## Deployment Workbook Review — <Workbook Name> §<Section>

### 🔴 Critical Violations
- [Line X] <violation> — <fix>

### 🟡 Standard Violations
- [Line X] <violation> — <fix>

### 🟢 Suggestions
- <suggestion>

### Summary
X critical, Y standard, Z suggestions.
[Verdict: PASS / FAIL]
```

PASS requires zero critical AND zero standard violations.

---

## GENERATE MODE — How to write a compliant entry

When generating a new sprint section, session entry, or accompanying commit:

1. Confirm the workbook target — ask if unclear.
2. Apply ALL §1–§12 rules from the start.
3. Use today's actual date (never approximate).
4. Compute the next sprint letter from the latest existing sprint in the workbook — don't reuse or skip letters.
5. Update the running changelog table at the top of the file with a new row.
6. Update the cumulative manifest at the end of the new sprint section.
7. If this is the first work in the workbook for a new subsystem, scaffold the full document control + related workbooks + changelog + naming convention front matter.
8. If a commit accompanies the update, generate the commit message inline matching §11.

---

## Quick Reference — Common Violations Checklist

| # | Violation | Severity |
|---|---|---|
| 1 | Editing an old closed sprint section instead of appending a `.5`/`.2` correction | 🔴 Critical |
| 2 | Missing Document Control / Running Changelog / Naming Convention front matter | 🔴 Critical |
| 3 | Reusing a sprint letter | 🔴 Critical |
| 4 | Relative date ("today", "last week") instead of `YYYY-MM-DD` | 🔴 Critical |
| 5 | Missing manual post-deploy steps when manual steps were required | 🔴 Critical |
| 6 | Commit message with no body / one-line message for non-trivial work | 🔴 Critical |
| 7 | Commit message missing the project's attribution footer (if the project uses one) | 🔴 Critical |
| 8 | Committing local-only artifacts (IDE caches, OS metadata, machine-local settings) | 🔴 Critical |
| 9 | Sprint section missing test results / pass count | 🟡 Standard |
| 10 | Sprint section missing exit criteria | 🟡 Standard |
| 11 | Sprint section missing cumulative manifest | 🟡 Standard |
| 12 | "All tests passing" with no numbers | 🟡 Standard |
| 13 | Missing cross-link to related design doc / dev plan | 🟡 Standard |
| 14 | Story IDs not cited in Stories Closed | 🟡 Standard |
| 15 | Source-of-truth callout missing when one is introduced | 🟡 Standard |
| 16 | Workbook created outside the dedicated directory | 🟡 Standard |
| 17 | Splitting a subsystem across multiple workbooks | 🟡 Standard |
| 18 | Commit subject line >72 chars or non-imperative | 🟡 Standard |
| 19 | No workbook reference in commit body | 🟡 Standard |
| 20 | Cumulative manifest counts inconsistent with prior sprint totals | 🟢 Suggestion |
| 21 | Session entry placed under wrong sprint (chronology error) | 🟢 Suggestion |
