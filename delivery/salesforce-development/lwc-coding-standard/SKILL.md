---
name: lwc-coding-standard
description: "Enforce and apply Salesforce Lightning Web Components (LWC) coding standards. Use this skill whenever the user shares LWC code for review, asks Claude to write a new LWC component, mentions component structure, wire service, custom events, pubsub, decorators (@api, @track, @wire), LWC Apex integration, LWC performance, accessibility, or asks anything about LWC quality or best practices. Always trigger this skill for any LWC-related task — even if the request seems simple like 'write me a component' or 'does this look ok?'. This skill covers both REVIEWING existing LWC code (flagging every violation, no exceptions) and GENERATING new LWC code that is fully compliant from the start."
---

# LWC Coding Standard Skill

This skill governs two modes:
1. **REVIEW MODE** — Audit existing LWC code and flag all violations strictly.
2. **GENERATE MODE** — Write new LWC components that are fully compliant from the start.

Detect the mode from context: if the user pastes code or asks "is this ok / review this", use REVIEW MODE. If they ask you to write/create a component, use GENERATE MODE. If both, generate compliant code AND explain what was wrong with the original.

---

## THE STANDARD

### 1. Component File Structure & Naming

Every LWC component is a **folder** — the folder name IS the component name.

| File | Required | Purpose |
|---|---|---|
| `componentName.html` | ✅ Yes | Template |
| `componentName.js` | ✅ Yes | Controller logic |
| `componentName.js-meta.xml` | ✅ Yes | Component metadata |
| `componentName.css` | ❌ Optional | Scoped styles |
| `componentName.svg` | ❌ Optional | Custom icon |

**Naming rules:**
- Folder and file names must use **camelCase** (e.g. `myAccountCard`, not `MyAccountCard` or `my-account-card`)
- In HTML templates, components are referenced in **kebab-case**: `<c-my-account-card>`
- No abbreviations unless universally known
- Names must be descriptive and self-documenting
- **No single-character variable names** — every variable, parameter, and constant must have a meaningful name that describes its purpose (e.g. `error` not `e`, `account` not `a`, `index` not `i`)
- **Use `_` prefix only for private methods and properties** — prefix a method or property with `_` only when it is used exclusively inside the `.js` file and is never referenced in the `.html` template. Methods and properties bound in the template (event handlers, getters, reactive properties) must NOT have a `_` prefix.

```js
// ❌ VIOLATION — _showError is called from the template (onclick etc.) so no _ prefix
<lightning-button onclick={_handleSave}></lightning-button>

// ❌ VIOLATION — isVerifyDisabled is bound in HTML so no _ prefix
_isVerifyDisabled = false; // used as {_isVerifyDisabled} in template

// ✅ COMPLIANT — handleSave is bound in HTML, no underscore
handleSave() { ... }

// ✅ COMPLIANT — _buildPayload is only called from within the .js file, never from HTML
_buildPayload() { ... }

// ✅ COMPLIANT — isLoading is bound in HTML ({isLoading}), no underscore
isLoading = false;

// ✅ COMPLIANT — _cachedData is internal state never exposed to the template
_cachedData = null;
```
- **All constants must live in `constants.js`** — this includes constants used in the `.js` file AND any hardcoded labels, values, or strings used in the `.html` template. The goal is a single source of truth: every constant in one place. There are two accepted ways to expose a template-bound constant:
  1. **Per-constant getter** — import the constant in `.js`, assign it to a getter, and bind the getter in the template.
  2. **Grouped `CONSTANTS` object (preferred when several strings are template-bound)** — group the template-bound values into a single exported object in `constants.js` (e.g. `LABELS`), assign it to a `CONSTANTS` class property in `.js`, and bind nested properties directly in the template (`{CONSTANTS.headerTitle}`). LWC templates support nested object-property access, so this removes the getter boilerplate while keeping constants in `constants.js`. This is the preferred style when a component binds more than ~2 constant strings.

```
// ✅ COMPLIANT — file structure
myAccountCard/
  myAccountCard.html
  myAccountCard.js
  myAccountCard.js-meta.xml
  constants.js          ← ALL constants go here (JS and HTML)

// constants.js
const MAX_RETRY_COUNT    = 3;
const DEFAULT_PAGE_SIZE  = 10;
const LABEL_SAVE_BUTTON  = 'Save Record';
const LABEL_CARD_TITLE   = 'Account Details';
export { MAX_RETRY_COUNT, DEFAULT_PAGE_SIZE, LABEL_SAVE_BUTTON, LABEL_CARD_TITLE };

// myAccountCard.js — import constants, expose HTML-bound ones via getters
import { MAX_RETRY_COUNT, DEFAULT_PAGE_SIZE, LABEL_SAVE_BUTTON, LABEL_CARD_TITLE } from './constants';

export default class MyAccountCard extends LightningElement {
    get labelSaveButton() {
        const result = LABEL_SAVE_BUTTON;
        return result;
    }
    get labelCardTitle() {
        const result = LABEL_CARD_TITLE;
        return result;
    }
}

// myAccountCard.html — bind via getter, never hardcode
<lightning-card title={labelCardTitle}>
    <lightning-button label={labelSaveButton}></lightning-button>
</lightning-card>

// ✅ COMPLIANT (preferred for multiple template strings) — grouped CONSTANTS object
// constants.js
const LABELS = {
    cardTitle: 'Account Details',
    saveButton: 'Save Record'
};
export { LABELS, MAX_RETRY_COUNT, DEFAULT_PAGE_SIZE };

// myAccountCard.js — assign the imported object to a CONSTANTS property, no getters
import { LABELS } from './constants';
export default class MyAccountCard extends LightningElement {
    CONSTANTS = LABELS;
}

// myAccountCard.html — bind nested properties directly
<lightning-card title={CONSTANTS.cardTitle}>
    <lightning-button label={CONSTANTS.saveButton}></lightning-button>
</lightning-card>

// ❌ VIOLATION — hardcoded string in HTML
<lightning-card title="Account Details">
    <lightning-button label="Save Record"></lightning-button>
</lightning-card>

// ❌ VIOLATION — constant defined inline in main .js
export default class MyAccountCard extends LightningElement {
    MAX_RETRY_COUNT = 3;
}
```

```
// ❌ VIOLATION — PascalCase folder
MyAccountCard/
  MyAccountCard.html

// ✅ COMPLIANT
myAccountCard/
  myAccountCard.html
  myAccountCard.js
  myAccountCard.js-meta.xml
  myAccountCard.css
```

---

### 2. JavaScript Class Structure

- One default-exported class per `.js` file, extending `LightningElement`.
- Import order: LWC core → Salesforce modules → Apex → utilities/constants.
- No logic in the class body outside of methods and decorated properties.
- Keep the class under ~200 lines — split into child components or utility modules if larger.
- **Methods must always return a named variable called `result` — never return an expression directly.** Returning a raw expression (ternary, inline construction, direct method call) skips the explicit assignment and makes the return value harder to read and debug.

```js
// ❌ VIOLATION — returning an expression directly
_isFormValid() {
    return this.recordId != null && this.name !== '';
}

// ❌ VIOLATION — returning a method call directly
_buildPayload() {
    return Object.assign({}, this.record, { updatedDate: new Date() });
}

// ✅ COMPLIANT — always assign to result first, then return
_isFormValid() {
    const result = this.recordId != null && this.name !== '';
    return result;
}

_buildPayload() {
    const result = Object.assign({}, this.record, { updatedDate: new Date() });
    return result;
}
```
- **Do not add unnecessary comments** — comments must only be added when the logic is genuinely complex or non-obvious. Never write comments that restate what the code does (e.g. `// call apex`, `// set loading to true`, `// dispatch event`). Explain the **why**, never the **what**.
- **Every handler method must read like a recipe** — the main handler (e.g. `handleSave`, `handleSubmit`) must contain only high-level steps, each delegating to a private helper method. Inline business logic inside a handler is a violation. Helper methods are the ingredients; the handler is the recipe.

```js
// ❌ VIOLATION — business logic crammed into the handler
async handleSave() {
    this.isLoading = true;
    if (!this.recordId || !this.name) {
        this.dispatchEvent(new ShowToastEvent({ title: 'Validation failed', variant: 'error' }));
        this.isLoading = false;
        return;
    }
    try {
        await saveRecord({ recordId: this.recordId, name: this.name });
        this.dispatchEvent(new ShowToastEvent({ title: 'Saved', variant: 'success' }));
        this.dispatchEvent(new CustomEvent('recordsaved'));
    } catch (saveError) {
        this.dispatchEvent(new ShowToastEvent({ title: saveError.body?.message, variant: 'error' }));
    } finally {
        this.isLoading = false;
    }
}

// ✅ COMPLIANT — handler reads like a recipe
async handleSave() {
    if (!this._isFormValid()) return;
    this.isLoading = true;
    try {
        await this._saveRecord();
        this._onSaveSuccess();
    } catch (saveError) {
        this._onSaveError(saveError);
    } finally {
        this.isLoading = false;
    }
}

_isFormValid() {
    if (!this.recordId || !this.name) {
        this._showToast('Validation failed', 'error');
        return false;
    }
    return true;
}

async _saveRecord() {
    await saveRecord({ recordId: this.recordId, name: this.name });
}

_onSaveSuccess() {
    this._showToast('Saved', 'success');
    this.dispatchEvent(new CustomEvent('recordsaved'));
}

_onSaveError(saveError) {
    this._showToast(saveError.body?.message ?? 'Save failed', 'error');
}

_showToast(message, variant) {
    this.dispatchEvent(new ShowToastEvent({ title: message, variant }));
}
```

```js
// ✅ COMPLIANT import order
import { LightningElement, api, wire, track } from 'lwc';
import { NavigationMixin } from 'lightning/navigation';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';
import { getRecord } from 'lightning/uiRecordApi';
import getAccounts from '@salesforce/apex/AccountController.getAccounts';
import ACCOUNT_NAME from '@salesforce/schema/Account.Name';
import { MY_CONSTANT } from 'c/myUtils';

export default class MyAccountCard extends LightningElement {
    // decorated properties first
    @api recordId;
    @track internalState = [];

    // getters
    get isReady() { return this.data != null; }

    // lifecycle hooks
    connectedCallback() { }
    disconnectedCallback() { }

    // wire handlers
    @wire(getRecord, { recordId: '$recordId', fields: [ACCOUNT_NAME] })
    wiredRecord;

    // event handlers (handle prefix)
    handleSave() { }

    // private methods last
    _formatData() { }
}
```

---

### 3. Decorator Usage (`@api`, `@track`, `@wire`)

#### `@api`
- Use for **public properties** exposed to parent components or App Builder.
- **Never mutate** an `@api` property from inside the component — treat as read-only.
- Public methods decorated with `@api` are allowed but must be documented.
- Validate `@api` inputs using getters/setters when constraints exist.

```js
// ❌ VIOLATION — mutating @api property
@api recordId;
connectedCallback() {
    this.recordId = '001...'; // VIOLATION
}

// ✅ COMPLIANT — copy to internal property
@api recordId;
_internalId;
connectedCallback() {
    this._internalId = this.recordId;
}
```

#### `@track`
- **Do not use `@track`** — as of Spring '20, Salesforce LWC tracks all property changes by default. Every property assignment (primitives, objects, arrays) already triggers re-render automatically. `@track` is fully redundant in virtually all cases and must not be added.
- The only narrow exception is **deep mutation of a nested object property without reassignment** (e.g. mutating `this.filters.status.active` in place without reassigning `this.filters`). Even then, prefer reassigning the object to trigger reactivity instead of using `@track`.
- Any use of `@track` that is not justified by the above exception is a **🔴 Critical** violation — remove it.

```js
// ❌ VIOLATION — @track on primitive (redundant, all primitives are reactive by default)
@track isLoading = false;
@track errorMessage = '';

// ❌ VIOLATION — @track on array (redundant, array reassignment is reactive by default)
@track accounts = [];

// ✅ COMPLIANT — plain properties, no @track needed
isLoading = false;
errorMessage = '';
accounts = [];

// ✅ COMPLIANT — the only justified @track use: deep nested mutation without reassignment
@track filters = { status: { active: true, closed: false } };
// ... later: this.filters.status.active = false; (mutating in place — @track justified here)

// ✅ BETTER — avoid @track entirely by reassigning the object
filters = { status: { active: true, closed: false } };
// ... later: this.filters = { ...this.filters, status: { ...this.filters.status, active: false } };
```

```js
// ❌ VIOLATION — @track on primitive (redundant)
@track isLoading = false;

// ✅ COMPLIANT
isLoading = false;

// ✅ COMPLIANT — @track justified for deep nested reactivity
@track filters = { status: { active: true, closed: false } };
```

#### `@wire`
- Use `@wire` for **read-only, reactive Salesforce data** (records, Apex, UI API).
- Wire adapter properties prefixed with `$` are **reactive** — the wire re-runs when they change.
- Always destructure `{ data, error }` from wire results and handle both branches.
- Never call imperative Apex AND wire the same method — pick one pattern.

```js
// ❌ VIOLATION — only handling data, ignoring error
@wire(getAccounts)
accounts;
// (template uses accounts.data with no error branch)

// ✅ COMPLIANT
@wire(getAccounts, { filters: '$activeFilters' })
wiredAccounts({ data, error }) {
    if (data) {
        this.accounts = data;
        this.error = undefined;
    } else if (error) {
        this.error = error;
        this.accounts = undefined;
    }
}
```

---

### 4. Error Handling

**Any async operation must handle errors explicitly. No silent failures.**

| Operation | Required Handling |
|---|---|
| `@wire` adapter | Always handle `error` branch |
| Imperative Apex `.then().catch()` | Both `.then()` AND `.catch()` required |
| `async/await` Apex calls | `try/catch` block required |
| `fetch` / HTTP calls | `try/catch` + status code check |
| `Promise.all` | Wrap in `try/catch` |

**Rules:**
- Never leave a `.catch()` empty — log and surface to user at minimum.
- Show user-facing errors via `ShowToastEvent` (variant `error`) or a visible error message in the template.
- Use `isLoading` / `hasError` / `hasData` boolean flags to control template rendering states.
- Log errors to console: `console.error('[ComponentName]', error)`.

```js
// ❌ VIOLATION — imperative Apex with no .catch()
getAccounts()
    .then(data => { this.accounts = data; });

// ❌ VIOLATION — async/await with no try/catch
async handleSave() {
    const result = await saveRecord({ record: this.record });
    this.dispatchEvent(new ShowToastEvent({ title: 'Saved', variant: 'success' }));
}

// ✅ COMPLIANT — imperative Apex
getAccounts()
    .then(data => {
        this.accounts = data;
        this.error = undefined;
    })
    .catch(error => {
        this.error = error;
        this.accounts = undefined;
        console.error('[MyComponent] getAccounts failed', error);
        this.dispatchEvent(new ShowToastEvent({
            title: 'Error loading accounts',
            message: error.body?.message ?? 'Unknown error',
            variant: 'error'
        }));
    })
    .finally(() => { this.isLoading = false; });

// ✅ COMPLIANT — async/await
async handleSave() {
    this.isLoading = true;
    try {
        await saveRecord({ record: this.record });
        this.dispatchEvent(new ShowToastEvent({ title: 'Saved', variant: 'success' }));
    } catch (error) {
        console.error('[MyComponent] saveRecord failed', error);
        this.dispatchEvent(new ShowToastEvent({
            title: 'Save failed',
            message: error.body?.message ?? 'Unknown error',
            variant: 'error'
        }));
    } finally {
        this.isLoading = false;
    }
}
```

---

### 5. Event Handling (Custom Events & Communication)

#### Custom Events
- Event names must be **all lowercase, no hyphens** (e.g. `recordsave`, `statuschange`).
- Always use `CustomEvent` — never dispatch raw `Event` objects for component communication.
- Pass data via `detail` property only.
- Document every dispatched event with a comment describing its `detail` shape.
- Parent listens with `on` + event name in template: `onrecordsave={handleRecordSave}`.

```js
// ❌ VIOLATION — uppercase or hyphenated event name
this.dispatchEvent(new CustomEvent('record-Save', { detail: this.record }));

// ❌ VIOLATION — passing complex mutable objects by reference in detail
this.dispatchEvent(new CustomEvent('update', { detail: this.records }));

// ✅ COMPLIANT
// Dispatches 'recordsave' with { recordId, name } in detail
this.dispatchEvent(new CustomEvent('recordsave', {
    detail: { recordId: this.record.Id, name: this.record.Name },
    bubbles: false,   // set true only if intentional bubbling is needed
    composed: false   // set true only to cross shadow DOM boundary — justify in comment
}));
```

#### Component Communication Patterns

| Scenario | Pattern |
|---|---|
| Parent → Child | `@api` property / method |
| Child → Parent | Custom event (`dispatchEvent`) |
| Sibling / Unrelated | LMS (Lightning Message Service) |
| **Never use** | `pubsub` utility module (deprecated pattern) |

- **Never use** the community `pubsub` module in new code — use Lightning Message Service (LMS) instead. Flag any `pubsub` import as 🔴 Critical.
- LMS channels must be defined in a `.messageChannel` metadata file.

```js
// ❌ VIOLATION — pubsub (deprecated)
import { fireEvent, registerListener } from 'c/pubsub';

// ✅ COMPLIANT — LMS
import { publish, subscribe, MessageContext } from 'lightning/messageService';
import MY_CHANNEL from '@salesforce/messageChannel/MyChannel__c';
```

---

### 6. Wire Service & Apex Integration

- Prefer `@wire` for data that is read-only and needs to stay reactive.
- Use **imperative Apex** when: call is conditional, triggered by user action, or needs explicit loading/error state control.
- Never call Apex in `connectedCallback` when `@wire` can handle it.
- Apex method imports must use descriptive aliases when the method name is ambiguous.
- Always pass parameters as **named objects** (not positional).

```js
// ❌ VIOLATION — Apex called in connectedCallback when @wire fits
connectedCallback() {
    getAccounts().then(data => { this.accounts = data; });
}

// ❌ VIOLATION — positional params (not valid in LWC anyway, but sometimes seen in older patterns)
// Always use named params:
getAccount({ id: this.recordId }) // ✅

// ✅ COMPLIANT — imperative Apex on user action
handleSearch() {
    this.isLoading = true;
    searchAccounts({ searchTerm: this.searchTerm, maxResults: 10 })
        .then(data => { this.results = data; })
        .catch(error => { this.error = error; })
        .finally(() => { this.isLoading = false; });
}
```

---

### 7. HTML Template Standards

- Always use `template` as the root element — no extra wrapper `div` unless layout requires it.
- **Always use `lwc:if` / `lwc:elseif` / `lwc:else` for conditional rendering** — the legacy `if:true` and `if:false` directives are deprecated and must not be used. Replace all occurrences with the modern directives to future-proof the code.
- Never use CSS `display:none` to hide logic-controlled content — use `lwc:if` instead.
- Use `for:each` with a unique `key` attribute — never use index as key.
- Never put complex expressions in templates — compute in JS getter instead.
- `lightning-*` base components are preferred over raw HTML equivalents.

```html
<!-- ❌ VIOLATION — legacy if:true / if:false (deprecated) -->
<template if:true={isSuccess}>
    <p>Success!</p>
</template>
<template if:false={isSuccess}>
    <p>Try again.</p>
</template>

<!-- ✅ COMPLIANT — modern lwc:if / lwc:else -->
<template lwc:if={isSuccess}>
    <p>Success!</p>
</template>
<template lwc:else>
    <p>Try again.</p>
</template>

<!-- ✅ COMPLIANT — lwc:if / lwc:elseif / lwc:else chain -->
<template lwc:if={isSuccess}>
    <p>Success!</p>
</template>
<template lwc:elseif={isLoading}>
    <lightning-spinner></lightning-spinner>
</template>
<template lwc:else>
    <p>Enter your code.</p>
</template>
```

```html
<!-- ❌ VIOLATION — index as key -->
<template for:each={items} for:item="item" for:index="idx">
    <c-item key={idx} item={item}></c-item>
</template>

<!-- ❌ VIOLATION — complex expression in template -->
<template if:true={record.fields.Status.value === 'Active'}>

<!-- ✅ COMPLIANT — unique key, getter for condition -->
<template for:each={items} for:item="item">
    <c-item key={item.id} item={item}></c-item>
</template>

<!-- In JS: -->
get isActive() { return this.record?.fields?.Status?.value === 'Active'; }
```

---

### 8. Performance

- **Never** perform DOM manipulation via `this.template.querySelector` inside loops.
- Avoid unnecessary reactive property updates — batch changes where possible.
- Use `renderedCallback` sparingly — it fires after every render. Guard with a boolean flag to run init logic only once.
- Lazy-load heavy child components using dynamic import where supported.
- Do not store large datasets in reactive properties if only a subset is displayed — filter/slice before assigning.

```js
// ❌ VIOLATION — renderedCallback without guard (runs every render)
renderedCallback() {
    this._initChart(); // expensive operation
}

// ✅ COMPLIANT
_chartInitialized = false;
renderedCallback() {
    if (this._chartInitialized) return;
    this._chartInitialized = true;
    this._initChart();
}
```

---

### 9. Accessibility (a11y)

- Every `<img>` must have a descriptive `alt` attribute (empty string only for decorative images).
- Interactive elements (`button`, `a`, custom clickable divs) must have accessible labels via `aria-label` or visible text.
- Never make a `<div>` or `<span>` interactive without `role` and `tabindex`.
- Use `<lightning-button>` over `<button>` where possible — it handles focus/keyboard by default.
- Form fields must have associated `<label>` elements or use `lightning-input` (which handles this).
- Color alone must not convey meaning — pair with text or icon.

```html
<!-- ❌ VIOLATION — missing alt -->
<img src={logoUrl} />

<!-- ❌ VIOLATION — div used as button -->
<div onclick={handleClick}>Save</div>

<!-- ✅ COMPLIANT -->
<img src={logoUrl} alt="Company logo" />
<button onclick={handleClick} aria-label="Save record">Save</button>
<!-- or better: -->
<lightning-button label="Save" onclick={handleSave}></lightning-button>
```

---

### 10. CSS & Styling

- **UI must always look consistent with Salesforce standard UI** — components must feel native to the Salesforce Lightning Experience. Do not introduce custom visual design patterns (custom card shapes, non-standard typography, bespoke color palettes, custom button styles) that deviate from the look and feel a user would expect in a standard Salesforce page. When in doubt, look at how a standard Salesforce base component renders and match it.
- **Prefer SLDS utility classes** — always use Salesforce SLDS classes (e.g. `slds-m-around_medium`, `slds-text-heading_small`, `slds-grid`, `slds-col`) directly in the HTML template before writing any custom CSS. Custom classes or selectors are only permitted when no SLDS equivalent exists.
- **Prefer `lightning-*` base components** over raw HTML equivalents — they are pre-styled to Salesforce standards and handle accessibility automatically (e.g. `lightning-card`, `lightning-button`, `lightning-input`, `lightning-badge`, `lightning-datatable`).
- Only use **scoped CSS** in the component's `.css` file — styles do not bleed out of shadow DOM.
- Use **SLDS design tokens** (`--slds-*` variables) rather than hardcoded colors or spacing.
- Never use `!important` — it signals a specificity problem; restructure selectors instead.
- Do not style child component internals from the parent (shadow DOM enforces this, but flag intent).

```html
<!-- ❌ VIOLATION — custom card with bespoke styling instead of lightning-card -->
<div class="my-custom-card" style="border-radius:12px; box-shadow: 0 4px 24px rgba(0,0,0,0.1);">
    <h2 class="my-title">Account Details</h2>
</div>

<!-- ✅ COMPLIANT — native Salesforce look via lightning-card -->
<lightning-card title="Account Details" icon-name="standard:account">
    <div class="slds-p-around_medium">...</div>
</lightning-card>
```

```css
/* ❌ VIOLATION — hardcoded color */
.status-badge { background-color: #ff0000; }

/* ✅ COMPLIANT — SLDS token */
.status-badge { background-color: var(--slds-c-badge-color-background, var(--sds-c-badge-color-background)); }
```

---

## REVIEW MODE — How to conduct a review

When reviewing LWC code, produce a structured report:

```
## LWC Code Review — <ComponentName>

### 🔴 Critical Violations (must fix before deployment)
- [File, Line X] <violation> — <compliant fix>

### 🟡 Standard Violations (must fix per coding standard)
- [File, Line X] <violation> — <compliant fix>

### 🟢 Suggestions (good practice improvements)
- <suggestion>

### Summary
X critical, Y standard, Z suggestions.
[Verdict: PASS / FAIL]
```

Rules:
- Flag **every** violation across all files in the component bundle.
- Always provide the compliant fix alongside the violation.
- PASS requires zero critical AND zero standard violations.
- Reference the specific file (`.html`, `.js`, `.css`) and line number.

---

## GENERATE MODE — How to write compliant components

When generating a new LWC component:
1. Generate **all required files**: `.html`, `.js`, `.js-meta.xml` (and `.css` if styles are needed).
2. Apply ALL rules from this standard from the start.
3. Use `camelCase` for folder/file names.
4. Default to `@wire` for reactive data; imperative Apex only for user-triggered actions.
5. Handle BOTH `data` and `error` in every wire / Apex call.
6. Wrap all async imperative calls in `try/catch` or `.catch()`.
7. Use LMS for cross-component communication — never `pubsub`.
8. Include `isLoading`, `error`, `hasData` state flags and reflect them in the template.
9. Add `aria-label` / `alt` attributes to all interactive and image elements.
10. Briefly annotate code to indicate which standard rule is being applied.

---

## Quick Reference — Common Violations Checklist

| # | Violation | Severity |
|---|---|---|
| 1 | `pubsub` used instead of LMS | 🔴 Critical |
| 2 | `@wire` with no `error` branch handled | 🔴 Critical |
| 3 | Imperative Apex with no `.catch()` or `try/catch` | 🔴 Critical |
| 4 | Empty `.catch()` / silent error swallow | 🔴 Critical |
| 5 | Mutating `@api` property inside component | 🔴 Critical |
| 6 | `async/await` Apex call without `try/catch` | 🔴 Critical |
| 7 | `for:each` with index as `key` | 🔴 Critical |
| 7a | `if:true` or `if:false` used — replace with `lwc:if` / `lwc:elseif` / `lwc:else` | 🔴 Critical |
| 8 | Single-character variable name (e.g. `e`, `a`, `i`) — use a meaningful name | 🔴 Critical |
| 8c | `_` prefix on a method/property that is bound in the HTML template — remove the underscore | 🔴 Critical |
| 8d | No `_` prefix on a method/property that is purely internal to the `.js` file — add the underscore | 🔴 Critical |
| 8b | Constants defined inline in `.js` or hardcoded in `.html` — all constants must live in `constants.js` | 🔴 Critical |
| 8a | Complex logic expression in HTML template | 🟡 Standard |
| 9 | `@track` used without justification — all properties are reactive by default, remove it | 🔴 Critical |
| 10 | Custom event name with uppercase or hyphens | 🟡 Standard |
| 11 | `bubbles: true` / `composed: true` without justification | 🟡 Standard |
| 12 | Apex called in `connectedCallback` when `@wire` fits | 🟡 Standard |
| 13 | `renderedCallback` without init guard | 🟡 Standard |
| 14 | Missing `alt` on `<img>` | 🟡 Standard |
| 15 | `<div>` used as interactive element without `role`/`tabindex` | 🟡 Standard |
| 16 | UI deviates from Salesforce standard look and feel — use `lightning-*` components and SLDS patterns | 🔴 Critical |
| 16a | Custom CSS class/selector used when an SLDS utility class exists — use SLDS first | 🔴 Critical |
| 16a | Hardcoded colors/spacing in CSS (use SLDS tokens) | 🟡 Standard |
| 17 | `!important` in CSS | 🟡 Standard |
| 18 | PascalCase component folder/file name | 🟡 Standard |
| 19 | No `isLoading` state during async operations | 🟢 Suggestion |
| 20 | Raw `<button>` instead of `lightning-button` | 🟢 Suggestion |
| 21 | Unnecessary comments that restate what the code does — remove them | 🔴 Critical |
| 21a | Handler method contains inline business logic instead of delegating to private helpers (recipe pattern) | 🔴 Critical |
| 21b | Method returns an expression directly instead of assigning to a named `result` variable first | 🔴 Critical |
| 21b | Component JS class exceeds ~200 lines | 🟢 Suggestion |
| 22 | Import order incorrect (LWC core → SF modules → Apex → utils) | 🟢 Suggestion |
