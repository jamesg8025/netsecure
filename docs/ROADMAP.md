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
- [ ] Security findings / warnings view with severity indicators — **Izaiah**
- [x] Scan history view — **Izaiah**
- [ ] Scan-in-progress indicator (NFR-02) — **Izaiah**

## Phase 4 — Security Findings (WBS 7.0) · Oct 12–Nov 1

- [ ] Define rule set mapping ports/services to warnings — **Austin + Zach**
- [ ] Implement warning text and severity levels (FR-05, FR-06) — **Austin + Zach**
- [ ] Storage integration for findings — **Matt**
- [ ] Display integration for findings — **Izaiah**

## Phase 5 — Component Integration (WBS 8.0) · Oct 19–Nov 8

- [ ] Connect scanner → backend → database → frontend — **James lead / all**
- [ ] Resolve interface mismatches — **James lead / all**
- [ ] End-to-end scan-to-dashboard workflow verified — **James lead / all**

## Phase 6 — Authentication and Access Controls (WBS 9.0) · Oct 26–Nov 8

- [ ] Implement login and session management — **James + Austin**
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
