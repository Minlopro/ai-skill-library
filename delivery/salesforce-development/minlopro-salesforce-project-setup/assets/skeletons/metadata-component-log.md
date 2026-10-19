# Metadata Component Log

> The authoritative inventory — every component touched, which epic owns it, and
> its deploy status. package.xml is regenerated from this. HARD RULE: update this
> log in the SAME change that touches metadata.

| # | Epic | Type | API Name | Action | Deployed: SB / UAT / PROD | Notes |
|---|------|------|----------|--------|---------------------------|-------|
| 1 | 01 | TODO | TODO | New | -- / -- / -- | |

Rebuild the manifest from the source tree any time:
`sf project generate manifest --source-dir force-app --name package.xml`
