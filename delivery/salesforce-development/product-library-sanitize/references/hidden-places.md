# Where client details hide in Salesforce metadata

Go through every row for every asset. "Open it" means read the XML or source, not the file name.

| Metadata | Where to look |
|---|---|
| Custom objects | `<label>`, `<pluralLabel>`, `<description>`, `<nameField><label>`, sharing model comments |
| Custom fields | `<label>`, `<description>`, `<inlineHelpText>`, `<defaultValue>`, `<formula>` string literals, picklist `<valueSet>` values and labels, `<referenceTo>` and relationship names |
| Record types | `<label>`, `<description>`, picklist value assignments |
| Validation rules | `<errorConditionFormula>` literals, `<errorMessage>`, `<description>` |
| Flows | `<label>`, `<description>`, `<interviewLabel>`, screen text and help, formulas and text templates, decision outcome labels, assignment literal values, record lookups filtering on names or IDs, fault paths with emails |
| Apex | String literals (SOQL `WHERE Name = '...'`, error messages), comments and Javadoc, `@isTest` data, class and method names, custom exception messages |
| LWC and Aura | HTML text, JS strings and comments, `.js-meta.xml` `<masterLabel>` and `<description>`, CSS comments, imported labels |
| Custom labels | Values and categories |
| Custom metadata records | Every value (these are data, not structure) |
| Permission sets and groups | `<label>`, `<description>` |
| Layouts and FlexiPages | Section labels, rich text components, visibility rules referencing profiles, users, or roles by name |
| List views | `<label>`, filters on owner, user, or name values, shared-to groups and roles |
| Reports and dashboards | Folder names, report names and descriptions, filter values, chart titles, running user |
| Email templates and letterheads | Everything (exclude unless generic) |
| Static resources | **Unzip and read**: JSON, CSV, images with client logos, fonts, docs |
| Translations | Every translated string |
| Tabs and apps | Labels, descriptions, logos, utility bar labels |
| Queues and groups (if included) | Names, emails, members |
| Test data and scripts (`tests/`, `data/`) | Every value. Synthetic only |
| README and asset.json | Origin, examples, screenshots, links |

Also check: file and folder names, git history of the asset folder (squash before the PR if an early commit had client details), and any URL (My Domain, Experience Cloud sites, integrations).
