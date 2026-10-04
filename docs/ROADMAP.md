# NetSecure — Roadmap

Derived from the Work Breakdown Structure in `PROJECT_PLAN.md`.
Check off items as they are completed. Each item shows its primary owner.

---

## Phase 1 — Planning and Requirements (WBS 1.0) · Sep 9–18

- [ ] Finalize project plan, SRS, roles, scope, GitHub workflow — **All / Zach lead**
- [ ] Technology decision: choose Django vs Flask, Tailwind vs Bootstrap — **All / Austin + Izaiah** *(WBS 1.1)*
- [ ] Development setup: standardize Git, Python, repo, branches, local environments — **James** *(WBS 1.2)*

## Phase 2 — Architecture and Interfaces (WBS 2.0) · Sep 16–27

- [ ] Define module boundaries, scan-result format, database interfaces, page/route map — **All / James lead**

## Phase 3 — Core Component Development · Sep 21–Oct 25

### Nmap Scanner (WBS 3.0) · Sep 21–Oct 18
- [ ] Configure Nmap and scan profiles — **Zach**
- [ ] Implement target validation (FR-02) — **Zach**
- [ ] Host discovery and service detection — **Zach**
- [ ] Structured output parsing (XML → dict) — **Zach**

### Backend Core (WBS 4.0) · Sep 21–Oct 25
- [x] Create Django project structure, settings, URLs — **Austin**
- [ ] REST API routes for scan, devices, findings, history — **Austin**
- [ ] Scan control: initiate, track status, return results — **Austin**
- [ ] Input validation and error handling — **Austin**

### Database (WBS 5.0) · Sep 21–Oct 18
- [ ] Design SQLite schema (scans, hosts, ports, services, findings) — **Matt**
- [ ] Schema initialization and migrations — **Matt**
- [ ] Data-access functions and scan-history queries — **Matt**

### Frontend (WBS 6.0) · Sep 21–Oct 25
- [ ] Dashboard layout and navigation — **Izaiah**
- [ ] Scan initiation page with target input — **Izaiah**
- [ ] Device list view — **Izaiah**
- [ ] Security findings / warnings view with severity indicators — **Izaiah**
- [ ] Scan history view — **Izaiah**
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
