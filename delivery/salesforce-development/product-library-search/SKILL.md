---
name: product-library-search
description: Find reusable, client-free Salesforce assets in the Minlopro product library (Minlopro/minlopro-product-library) before building anything new. Use this whenever a story, requirement, SOW item, build plan, or hand-off needs Salesforce metadata (objects, fields, record types, flows, Apex, LWC, permission sets, list views, reports, test data, demo scenes), whenever someone asks "do we already have something for X", and whenever HELM plans or builds a card, even if nobody mentions the library.
---

# Product library search

Find what the Minlopro product library already has for a piece of Salesforce work, judge how well it fits, and say exactly what to reuse, what to configure, and what is still left to build. Reusing a proven asset is faster and safer than building again; a bad fit reused blindly is worse than building fresh. The job is the judgment between the two.

## Ground rules

- **Read only this repo.** The library (`Minlopro/minlopro-product-library`) is the only source. Never search, open, or copy from client delivery repos, even ones you can reach: they carry client details, and reuse from them is how client information leaks between engagements.
- **Read-only.** Searching never changes the library. Copying an asset into an engagement is a separate, recorded step (see "Use it").
- **Say when nothing fits.** "No match: build new" is a good answer. Never stretch an asset to cover something it doesn't do.

## 1. Sync

Work from the current `main`:

```bash
gh repo clone Minlopro/minlopro-product-library ~/.helm/library/mirror   # first time
git -C ~/.helm/library/mirror pull --ff-only                               # after that
```

Note the commit (`git -C <dir> rev-parse --short HEAD`): whoever reuses an asset records it.

## 2. Turn the need into search terms

A story says what a person wants; assets are described by what they are. Translate before searching. From the story or requirement, write down:

| Facet | Examples |
|---|---|
| Business object | referral, intake, case, order, vehicle, warranty, appointment, consent |
| Salesforce objects | custom object, Account/Contact record types, Case, Opportunity, Lead |
| Pattern | intake queue, routing, SLA timers, approval, lifecycle timestamps, record-type split, console workspace, timeline, dashboard, test data, demo seed |
| Metadata types | CustomObject, CustomField, RecordType, Flow, ApexClass, LightningComponentBundle, PermissionSet, ListView, Report, FlexiPage |
| Cloud and edition | Service Cloud, Sales Cloud, Health Cloud, Experience Cloud |

Include synonyms the library might use (a "work queue" may be tagged `queue` or `routing`; "parent account for individuals and companies" is a record-type split). Three to eight terms is right; more dilutes ranking.

## 3. Search

Run the bundled search. It reads every `assets/<category>/<name>/asset.json` plus the asset's README, scores each against your terms, and prints a ranked table with the reasons each asset matched:

```bash
python3 scripts/search.py --library ~/.helm/library/mirror "referral intake" queue routing "record type" --cloud "Service Cloud"
```

Options: `--category data-model|automation|ui|access|integration|testing|demo`, `--metadata Flow` (repeatable), `--json` for machine-readable output, `--top N`.

Then read, don't trust the score: open the top three assets' `README.md` and `asset.json`, and skim their `force-app/` file list. A high score from tag overlap can still be the wrong shape.

## 4. Judge the fit

For each candidate, decide one of:

| Verdict | Means |
|---|---|
| **Use as is** | Covers the need with configuration only (values in custom metadata, picklists, a permission set assignment) |
| **Adapt** | Right shape, needs extension (extra fields, another routing rule) that the asset's design allows without forking it |
| **Partial** | Covers part of the need (for example the data model but not the automation); build the rest alongside |
| **No fit** | Different problem, conflicting data model, or would need rewriting. Build new |

Check before recommending anything but "No fit":

- **Dependencies** (`dependencies` in `asset.json`): reusing one asset may require others. List the whole set.
- **Data model conflicts**: does the asset add objects, record types, or fields that collide with what the engagement already has? Person Accounts vs Account/Contact is the classic one.
- **Cloud and licenses**: an asset built on Service Cloud features won't install on Sales Cloud alone.
- **API version and install method** (`install`): source-format assets deploy with `sf project deploy start`.
- **Configuration** (`configuration` in `asset.json`): every listed step becomes a task in the build plan.
- **Version**: prefer the latest; note it.

## 5. Report

Lead with the answer, then the table:

```markdown
**Reuse 2 assets, build 1 piece new.**

| Need | Asset (version) | Verdict | Configure | Still to build |
|---|---|---|---|---|
| Referral record and lifecycle fields | data-model/referral-intake-model (1.0.0) | Use as is | Set urgency SLA values in custom metadata | None |
| Route to specialty queues | automation/referral-lifecycle-routing (1.0.0) | Adapt | Map specialties to queues | Add the fax-source rule |
| Fax OCR intake | none | No fit | | Build new |

Library commit: ff746d8
```

Keep the "why" to one line per row. Name every dependency the recommendation pulls in.

## 6. Use it (when the plan is approved)

Copy the asset's `force-app/` into the engagement repo without overwriting the engagement's own files, then record it in the engagement's `ASSETS.md`:

```markdown
| Asset | Version | Library commit | Files |
|---|---|---|---|
| referral-intake-model | 1.0.0 | ff746d8 | 24 |
```

HELM does this automatically for assets named in an approved build plan. Configure, then extend; don't edit the copied asset's core files unless the plan says so, and if you improve the asset, contribute the improvement back (see the `product-library-sanitize` skill).
