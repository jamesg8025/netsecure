# NetSecure database

SQLite implementation of the recovered five-table design:
users -> scans -> hosts -> services -> findings.

This package includes an empty netsecure.db for inspection, schema.sql,
init_db.py, and test_db.py. It has not been connected to Austin's Django project.

## Setup

Use the included database, or on a fresh checkout run:

    python init_db.py
    python test_db.py

Python's standard library is sufficient. schema.sql is a one-time initialization
script, not an upgrade script. It deliberately fails if these tables already
exist. Do not run it against the team's existing database.

## Sections

1. users: account name, password hash, and proposed user/admin role.
2. scans: user ownership, target, lifecycle, timestamps, and failure details.
3. hosts: devices discovered within a particular scan; repeated scans keep
   separate copies so past results are not overwritten.
4. services: network services on each host, identified by port and protocol.
5. findings: security warnings attached to a service, with severity.
6. indexes: faster user history and service findings lookup. UNIQUE constraints
   already index scan/IP and host/port/protocol.

## Backend contract

- Decide authentication integration BEFORE using this schema in Django.
  The users table preserves the original ERD but is not a drop-in Django User.
  If Austin already uses Django authentication, reference settings.AUTH_USER_MODEL
  in the Scan model and generate matching migrations; do not maintain two
  independent login/password stores. No Django models are supplied because the
  existing project and migrations have not been provided.
- Django migrations should own schema changes once integrated. Preserve simple
  table names using db_table and existing primary-key names explicitly if needed.
  Do not both execute this schema and apply migrations that recreate the tables.
- Hash and verify passwords using the backend's password tools; never save
  plaintext. The database cannot verify whether a supplied value is a real hash.
- Enable PRAGMA foreign_keys = ON on each direct SQLite connection before any
  transaction. Use parameterized queries or Django ORM, never string interpolation.
- Timestamps are UTC text, always YYYY-MM-DD HH:MM:SS; CURRENT_TIMESTAMP gives
  that format. Normalize timestamps in the backend; SQL does not validate their
  complete format. started_at is actual execution time, not queue time.
- Create pending scans with timestamps NULL. Set status=running and started_at
  together. Save results and mark completed/finished_at together in a short
  transaction. Run Nmap outside database transactions. For failed scans set
  finished_at and error_message together; started_at may be NULL for startup failures.
- Store one normalized IP per host per scan. Validate target/IP syntax and scan
  authorization in the backend. Enforce role and scan-ownership access there too.
- Assumption: services contains discovered OPEN TCP/UDP ports only; no port-state
  column yet. Findings are service-specific, not host-wide or scan-wide.
- A scan can complete with zero hosts or findings. Duplicate finding descriptions
  are allowed because multiple checks may yield similar warnings.
- Save each scan result batch once; don't blindly retry committed inserts.
- Deleting a scan deletes its hosts/services/findings. Deleting a user who owns
  scans is blocked. Permission to delete must be checked by the backend.
- Dashboard queries should count hosts and findings separately to avoid inflated
  host counts caused by one-to-many joins.
- Each developer uses a separate local database. SQLite has one writer at a time;
  keep writes short and reassess database choice if concurrent jobs become heavy.

## Git and GitHub

Commit schema.sql, init_db.py, test_db.py, README.md, .gitignore and, once added,
Django models and migrations. Merge the ignore patterns into the repository's
existing .gitignore. Do not commit live databases, credentials or real scan data.
Git shares source and schema changes; it does not synchronize running databases.
The empty database in this download is a convenience and is ignored by Git.
No remote repository was provided, so nothing has been pushed to GitHub.

## Decisions still needed

1. Austin's Django User model, Django version, existing models and migrations.
2. Zach's sample parsed scanner output, including protocols and port states.
3. Whether findings can apply to an entire host or scan.
4. Roles, who can view/delete whose scans, and scan-retention policy.
5. Required extras: CVE IDs, remediation, service versions, raw output, reports.
6. Whether queued/canceled/retried scans and multiple simultaneous jobs are needed.
