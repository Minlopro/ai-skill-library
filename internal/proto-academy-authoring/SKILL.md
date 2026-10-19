---
name: proto-academy-authoring
description: >-
  Author Proto Academy content directly in the live Proto Salesforce org through
  the Salesforce Create/Edit/Read MCP connection, as a content creator (not a
  developer). Use when an Academy manager or content creator wants to create or
  update a training (course), step, quiz, evidence step with manager approval,
  learning path, or certification by writing records, without Apex seed scripts
  or metadata deploys. Covers the permission gate, the no-delete record-write
  order, the body-HTML and quiz rules, evidence + approval trainings,
  draft-and-confirm, and the data-only boundary.
---

# Proto Academy content authoring (production, via MCP)

Proto Academy is Minlopro's internal LMS, built natively on the Proto Salesforce
org. This skill is for a **content creator or Academy manager** authoring content
**directly in the live org** through a **Salesforce Create/Edit/Read MCP
connection**, by creating and updating records. It is the record-level
counterpart to the developer skill `proto-academy-content`, which builds content
as anonymous Apex seed scripts and deploys them in a sandbox. If you are a
developer seeding or changing engine logic, use that skill instead.

The MCP connection runs **as the signed-in user**, so Salesforce enforces that
user's object and field permissions on every write. This skill adds a human-level
playbook and guardrails on top of that enforcement.

## Non-negotiable guardrails

- **This writes to the live Proto org.** Everything here creates or edits real,
  learner-visible records. Treat it like editing production, because it is.
- **Permission gate.** Only proceed if the signed-in user holds the
  `Proto_Academy_Manager` permission set. Run the preflight below first and stop
  if it is not assigned.
- **Never delete records.** Idempotency here is query-then-update-or-create, never
  delete-and-reinsert. To unpublish a course set its `Status__c` away from
  `Active`; to drop a single step, hand it to a human in the Build UI. The skill
  does not delete.
- **Draft, then confirm, then write.** A course is many records (a bulk change).
  Draft the full thing (every step, every question) in the chat, show exactly what
  will be created or changed, get an explicit yes, then write.
- **No PHI, no client data.** Academy content is internal enablement. Never embed a
  client's name, a client's data, or any patient-level or regulated data in a
  training. Describe engagements by shape, not by name.
- **No em dashes or en dashes in learner-facing content.** Use commas, colons,
  parentheses, or full stops.
- **Data only.** You can write records. You cannot create fields or objects, deploy
  Apex or LWC, add picklist values, upload images, or change the certificate PDF.
  See "What this path cannot do" and hand those to a developer.

## Preflight (run every time, before any write)

1. **Confirm the org.** Call the connector's `getUserInfo`. Verify `companyName` is
   Minlopro and the username is the intended org (a sandbox username usually carries
   a `.sandbox` suffix; production does not). If it is not the org the user meant,
   stop and tell them to reconnect the MCP.
2. **Confirm the permission.** SOQL:
   ```sql
   SELECT PermissionSet.Name FROM PermissionSetAssignment
   WHERE AssigneeId = '<userId from getUserInfo>'
     AND PermissionSet.Name = 'Proto_Academy_Manager'
   ```
   If it returns no rows, stop: the user is not provisioned to author Academy
   content. Point them to whoever grants `Proto_Academy_Manager`.
3. **Confirm the field shape if unsure.** Use `getObjectSchema` on `Training__c`,
   `Training_Step__c`, etc. before writing, so you use fields that exist in this org
   rather than assuming. Field lists are in `references/data-model.md`.

## The write engine (MCP operations)

Use the connector's data operations, not Apex or the CLI:

- `soqlQuery` / `find` - look up existing parents and children (idempotency).
- `getObjectSchema` - confirm fields on an object.
- `createSobjectRecord` - create one record.
- `updateSobjectRecord` - edit one record by Id.

There is no transaction across calls, so write **parents before children** and keep
the created Ids to wire up the lookups.

### Write order for a full course

1. **Training__c** (the course). Query by `Name` first; if it exists, update it,
   otherwise create it. Keep it `Status__c = Draft` (or any non-Active value) while
   you build, and flip to `Active` only when it is ready to publish.
2. **Training_Step__c** - one per step, in order. Set `Training__c` to the course
   Id and `Sort_Order__c` to 10, 20, 30, ... (leave gaps so steps can be inserted
   later without renumbering). Match existing steps by (`Training__c`,
   `Sort_Order__c`) or (`Training__c`, `Title__c`) and update in place rather than
   creating duplicates.
3. **Training_Question__c** - if the course has a quiz. Set `Training__c`,
   `Sort_Order__c`, `Type__c = Single`.
4. **Training_Answer_Option__c** - the options for each question. Set
   `Training_Question__c`, `Sort_Order__c`, `Answer_Text__c`, and `Is_Correct__c`.
   **Exactly one option per question** has `Is_Correct__c = true`.
5. **Learning_Path__c** and **Learning_Path_Item__c** - optional track. Create the
   path, then one item per training with `Sort_Order__c` and `Required__c`.
6. **Academy_Certification__c** - optional credential definition, mapped to the
   `Training__c` or `Learning_Path__c` that earns it. Credentials
   (`Academy_Credential__c`) are issued automatically when a learner completes, so
   you only author the definition, never the earned credential.

### Idempotency without deletes

- Always query for the record first (by `Name` for parents, by parent + sort order
  or title for children). Update when found, create when not.
- To retire a course, set `Status__c` to a non-Active value. Do not delete it.
- To reorder steps, update `Sort_Order__c`. To truly remove a step, ask a human to
  delete it in the Proto Academy Build UI; this skill does not delete records.

## Content rules

### Step bodies (`Body__c`)

`Body__c` renders through `lightning-formatted-rich-text`, a subset of HTML:

- Use `<p>`, `<b>`, `<i>`, `<ul>` / `<ol>` / `<li>`, `<a href>`. These render.
- **Do not use `<table>` or inline `style=`.** They do not render reliably. For a
  matrix, use bold section headers with `<ul>` lists instead.
- Keep paragraphs short; lead each section with a bold label.
- No em or en dashes. Use straight quotes.

### Step kinds and styling

- `Kind__c` is `Intro` (welcome), `Content` (the teaching), `Tool` (a Delivery
  Excellence tool deep dive, can use the tool-step fields), `Outro` (wrap and
  next steps), or `Evidence` (the learner uploads a file to submit for manager
  approval; see "Evidence steps and manager approval"). A typical course is
  Intro, several Content steps, Outro.
- `Icon__c` is an SLDS utility name (`utility:info`, `utility:shield`,
  `utility:success`, ...). `Accent_Color__c` is a hex string like `#5a3fa0`.

### Quizzes

- On the course set `Requires_Quiz__c = true` and `Passing_Score__c` (a percent).
- Grading is server-side. Exactly one option per question is correct.
- Vary which position the correct option sits in across questions so it is not
  always first. `Explanation__c` on the question is shown after answering.

### Learning paths

- `LearningPathController.getMyPaths` returns all `Active` paths to every learner;
  per-item availability follows each training's `Status__c` and the learner's
  assignment. Keep a path non-Active until it is ready, or gate rollout with an
  `Academy_Rule__c`.

## Evidence steps and manager approval

Some trainings require the learner to upload proof of a hands-on exercise (for
example a scorecard screenshot) and have a manager approve it before they are
marked complete. The evidence engine handles the upload, the review queue, the
approval, and the bell notifications. You author it as data:

1. On the `Training__c`, set `Requires_Manager_Approval__c = true`.
2. Add a `Training_Step__c` with `Kind__c = 'Evidence'` as the **last step**. Put
   the upload instructions in `Body__c` (same body-HTML rules as any step), for
   example "Upload a screenshot of your completed scorecard." Give it a clear
   `Title__c`.
3. Leave the quiz off for an approval training (`Requires_Quiz__c = false`): the
   Evidence step is the terminal gate, so a quiz on the same training is skipped.

What the engine then does (not you):
- The learner uploads a file on the Evidence step and submits. The assignment
  moves to **Submitted for Approval** (not Completed), and the learner's manager
  gets a bell notification.
- A reviewer (the learner's direct manager, or any Proto Academy manager) sees it
  in the **Evidence Review** queue on the Manage Training page and approves or
  rejects. **Approve** completes the assignment and issues any mapped
  certification, and the learner gets a bell. **Reject** sends it back with a
  required note; the learner gets a bell with the reason and a banner on the
  Evidence step to redo and resubmit.

Rules and limits:
- Keep the Evidence step **last**; the engine treats it as the terminal action.
- Point a `Academy_Certification__c` at the training (as usual) if you want
  approval to award a credential. It issues on completion, which here means on
  approval.
- `Training_Evidence__c` rows are **engine-managed**: the learner's upload creates
  them and the reviewer updates them. Never create, edit, or delete evidence
  records by hand (the no-delete rule applies, and hand-editing breaks the flow).
- Review routing uses `Contact.Contact_User_Record__c` then `User.ManagerId`.
  Where a learner has no manager on file, review falls back to Academy managers.
- If `Requires_Manager_Approval__c` or the `Evidence` step kind is missing in your
  org, the evidence engine has not been deployed there. That is a developer task
  (see `proto-academy-content`), not something you can configure as data.

## What this path cannot do (hand off to a developer)

The MCP writes data. These are metadata or code and need the developer skill
`proto-academy-content` plus a deploy:

- New fields, objects, or picklist values.
- Apex, LWC, or the Visualforce certificate PDF.
- Uploading screenshots or images (static resources / ContentVersion). You can set
  `Video_Url__c` (a URL) on a step, but image upload is a developer task.
- Auto-assign rule execution plumbing, analytics, or any logic change.

When a request needs one of these, say so plainly and route it to a developer
rather than faking it.

## Publish and verify

1. Flip `Training__c.Status__c` to `Active` only when the course is complete and
   reviewed.
2. Verify by querying back what you wrote (course, step count, question count,
   exactly one correct option per question) and read it against the draft the user
   approved.
3. Report what was created or changed (record names and Ids), and confirm the
   course is visible on **Academy Home** for learners once Active.

## Default authoring loop

1. Preflight: confirm org and `Proto_Academy_Manager`.
2. Confirm scope with the user (topic, audience, quiz? cert? path?).
3. Draft the full content (em-dash-free, body-HTML rules above).
4. Show exactly what will be created or changed, and get an explicit yes.
5. Write parents before children, idempotently, no deletes.
6. Publish (`Status__c = Active`) and verify by querying it back.
7. Report record names and Ids and leave anything metadata or code to a developer.
