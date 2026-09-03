---
name: flow-coding-standard
description: >-
  Enforce and apply Salesforce Flow best practices: build reliable, bulk-safe, maintainable Flows
  and know when a Flow is the wrong tool. Use whenever the user builds or reviews a record-triggered,
  screen, scheduled, or autolaunched Flow, or mentions Flow Builder, before-save vs after-save, fault
  paths, subflows, or "should this be a Flow or Apex?". Covers GENERATE mode (design a compliant Flow)
  and REVIEW mode (audit an existing Flow and flag every violation).
---

# Flow Coding Standard

Flows are real business logic and deserve the same rigor as Apex. Most production Flow incidents come
from a handful of avoidable mistakes: DML in loops, no fault handling, and too many Flows fighting
over the same object.

## Flow or Apex?

- **Flow** for declarative automation: field updates, record create/update, simple branching, screen
  UIs, scheduled batch-lite jobs, and calling invocable Apex.
- **Apex** for heavy/complex logic, large-volume processing, complex callouts, recursion control, or
  anything that needs real unit tests and precise error handling. When a Flow grows into dozens of
  elements and nested decisions, that's the signal to move logic into an invocable Apex action the
  Flow calls.

## Record-triggered Flow rules

- **One automation per object per context, coordinated.** Multiple record-triggered Flows on the same
  object + same trigger fire in **no guaranteed order**. Prefer one entry Flow per object/context (or
  a documented ordering) so behavior is predictable.
- **Before-save vs after-save:**
  - **Before-save** for updating fields on the *same* record that triggered it: no DML, dramatically
    faster, no extra element. Use it for same-record field defaulting/derivation.
  - **After-save** when you need related records, to create/update *other* records, send emails, or
    call actions.
- **Tight entry conditions.** Set entry criteria (and "only when changes meet the condition") so the
  Flow runs only when it must. Every needless run is CPU + a recursion risk.
- **Guard recursion.** A Flow that updates records that re-trigger it can loop. Use entry conditions
  and "only when a field changed" to break cycles.

## Bulkification (the #1 killer)

- **Never put Get Records, Create/Update/Delete, or an Action inside a loop.** Loop to build a
  **collection**, then do a single Get/DML on the collection after the loop. DML-in-loop hits governor
  limits the moment more than a handful of records are processed together.
- Filter and query the minimum: select only needed fields, add filters, cap with sort/limit where
  possible.

## Reliability

- **Fault path on every element that can fail** (Get, DML, Action, callout). Route faults to a
  handler that surfaces a clear screen error (screen Flows) or logs/notifies (background Flows).
  A silent unhandled fault rolls back the whole transaction with a cryptic message.
- **No hardcoded IDs.** Record type IDs, user IDs, queue IDs, and config values come from Custom
  Metadata, Custom Labels, or a lookup, never a pasted 15/18-char Id that breaks between orgs.
- **Null-safe.** Check for empty collections / null lookups before using them.

## Maintainability

- **Name + describe everything.** Flow API name, every element, and every variable get clear names
  and a description. Future-you (and the reviewer) reads the canvas cold.
- **Subflows for reuse.** Factor shared logic into autolaunched subflows instead of copy-pasting.
- **One responsibility per Flow.** If it's doing three unrelated things, split it.

## Testing + deployment

- **Flow Tests** (API 65+) let you assert record-triggered Flow outcomes declaratively; add them for
  meaningful branches. Otherwise cover the Flow's effects with an Apex test that performs the DML that
  triggers it and asserts the result.
- Deploy Flows as **Active** deliberately; know that deploying a new version and activating it are
  distinct, and that inactive prior versions accumulate. Confirm the active version post-deploy.

## Review-mode checklist

- Any DML / Get / Action **inside a loop**? (blocker)
- **Fault paths** on every failable element?
- Before-save used for same-record field updates?
- Entry conditions tight; recursion guarded?
- Hardcoded IDs? Named/described elements? Empty-collection checks?
- Multiple record-triggered Flows on this object with undefined order?
