---
name: apex-coding-standard
description: "Enforce and apply Salesforce Apex coding standards. Use this skill whenever the user shares Apex code for review, asks Claude to write new Apex code, mentions triggers, handler classes, SOQL queries, DML operations, test classes, or asks anything about Apex quality, structure, naming, or best practices. Always trigger this skill for any Apex-related task — even if the request seems simple like \"write me a trigger\" or \"does this code look ok?\". This skill covers both REVIEWING existing code (flagging every violation, no exceptions) and GENERATING new code that is fully compliant from the start."
---

# Apex Coding Standard Skill

This skill governs two modes:
1. **REVIEW MODE** — Audit existing Apex code and flag all violations strictly.
2. **GENERATE MODE** — Write new Apex code that is fully compliant from the start.

Detect the mode from context: if the user pastes code or asks "is this ok / review this", use REVIEW MODE. If they ask you to write/create code, use GENERATE MODE. If both, generate compliant code AND explain what was wrong with the original.

---

## THE STANDARD

### 1. Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Classes | Project prefix + PascalCase | `App_AccountService` |
| Triggers | `<Object>Trigger` | `AccountTrigger` |
| Trigger Handlers | `<Object>TriggerHandler` | `AccountTriggerHandler` |
| Test Classes | `<ClassName>Test` | `AccountServiceTest` |
| Methods | camelCase | `updateRelatedContacts()` |
| Variables / Properties | camelCase | `accountList` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| Custom Objects/Fields | Upper_Case_With_Underscores | `My_Custom_Field__c` |

**Rules:**
- All top-level class names must be prefixed with your project's class-name prefix (shown throughout this skill as `App_`; set it per project in the project's coding standard / CLAUDE.md) (e.g. `App_AccountService`, `App_BatchStepHandler`)
- **Inner classes must NOT use the `App_` prefix** — inner classes used to pass data back to the caller must be named `Result` (e.g. `public class Result { }`) and referenced as `ClassName.Result` by consumers
- No abbreviations unless universally known (e.g. `Id`, `DML`, `SOQL`)
- Names must be descriptive and self-documenting
- **No single-character variable names** — every variable must have a meaningful name that describes its purpose (e.g. `account` not `a`, `errorMessage` not `e`, `index` not `i`)
- Boolean variables/methods must start with `is`, `has`, or `can` (e.g. `isActive`, `hasRelatedRecords`)

---

### 2. Trigger Architecture

- **One trigger per object** — no exceptions. Multiple triggers on the same object are a violation.
- **Logic-less triggers** — triggers must only route to a handler. Zero business logic inside the trigger file.
- **One trigger per object includes all events** — combine before insert, before update, after insert, etc. into a single trigger.

**Compliant trigger pattern:**
```apex
trigger AccountTrigger on Account (
    before insert, before update, before delete,
    after insert, after update, after delete, after undelete
) {
    AccountTriggerHandler handler = new AccountTriggerHandler();
    handler.run();
}
```

**Handler class pattern:**
```apex
public with sharing class AccountTriggerHandler {
    public void run() {
        if (Trigger.isBefore) {
            if (Trigger.isInsert) { onBeforeInsert(); }
            if (Trigger.isUpdate) { onBeforeUpdate(); }
        }
        if (Trigger.isAfter) {
            if (Trigger.isInsert) { onAfterInsert(); }
            if (Trigger.isUpdate) { onAfterUpdate(); }
        }
    }
    private void onBeforeInsert() { /* logic here */ }
    private void onAfterInsert() { /* logic here */ }
    private void onBeforeUpdate() { /* logic here */ }
    private void onAfterUpdate() { /* logic here */ }
}
```

---

### 3. Bulkification (Governor Limit Safety)

**Violations — flag all of these:**
- SOQL query inside a `for` loop
- DML statement inside a `for` loop
- Using `Trigger.new[0]` (assumes single record — never valid)
- `Database.query()` inside a loop

**Compliant pattern:**
```apex
// ❌ VIOLATION
for (Account acc : Trigger.new) {
    List<Contact> contacts = [SELECT Id FROM Contact WHERE AccountId = :acc.Id];
}

// ✅ COMPLIANT
Set<Id> accountIds = new Map<Id, Account>(Trigger.new).keySet();
Map<Id, List<Contact>> contactsByAccount = new Map<Id, List<Contact>>();
for (Contact c : [SELECT Id, AccountId FROM Contact WHERE AccountId IN :accountIds]) {
    if (!contactsByAccount.containsKey(c.AccountId)) {
        contactsByAccount.put(c.AccountId, new List<Contact>());
    }
    contactsByAccount.get(c.AccountId).add(c);
}
```

---

### 4. Security

- All classes must declare `with sharing` or `without sharing` explicitly — never omit it.
- Default to `with sharing` unless there is a documented business reason for `without sharing`.
- Never use dynamic SOQL without sanitizing input (SOQL injection risk).
- Never hardcode record IDs, org-specific IDs, or profile IDs — use Custom Metadata or Custom Settings.
- Respect CRUD and FLS where applicable (use `Schema.SObjectType` checks or Security.stripInaccessible).

```apex
// ❌ VIOLATION — no sharing keyword
public class AccountService { }

// ✅ COMPLIANT
public with sharing class AccountService { }
```

---

### 5. Exception Handling

**Any operation that can throw must be wrapped in a try-catch. No exceptions (pun intended).**

#### Operations that MUST have try-catch:

| Operation Type | Examples |
|---|---|
| DML statements | `insert`, `update`, `delete`, `upsert`, `merge`, `undelete` |
| Database methods | `Database.insert()`, `Database.update()`, `Database.delete()`, `Database.upsert()` |
| HTTP / API callouts | `Http.send()`, any `HttpRequest` execution |
| External service calls | Any class making REST/SOAP callouts |
| Dynamic SOQL | `Database.query()` — can throw `QueryException` |
| JSON parsing | `JSON.deserialize()`, `JSON.deserializeStrict()` — can throw `JSONException` |
| Type casting | `(MyType) obj` — can throw `TypeException` |
| Queueable / Future / Batch logic | Any async Apex with DML or callout inside |

**Rules:**
- Never swallow exceptions silently — empty catch blocks are a **🔴 Critical** violation.
- Catch the **most specific** exception type available (e.g. `DmlException`, `CalloutException`, `QueryException`) before catching the generic `Exception`.
- Log every caught exception — at minimum `System.debug(LoggingLevel.ERROR, ...)`, ideally via a platform event or custom logging framework.
- Re-throw, surface via `ApexPages.addMessage`, or handle gracefully — never silently discard.
- When using `Database.*` methods with `allOrNone = false`, still wrap in try-catch AND check `Database.SaveResult` / `Database.DeleteResult` for row-level errors.

```apex
// ❌ VIOLATION — no try-catch on DML
update accounts;

// ❌ VIOLATION — empty catch (silent swallow)
try {
    update accounts;
} catch (Exception e) { }

// ❌ VIOLATION — callout with no try-catch
HttpResponse res = http.send(req);

// ❌ VIOLATION — JSON parse with no try-catch
MyWrapper w = (MyWrapper) JSON.deserialize(payload, MyWrapper.class);

// ✅ COMPLIANT — DML with specific exception type
try {
    update accounts;
} catch (DmlException e) {
    System.debug(LoggingLevel.ERROR, 'DML failed: ' + e.getMessage());
    throw e; // or handle gracefully
}

// ✅ COMPLIANT — HTTP callout
try {
    Http http = new Http();
    HttpResponse res = http.send(req);
    if (res.getStatusCode() != 200) {
        throw new CalloutException('Unexpected status: ' + res.getStatusCode());
    }
} catch (CalloutException e) {
    System.debug(LoggingLevel.ERROR, 'Callout failed: ' + e.getMessage());
    throw e;
}

// ✅ COMPLIANT — Database method with partial success + error checking
List<Database.SaveResult> results = Database.insert(records, false);
for (Database.SaveResult sr : results) {
    if (!sr.isSuccess()) {
        for (Database.Error err : sr.getErrors()) {
            System.debug(LoggingLevel.ERROR, 'Insert error: ' + err.getMessage());
        }
    }
}

// ✅ COMPLIANT — JSON parsing
try {
    MyWrapper w = (MyWrapper) JSON.deserialize(payload, MyWrapper.class);
} catch (JSONException e) {
    System.debug(LoggingLevel.ERROR, 'JSON parse failed: ' + e.getMessage());
    throw e;
}
```

---

### 6. SOQL Best Practices

- Always use `WHERE` clauses — never query all records of an object without filtering.
- Never use `SELECT *` patterns — only select fields you actually need.
- Use `LIMIT` when querying potentially large datasets.
- Use `FOR UPDATE` only when intentional record locking is needed.
- Prefer relationship queries over multiple separate queries.

---

### 7. Asynchronous Apex

- Use `@future`, `Queueable`, `Batchable`, or `Schedulable` for long-running or resource-intensive operations.
- `@future` methods must be `static` and accept only primitive types or collections of primitives (no SObject parameters).
- Batch Apex `execute()` must be bulk-safe and handle partial failures.
- Always implement `Database.Stateful` in Batch classes when state must persist across batches.

---

### 8. Test Classes

- Minimum **75% code coverage** required by Salesforce; target **90%+**.
- Test classes must use `@isTest` annotation.
- Use `@TestSetup` for shared test data — do not repeat data creation in every test method.
- Use **Test Data Factories** (a dedicated `TestDataFactory` class) — never hardcode test records inline.
- Every test method must have at least one `System.assert`, `System.assertEquals`, or `System.assertNotEquals`.
- Test both **positive** (happy path) and **negative** (error/edge) scenarios.
- Never use `SeeAllData=true` unless absolutely unavoidable and documented.
- Test method names must describe what they test: `testUpdateAccount_withNullName_shouldThrowException()`.

```apex
// ❌ VIOLATION
@isTest
static void test1() {
    Account a = new Account(Name='Test');
    insert a;
    // no assertions
}

// ✅ COMPLIANT
@isTest
static void testInsertAccount_withValidName_shouldSucceed() {
    Account acc = TestDataFactory.createAccount('Test Corp');
    Test.startTest();
    insert acc;
    Test.stopTest();
    Account result = [SELECT Id, Name FROM Account WHERE Id = :acc.Id];
    System.assertEquals('Test Corp', result.Name, 'Account name should match');
}
```

---

### 9. Code Comments & Documentation

- **Do not add unnecessary comments** — if the code is self-explanatory through clear naming, no comment is needed. Over-commenting clutters the code and creates maintenance burden when logic changes but comments do not.
- Comments must only be added when the logic is genuinely complex or non-obvious — explain the **why**, not the **what**.
- Never write comments that simply restate what the code does (e.g. `// loop through accounts`, `// set the name`, `// return result`).
- Never add section-divider comments or header comments for straightforward methods.

```apex
// ❌ VIOLATION — comment restates the obvious
// Loop through all accounts and update the name
for (Account acc : accounts) {
    acc.Name = acc.Name.trim(); // trim whitespace from name
}

// ❌ VIOLATION — unnecessary method header comment
// This method returns the account name
public String getAccountName() {
    return this.accountName;
}

// ✅ COMPLIANT — comment explains a non-obvious constraint
// Auth.SessionManagement requires without sharing to operate across session context
public without sharing class App_TotpVerificationController { }

// ✅ COMPLIANT — comment explains why a specific value is used
// Offset pads the last digit which is visually clipped due to letter-spacing
padding: 0.875rem 1rem 0.875rem 1.6rem;
```

---

### 10. Recipe Pattern — Main Function Structure

**Every method must read like a recipe.** The main (public) method should contain only high-level steps — each step delegates to a private helper. A reader should be able to understand the full flow from the main method alone without reading any sub-function. Sub-functions are the ingredients; the main function is the recipe.

**Rules:**
- The main method must not contain inline business logic — it orchestrates calls to private helpers.
- Each private helper must do exactly one thing and be named to describe that thing.
- The main method should read top-to-bottom as a sequence of plain-English steps.
- Helpers must not call other helpers in a deep chain — max one level of helper nesting below the main function.

```apex
// ❌ VIOLATION — all logic crammed into one method
@AuraEnabled
public static Result submitBatch(Id batchId) {
    Result result = new Result();
    Batch_Production_Record__c batch = [SELECT Id, Status__c, Phase__c FROM Batch_Production_Record__c WHERE Id = :batchId];
    if (batch.Status__c != 'In Progress') {
        result.success = false;
        result.errorMessage = 'Batch must be In Progress.';
        return result;
    }
    batch.Status__c = 'Submitted';
    batch.Submitted_Date__c = Date.today();
    try {
        update batch;
        result.success = true;
    } catch (DmlException dmlException) {
        result.success = false;
        result.errorMessage = dmlException.getMessage();
    }
    return result;
}

// ✅ COMPLIANT — main function reads like a recipe
@AuraEnabled
public static Result submitBatch(Id batchId) {
    Result result = new Result();
    Batch_Production_Record__c batch = fetchBatch(batchId);
    if (!isBatchEligibleForSubmission(batch)) {
        return buildErrorResult(MSG_BATCH_NOT_ELIGIBLE);
    }
    prepareBatchForSubmission(batch);
    return saveBatch(batch);
}

private static Batch_Production_Record__c fetchBatch(Id batchId) {
    return [SELECT Id, Status__c, Phase__c FROM Batch_Production_Record__c WHERE Id = :batchId];
}

private static Boolean isBatchEligibleForSubmission(Batch_Production_Record__c batch) {
    return batch.Status__c == 'In Progress';
}

private static void prepareBatchForSubmission(Batch_Production_Record__c batch) {
    batch.Status__c = 'Submitted';
    batch.Submitted_Date__c = Date.today();
}

private static Result saveBatch(Batch_Production_Record__c batch) {
    Result result = new Result();
    try {
        update batch;
        result.success = true;
    } catch (DmlException dmlException) {
        result.success = false;
        result.errorMessage = dmlException.getMessage();
    }
    return result;
}

private static Result buildErrorResult(String message) {
    Result result = new Result();
    result.success = false;
    result.errorMessage = message;
    return result;
}
```

---

### 11. Return Value Naming

**Methods must always return a named variable called `result` — never return an expression directly.**

Returning a raw expression (ternary, method call, inline construction) skips the explicit assignment and makes the return value harder to read, debug, and extend.

```apex
// ❌ VIOLATION — returning an expression directly
return isValid ? buildSuccessResult() : buildErrorResult(MSG_INCORRECT_CODE);

// ❌ VIOLATION — returning an inline construction
return new Result();

// ❌ VIOLATION — returning a method call directly
return buildErrorResult(MSG_INVALID_CODE);

// ✅ COMPLIANT — always assign to result first, then return
Result result = isValid ? buildSuccessResult() : buildErrorResult(MSG_INCORRECT_CODE);
return result;

// ✅ COMPLIANT
Result result = buildErrorResult(MSG_INVALID_CODE);
return result;
```

---

### 12. General Code Quality

- No magic numbers or magic strings — assign to a named constant.
- Methods must do one thing — split methods exceeding ~30 lines into smaller helpers.
- No deeply nested logic (max 3 levels of nesting) — extract to methods.
- **Never add `System.debug` statements** — debug logs must not be written at any stage of development. Use a proper logging framework or platform events if runtime observability is needed.
- Classes should follow Single Responsibility Principle — one class, one purpose.

---

## REVIEW MODE — How to conduct a review

When reviewing code, produce a structured report using this format:

```
## Apex Code Review

### 🔴 Critical Violations (must fix before deployment)
- [Line X] <violation description> — <compliant alternative>

### 🟡 Standard Violations (must fix per coding standard)
- [Line X] <violation description> — <compliant alternative>

### 🟢 Suggestions (good practice improvements)
- <suggestion>

### Summary
X critical violations, Y standard violations, Z suggestions.
[Overall verdict: PASS / FAIL]
```

Rules for review:
- Flag **every** violation — no exceptions, no skipping minor issues.
- Always provide the compliant fix alongside the violation.
- A verdict of PASS requires zero critical and zero standard violations.
- Be specific: reference line numbers or code snippets.

---

## GENERATE MODE — How to write compliant code

When generating new Apex code:
1. Apply ALL rules from this standard from the start.
2. Include the class/method header comments.
3. Use `with sharing` by default.
4. Structure triggers with handler pattern.
5. Write bulk-safe code (no SOQL/DML in loops).
6. Wrap ALL DML, callouts, JSON parsing, type casts, and any other exception-prone operations in try-catch with specific exception types and proper logging — never leave them bare.
7. If generating a trigger, also generate the handler class skeleton.
7. If generating a class, offer to generate the test class as well.
8. Briefly annotate the code to show which standard rules are being applied.

---

## Quick Reference — Common Violations Checklist

| # | Violation | Severity |
|---|---|---|
| 1 | SOQL inside loop | 🔴 Critical |
| 2 | DML inside loop | 🔴 Critical |
| 3 | Missing `with sharing` / `without sharing` | 🔴 Critical |
| 4 | Hardcoded IDs | 🔴 Critical |
| 5 | Logic inside trigger (not handler) | 🔴 Critical |
| 6 | Multiple triggers on same object | 🔴 Critical |
| 7 | Empty catch block | 🔴 Critical |
| 8 | Test class with no assertions | 🔴 Critical |
| 9 | `SeeAllData=true` without justification | 🔴 Critical |
| 10 | Class name missing `App_` prefix | 🟡 Standard |
| 10a | Missing class header comment | 🟡 Standard |
| 11 | Non-descriptive variable/method names | 🟡 Standard |
| 11a | Single-character variable name (e.g. `e`, `a`, `i`) — use a meaningful name | 🔴 Critical |
| 12 | No WHERE clause in SOQL | 🟡 Standard |
| 13 | Missing try-catch on DML / callout / JSON parse / type cast | 🔴 Critical |
| 13a | Empty catch block (silent exception swallow) | 🔴 Critical |
| 14 | `@future` with SObject parameters | 🟡 Standard |
| 15 | No `@TestSetup` / inline test data | 🟡 Standard |
| 16 | Test method name is non-descriptive | 🟡 Standard |
| 17 | Magic numbers/strings | 🟡 Standard |
| 18 | Unnecessary comments that restate what the code does — remove them | 🔴 Critical |
| 18a | Main method contains inline business logic instead of delegating to private helpers (recipe pattern) | 🔴 Critical |
| 18b | Method returns an expression directly instead of assigning to a named `result` variable first | 🔴 Critical |
| 18b | Method exceeds ~30 lines | 🟢 Suggestion |
| 19 | Nesting deeper than 3 levels | 🟢 Suggestion |
| 20 | `System.debug` left in production code | 🟢 Suggestion |