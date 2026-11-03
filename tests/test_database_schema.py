"""Constraint tests for database/schema.sql, run against an in-memory database.

Converted from Matt's database/test_db.py so `python -m unittest discover -s tests`
runs it. Nothing here touches a database file on disk.
"""
import sqlite3
import unittest
from pathlib import Path

SCHEMA = Path(__file__).resolve().parent.parent / "database" / "schema.sql"


class SchemaTestCase(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.executescript(SCHEMA.read_text())
        # Unusable test password marker, not an actual login.
        self.db.execute("INSERT INTO users VALUES (1, 'matt', '!disabled', 'user')")

    def tearDown(self):
        self.db.close()

    def reject(self, sql, params=()):
        with self.assertRaises(sqlite3.IntegrityError, msg=sql):
            self.db.execute(sql, params)

    def count(self, table):
        return self.db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    def add_scan(self, scan_id=1, host_id=1):
        self.db.execute(
            "INSERT INTO scans (scan_id, user_id, target) VALUES (?, 1, '192.0.2.1')", (scan_id,))
        self.db.execute(
            "INSERT INTO hosts (host_id, scan_id, ip_address) VALUES (?, ?, '192.0.2.1')",
            (host_id, scan_id))


class UserTests(SchemaTestCase):
    def test_usernames_are_case_insensitive_unique(self):
        self.reject("INSERT INTO users VALUES (2, 'MATT', '!disabled', 'user')")

    def test_user_with_scans_cannot_be_deleted(self):
        self.add_scan()
        self.reject("DELETE FROM users WHERE user_id=1")


class HostAndServiceTests(SchemaTestCase):
    def test_scan_requires_existing_user(self):
        self.reject("INSERT INTO scans (user_id, target) VALUES (99, '192.0.2.1')")

    def test_repeated_scans_keep_separate_hosts(self):
        self.add_scan(1, 1)
        self.add_scan(2, 2)
        self.assertEqual(self.count("hosts"), 2)

    def test_one_ip_per_scan(self):
        self.add_scan()
        self.reject("INSERT INTO hosts (host_id, scan_id, ip_address) VALUES (3, 1, '192.0.2.1')")

    def test_tcp_and_udp_share_a_port(self):
        self.add_scan()
        self.db.execute("INSERT INTO services (host_id, port, protocol, service_name) VALUES (1, 53, 'tcp', 'domain')")
        self.db.execute("INSERT INTO services (host_id, port, protocol, service_name) VALUES (1, 53, 'udp', 'domain')")
        self.reject("INSERT INTO services (host_id, port, protocol, service_name) VALUES (1, 53, 'tcp', 'domain')")

    def test_port_must_be_an_integer_in_range(self):
        self.add_scan()
        for port in (65536, -1, 80.5):
            with self.subTest(port=port):
                self.reject("INSERT INTO services (host_id, port, protocol) VALUES (1, ?, 'tcp')", (port,))


class FindingTests(SchemaTestCase):
    def setUp(self):
        super().setUp()
        self.add_scan()
        self.db.execute("INSERT INTO services (service_id, host_id, port, protocol) VALUES (1, 1, 53, 'tcp')")

    def test_finding_requires_existing_service(self):
        self.reject("INSERT INTO findings (service_id, severity, description) VALUES (999, 'high', 'Example')")

    def test_severity_must_be_known(self):
        self.reject("INSERT INTO findings (service_id, severity, description) VALUES (1, 'bad', 'Example')")

    def test_description_is_required(self):
        self.reject("INSERT INTO findings (service_id, severity, description) VALUES (1, 'high', '  ')")


class ScanLifecycleTests(SchemaTestCase):
    def setUp(self):
        super().setUp()
        self.add_scan(1, 1)
        self.add_scan(2, 2)

    def test_completed_requires_start_time(self):
        self.reject("UPDATE scans SET status='completed', finished_at='2026-10-20 01:01:00' WHERE scan_id=1")

    def test_running_then_completed(self):
        self.db.execute("UPDATE scans SET status='running', started_at='2026-10-20 01:00:00' WHERE scan_id=1")
        self.reject("UPDATE scans SET status='completed', finished_at='2026-10-19 01:00:00' WHERE scan_id=1")
        self.db.execute("UPDATE scans SET status='completed', finished_at='2026-10-20 01:01:00' WHERE scan_id=1")

    def test_failed_requires_error_message(self):
        self.reject("UPDATE scans SET status='failed', finished_at=CURRENT_TIMESTAMP WHERE scan_id=2")
        self.db.execute(
            "UPDATE scans SET status='failed', finished_at=CURRENT_TIMESTAMP, "
            "error_message='Startup failed' WHERE scan_id=2")

    def test_error_message_only_on_failed_scans(self):
        self.reject("UPDATE scans SET error_message='oops' WHERE scan_id=1")


class AddedColumnTests(SchemaTestCase):
    """Columns added on integration: profile, owner-less scans, product/version, title."""

    def test_scan_without_owner_until_login_exists(self):
        self.db.execute("INSERT INTO scans (target) VALUES ('192.0.2.1')")

    def test_profile_defaults_to_basic_and_is_restricted(self):
        self.db.execute("INSERT INTO scans (scan_id, target) VALUES (5, '192.0.2.1')")
        profile = self.db.execute("SELECT profile FROM scans WHERE scan_id=5").fetchone()[0]
        self.assertEqual(profile, "basic")
        self.db.execute("INSERT INTO scans (target, profile) VALUES ('192.0.2.1', 'discovery')")
        self.reject("INSERT INTO scans (target, profile) VALUES ('192.0.2.1', '-A')")

    def test_service_product_and_version_are_optional(self):
        self.add_scan()
        self.db.execute(
            "INSERT INTO services (host_id, port, protocol, service_name, product, version) "
            "VALUES (1, 22, 'tcp', 'ssh', 'OpenSSH', '9.6')")
        self.db.execute("INSERT INTO services (host_id, port, protocol) VALUES (1, 80, 'tcp')")

    def test_finding_title_is_optional(self):
        self.add_scan()
        self.db.execute("INSERT INTO services (service_id, host_id, port, protocol) VALUES (1, 1, 23, 'tcp')")
        self.db.execute(
            "INSERT INTO findings (service_id, severity, title, description) "
            "VALUES (1, 'high', 'Telnet open', 'Telnet sends passwords in plain text.')")
        self.db.execute("INSERT INTO findings (service_id, severity, description) VALUES (1, 'low', 'Example')")


class QueryFileTests(SchemaTestCase):
    """Matt's dashboard queries must stay valid against the schema."""

    def run_query(self, name, params):
        sql = (SCHEMA.parent / name).read_text()
        return self.db.execute(sql, params).fetchall()

    def setUp(self):
        super().setUp()
        self.add_scan()
        self.db.execute("INSERT INTO hosts (host_id, scan_id, ip_address) VALUES (2, 1, '192.0.2.2')")
        self.db.execute("INSERT INTO services (service_id, host_id, port, protocol) VALUES (1, 1, 23, 'tcp')")
        self.db.execute("INSERT INTO services (service_id, host_id, port, protocol) VALUES (2, 1, 80, 'tcp')")
        for severity in ("low", "critical"):
            self.db.execute(
                "INSERT INTO findings (service_id, severity, description) VALUES (1, ?, 'x')", (severity,))

    def test_history_counts_hosts_and_findings_separately(self):
        rows = self.run_query("history_results.sql", {"user_id": 1})
        self.assertEqual(rows, [(1, "192.0.2.1", None, None, "Pending", 2, 2)])

    def test_devices_include_hosts_without_services(self):
        rows = self.run_query("service_results.sql", {"scan_id": 1})
        self.assertEqual([(r[1], r[4]) for r in rows], [("192.0.2.1", 23), ("192.0.2.1", 80), ("192.0.2.2", None)])

    def test_findings_sorted_most_severe_first(self):
        rows = self.run_query("finding_results.sql", {"scan_id": 1})
        self.assertEqual([(r[1], r[2]) for r in rows], [("critical", "Untitled finding"), ("low", "Untitled finding")])


class DeletionTests(SchemaTestCase):
    def test_deleting_a_scan_cascades_to_its_results(self):
        self.add_scan(1, 1)
        self.add_scan(2, 2)
        self.db.execute("INSERT INTO services (service_id, host_id, port, protocol) VALUES (1, 1, 53, 'tcp')")
        self.db.execute("INSERT INTO findings (service_id, severity, description) VALUES (1, 'high', 'Example')")

        self.db.execute("DELETE FROM scans WHERE scan_id=1")

        self.assertEqual(self.count("hosts"), 1)
        self.assertEqual(self.count("services"), 0)
        self.assertEqual(self.count("findings"), 0)
        self.assertEqual(self.db.execute("PRAGMA foreign_key_check").fetchall(), [])
        self.assertEqual(self.db.execute("PRAGMA integrity_check").fetchone()[0], "ok")


if __name__ == "__main__":
    unittest.main()
