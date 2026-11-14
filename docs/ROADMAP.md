# NetSecure — Roadmap

Derived from the Work Breakdown Structure in `PROJECT_PLAN.md`.
Check off items as they are completed. Each item shows its primary owner.

---

## Phase 1 — Planning and Requirements (WBS 1.0) · Sep 9–18

- [ ] Finalize project plan, SRS, roles, scope, GitHub workflow — **All / Zach lead**
- [x] Technology decision: chose Django over Flask, Tailwind over Bootstrap — **All / Austin + Izaiah** *(WBS 1.1)*
- [ ] Development setup: standardize Git, Python, repo, branches, local environments — **James** *(WBS 1.2)*

## Phase 2 — Architecture and Interfaces (WBS 2.0) · Sep 16–27

- [ ] Define module boundaries, scan-result format, database interfaces, page/route map — **All / James lead**

## Phase 3 — Core Component Development · Sep 21–Oct 25

### Nmap Scanner (WBS 3.0) · Sep 21–Oct 18
- [x] Configure Nmap and scan profiles — **Zach**
- [x] Implement target validation (FR-02) — **Zach**
- [x] Host discovery and service detection — **Zach**
- [x] Structured output parsing (XML → dict) — **Zach**

Scanner component implementation and Windows localhost verification completed
October 29, 2026: 17 tests pass. See `SCANNER_HANDOFF.md` for the actual result
contract and remaining team integration/Ubuntu acceptance checks. These scanner
checkboxes do not mark whole-system testing or other owners' work complete.

### Backend Core (WBS 4.0) · Sep 21–Oct 25
- [x] Create Django project structure, settings, URLs — **Austin**
- [x] REST API routes for scan, devices, findings, history — **Austin**
- [ ] Scan control: initiate, track status, return results — **Austin**
- [ ] Input validation and error handling — **Austin**

### Database (WBS 5.0) · Sep 21–Oct 18
- [x] Design SQLite schema (scans, hosts, ports, services, findings) — **Matt**
- [x] Schema initialization and migrations — **Matt**
- [x] Data-access functions and scan-history queries — **Matt**

### Frontend (WBS 6.0) · Sep 21–Oct 25
- [x] Dashboard layout and navigation — **Izaiah**
- [ ] Scan initiation page with target input — **Izaiah**
- [x] Device list view — **Izaiah**
- [x] Security findings / warnings view with severity indicators — **Izaiah**
- [x] Scan history view — **Izaiah**
- [x] Scan-in-progress indicator (NFR-02) — **Izaiah**

## Phase 4 — Security Findings (WBS 7.0) · Oct 12–Nov 1

- [x] Define rule set mapping ports/services to warnings — **Austin + Zach**
- [x] Implement warning text and severity levels (FR-05, FR-06) — **Austin + Zach**
- [x] Storage integration for findings — **Matt**
- [x] Display integration for findings — **Izaiah**

## Phase 5 — Component Integration (WBS 8.0) · Oct 19–Nov 8

- [ ] Connect scanner → backend → database → frontend — **James lead / all**
- [ ] Resolve interface mismatches — **James lead / all**
- [ ] End-to-end scan-to-dashboard workflow verified — **James lead / all**

## Phase 6 — Authentication and Access Controls (WBS 9.0) · Oct 26–Nov 8

- [x] Implement login and session management — **James + Austin**
- [ ] Restrict scans to authorized users and approved targets — **James + Austin**

## Phase 7 — System Testing (WBS 10.0) · Nov 2–15

- [ ] Functional testing against SRS requirements — **James lead / all**
- [ ] Integration and failure-path testing — **James lead / all**
- [ ] Repeatability, usability, and compatibility tests (NFR-03, NFR-06) — **James lead / all**

## Phase 8 — Bug Fixing and Hardening (WBS 11.0) · Nov 9–15

- [ ] Resolve critical defects — **All**
- [ ] Improve error handling and polish scan rules — **All**
- [ ] UI polish and usability fixes — **All**

## Phase 9 — Final Documentation and Demo (WBS 12.0) · Nov 9–20

- [ ] Setup guide and final report updates — **All / Zach coordinate**
- [ ] Screenshots and demo plan — **All / Zach coordinate**
- [ ] Presentation practice and final submission — **All / Zach coordinate**

---

**Target:** Project complete and presentation-ready by **November 20, 2026**.

### Scanner progress — October 23, 2026

WBS 3.0: CLI target input and private IPv4 validation are implemented on
`feature/nmap-scanner`. Seven offline regression tests pass, including proof
that rejected input never starts Nmap, loopback size limits, result parsing,
and execution failures. Usage and the current result contract are documented
in `scanner/README.md`. Public-target rejection was also checked through the CLI.
Live Nmap scanning on this environment and Ubuntu verification remain pending;
Nmap was unavailable on PATH. The provisional backend result contract still
needs team agreement before integration. Broader roadmap items remain unchecked.

### Integration progress — November 1, 2026

WBS 8.0 first slice (#9): `POST /api/scans/` validates the target through
`scanner.validator` (FR-02) and returns the scanner's host/service list; the
New Scan page calls it and shows a scanning state, results, and errors. Scans
run synchronously and nothing is persisted yet. Database storage (WBS 5.0),
background jobs, and auth (WBS 9.0) remain open, so no roadmap boxes are
checked by this change.

### Database progress — November 2, 2026

WBS 5.0: Matt's schema, queries, and importer are in `database/`, with
`product`/`version`/`title`/`profile` columns added. Django models and a
migration mirror the schema (`backend/api/models.py`), and
`backend/api/scan_store.py` holds the scan lifecycle, result saving, and
history/devices/findings queries. `POST /api/scans/` now saves every scan,
including failures with their reason (FR-03, NFR-04). Scans have no owner
until login exists (WBS 9.0). Still open: API routes and frontend pages for
history/devices/findings, storing rule-engine findings (WBS 7.0), and
background jobs (NFR-02).

### Integration progress — November 2, 2026

WBS 4.0/8.0: read endpoints for saved scans: `GET /api/scans/` (history),
`GET /api/scans/{id}/devices/`, and `GET /api/scans/{id}/findings/`, listed in
`ARCHITECTURE.md` under API Endpoints. Every scan is visible until login exists
(WBS 9.0). Next: the frontend History, Devices, and Findings pages (WBS 6.0).

### Integration progress — November 4, 2026

WBS 6.0/8.0 (#13): the History page lists saved scans from `GET /api/scans/`,
with loading, error, and empty states, and shows why a scan failed (NFR-04).
Still open for UC-05: selecting a scan to see its results. Next: the Devices and
Findings pages.

### Frontend review follow-up — November 5, 2026

WBS 6.0 (#14): restore the New Scan status message, align History table cells,
and keep each Devices service's port, product, and version together. Device
search covers host, service, product, and version fields. Focused component tests
cover the device service rows and product/version search.

### Device data integration — November 6, 2026

WBS 6.0/8.0: the Devices page now loads the newest completed scan and its
device/service rows from `GET /api/scans/` and `GET /api/scans/{id}/devices/`.
It shows loading, error, no-completed-scan, no-device, and no-search-match
states. Its summary distinguishes unique devices from displayed rows; search
matches combined host and service fields. Tests cover API errors including
`scan_not_found`. Selecting older scans and broader end-to-end verification
remain open.

### Findings cleanup — November 6, 2026

WBS 6.0 (#16): Findings search includes the port, trims/tokenizes the query,
and uses the visible row hover treatment. A Service-column test covers its
rendering. Findings API integration remains open.

### Scan button cleanup — November 6, 2026

WBS 6.0 (#16): the Start Scan button has pointer and enabled-hover styling.

### Scan selection — November 7, 2026

WBS 6.0/8.0 (#16, UC-05): History links each completed scan to its devices
(`/devices?scan=<id>`). Without `?scan=`, Devices still shows the newest
completed scan. An unknown scan, or one that failed or hasn't finished, gets a
message and a link back to History. The shared `useSelectedScan` hook will also
serve Findings. Findings API integration remains open.

### Findings data integration — November 7, 2026

WBS 6.0/8.0 (#16, UC-04): Findings loads the chosen scan's findings from
`GET /api/scans/{id}/findings/` through the same hook, and History links each
completed scan to them. Severities map to labels, with an Info level. Nothing
stores findings until the rule engine lands (WBS 7.0), so the empty state says
an empty list doesn't mean the network is safe.

### Service-review findings — November 8, 2026 (feature branch)

WBS 7.0, FR-05/FR-06: `backend/service-findings` implements five conservative
service-review rules, atomic finding storage with scan results, and updated
Findings guidance. See `SECURITY_RULES.md` for matches, severities, exclusions,
and testing. The feature branch awaits team review/merge; the main-branch
checkboxes remain unchanged until review. The login screen and approved-user
scan access control remain separate WBS 9.0 work.

### Login backend — November 8, 2026

WBS 9.0 (UC-01): `POST /api/auth/login/`, `POST /api/auth/logout/`, and
`GET /api/auth/me/` use Django session authentication. Sessions last 8 hours in
an HTTP-only cookie; session and CSRF cookies are HTTPS-only when debug is off.
Accounts come from `createsuperuser` or the admin. The login item stays
unchecked until the frontend has a login page (WBS 6.0). The scan endpoints
don't require login yet: that, and limiting each user to their own scans, is the
next item ("Restrict scans to authorized users"). Repeated failed logins are
not throttled yet.

### Login page — November 8, 2026

WBS 6.0/9.0 (#23, UC-01): the frontend now has a standalone `/login` page and
calls the session login endpoint. It keeps the returned CSRF token for later
requests and redirects to New Scan after login. This slice does not yet protect
dashboard routes or add logout; those stay in the follow-up authentication PR.

### Dashboard session protection — November 9, 2026

WBS 6.0/9.0 (#28, UC-01–UC-05): the frontend loads the current session user,
protects dashboard routes, returns users to their requested page after login,
and redirects signed-in users away from `/login`. The dashboard header shows
the username and logs out; API 401 responses clear frontend auth state, and
logout handles the empty 204 and clears the cached CSRF token. Backend scan
authorization and per-user scan ownership remain open under "Restrict scans to
authorized users and approved targets."

### Login complete — November 9, 2026

WBS 9.0 (UC-01): "Implement login and session management" is checked off. The
backend login, logout, and current-user endpoints (#22), the login page (#27),
and dashboard protection with logout (#29) are all merged. Still open:
"Restrict scans to authorized users and approved targets". Until then the
browser enforces login but the scan API doesn't, and every scan is visible to
any caller. Repeated failed logins are not throttled yet.

### Scan-in-progress indicator — November 11, 2026

WBS 6.0 (#32, NFR-02, UC-02): while a scan runs, the Start Scan button shows a
spinner and New Scan shows a status card with the target, an elapsed timer,
and an indeterminate progress bar, so the page doesn't look frozen. A shared
`Spinner` component is available for other loading states. The timer isn't
announced on every tick, and with reduced motion the spinner stops and the bar
is hidden. The bar can't show a real percentage because scans are still
synchronous; that waits on "Scan control: initiate, track status, return
results" (WBS 4.0).
