---
name: product-library-sanitize
description: The exact procedure for stripping client details out of Salesforce metadata and packaging it as a reusable, generic asset for the Minlopro product library (Minlopro/minlopro-product-library). Use this every time anything is contributed or updated in the library, during HELM's closeout asset review, whenever someone says "make this generic", "productize", "package this for reuse", or "strip the client out", and before opening any pull request to the library. Follow every step, every time; no step is optional.
---

# Product library sanitize

Turn components built for one client into an asset any engagement can install, with nothing left that identifies the client. Minlopro's rule is absolute: one client's data or details never go into another client's work or into reusable assets. A single client name in a field description is a leak. This procedure exists so that never happens, and so every asset in the library looks and installs the same way.

Do every step in order. When a step finds something, fix it and rerun the scan from step 5.

## 1. Collect what identifies the client

Before touching files, write the **client terms list** in a scratch file (never in the asset):

- Client legal and short names, abbreviations, and ticker or domain (for example `Acme Health`, `Acme`, `AHS`, `acmehealth.org`)
- Brand, product, program, and site names (clinic names, plant names, regions)
- People: stakeholders, users, and anyone named in the build (first and last names separately)
- The client's API prefix (`ACME_`, `ah_`) and any internal codes or project names
- The engagement's own org ID, alias, and usernames

This list feeds the scan in step 5. When in doubt, add it: a false alarm costs a minute; a leak costs trust.

## 2. Keep only what belongs in an asset

An asset folder holds exactly:

```
assets/<category>/<asset-name>/
  asset.json      manifest
  README.md       what, when, install, configure, test, limits
  force-app/      source-format metadata only
  tests/          optional: E2E steps or scripts with synthetic data
```

Remove everything else: `sfdx-project.json`, `.sf/`, `.sfdx/`, `manifest/package.xml` from the engagement, scratch-org definitions with the client's org name, `data/` exports, screenshots from the client's org, docs written for the client, and any file you can't explain.

Exclude these metadata types entirely (they're org-specific or carry secrets): Connected Apps, Named Credentials and External Credentials with real endpoints, Auth Providers, Remote Site Settings and CSP Trusted Sites for client hosts, Certificates, Profiles (ship a permission set instead), Users, Sites with client domains, and email templates with client branding. If the asset needs an endpoint, document it as configuration.

## 3. Rename to neutral API names

- Drop the client prefix from every API name: objects, fields, record types, flows, Apex classes and tests, LWC bundles, permission sets, custom labels, custom metadata types, list views, reports and folders, tabs, apps, FlexiPages.
- **No firm prefix either.** Don't use `MLP_` or `Minlopro_`: API names show up in every client org that installs the asset, and "MLP" never appears in client-facing work. Name by function: `Referral__c`, `IntakeRoutingRule__mdt`, `referralTimeline`.
- Rename consistently in **every reference**: layouts, FlexiPages, permission sets, flows (including formulas and element references), Apex (classes, tests, SOQL strings), LWC (JS, HTML, `.js-meta.xml` targets), list views, reports, translations, and test data. Rename files and folders too. Then search the whole asset for the old name; there must be zero hits.
- Labels and plurals: human-readable and generic ("Referral", "Intake Coordinator").

## 4. Make client values configuration

Anything that was true for this client only becomes something the installing org sets:

| Was | Becomes |
|---|---|
| Picklist values naming client sites, products, or teams | Generic examples (`Location A`, `Specialty 1`) plus a README step to replace them, or a Custom Metadata Type of options |
| Hard-coded record, queue, user, or record type IDs | Lookups by `DeveloperName`, or Custom Metadata |
| Thresholds, SLAs, routing rules | Custom Metadata Type records with sensible defaults |
| Client wording in error messages, help text, emails | Neutral wording |

List every such step in `asset.json` `configuration` and in the README's Configure section.

Read `references/hidden-places.md` now: client details hide in places nobody opens (descriptions, help text, formula strings, flow screen text, Apex string literals and comments, static resources, translations, list view filters, report filters). Go through every place on that list.

## 5. Scan: zero findings, every time

Run the bundled scanner over the asset with your client terms:

```bash
python3 scripts/scan.py assets/<category>/<asset-name> --terms-file /tmp/client-terms.txt --prefix ACME_
```

It checks every file, including inside zipped static resources, for: client terms (any casing, word starts), the old prefix, Salesforce org IDs and record IDs, emails, org and My Domain URLs, phone numbers, `MLP` in names or labels, and patient-data patterns (named patients, dates of birth with dates, MRNs and member IDs with values, SSNs). It masks what it reports and exits non-zero on any finding.

**The scan must report zero findings.** Then do a manual read of every file anyway. The scanner catches patterns; it can't know that "Riverside" is the client's flagship site unless it's in your terms list.

HELM's closeout asset review runs the same checks automatically and won't open a pull request until its re-scan is clean.

## 6. Prove it works on its own

- **Synthetic test data only, and obviously synthetic.** Test classes and fixtures create their own data. Every person and identifier carries **TEST** so no reviewer or security scan can mistake it for real data: `Test Patient 1`, `MRN-TEST-0001`, `DOB 1900-01-01`, `test.user@example.com`, `(555) 010-0000`. Never realistic names with realistic identifiers (a "Maria Alvarez, MRN-900123" fixture reads as PHI even when it's invented), never real people, never `SeeAllData=true`. Placeholder record IDs with long zero runs (`001000000000001AAA`) are fine.
- **Apex tests with real assertions.** At least 75% coverage per class; aim for 85%.
- **Check-only deploy to a fresh scratch org** from the Minlopro Dev Hub, with local tests:

  ```bash
  sf project deploy validate --source-dir force-app --target-org <scratch> --test-level RunLocalTests
  ```

  Copy `force-app/` into a throwaway SFDX project to run it, so no project files end up in the asset. It must pass. If the asset depends on other library assets, deploy those first and list them in `dependencies`.

## 7. Package

`asset.json`:

```json
{
  "name": "referral-intake-model",
  "title": "Referral intake data model",
  "summary": "One sentence, generic, saying what it is.",
  "category": "data-model",
  "clouds": ["Service Cloud"],
  "tags": ["referral", "intake", "record-type"],
  "metadata": ["CustomObject", "CustomField", "RecordType"],
  "configuration": ["Each step the installing org takes."],
  "version": "1.0.0",
  "install": "source",
  "dependencies": [],
  "origin": "Contributed from a <cloud> engagement; client details removed and reviewed."
}
```

- `origin` never names the client, its industry niche, location, or the engagement.
- `version` follows semver: 1.0.0 for new; patch for fixes, minor for compatible additions, major for anything that breaks an existing install.
- README sections, in order: **What it is**, **When to use it**, **What's in it** (metadata list), **Install**, **Configure**, **How it's tested**, **Known limits**. Generic throughout, no em dashes, no "MLP".

## 8. Pull request

Branch `contrib/<asset-name>` (or `update/<asset-name>`), commit only the asset folder (and `CATALOG.md` if you regenerate it), and open the PR with the template checklist filled in honestly, plus:

- The scan result (zero findings) and the check-only deploy ID.
- Who did the manual read for client details.

A second person reviews, starting with client details, before it merges. Never push to `main`.

## Updating an existing asset

Same procedure, scoped to what changed: collect terms for the engagement the change came from, rename and configure the new parts, rescan the **whole** asset, revalidate, bump `version`, and say what changed at the top of the README.

To fix naming in an asset already in the library (for example an `MLP_` prefix), treat it as a major version: rename per step 3 across every reference, rescan, revalidate, bump the major version, and note the rename so engagements that installed the old version know to migrate.
