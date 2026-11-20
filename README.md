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

export DJANGO_DEBUG=1              # see backend/.env.example for other settings
python manage.py migrate
python manage.py createsuperuser   # creates your login account
python manage.py runserver         # http://127.0.0.1:8000
```

### 2. Frontend

In a second terminal:

```bash
cd frontend
npm ci
npm run dev                        # http://localhost:5173
```

The dev server forwards `/api` requests to the Django server, so keep both running.

### 3. Run a scan

Open <http://localhost:5173>, log in with the account you created, go to
**New Scan**, enter a target such as `127.0.0.1` or `192.168.1.0/24`, and click
**Start Scan**.

### Tests

From the repo root:

```bash
(cd backend && python manage.py test)
(cd frontend && npm test)
```

## Project Docs

Requirements, architecture, design, and the roadmap live in [`docs/`](docs/).
Contributors should start with [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md)
and [`AGENTS.md`](AGENTS.md).

## License

[MIT](LICENSE)
