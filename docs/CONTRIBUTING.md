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

## Backend Setup

Requires Python 3.14.7. From the repo root:

```bash
cd backend
python3 -m venv .venv                      # Windows: python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Settings come from environment variables (see `backend/.env.example`). Nothing
loads a `.env` file automatically, so export them in your shell. For local
development, `DJANGO_DEBUG=1` is enough:

```bash
export DJANGO_DEBUG=1            # PowerShell: $env:DJANGO_DEBUG = "1"
python manage.py migrate         # create/update your local db.sqlite3 (re-run after pulling new migrations)
python manage.py test
python manage.py runserver       # then open http://127.0.0.1:8000/api/health/
```

## Frontend Setup

Requires Node 24 (22.22+ also works). The repo root has an `.nvmrc`, so with
[nvm](https://github.com/nvm-sh/nvm) run `nvm install` once, then `nvm use` in
new terminals.

```bash
cd frontend
npm ci                           # install exact versions from package-lock.json
npm run dev                      # http://localhost:5173
npm test                         # Vitest, once; npm run test:watch to re-run on save
npm run lint
npm run build                    # type-check + production build
```

The dev server forwards `/api/*` to the Django server at `127.0.0.1:8000`, so
run the backend alongside it. The header shows **Backend: Connected** when
it can reach `GET /api/health/`, and **Unreachable** when it can't.

## Creating an Account and Logging In

The dashboard requires a login, and there is no sign-up page: accounts are
created on the backend. Accounts live in your local `db.sqlite3`, so each
teammate creates their own.

**Create an account (once).** In `backend/`, with the virtualenv active and
`migrate` already run:

```bash
python manage.py createsuperuser  # prompts for username, email (optional), and password
```

The password must be at least 8 characters, not too common, not all numbers,
and not too similar to the username.

To add more accounts later, run `createsuperuser` again, or log in at
<http://127.0.0.1:8000/admin/> with your superuser and use **Users → Add user**.
Dashboard accounts don't need staff or superuser status.

**Log in.** With both servers running (`runserver` and `npm run dev`):

1. Open <http://localhost:5173>. If you're not logged in, you're sent to `/login`.
2. Enter your username and password. A wrong username or password shows the
   same "Incorrect username or password." message either way.
3. After logging in, you land on the page you originally asked for. The header
   shows your username and a **Log out** button.

Your login is kept in a Django session cookie. If the session ends, or any API
call returns 401, the dashboard sends you back to `/login`.

After 5 wrong passwords for one username (or 20 from your machine) within 15
minutes, login is blocked for the rest of that window, even with the right
password. In development, restarting `runserver` clears the block.

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
