# NetSecure

A web-based network asset and vulnerability scanner built on [Nmap](https://nmap.org/).

NetSecure gives small organizations a simple dashboard for seeing what is on
their local network. A signed-in user enters a private IP address or subnet;
the backend validates it, runs Nmap to discover active hosts, open ports, and
running services, and flags services that deserve a security review (for
example Telnet, FTP, or exposed raw printing ports). Results are saved so past
scans can be reviewed from the History, Devices, and Findings pages.

For safety, NetSecure only scans **private IPv4 networks and loopback
addresses**, up to 256 addresses per scan. Only scan networks you are
authorized to test.

## Tech Stack

| Layer    | Technology                                              |
|----------|---------------------------------------------------------|
| Scanner  | Python, Nmap                                            |
| Backend  | Python, Django (REST API, session login, rule engine)   |
| Database | SQLite                                                  |
| Frontend | React, TypeScript, Vite, Tailwind CSS                   |

## Local Setup

### Prerequisites

- Python 3.14
- Node.js 24 (see `.nvmrc`)
- Nmap installed and on your `PATH` (`nmap --version` should work)

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

export DJANGO_DEBUG=1              # PowerShell: $env:DJANGO_DEBUG = "1"
python manage.py migrate
python manage.py runserver         # http://127.0.0.1:8000
```

Settings come from environment variables (see `backend/.env.example`). Nothing
loads a `.env` file automatically, so export them in your shell. For local
development, `DJANGO_DEBUG=1` is enough.

### 2. Frontend

In a second terminal:

```bash
cd frontend
npm ci
npm run dev                        # http://localhost:5173
```

The dev server forwards `/api` requests to the Django server, so keep both
running. The header shows **Backend: Connected** when it can reach the API and
**Unreachable** when it can't.

### 3. Create an account

The dashboard requires a login, and there is no sign-up page: accounts are
created on the backend and stored in your local `db.sqlite3`. In `backend/`,
with the virtualenv active and `migrate` already run:

```bash
python manage.py createsuperuser   # prompts for username, email (optional), and password
```

The password must be at least 8 characters, not too common, not all numbers,
and not too similar to the username.

To add more accounts later, run `createsuperuser` again, or log in at
<http://127.0.0.1:8000/admin/> and use **Users → Add user**. Dashboard
accounts don't need staff or superuser status.

### 4. Log in and run a scan

With both servers running:

1. Open <http://localhost:5173>. If you're not logged in, you're sent to `/login`.
2. Enter your username and password. After logging in, the header shows your
   username and a **Log out** button.
3. Go to **New Scan**, enter a target such as `127.0.0.1` or `192.168.1.0/24`,
   and click **Start Scan**.

Your login is kept in a session cookie. If the session ends, the dashboard
sends you back to `/login`.

After 5 wrong passwords for one username (or 20 from one machine) within 15
minutes, login is blocked for the rest of that window, even with the right
password. In development, restarting `runserver` clears the block.

### Tests

From the repo root:

```bash
python3 -m unittest discover -s tests   # scanner and database schema
(cd backend && python manage.py test)
(cd frontend && npm test)
(cd frontend && npm run lint)
```

## Project Docs

Requirements, architecture, design, and the roadmap live in [`docs/`](docs/).
Contributors should start with [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md)
and [`AGENTS.md`](AGENTS.md).

## License

[MIT](LICENSE)
