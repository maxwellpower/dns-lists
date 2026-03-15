# Automation Plan for O365 Allow Lists

This file is the long-term working note for humans, Codex, ChatGPT, and other agents that need to maintain or extend this repository.

It describes:
- the purpose of the repository
- the expected output files
- the desired automation behaviour
- the update rules and safeguards
- the implementation plan for GitHub Actions
- the assumptions future agents should preserve

---

## Repository purpose

This repository publishes Microsoft 365 / Office 365 allow lists in adblock-style exception format for Pi-hole and similar systems.

The repository currently maintains three list tiers:
- `o365-minimal-allowlist.txt`
- `o365-sane-allowlist.txt`
- `o365-full-allowlist.txt`

These files are intended to be consumed directly as hosted subscribed lists.

---

## Current file roles

### `o365-minimal-allowlist.txt`
Smallest allow list.

Purpose:
- allow sign-in
- allow Microsoft identity flows
- allow Outlook / Exchange core functionality
- allow basic tenant routing

This list should stay intentionally narrow.

### `o365-sane-allowlist.txt`
Recommended default list.

Purpose:
- keep Microsoft 365 working normally for most users
- include core domains for authentication, Outlook, Teams, SharePoint, OneDrive, and Office web apps
- include newer Microsoft infrastructure such as `cloud.microsoft`
- avoid broader telemetry, CDN, and optional Microsoft domains where reasonably possible

This list should remain curated and conservative.

### `o365-full-allowlist.txt`
Maximum compatibility list.

Purpose:
- include nearly everything needed or published for Microsoft 365 and related service compatibility
- be useful for troubleshooting breakage caused by block lists
- prioritise compatibility over strict minimisation

This list may be broader and more dynamic.

---

## Automation goals

We want a tight, maintainable, low-noise GitHub Actions workflow that:

1. Regenerates or validates the allow lists on a schedule.
2. Uses Microsoft endpoint data as the source for broad compatibility coverage.
3. Preserves manual curation for the `minimal` and `sane` lists.
4. Updates `full` automatically from upstream endpoint data.
5. Commits changes only when there is a real diff.
6. Avoids unnecessary churn from ordering, duplicates, or formatting noise.
7. Is safe for future agents to run repeatedly without widening the curated lists by accident.

---

## Design principles

### 1. Curated versus generated
The three files are not all treated the same.

#### `o365-minimal-allowlist.txt`
This should be curated in code, not fully generated from upstream.

Reason:
- this file is opinionated
- it is meant to stay small
- upstream additions should not silently expand it

#### `o365-sane-allowlist.txt`
This should also be curated in code, not fully generated.

Reason:
- this is the recommended daily-use list
- it needs stability
- it should not grow every time Microsoft adds new optional infrastructure

#### `o365-full-allowlist.txt`
This should be generated from Microsoft endpoint data, with normalisation and cleanup.

Reason:
- this file is specifically for broad compatibility
- it benefits most from automation
- it should track Microsoft changes over time

---

## Implemented automation

The repository now includes:

- `scripts/generate_o365_lists.py`
- `tests/test_generate_o365_lists.py`
- `.github/workflows/update-o365-lists.yml`
- `.github/workflows/validate-o365-lists.yml`
- `data/m365-endpoint-metadata.json`
- this `automation.md` file as the operational spec

Current model:
- `minimal` is generated from fixed curated constants
- `sane` is generated from fixed curated constants
- `full` is generated from the official Microsoft 365 endpoint web service
- CI validates structure and formatting on every push and pull request
- the scheduled workflow refreshes upstream-derived data weekly and commits only when content changes

---

## Source of truth

### Primary upstream source
Use Microsoft's published Microsoft 365 endpoint source, derived from the official Microsoft 365 endpoint data / web service.

The automation should fetch the current endpoint data and extract domain-based destinations.

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

All generated lists must use adblock-style exception rules in this exact general form:

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
- no regex format in these public list files

---

## Normalisation rules

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
- if a broader parent domain already covers a more specific subdomain for the purposes of the full list, the implementation may collapse to the broader entry when safe and intentional
- do not over-collapse if the broader domain would meaningfully widen the list beyond what upstream specified unless that is explicitly desired for compatibility

### Safety
- never emit raw regex into the allow list files
- never emit IP addresses into these list files
- never emit invalid hostname syntax

---

## Curated domain sets

The automation should keep the curated lists as explicit constant sets inside the generator script.

### Minimal list policy
This list should stay limited to:
- Microsoft identity and authentication
- Outlook / Exchange core access
- tenant routing / modern Microsoft service entry points that are required even for basic use

Current intended entries:

```txt
aadcdn.microsoftonline-p.com
aka.ms
cloud.microsoft
live.com
login.live.com
mail.protection.outlook.com
microsoftonline.com
microsoftonline-p.com
msauth.net
msauthimages.net
msftidentity.com
office.com
office365.com
onmicrosoft.com
outlook.com
outlook.office.com
outlook.office365.com
protection.outlook.com
```

### Sane list policy
This list should include the minimal/core service set plus the main domains needed for:
- Teams
- SharePoint
- OneDrive
- Office web apps
- newer Microsoft cloud-hosted service front ends

Current intended entries:

```txt
aadcdn.microsoftonline-p.com
aka.ms
cloud.microsoft
config.office.com
live.com
login.live.com
lync.com
mail.protection.outlook.com
microsoft365.com
microsoftonline.com
microsoftonline-p.com
msauth.net
msauthimages.net
msftidentity.com
office.com
office.live.com
office.net
office365.com
officeapps.live.com
officecdn.microsoft.com
onmicrosoft.com
onedrive.com
onenote.com
outlook.com
outlook.office.com
outlook.office365.com
protection.outlook.com
sharepoint.com
sharepointonline.com
skype.com
skypeforbusiness.com
static.microsoft
storage.live.com
teams.microsoft.com
usercontent.microsoft
```

### Rule for future agents
Future agents must not silently add new domains to `minimal` or `sane` just because the upstream Microsoft endpoint source changed.

Any change to those curated sets should be intentional and explained in a commit message or PR note.

---

## Full list generation policy

The `o365-full-allowlist.txt` file should be regenerated automatically from upstream domain data.

Suggested behaviour:

1. Fetch upstream endpoint data.
2. Extract domain-like entries.
3. Normalise and clean them.
4. Remove IPs and non-domain artefacts.
5. Convert each valid domain into adblock exception syntax.
6. Sort deterministically.
7. Write the file with a short explanatory header.

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

If validation fails, the workflow should fail.

---

## GitHub Actions behaviour

We now use two workflows with distinct responsibilities.

Files:
- `.github/workflows/update-o365-lists.yml`
- `.github/workflows/validate-o365-lists.yml`

Update workflow triggers:
- `workflow_dispatch`
- scheduled weekly run

Update workflow behaviour:
1. Check out the repository.
2. Set up Python.
3. Run unit tests.
4. Run the generator script.
5. Validate generated files.
6. Commit changes only if tracked files changed.
7. Push back to the default branch.

Validation workflow triggers:
- `push`
- `pull_request`

Validation workflow behaviour:
1. Check out the repository.
2. Set up Python.
3. Run unit tests.
4. Validate the tracked allowlist files.

### Churn control
The workflow should avoid noisy commits.

Requirements:
- stable ordering
- no timestamp banners in output files
- no generated-on dates in the list files
- commit only when file contents actually changed

---

The workflow files in the repo are now the source of truth. Keep them simple, dependency-light, and deterministic.

---

## Generator script expectations

The future `scripts/generate_o365_lists.py` should:

1. Fetch endpoint data.
2. Parse all endpoint records.
3. Extract domains from URL/domain destination fields.
4. Normalise and clean the domains.
5. Build:
   - `minimal` from fixed curated constants
   - `sane` from fixed curated constants
   - `full` from upstream-derived cleaned domains
6. Render all files in stable adblock exception format.
7. Optionally validate file integrity before writing.

### Suggested internal structure

- `fetch_upstream_data()`
- `extract_domains(records)`
- `normalise_domain(domain)`
- `render_adblock_rules(domains, header_lines)`
- `validate_output(lines)`
- `write_if_changed(path, content)`

---

## README handling

The README is hand-written and documents:
- list roles
- automation behaviour
- local usage commands

The automation does not rewrite `README.md`.

---

## Agent instructions

If an LLM, Codex instance, or other agent is asked to modify this repo later, it should follow these rules:

1. Do not widen `minimal` casually.
2. Do not widen `sane` casually.
3. Treat `full` as the only automatically expansive list.
4. Preserve adblock exception output format.
5. Prefer stable, low-noise changes.
6. Do not switch the public list files back to regex format.
7. Keep this file updated when the automation design changes.

---

## Current implementation milestone

The current repo now supports:

- regenerating `o365-full-allowlist.txt` from upstream Microsoft endpoint data
- regenerating `o365-minimal-allowlist.txt` from curated constants
- regenerating `o365-sane-allowlist.txt` from curated constants
- validating all three files
- running manually in GitHub Actions
- running weekly scheduled updates
- unit testing the normalization and validation logic
- committing only when generated content changes

---

## Later improvements

Possible later additions:

- open a PR instead of pushing directly
- schema validation for upstream endpoint fields
- optional diff summary in workflow logs
- optional issue creation if upstream fetch fails repeatedly
- optional support for additional list formats if ever needed

---

## Current repository check snapshot

At the time this file was written, the intended starting state is:

- `o365-minimal-allowlist.txt`: curated and narrow
- `o365-sane-allowlist.txt`: curated and recommended default
- `o365-full-allowlist.txt`: broad compatibility list in adblock exception format

If future agents find duplicates, malformed escaped domains, regex remnants, or file-role confusion, they should correct those issues before expanding automation.
