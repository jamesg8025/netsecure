# NetSecure — Design Document

## 1. Overview

NetSecure is a web-based network asset and vulnerability scanner that wraps Nmap
in a controlled Python backend, stores results in SQLite, evaluates security
rules against those results, and surfaces everything through a React dashboard.

This document describes the component design, their responsibilities, and how
they interact. For requirements see `SRS.md`; for the build schedule see
`ROADMAP.md`.

## 2. Component Responsibilities

| Component | Directory | Responsibility |
|-----------|-----------|----------------|
| Scanner | `/scanner` | Validate targets (FR-02), invoke Nmap via subprocess arg lists, parse XML/structured output into a normalized result dict. |
| Backend | `/backend` | Django app — REST API, scan lifecycle (start / poll / complete), business logic, security rule engine (FR-05, FR-06). |
| Database | `/database` | SQLite schema, migrations, data-access layer. Stores scans, hosts, ports/services, findings, timestamps (FR-03). |
| Frontend | `/frontend` | React + TypeScript + Vite + Tailwind v4 dashboard — login, scan initiation, device list, findings, scan history (FR-04). |

## 3. UML — Component Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          NetSecure System                           │
│                                                                     │
│  ┌──────────────┐     ┌──────────────────┐     ┌────────────────┐  │
│  │   Frontend    │     │     Backend      │     │    Scanner     │  │
│  │              │     │                  │     │                │  │
│  │  React/TS    │────▶│  Django REST API  │────▶│  Nmap wrapper  │  │
│  │  Vite        │◀────│                  │◀────│  Target valid. │  │
│  │  Tailwind v4 │     │  Rule engine     │     │  Result parser │  │
│  └──────────────┘     └────────┬─────────┘     └────────────────┘  │
│         ▲                      │                       │            │
│         │                      ▼                       ▼            │
│         │              ┌──────────────┐         ┌────────────┐     │
│         │              │   Database   │         │    Nmap     │     │
│         │              │              │         │  (external) │     │
│         │              │  SQLite      │         └────────────┘     │
│         │              │  Schema/DAL  │                             │
│         │              └──────────────┘                             │
│         │                      │                                    │
│         └──────────────────────┘                                    │
│              (findings, history, device data)                      │
└─────────────────────────────────────────────────────────────────────┘
```

## 4. UML — Sequence Diagram (Scan Request)

```
User        Frontend        Backend         Scanner         Nmap        Database
 │              │               │               │              │            │
 │──start scan─▶│               │               │              │            │
 │              │──POST /scan──▶│               │              │            │
 │              │               │──validate()──▶│              │            │
 │              │               │◀─── ok ───────│              │            │
 │              │               │               │──subprocess─▶│            │
 │              │               │               │◀──XML result─│            │
 │              │               │◀──parsed dict─│              │            │
 │              │               │──store()──────────────────────────────────▶│
 │              │               │──evaluate_rules()            │            │
 │              │               │──store_findings()────────────────────────▶│
 │              │◀──200 + data──│               │              │            │
 │◀─display─────│               │               │              │            │
```

## 5. UML — Class / Module Sketch

```
┌─────────────────────┐
│ scanner/             │
│  scanner.py          │
│   + validate_target()│
│   + run_scan()       │
│   + parse_results()  │
└─────────┬───────────┘
          │ imports / calls
┌─────────▼───────────┐
│ backend/             │
│  views.py            │
│   + start_scan()     │
│   + get_devices()    │
│   + get_findings()   │
│   + get_history()    │
│  rules.py            │
│   + evaluate()       │
│   + RULE_SET[]       │
└─────────┬───────────┘
          │ reads / writes
┌─────────▼───────────┐
│ database/            │
│  schema.sql          │
│  models.py           │
│   + Scan             │
│   + Host             │
│   + Port             │
│   + Finding          │
└─────────────────────┘
```

## 6. Data Flow Summary

1. **User** clicks "Scan" in the dashboard.
2. **Frontend** sends a POST to the backend API with the target string.
3. **Backend** forwards the target to the Scanner for validation (FR-02).
4. **Scanner** validates the target, invokes Nmap via `subprocess` (never `shell=True`), and parses the structured output.
5. **Backend** receives the parsed result, persists hosts/ports/services to **Database** (FR-03).
6. **Backend** runs the security **rule engine** against the stored results, generating findings with severity (FR-05, FR-06).
7. **Backend** returns a summary response to the **Frontend**.
8. **Frontend** renders the dashboard: device list, findings with severity badges, scan history (FR-04).

## 7. Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Django over Flask | Team decided; Django's ORM and admin simplify DB and auth work. |
| SQLite | Sufficient for single-server lab use; no external DB server needed. |
| Subprocess arg lists, never `shell=True` | Prevents command injection (FR-02, NFR-01). |
| Tailwind CSS v4 + shadcn/ui | Modern component library; consistent styling with minimal CSS. |
| Scans run asynchronously | Dashboard must not freeze during scans (NFR-02). |

## 8. Security Considerations

- All scan targets are validated before reaching Nmap (FR-02).
- Default targets restricted to private/local ranges (NFR-01).
- Authentication required before any scan or data access (UC-01).
- No exploitation or intrusive testing capabilities (SRS scope).
