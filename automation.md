# Automation Plan for DNS Lists

This file is the long-term working note for humans, Codex, ChatGPT, and other agents that need to maintain or extend this repository.

It describes:
- the purpose of the repository
- which files are automated versus manual
- the O365 update and validation rules
- the GitHub Actions behaviour
- the assumptions future agents should preserve

---

## Repository purpose

This repository publishes DNS allow lists in adblock-style exception format for Pi-hole and similar systems.

The main managed scope is Microsoft 365 under `o365/`.

The repository currently maintains:
- `o365/o365-minimal-allowlist.txt`
- `o365/o365-sane-allowlist.txt`
- `o365/o365-full-allowlist.txt`
- `github/github-allowlist.txt`
- `google/google-allowlist.txt`
- `okta/okta-allowlist.txt`

The O365 files are the primary public outputs and are intended to be consumed directly as hosted subscribed lists.

The GitHub, Google, and Okta files are small manual sidecars that are useful in practice but are not the primary automation target.

---

## File roles

### `o365/o365-minimal-allowlist.txt`
Smallest O365 allow list.

Purpose:
- allow sign-in
- allow Microsoft identity flows
- allow Outlook / Exchange core functionality
- allow basic tenant routing

This list should stay intentionally narrow.

### `o365/o365-sane-allowlist.txt`
Recommended default O365 list.

Purpose:
- keep Microsoft 365 working normally for most users
- include core domains for authentication, Outlook, Teams, SharePoint, OneDrive, and Office web apps
- include newer Microsoft infrastructure such as `cloud.microsoft`
- avoid broader telemetry, CDN, and optional Microsoft domains where reasonably possible

This list should remain curated and conservative.

### `o365/o365-full-allowlist.txt`
Maximum compatibility O365 list.

Purpose:
- include nearly everything needed or published for Microsoft 365 and related service compatibility
- be useful for troubleshooting breakage caused by block lists
- prioritize compatibility over strict minimization

This list may be broader and more dynamic.

### `github/github-allowlist.txt`
Manual GitHub sidecar.

Purpose:
- keep core GitHub web, API, and asset flows working
- stay intentionally conservative
- avoid trying to model every GitHub-adjacent service

### `okta/okta-allowlist.txt`
Manual Okta sidecar.

Purpose:
- keep core Okta / Okta Verify flows working
- remain small and practical
- avoid turning into a full generic Okta network policy

### `google/google-allowlist.txt`
Manual Google sidecar.

Purpose:
- reduce common Google-service breakage caused by aggressive blocklists
- cover practical Google identity, API, Firebase Hosting, and Firebase Cloud Messaging endpoints
- stay intentionally conservative rather than becoming a full Google Workspace or Android policy list

---

## Automation goals

We want a tight, maintainable, low-noise GitHub Actions setup that:

1. Regenerates or validates the O365 allow lists on a schedule.
2. Uses Microsoft endpoint data as the source for broad O365 compatibility coverage.
3. Preserves manual curation for the `minimal` and `sane` O365 lists.
4. Updates `o365/o365-full-allowlist.txt` automatically from upstream endpoint data.
5. Commits changes only when there is a real diff.
6. Avoids unnecessary churn from ordering, duplicates, formatting noise, or date-only changes.
7. Is safe for future agents to run repeatedly without widening the curated O365 lists by accident.
8. Validates manual sidecar lists without pretending they are automatically sourced from upstream providers.

---

## Managed versus manual

### Managed by automation
- `o365/o365-minimal-allowlist.txt`
- `o365/o365-sane-allowlist.txt`
- `o365/o365-full-allowlist.txt`
- `data/m365-endpoint-metadata.json`

### Manual but validated
- `github/github-allowlist.txt`
- `google/google-allowlist.txt`
- `okta/okta-allowlist.txt`

Current model:
- `minimal` is generated from fixed curated constants
- `sane` is generated from fixed curated constants
- `full` is generated from the official Microsoft 365 endpoint web service
- GitHub, Google, and Okta lists are maintained by hand
- CI validates structure and formatting on every push and pull request
- the scheduled workflow refreshes upstream-derived O365 data weekly and commits only when content changes

---

## Source of truth

### Primary upstream source for O365
Use Microsoft's published Microsoft 365 endpoint source, derived from the official Microsoft 365 endpoint web service.

Current implementation details:
- instance: `Worldwide`
- version endpoint: `https://endpoints.office.com/version/Worldwide`
- data endpoint: `https://endpoints.office.com/endpoints/Worldwide`
- stable `ClientRequestId`: `3f7f7d83-f9b9-4f6b-8c8d-3d4e6db245e1`

### What to extract
Extract:
- hostnames
- domains
- wildcard-style destinations where applicable

Do not keep:
- IP addresses
- subnets
- ports
- protocol-only entries
- comments copied from upstream

---

## Output format requirements

All public list files must use adblock-style exception rules in this general form:

```txt
@@||office.com^
@@||microsoftonline.com^
@@||cloud.microsoft^
```

Rules:
- one rule per line
- no duplicates
- stable sorted order
- Unix newlines
- short header comments allowed
- no regex format in the public list files

---

## Normalization rules

When generating or validating domains, apply the following rules.

### Domain cleanup
- strip whitespace
- lowercase everything
- remove leading `*.` when converting wildcard domains to adblock exception format
- remove leading `*` for wildcard forms such as `*cdn.onenote.net`
- collapse unsupported mid-label wildcards such as `autodiscover.*.onmicrosoft.com` to the suffix that can be represented safely in adblock syntax
- remove accidental escaping such as `\-` in domain names
- remove trailing dots
- ignore empty values

### Deduplication
- dedupe exact duplicates
- keep stable ordering
- do not widen curated O365 lists based on upstream changes alone

### Safety
- never emit raw regex into allow list files
- never emit IP addresses into these list files
- never emit invalid hostname syntax

---

## Curated O365 domain sets

The automation should keep the curated O365 lists as explicit constant sets inside the generator script.

### Minimal list policy
This list should stay limited to:
- Microsoft identity and authentication
- Outlook / Exchange core access
- tenant routing / modern Microsoft service entry points that are required even for basic use

### Sane list policy
This list should include the minimal/core service set plus the main domains needed for:
- Teams
- SharePoint
- OneDrive
- Office web apps
- newer Microsoft cloud-hosted service front ends

### Rule for future agents
Future agents must not silently add new domains to `minimal` or `sane` just because the upstream Microsoft endpoint source changed.

Any change to those curated sets should be intentional and explained in a commit message or PR note.

---

## Full O365 list generation policy

The `o365/o365-full-allowlist.txt` file should be regenerated automatically from upstream domain data.

Suggested behavior:

1. Fetch upstream endpoint data.
2. Extract domain-like entries.
3. Normalize and clean them.
4. Remove IPs and non-domain artifacts.
5. Convert each valid domain into adblock exception syntax.
6. Sort deterministically.
7. Write the file with a short explanatory header.
8. Preserve `Last Updated` unless the actual rule content changed.

### Full list bias
When uncertain, prefer compatibility over minimalism for the full list.

However:
- still do basic cleanup
- still remove obviously invalid entries
- still avoid duplicate noise

---

## Validation requirements

The generator or validator should check at minimum:

- every non-comment line starts with `@@||`
- every rule ends with `^`
- no line contains spaces in the hostname portion
- no line contains raw regex syntax intended for the old format
- no IP address lines are present
- files are sorted and deduplicated
- required curated entries remain present in `minimal` and `sane`
- manual sidecar lists still conform to the same adblock-style allowlist format

If validation fails, the workflow should fail.

---

## GitHub Actions behavior

We use two workflows with distinct responsibilities.

Files:
- `.github/workflows/update-dns-lists.yml`
- `.github/workflows/validate-dns-lists.yml`

### Update workflow
Triggers:
- `workflow_dispatch`
- scheduled weekly run

Behavior:
1. Check out the repository.
2. Set up Python.
3. Run unit tests.
4. Run the generator script.
5. Validate the tracked allowlist files, including manual sidecars.
6. Commit changes only if managed O365 files changed.
7. Push back to the default branch.

### Validation workflow
Triggers:
- `push`
- `pull_request`

Behavior:
1. Check out the repository.
2. Set up Python.
3. Run unit tests.
4. Validate the tracked allowlist files, including manual sidecars.

---

## README handling

The README is hand-written and documents:
- repo layout
- O365 list roles
- managed versus manual scope
- automation behavior
- local usage commands

The automation does not rewrite `README.md`.

---

## Current implementation milestone

The current repo now supports:

- regenerating `o365/o365-full-allowlist.txt` from upstream Microsoft endpoint data
- regenerating `o365/o365-minimal-allowlist.txt` from curated constants
- regenerating `o365/o365-sane-allowlist.txt` from curated constants
- validating all managed and manual list files
- running manually in GitHub Actions
- running weekly scheduled O365 updates
- unit testing the normalization and validation logic
- committing only when managed generated content changes

---

## Later improvements

Possible later additions:
- open a PR instead of pushing directly
- schema validation for upstream endpoint fields
- optional diff summary in workflow logs
- optional issue creation if upstream fetch fails repeatedly
- provider-specific manual validators if the sidecar list count grows
