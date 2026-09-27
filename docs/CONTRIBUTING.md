# Contributing to NetSecure

A quick guide for teammates using Claude Code (or any agentic coding tool) on
this repo. For the full rules — safety, branching, commits — see
[`AGENTS.md`](../AGENTS.md) in the repo root.

---

## Starting a Session

1. Open a terminal in the repo root (`netsecure/`).
2. Launch Claude Code: `claude`
3. Point the agent at the roadmap so it knows what to work on:

   > "Read docs/ROADMAP.md and find the next unchecked item in Phase 3 that
   > belongs to me."

4. The agent will pick up `AGENTS.md` automatically — it contains the safety
   rules, workflow, and commit conventions.

## Typical Workflow

1. **Pick a roadmap item.** Ask the agent to read `docs/ROADMAP.md` and propose
   a branch name for the next unchecked item in your area.
2. **Confirm before creating.** The agent will propose a branch/PR split — say
   yes or adjust before it writes code.
3. **Implement in small slices.** One logical commit per change. Tests go in the
   same commit as the code they cover.
4. **Check off the item.** When the work is done, ask the agent to mark the
   roadmap item complete.
5. **Open a PR.** The agent can push the branch and open a PR that references
   the roadmap item and any SRS requirements.

## Branch and PR Conventions

- Branch format: `<area>/<short-description>`
  - Examples: `backend/scan-validation`, `frontend/device-list-view`, `database/schema-init`
- PR description should name the roadmap item and the SRS requirement it
  addresses (e.g., "Implements WBS 3.0 target validation — FR-02").
- `main` has branch protection: PRs required, no direct pushes.

## Good Prompts vs. Vague Prompts

| Good (scoped, actionable) | Vague (too broad, unclear) |
|---------------------------|---------------------------|
| "Read docs/ROADMAP.md and implement the target validation function in scanner/. It should accept an IP or CIDR string, reject anything else, and return a clear error. Add tests." | "Build the scanner." |
| "Add the SQLite schema from DESIGN.md — tables for scans, hosts, ports, and findings. Put the SQL in database/schema.sql and add an init script." | "Set up the database." |
| "In frontend/, create a DeviceList component that fetches from /api/devices and renders a table with IP, hostname, open ports, and a severity badge. Use shadcn/ui Table." | "Make the frontend look good." |

**Why this matters:** A scoped prompt lets the agent make one focused PR that's
easy to review. A vague prompt leads to sprawling changes that are hard to review
and may step into another owner's area.

## Rules to Remember

- **Never skip target validation** — see the Critical Safety Rule in `AGENTS.md`.
- **Flag cross-area changes** before making them.
- **Don't change the SQLite schema** without discussing it first.
- **Tests ship with the code**, not in a follow-up.

For the full set of rules, read [`AGENTS.md`](../AGENTS.md).
