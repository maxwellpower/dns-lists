# DNS Lists

DNS allow lists in adblock-style exception format for Pi-hole and similar DNS or content filtering systems.

The main managed outputs in this repo are the Microsoft 365 set under `o365/` and the GitHub core sidecar under `github/`. The repo also includes a small number of manually maintained provider-specific sidecar lists where they are practically useful.

## Repo Layout

### `o365/`
Managed Microsoft 365 lists.

Files:
- `o365/o365-minimal-allowlist.txt`
- `o365/o365-sane-allowlist.txt`
- `o365/o365-full-allowlist.txt`

These remain the main public focus of the repo.

### `github/`
Managed GitHub sidecar lists.

Current file:
- `github/github-allowlist.txt`

### `google/`
Manual Google sidecar lists.

Current file:
- `google/google-allowlist.txt`

### `okta/`
Manual Okta sidecar lists.

Current file:
- `okta/okta-allowlist.txt`

### `scripts/generate_o365_lists.py`
Single source of truth for:
- curated O365 domain sets
- Microsoft endpoint fetching
- GitHub meta API fetching
- domain normalization
- allowlist rendering
- validation of both managed and manual lists

### `data/`
Metadata for the managed upstream-backed lists.

Files:
- `data/m365-endpoint-metadata.json`
- `data/github-meta-metadata.json`

### `.github/workflows/update-dns-lists.yml`
Scheduled and manual updater for the managed Microsoft 365 and GitHub lists. Runs weekly and only commits when generated files actually change.

### `.github/workflows/validate-dns-lists.yml`
CI validation for pushes and pull requests. Verifies tests and file integrity for the managed O365 and GitHub lists plus the manual sidecars.

## O365 Tiers

### `o365/o365-minimal-allowlist.txt`
Smallest starting point.

Use this when you mainly want:
- sign-in and identity flows
- Outlook / Exchange access
- basic tenant routing

This is best for desktop Office and Outlook setups where you do not need full Teams, SharePoint, or OneDrive web functionality.

### `o365/o365-sane-allowlist.txt`
Recommended default.

Use this when you want the best balance between:
- Microsoft 365 working normally
- avoiding broader Microsoft domains that may be blocked by privacy lists for good reason

This list covers the core domains for:
- authentication
- Outlook / Exchange
- Teams
- SharePoint
- OneDrive
- Office web apps
- newer Microsoft `cloud.microsoft` infrastructure

### `o365/o365-full-allowlist.txt`
Maximum compatibility list.

Use this when you want to allow nearly everything published or commonly required for Microsoft 365 and related services, including many supporting and optional domains.

This list is useful for:
- troubleshooting broken Microsoft 365 behaviour
- testing whether a block list is interfering with service operation
- environments where compatibility matters more than minimising allowed Microsoft infrastructure

## Format

All list files use adblock-style exception syntax, for example:

```txt
@@||office.com^
@@||microsoftonline.com^
@@||cloud.microsoft^
```

## Suggested Starting Point

Start with `o365/o365-sane-allowlist.txt`.

Move to `o365/o365-minimal-allowlist.txt` if you want a tighter setup and know you do not need the extra Microsoft 365 web services.

Move to `o365/o365-full-allowlist.txt` if something is still breaking and you want to rule out domain blocking first.

## Notes

- These lists are intended as practical starting points, not a guarantee that every feature will work in every environment.
- The managed automation scope is `o365/` plus `github/github-allowlist.txt`.
- `minimal` and `sane` are intentionally hand-curated in code and are not widened automatically when Microsoft adds new endpoints.
- `google/` and `okta/` are manual sidecars. They are validated in CI for format, but they are not fetched or rewritten by automation.
- `github/github-allowlist.txt` is generated from the GitHub meta API website domains plus a curated subset of core API and download endpoints. It is still intentionally conservative and does not try to cover every GitHub-adjacent service such as Actions, Packages, Codespaces, or Copilot.
- The Google sidecar is intentionally conservative. It aims to reduce common breakage around Google sign-in, Google APIs, Firebase Hosting, and Firebase Cloud Messaging, but it is not a complete Google Workspace or Android network policy.
- Microsoft continues moving services onto newer domains such as `cloud.microsoft`, so the O365 lists will continue to evolve over time.

## Automation

The intended long-term process is:

1. GitHub Actions runs weekly or on manual dispatch.
2. The generator fetches the latest Microsoft endpoint data.
3. The generator fetches the latest GitHub meta payload.
4. `o365/o365-full-allowlist.txt` is rebuilt from upstream domains after normalization and cleanup.
5. `o365/o365-minimal-allowlist.txt` and `o365/o365-sane-allowlist.txt` are rebuilt from explicit curated constants.
6. `github/github-allowlist.txt` is rebuilt from GitHub website domains plus selected core API/download endpoints.
7. The workflow validates file integrity for both managed and manual lists.
8. Only the managed O365 and GitHub outputs are automatically rewritten and committed.

This keeps the broad compatibility lists fresh, protects the curated Microsoft lists from accidental expansion, and still catches formatting issues in the manual sidecars.

## Local Usage

Regenerate the managed O365 and GitHub files:

```bash
python3 scripts/generate_o365_lists.py
```

Validate the tracked list files:

```bash
python3 scripts/generate_o365_lists.py --validate-only
```

Run unit tests:

```bash
python3 -m unittest discover -s tests
```
