# Proto Academy data model reference

Field API names for the objects a content creator writes. Confirm the live shape
in your org with the connector's `getObjectSchema` before writing, since a given
org may add or remove fields.

## Training__c (a course)
- `Name` (text) - course title.
- `Category__c` (picklist) - e.g. Compliance, Onboarding, Platform, Process.
- `Status__c` (picklist) - `Active` to publish; a non-Active value keeps it hidden.
- `Description__c` (long text) - catalog blurb.
- `Icon__c` (text) - SLDS utility icon, e.g. `utility:shield`.
- `Accent_Color__c` (text) - hex, e.g. `#5a3fa0`.
- `Requires_Quiz__c` (checkbox).
- `Passing_Score__c` (number, percent).
- `Estimated_Minutes__c` (number).
- `Version__c` (number).

## Training_Step__c (an ordered step)
- `Training__c` (lookup), `Sort_Order__c` (number; use 10, 20, 30, ... for gaps).
- `Kind__c` (picklist): `Intro` | `Content` | `Tool` | `Outro`.
- `Title__c` (text), `Body__c` (rich text HTML; see body rules in SKILL.md).
- `Icon__c`, `Accent_Color__c`.
- `Video_Url__c` (url) - youtube-nocookie / vimeo embed supported.
- `Image_Version_Ids__c` (long text, JSON array of ContentVersion Ids) and
  `Image_Static_Resource__c` (text) - **image upload is a developer task**, not
  part of the MCP authoring path.
- Tool-step fields (Kind = Tool): `Tagline__c`, `What_It_Is__c`, `Why_It_Matters__c`,
  `What_It_Drives__c`, `Roles__c`.

## Training_Question__c (quiz question)
- `Training__c` (lookup), `Sort_Order__c`, `Type__c` (`Single`),
  `Question_Text__c` (text), `Explanation__c` (shown after answering).

## Training_Answer_Option__c (quiz option)
- `Training_Question__c` (lookup), `Sort_Order__c`, `Answer_Text__c`, `Is_Correct__c`.
- Exactly one option per question is correct.

## Learning_Path__c (a track)
- `Name`, `Description__c`, `Icon__c`, `Accent_Color__c`, `Status__c` (`Active`), `Category__c`.

## Learning_Path_Item__c (path member)
- `Learning_Path__c` (lookup), `Training__c` (lookup), `Sort_Order__c`, `Required__c`.

## Academy_Rule__c (auto-assign)
- `Active__c`, `Applies_To__c` (`All Employees` | `Title Contains`), `Criteria_Value__c`,
  `Due_In_Days__c`, `Required__c`, `Training__c` OR `Learning_Path__c`, `Last_Run__c`.
- Rule execution is run from the Manage Training UI, not written here.

## Training_Assignment__c (a person's assignment)
- `Contact__c`, `Training__c`, `Learning_Path__c`, `Status__c` (`Not Started` |
  `In Progress` | `Completed`), `Required__c`, `Due_Date__c`, `Completed_Date__c`,
  `Progress__c`, `Assigned_By__c`, `Assigned_Date__c`, `Last_Step_Reached__c`.

## Academy_Certification__c (credential definition)
- `Name`, `Training__c` (lookup) OR `Learning_Path__c` (lookup) - what earns it,
- `Validity_Months__c` (blank = never expires), `Badge_Icon__c`, `Accent_Color__c`,
  `Description__c`, `Active__c`.

## Academy_Credential__c (an earned credential) - read only for authors
- Issued automatically on completion. Do not create these by hand.
- `Name` (auto-number credential id), `Contact__c`, `Certification__c`,
  `Issued_Date__c`, `Expiration_Date__c`, `Status__c`, `Final_Score__c`,
  `Source_Assignment__c`.

## Employee linkage (important)
- Employees are `Contact` records linked to a `User`. Academy participation keys on
  the Contact, so an employee with no linked Contact cannot be assigned trainings or
  earn credentials. Assignment and credentialing are usually done from the Manage
  Training UI rather than hand-written here.
