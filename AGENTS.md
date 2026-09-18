# AGENTS.md — NetSecure

## Project Context
NetSecure is a web-based network asset and vulnerability scanner built on Nmap, for a 5-person project team. Full context lives in `docs/`: SRS.md (requirements), PROJECT_PLAN.md (schedule/roles), ARCHITECTURE.md (system design), ROADMAP.md (current phase/next item).

## Repo Map
- `/scanner` — Nmap integration, scan execution
- `/backend` — Python web app, API, security rule engine
- `/database` — SQLite schema, migrations, data access
- `/frontend` — React/TypeScript/Vite/Tailwind dashboard
- `/docs` — requirements, plan, architecture, roadmap
- Integration/testing/CI spans all areas

## Critical Safety Rule
Any path between user input and Nmap execution MUST validate the target first (SRS FR-02). Never build a shell command by concatenating or interpolating unvalidated input — use subprocess argument lists, not `shell=True`. If a task touches scan-target handling, scanner invocation, or anything that constructs a command string, stop and flag it explicitly rather than proceeding on inferred intent. This is a hard stop, not a style preference.

## Stack
- Scanner: Python, Nmap
- Backend: Python (Django)
- Database: SQLite
- Frontend: React, TypeScript, Vite, Tailwind CSS v4, ESLint, shadcn/ui
- Source control: GitHub, classic branch protection on `main` (PR required, no direct pushes)

## Workflow
1. Check `docs/ROADMAP.md` for the current phase and next unchecked item.
2. Propose the branch/PR split for that item; wait for confirmation before creating anything.
3. Create the branch, implement the smallest coherent slice of that item.
4. Add or update tests alongside the change — not deferred to a later commit.
5. Check off the roadmap item when done; update SRS/ARCHITECTURE/ROADMAP if the change affects them.
6. Don't jump ahead to a later phase or another owner's area without flagging why.
7. Push the branch and open the PR once the item's commits are complete.

## Commits
- One logical, reviewable unit per commit — a feature, fix, or refactor with a clear purpose. Don't squash a whole roadmap item into one commit.
- Split multi-part work by concern (schema change separate from the endpoint using it; a detection rule separate from its tests).
- Reference the roadmap/WBS item: `Add FTP detection rule (WBS 7.0, FR-05)`.

## Branching and PRs
- `<area>/<short-description>` — e.g. `frontend/device-list-view`, `backend/scan-validation`.
- PR description names the roadmap item and the SRS requirement it addresses, if any.

## Crossing Into Another Owner's Area
Flag it and say why before doing it. Ownership boundaries exist so five people aren't stepping on each other — a cross-area change should be a coordinated decision, not a silent side effect of "fixing" something adjacent.

## Don't
- Don't commit VM disk files or exports (already gitignored — `.vdi`, `.ova`, etc.).
- Don't loosen scan-target validation to make a demo work.
- Don't change the SQLite schema without flagging it — other components depend on its shape.