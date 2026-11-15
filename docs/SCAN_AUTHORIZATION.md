# Scan authorization (WBS 9.0)

The scan API requires an active Django login session for History, scan creation,
Devices, and Findings. Anonymous requests receive JSON `401 not_authenticated`.
CSRF remains mandatory for POST: a missing or invalid token may produce 403
before the authentication check. A valid CSRF token alone never permits scanning.

New scans belong to `request.user`, including failures. Client-supplied owner
fields cannot override that identity. History includes only that user's scans.
Detail endpoints return the same `404 scan_not_found` for nonexistent IDs,
another user's scans, and legacy scans without an owner. Staff and superuser
accounts have no ownership bypass in these dashboard API endpoints.

## Existing databases and deployment

No schema migration, dependency update, or automatic ownership backfill is
required. Old unowned scans remain in SQLite but will disappear from dashboard
History when this branch is deployed. They are not deleted. Do not automatically
claim them for whichever account logs in first. An administrator must establish
ownership before any separate, deliberate data migration; otherwise retain them
as archived evidence and run new scans while signed in.

The presentation app and its separate screenshot database remain on their existing
build until this branch is reviewed and deployed. Ubuntu validation uses a separate
source/database directory, so earlier demo results remain available.

The existing private-IPv4/range validation remains unchanged. This feature does
not add an organization-specific approved-target allowlist, login throttling, or
dependency remediation. Private addressing alone is not authorization to scan a
network. Only scan lab targets you control or have permission to test.

## Verification

`backend/api/test_authorization.py` tests anonymous reads and valid-CSRF POSTs,
no scanner call or new scan on rejection, per-user history, owner-only device and
finding access, identical 404s, forged owner IDs, CSRF enforcement, logout, and
staff isolation. Existing scanner/API/result tests now use authenticated clients
and owned fixtures. Target validation and Nmap invocation are unchanged.
