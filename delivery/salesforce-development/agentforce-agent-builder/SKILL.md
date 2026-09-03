---
name: agentforce-agent-builder
description: >-
  Build, edit, debug, and ship a Salesforce **Agentforce** agent the source-first way:
  Agent Script (`.agent` AiAuthoringBundle) + Apex invocable actions, published and
  activated with `sf agent`, deployed to a Messaging-for-Web (MIAW) channel. Use whenever
  the work touches an Agentforce agent: authoring/editing a `.agent` bundle, adding topics
  or actions, wiring Apex invocable actions, publishing/activating a new agent version,
  designing the conversation flow, or fixing agent behavior (out-of-order questions, not
  calling an action, repetitive/robotic tone, duplicate records, transcript capture), the
  MIAW channel/embed, or verifying an agent before it goes in front of a client. Trigger
  phrases: "Agentforce agent", "agent script", "`.agent`", "add a topic/action",
  "publish/activate the agent", "the bot is asking things out of order", "agent isn't
  calling the action", "make the agent more natural", "messaging for web", "chat transcript".
  Encodes hard-won lessons from full production Agentforce deliveries.
---

# Agentforce Agent Builder

Source-first playbook for building Agentforce Service Agents that hold up in production.
Distilled from full delivery cycles: build, go-live, and hypercare loops where several
well-intentioned instruction changes caused regressions before the flow was stabilized.

## Golden rules — read first

1. **Over-prompting is the #1 cause of flaky agents.** Piling on `MUST` / `NEVER` / `REQUIRED`
   guards to fix one behavior destabilizes others. When an agent goes out of order, bundles
   questions, or wraps up early, the fix is almost always to **remove and consolidate** the
   instructions into one clean, linear flow, not add another guard. Change one thing at a time;
   every change can introduce a new regression.
2. **`publish` does NOT activate.** `sf agent publish` creates a new *inactive* version. You must
   then `sf agent activate --api-name <Api> --version <N>`. Forgetting this is the usual reason "my
   change didn't take effect." Versions increment on every publish.
3. **Put critical/deterministic logic in Apex, not the LLM.** Anything that must happen every time
   (deduplication, required-field enforcement, ID threading, picklist mapping) belongs in the
   invocable action. Never rely on the model to "remember to pass the Id" or "always call X".
4. **Verify before it goes to the client.** The regression spiral comes from shipping unverified
   agent changes. Drive a real conversation and check actual records/behavior, not just that it
   validated (see *Testing & verification*).
5. **Validate against real records, not vibes.** When debugging, pull the actual records the test
   produced and inspect field-by-field + created-vs-modified timestamps (created≈modified = single
   insert; a gap = create-then-enrich). The on-screen chat can look fine while data silently drops.

## Source-first workflow

Author the agent as an **Agent Script `.agent`** file in `aiAuthoringBundles/<Name>/`, version-
controlled, not click-built. Cycle:

```
# edit force-app/main/default/aiAuthoringBundles/<Name>/<Name>.agent
sf agent validate authoring-bundle --api-name <Name> --target-org <org>
sf agent publish  authoring-bundle --api-name <Name> --target-org <org>   # NEW inactive version
sf agent activate --api-name <Name> --version <N>   --target-org <org>    # <-- REQUIRED, easy to forget
```

- Publishing also writes `bots/<Name>/vN.botVersion` + `genAiPlannerBundles/<Name>_vN` into source.
  Commit those with the `.agent`.
- The active version is what the channel serves. Confirm:
  `SELECT VersionNumber, Status FROM BotVersion WHERE BotDefinition.DeveloperName='<Name>'`.

## Agent Script structure

- **`system.instructions`** — persona + global guardrails. Keep tone rules short: *default to no
  acknowledgement opener; never repetitive/awkward pleasantries; never celebratory in sensitive
  contexts.*
- **`system.messages.welcome`** — the opening line(s).
- **Topics** — each has `reasoning.instructions` (the flow) + an `actions` block. Instructions are
  where people over-engineer; keep them **linear and single-purpose**.
- **Action bindings** — `ActionName: @actions.ActionName`, then `with input = ...` (agent-supplied) or
  `with input = @variables.X` (context, e.g. `RoutableId` = MessagingSession Id). Input defs set
  `is_user_input: True` (agent fills from the conversation) or `False` (system/context, never asked).

## Apex invocable actions

- Thin, deterministic, `@InvocableMethod`. Prefer **one orchestrator** the agent calls at the end
  (composing granular actions) over many chatty actions.
- **Guard premature/incomplete calls:** return a `NeedsInfo` result naming the missing field so the
  agent asks for it. Don't create partial records. Never accept blank / "unknown" / made-up values.
- **Deduplicate in Apex, deterministically.** If two actions can create the same record (early-save +
  enrich), key off a stable id (the messaging session) and *enrich the existing record when no
  explicit Id was passed*. Don't trust the LLM to thread the Id. (Pattern: an intake action falls
  back to the record already tied to the chatbot session id on the record.)
- **Querying Data Cloud from Apex:** use `ConnectApi.CdpQuery.queryANSISqlV2`. The default
  `queryANSISql` output rows are NOT Apex-consumable; V2's `CdpQueryV2Row.rowData` is a clean
  positional list.

## Conversation design (what actually reads well)

- **One question per turn, fixed order.** Don't skip, reorder, combine, or wrap up until every
  required item is collected.
- **Create early, enrich later.** Save the record the moment you can identify the person (name +
  phone/email) so a drop-off isn't lost; enrich at the end. Dedup in Apex (above).
- **Gate the closing.** Never say "someone will reach out / you're all set" until the
  create/complete action returned success in the *same turn*. Premature wrap-up (then asking for a
  missed field) is the classic over-prompting symptom.
- **Natural tone:** most turns just answer + ask the next question with no opener. Vary any
  acknowledgement; never repeat "Thanks / Thank you / Understood" back-to-back; never "Perfect /
  Great" in sensitive moments.
- The agent **cannot capture its own final message** or anything after it. Don't design around that.

## Testing & verification

- **Prod deploy needs ≥75% Apex coverage + passing tests.** For actions calling `ConnectApi` or other
  un-mockable APIs, isolate the call behind a `@TestVisible` seam and inject mock rows in tests.
- **`sf agent test` (Testing Center) may not be enabled** in a given org ("Not available for deploy").
  Don't assume it's there.
- **`sf agent preview` needs a real TTY** — it uses an Ink UI and errors on piped stdin, so it can't
  be driven headlessly. A human runs it in a terminal; `--output-dir` saves the transcript to read.
- **You cannot browser-drive the MIAW widget** — the chat renders in a **cross-origin iframe**; a11y
  snapshots and page JS can't reach it. Verify via `sf agent preview` (human) or by inspecting the
  records a real chat produced.
- After any behavior change: run a real conversation, then **pull the created record and check every
  field + the created/modified timestamps** before telling the client it's fixed.

## MIAW channel, attribution & transcript gotchas

- **Custom-parameter passthrough (e.g. GCLID):** custom parameters + parameter mappings alone are
  silently dropped. The value only arrives if it's ALSO a **hidden pre-chat field** on a
  **re-published** Embedded Service deployment. Any new passthrough param = redo hidden-field +
  re-publish.
- **Full transcript:** raw `ConversationEntry` is **not SOQL-queryable** for guest MIAW (0 rows).
  Enable *Share Conversation Transcripts with Data Cloud* and pull from the Data Cloud DLO
  (`CONVERSATION_ENTRY_<orgId15>__dll`) on a schedule. Ingest is **hourly** (not real-time), so keep
  an instant agent-written copy for the interim (pattern: a scheduled transcript-sync job).
- **Guest transcript download** can 403 (unauthenticated-messaging permission). Treat as a product
  limitation, not always a bug you can fix.
- Scheduled Apex can't call out directly, and one class can't be both `Schedulable` + `Queueable`. A
  thin Schedulable enqueues a callout-capable Queueable.

## Configurability

Keep business rules (ages, locations/zips, insurance, hours) in **admin-editable config**: Custom
Metadata Types + custom objects read by the actions, so the client changes criteria without a
deploy. Apex is the thin escape hatch, not the rulebook.

## Commands cheat-sheet

```
sf agent validate authoring-bundle --api-name <Name> -o <org>
sf agent publish  authoring-bundle --api-name <Name> -o <org>
sf agent activate --api-name <Name> --version <N> -o <org>
sf agent preview  --api-name <Name> -o <org> --output-dir <dir>   # human / real TTY only
sf data query -q "SELECT VersionNumber,Status FROM BotVersion WHERE BotDefinition.DeveloperName='<Name>'" -o <org>
```

## Reference layout

A production Agentforce delivery typically has:

- **Agent bundle:** `aiAuthoringBundles/<Name>/<Name>.agent` (+ generated `bots/`, `genAiPlannerBundles/`)
- **Actions:** an orchestrator class the agent calls at the end, composing granular action classes;
  a create/intake action with **session-based dedup**; a scheduled **transcript-sync** class pair
  (Schedulable enqueues a Queueable) if you capture full transcripts from Data Cloud
- **Config:** Custom Metadata Types + custom objects holding the editable business rules
- **Design docs:** the intake/conversation design, the transcript-sync design, and the
  configurability model, in the project's `technical-design/`
