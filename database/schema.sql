-- NetSecure: run once against a new SQLite database.
-- Enable this on EVERY connection, before starting a transaction.
PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

-- 1. Users
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT NOT NULL COLLATE NOCASE UNIQUE
        CHECK (length(trim(username)) > 0),
    password_hash TEXT NOT NULL CHECK (length(password_hash) > 0),
    role TEXT NOT NULL DEFAULT 'user'
        CHECK (role IN ('user', 'admin'))
);

-- 2. Scans
CREATE TABLE scans (
    scan_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    target TEXT NOT NULL CHECK (length(trim(target)) > 0),
    started_at TEXT,
    finished_at TEXT,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    error_message TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE RESTRICT,
    CHECK (
        (status = 'pending' AND started_at IS NULL AND finished_at IS NULL)
        OR (status = 'running' AND started_at IS NOT NULL AND finished_at IS NULL)
        OR (status = 'completed' AND started_at IS NOT NULL AND finished_at IS NOT NULL)
        OR (status = 'failed' AND finished_at IS NOT NULL)
    ),
    CHECK (finished_at IS NULL OR started_at IS NULL OR finished_at >= started_at),
    CHECK (status != 'failed' OR
        (error_message IS NOT NULL AND length(trim(error_message)) > 0)),
    CHECK (status = 'failed' OR error_message IS NULL)
);

-- 3. Hosts: a separate record for each scan preserves history.
CREATE TABLE hosts (
    host_id INTEGER PRIMARY KEY,
    scan_id INTEGER NOT NULL,
    ip_address TEXT NOT NULL CHECK (length(trim(ip_address)) > 0),
    hostname TEXT,
    FOREIGN KEY (scan_id) REFERENCES scans(scan_id) ON DELETE CASCADE,
    UNIQUE (scan_id, ip_address)
);

-- 4. Services: TCP and UDP may use the same port.
CREATE TABLE services (
    service_id INTEGER PRIMARY KEY,
    host_id INTEGER NOT NULL,
    port INTEGER NOT NULL CHECK (typeof(port) = 'integer' AND port BETWEEN 0 AND 65535),
    protocol TEXT NOT NULL CHECK (protocol IN ('tcp', 'udp')),
    service_name TEXT,
    FOREIGN KEY (host_id) REFERENCES hosts(host_id) ON DELETE CASCADE,
    UNIQUE (host_id, port, protocol)
);

-- 5. Findings
CREATE TABLE findings (
    finding_id INTEGER PRIMARY KEY,
    service_id INTEGER NOT NULL,
    severity TEXT NOT NULL
        CHECK (severity IN ('info', 'low', 'medium', 'high', 'critical')),
    description TEXT NOT NULL CHECK (length(trim(description)) > 0),
    FOREIGN KEY (service_id) REFERENCES services(service_id) ON DELETE CASCADE
);

-- 6. Indexes for history and finding lookups.
CREATE INDEX scans_user ON scans(user_id, scan_id);
CREATE INDEX findings_service ON findings(service_id);

COMMIT;
