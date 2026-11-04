# AGENTS.md — NetSecure

## Project Context

NetSecure is a web-based network asset and vulnerability scanner built on Nmap,
for a 5-person senior project team. Full context lives in `docs/`:

- `SRS.md` — requirements (FR-01 through FR-06, NFR-01 through NFR-06)
- `PROJECT_PLAN.md` — schedule, roles, risks, milestones
- `ARCHITECTURE.md` — system design and Mermaid data-flow diagram
- `DESIGN.md` — component design, UML diagrams, interface sketches
- `ROADMAP.md` — current phase and next unchecked item
- `CONTRIBUTING.md` — onboarding guide for teammates

## Team

| Role | Owner |
|------|-------|
| Project Manager / Network Scanning | Zach |
| Backend Development | Austin |
| Database Development | Matt |
| Frontend Development | Izaiah |
| Integration / Testing / GitHub | James |

## Repo Map

| Directory | Contents | Status |
|-----------|----------|--------|
| `/scanner` | Nmap integration, target validation, scan execution, result parsing | Scaffolded (`.gitkeep` only) |
| `/backend` | Python/Django web app, REST API, security rule engine | Initialized — Django 6.1 project (`config/`), `api` app with `/api/health/`, `/api/csrf/`, synchronous `POST /api/scans/` (validated via the scanner, results saved), `GET /api/scans/` history and per-scan devices/findings, scan models and `scan_store` data-access layer, JSON error handling, request validation helpers |
| `/database` | SQLite schema, migrations, data-access layer | Reference schema and queries (Matt); Django migrations in `backend/api/` own the live schema |
| `/frontend` | React + TypeScript + Vite + Tailwind v4 dashboard | Dashboard shell — routed pages, `/api` dev proxy, backend health indicator; New Scan calls `POST /api/scans/` and lists results; History lists `GET /api/scans/` |
| `/docs` | SRS, project plan, architecture, design, roadmap, contributing guide | Active |

## Critical Safety Rule

Any path between user input and Nmap execution **MUST** validate the target
first (SRS FR-02). Never build a shell command by concatenating or interpolating
unvalidated input — use subprocess argument lists, not `shell=True`. If a task
touches scan-target handling, scanner invocation, or anything that constructs a
command string, stop and flag it explicitly rather than proceeding on inferred
intent. This is a hard stop, not a style preference.

## Stack

| Layer | Technology |
|-------|------------|
| Scanner | Python, Nmap (subprocess, never `shell=True`) |
| Backend | Python, Django |
| Database | SQLite |
| Frontend | React 19, TypeScript, Vite, Tailwind CSS v4, React Router, ESLint, Vitest + React Testing Library, shadcn/ui (planned) |
| Source control | GitHub — classic branch protection on `main` (PR required, no direct pushes) |

## Workflow

1. Check `docs/ROADMAP.md` for the current phase and next unchecked item.
2. Propose the branch/PR split for that item; wait for confirmation before creating anything.
3. Create the branch, implement the smallest coherent slice of that item.
4. Add or update tests alongside the change — not deferred to a later commit.
5. Check off the roadmap item when done; update SRS / ARCHITECTURE / ROADMAP if the change affects them.
6. Don't jump ahead to a later phase or another owner's area without flagging why.
7. Push the branch and open the PR once the item's commits are complete.

## Commits

- One logical, reviewable unit per commit — a feature, fix, or refactor with a clear purpose. Don't squash a whole roadmap item into one commit.
- Split multi-part work by concern (schema change separate from the endpoint using it; a detection rule separate from its tests).
- Reference the roadmap/WBS item: `Add FTP detection rule (WBS 7.0, FR-05)`.

## Branching and PRs

- Branch name: `<area>/<short-description>` — e.g. `frontend/device-list-view`, `backend/scan-validation`.
- PR description names the roadmap item and the SRS requirement it addresses, if any.

## Crossing Into Another Owner's Area

Flag it and say why before doing it. Ownership boundaries exist so five people
aren't stepping on each other — a cross-area change should be a coordinated
decision, not a silent side effect of "fixing" something adjacent.

## Don't

- Don't commit VM disk files or exports (already gitignored — `.vdi`, `.ova`, etc.).
- Don't loosen scan-target validation to make a demo work.
- Don't change the SQLite schema without flagging it — other components depend on its shape.
- Don't add dependencies without flagging it — the team should agree on new packages.
