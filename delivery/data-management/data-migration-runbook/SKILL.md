---
name: data-migration-runbook
description: >-
  Plan and execute a Salesforce data migration or transformation the safe, repeatable way: profile,
  map, transform, load, validate, reconcile. Use whenever the user is migrating or loading data into
  Salesforce, mapping a source system to target objects, deduplicating, doing an ETL, or asks about
  Data Loader / Bulk API, external IDs, upserts, or load order. Includes the data-handling rule for
  working with real client data.
---

# Data Migration Runbook

A migration is a pipeline, not a one-shot load. Run every phase in a sandbox first, keep it
idempotent so you can re-run cleanly, and reconcile before you call it done.

## Data handling (read first)

- **Non-PHI client data: transact, never store.** When the task is an authorized migration or
  transformation, you can work with the real non-PHI data to do the job. Delete extracts as soon as
  the task is finished; never leave client data sitting in chats, downloaded files, project folders,
  or repos any longer than the work requires.
- **PHI and regulated data (patient/health, minors/enrollees, 21 CFR) get extra scrutiny.** Keep it
  out of general AI tools that aren't covered by a BAA. De-identify or work on the *structure*
  (schema, field mappings, aggregates) instead of raw records, use the minimum necessary, and escalate
  before processing raw regulated data through any AI tool.
- Encrypt data at rest and in transit; restrict who can touch the extract; log what moved.

## Phases

1. **Profile the source.** Row counts, distinct values, formats, required fields, orphan/duplicate
   rates, relationships. You cannot map what you haven't profiled.
2. **Map source → target.** A field-mapping doc per object: source field, target field,
   transformation, default when blank, and the match key. Note picklist value mappings and any
   type/format conversions.
3. **Prep & transform.** Clean, standardize, de-duplicate, and stage the data with the target
   external-id column populated. Do transformation in the staging layer, not by hand mid-load.
4. **Load.** Parents before children; use **upsert on an External Id** so re-runs update rather than
   duplicate, and so child records resolve their parent by external id.
5. **Validate & reconcile.** Prove it landed correctly (below) before sign-off.

## Load mechanics

- **Order by dependency:** accounts before contacts before related records; anything a lookup points
  to loads first. Self-referencing lookups (e.g. parent account) load in a second pass.
- **External Ids + upsert** are the backbone: they make loads idempotent and let child records point
  to parents by a stable business key instead of a Salesforce Id you don't have yet.
- **Bulk API** for volume (Data Loader / CLI); tune batch size to avoid row-lock and limit errors.
  Watch for **record locking** when children referencing the same parent land in different batches
  (serialize or order to reduce contention).
- **Quiet the org during load:** deactivate triggers, record-triggered Flows, validation rules, and
  duplicate rules that would fire per row, then **reactivate them after** and re-run validation to
  catch anything they would have enforced. Track exactly what you toggled.

## Deduplication

- Decide the **match key** up front (email, external id, name+phone) and dedup in the staging layer,
  deterministically, rather than trusting a fuzzy tool mid-load.
- If two sources can produce the same record, define which wins (survivorship) and merge before load.

## Validate & reconcile

- **Counts and sums:** source rows vs. loaded rows vs. expected, per object. Reconcile totals of key
  numeric fields.
- **Spot-check field-by-field** on a sample, including **created vs. modified timestamps**
  (created ≈ modified = clean single insert; a gap = create-then-update, which may mean automation
  altered the data).
- **Relationships:** no orphaned children; parent lookups resolved.
- **Error rows:** capture every failed row with its error; fix at the source/mapping and re-run
  (idempotent upsert makes this safe).

## Safety net

- **Back up the target** (or confirm it's an empty/sandbox org) before any load; know your rollback
  (delete by the batch's external ids, or restore from backup).
- **Dry-run the whole pipeline in a sandbox** with production-shaped data first. Never rehearse in prod.
- Keep the mapping doc, the toggled-automation list, and the reconciliation numbers as the audit trail.
