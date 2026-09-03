---
name: apex-test-authoring
description: >-
  Write meaningful Salesforce Apex test classes: real assertions and realistic data, not just
  coverage padding. Use whenever the user asks to write tests for Apex, fix failing tests or low
  coverage, prepare a class for a production deploy, or mentions test classes, @isTest,
  @TestSetup, Test.startTest/stopTest, mocking callouts, or code coverage. Covers GENERATE mode
  (author compliant tests from the start) and REVIEW mode (flag weak or missing tests).
---

# Apex Test Authoring

Coverage is the floor, not the goal. A good test proves the code does the right thing and fails
loudly when it doesn't. 90% coverage with no assertions is worthless.

## Non-negotiables

- **Assert real outcomes.** Every test ends in `System.assertEquals(expected, actual, 'message')`
  on the behavior that matters (the record was updated, the total is right, the error was thrown).
  A test with no asserts, or only "it didn't throw", is a coverage stunt, not a test.
- **Make your own data.** `@isTest` classes see no org data by default (never set `SeeAllData=true`).
  Create the records the test needs. Centralize shared setup in a `@TestSetup` method or a reusable
  test-data factory so tests stay readable and consistent.
- **Wrap the exercise in `Test.startTest()` / `Test.stopTest()`.** It gives the code under test a
  fresh set of governor limits and forces async work (`@future`, Queueable, Batch, scheduled) to
  run before `stopTest()` returns so you can assert on its results.
- **Test behavior, not lines.** One test method per behavior, named for it
  (`reopeningAPaidLineIsBlocked`), following arrange / act / assert.

## What to cover

- **Positive path** — valid input produces the right records/values.
- **Negative path** — invalid input is rejected; assert the exception with
  `try { ... System.assert(false,'should have thrown'); } catch (Ex e) { System.assert(e.getMessage().contains('...')); }`.
- **Bulk** — insert ~200 records and assert the batch result. This catches SOQL/DML-in-loop and
  governor-limit bugs single-record tests miss. Triggers and services must be tested in bulk.
- **Edge cases** — nulls, empty collections, boundary values, duplicates, mixed valid/invalid in one
  DML (`Database.insert(list, false)` partial success).
- **Permissions/sharing** when relevant — use `System.runAs(user)` to test as a specific profile/
  permission set. (Note: `System.runAs` only works inside a test method, and Apex ignores FLS in
  system context unless you opt into user mode.)

## Mocking the un-mockable

- **Callouts:** implement `HttpCalloutMock` (or `Test.createStub` for interfaces) and register it
  with `Test.setMock` before the call.
- **ConnectApi / Metadata / other un-mockable classes:** isolate the call behind a `@TestVisible`
  seam (a method or injectable variable) and feed mock results in the test. Tests run in system mode,
  so they pass while a user-mode caller would still hit FLS — don't let a green test hide that.

## Common failure causes (fix the data, not the assert)

- **Required fields / validation rules** — build records that satisfy every active rule, or the
  insert fails before your logic runs.
- **Restricted picklists** — use a currently-active value; a removed value throws
  `INVALID_OR_NULL_FOR_RESTRICTED_PICKLIST`.
- **Formula / roll-up / auto-number fields** — read-only; you can't set them. Set the inputs and let
  them compute.
- **Long-text / rich-text fields** — can be selected but **not filtered** in SOQL (`WHERE Body__c = ...`
  fails). Filter on something else.
- **Org automation** — flows, triggers, and processes fire during your inserts; build data that
  survives them, or the test fails for reasons unrelated to the class under test.

## Running + coverage gate

```
sf apex run test -o <org> --tests <TestClass> --result-format human --code-coverage --synchronous
```

A **production deploy requires ≥75% coverage on each changed class AND all specified tests passing**;
`RunSpecifiedTests` runs only the tests you name, so name the ones that cover the deployed classes.
Coverage is enforced per class, so a well-covered class can still block a deploy if a *co-deployed*
class is under 75% — include its test too.

## Review-mode checklist

- Are there asserts, and do they check the *outcome* (not just "ran")?
- Is there a bulk (200) test for anything that does DML/SOQL?
- Negative + edge cases present?
- Any `SeeAllData=true`, empty catch blocks, or `assert(true)` filler? Flag them.
- Do callouts/ConnectApi use mocks behind a seam?
