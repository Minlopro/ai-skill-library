---
name: browser-qa
description: "Drive a real Chrome browser via the chrome-devtools MCP to QA a web app's UI — reproduce/verify bugs, exercise user flows, read the console + network, and cross-check the result against the app's data layer (API/DB/CLI). Use whenever the user asks to QA or test the app in a browser, reproduce a UI issue, confirm a fix works in the real UI, click through a flow, screenshot the app, or run an exploratory/regression UI pass. Client- and stack-agnostic; reads project specifics (auth, URLs, data-verification command) from the project's QA design doc / CLAUDE.md."
---

# Browser QA Skill (chrome-devtools MCP)

Drive a real browser against the app under test and run the **full QA loop**: act in the UI → observe the console/network → **verify the data layer**. UI-only assertions miss data bugs (a form can toast "Saved" while persisting nulls), so always close the loop by confirming the underlying record/state through the app's API, database, or CLI.

This is for **assistive/exploratory QA in non-production environments**. It is **not** a validation/compliance artifact on its own (see Guardrails). Durable regression suites (e.g. Playwright) are a separate track.

This skill is **client- and stack-agnostic**. Anything project-specific — which environment/URL to hit, how to authenticate, and the command to verify the data layer — comes from the project (its QA design doc, CLAUDE.md, or the user). If those aren't documented, **ask** rather than assume.

---

## Prerequisites (verify once)

- `.mcp.json` (or the client's MCP config) registers the `chrome-devtools` server: `npx -y chrome-devtools-mcp@latest`. Tools appear as `mcp__chrome-devtools__*`.
- Node ≥ 23 (`node --version`) and a Chrome/Chromium install.
- If the tools aren't loaded, the user must **restart the client** and approve the project MCP server. Confirm liveness with `mcp__chrome-devtools__list_pages`.
- Default browser is **headed with a persistent profile** → a login survives across runs.

---

## Step 1 — Authenticate the browser

Get the browser into an authenticated session using whatever the project supports, in order of preference:
1. **Reuse a logged-in profile / existing session** (persistent profile, or attach to a running Chrome via `--browserUrl`).
2. **A session/"magic" URL** if the platform mints one (e.g. an SSO frontdoor/one-time-token URL from a CLI) — navigate straight to it, no credentials in the loop.
3. **Drive the login form** — only if the project provides test credentials; never invent or request real user passwords/MFA.

> Session/frontdoor URLs and tokens are **local-use only** — never commit them or send them anywhere external.

## Step 2 — Navigate to the target

Navigate (`mcp__chrome-devtools__navigate_page`, type=url) to the record/page/route under test, then `mcp__chrome-devtools__wait_for` on a known on-page string before snapshotting. Pull target URLs from the project docs or the user.

## Step 3 — Locate elements (snapshot, don't screenshot)

- `mcp__chrome-devtools__take_snapshot` returns the a11y tree with a `uid` per element. Prefer it over screenshots for finding things.
- **For large pages, save the snapshot to a file and grep it** instead of dumping to context:
  `take_snapshot({ filePath: "<scratch>/qa_snap.txt" })` → `grep -nE "Save|<field label>|<marker>" <scratch>/qa_snap.txt`.
  The path **must be inside the workspace root** — external paths like `/tmp/...` are rejected. Clean up scratch files when done.
- **uids are per-snapshot and change** — re-snapshot after any navigation or large re-render and use the latest uids.

## Step 4 — Act

`fill {uid, value}` for inputs, `click {uid}`, `press_key`, `select_page`, etc. For multi-step flows, drive deterministically. Buttons in a persistent app shell often keep a **stable uid across inner re-renders** (you can click them repeatedly without re-snapshotting); content that re-renders does not.

## Step 5 — Observe

- `mcp__chrome-devtools__list_console_messages({ types: ["error","warn"] })` after the action.
- `mcp__chrome-devtools__list_network_requests({ resourceTypes: ["fetch","xhr"] })` to confirm the request fired / inspect failures.
- `take_screenshot` only when a visual is the deliverable.

## Step 6 — VERIFY THE DATA LAYER (do not skip)

The UI can show success while the data is wrong. Confirm the underlying state through the project's data-verification path — a backend API/MCP, a database/CLI query, or a read-back endpoint. Report **PASS/FAIL against expected values, citing the actual persisted record**. If you don't know how to verify the data layer for this project, ask.

---

## Universal gotchas

- **Web-component / shadow DOM popups:** the a11y snapshot usually pierces shadow DOM, but **menu/combobox/listbox options often render in a portal the snapshot can't see** (an open dropdown can look like an empty listbox). Navigate another way (stable buttons, direct URL) rather than fighting an invisible popup.
- **Client-side bundle cache:** after a front-end deploy the browser may run the **stale bundle**. Hard-refresh (`navigate_page` type=reload, `ignoreCache:true`, or Cmd/Ctrl+Shift+R) before trusting a UI result — otherwise a "no-op" can just be a cached build.
- **Dynamic IDs are unstable.** For durable locators, prefer `data-testid` (or equivalent) on components you control and role/label/text for third-party components.
- **Multi-actor flows** (dual sign-off, approvals, separation-of-duties) may need a *different* authenticated user; the agent can drive up to the gate but completion may require a second session or be covered by unit tests.

## Guardrails

- **Non-production only.** Never point write actions at production. Reads/navigation are unrestricted; **scope writes** to the specific record under test and tell the user what you changed.
- **Exploratory AI QA is a dev aid, not validation evidence.** For regulated/critical systems, don't represent it as formal qualification (IQ/OQ/PQ) or compliance testing — the auditable artifact is a human-reviewed, version-controlled regression suite.
- **Secrets hygiene:** keep session tokens/URLs local; never commit or transmit them. Prefer redacting sensitive network headers if attaching to a real session.
- **Clean up** scratch snapshot files at the end.

## Project specifics

Read these from the project before starting (or ask the user):
- **Environment + org/account** and **target URLs** for the flow under test.
- **Auth method** (which of Step 1's options applies, and any CLI to mint a session URL).
- **Data-verification command** for Step 6 (the API/DB/CLI query that proves persistence).
- **Stable-locator convention** (test-id attribute, naming) if one exists.

For this repository, those details live in the project's QA design doc and CLAUDE.md.
