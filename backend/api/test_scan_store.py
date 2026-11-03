"""Tests for api.scan_store: lifecycle, saving scanner results, dashboard queries."""
from pathlib import Path

from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase

from . import scan_store
from .models import Finding, Host, Scan, Service
from .scan_store import ScanStateError

DATABASE_DIR = Path(__file__).resolve().parents[2] / 'database'

# Shape from docs/SCANNER_HANDOFF.md; missing metadata is ''.
SCANNER_HOSTS = [
    {
        'ip': '192.168.1.1',
        'hostname': 'router',
        'services': [
            {'port': 80, 'protocol': 'tcp', 'service': 'http', 'product': 'lighttpd', 'version': '1.4'},
            {'port': 53, 'protocol': 'udp', 'service': 'domain', 'product': '', 'version': ''},
            {'port': 53, 'protocol': 'tcp', 'service': 'domain', 'product': '', 'version': ''},
        ],
    },
    {'ip': '192.168.1.20', 'hostname': '', 'services': []},
]


def running_scan(**kwargs):
    scan = scan_store.create_scan('192.168.1.0/24', **kwargs)
    scan_store.start_scan(scan)
    return scan


class LifecycleTests(TestCase):
    def test_create_scan_is_pending_without_timestamps(self):
        scan = scan_store.create_scan('192.168.1.1', profile='discovery')
        scan.refresh_from_db()

        self.assertEqual((scan.status, scan.profile, scan.started_at, scan.finished_at),
                         ('pending', 'discovery', None, None))

    def test_start_sets_running_and_start_time_to_the_second(self):
        scan = running_scan()
        scan.refresh_from_db()

        self.assertEqual(scan.status, 'running')
        self.assertEqual(scan.started_at.microsecond, 0)

    def test_start_twice_is_rejected(self):
        scan = running_scan()

        with self.assertRaises(ScanStateError):
            scan_store.start_scan(scan)

    def test_fail_records_reason(self):
        scan = running_scan()

        scan_store.fail_scan(scan, 'Nmap timed out after 300 seconds.')
        scan.refresh_from_db()

        self.assertEqual(scan.status, 'failed')
        self.assertEqual(scan.error_message, 'Nmap timed out after 300 seconds.')
        self.assertIsNotNone(scan.finished_at)

    def test_fail_before_start_and_with_blank_message(self):
        scan = scan_store.create_scan('192.168.1.1')

        scan_store.fail_scan(scan, '  ')
        scan.refresh_from_db()

        self.assertEqual((scan.status, scan.started_at, scan.error_message), ('failed', None, 'Scan failed.'))

    def test_finished_scan_cannot_fail(self):
        scan = running_scan()
        scan_store.save_results(scan, [])

        with self.assertRaises(ScanStateError):
            scan_store.fail_scan(scan, 'late')


class SaveResultsTests(TestCase):
    def test_saves_hosts_and_services_and_completes(self):
        scan = running_scan()

        self.assertEqual(scan_store.save_results(scan, SCANNER_HOSTS), (2, 3))

        scan.refresh_from_db()
        self.assertEqual(scan.status, 'completed')
        self.assertGreaterEqual(scan.finished_at, scan.started_at)
        http = Service.objects.get(port=80)
        self.assertEqual((http.service_name, http.product, http.version), ('http', 'lighttpd', '1.4'))

    def test_blank_scanner_metadata_is_stored_as_null(self):
        scan = running_scan()
        scan_store.save_results(scan, SCANNER_HOSTS)

        self.assertIsNone(Host.objects.get(ip_address='192.168.1.20').hostname)
        dns = Service.objects.get(port=53, protocol='udp')
        self.assertEqual((dns.product, dns.version), (None, None))

    def test_zero_hosts_is_a_completed_scan(self):
        # import_scan.py rejected empty reports; the scanner returns [] for a quiet subnet.
        scan = running_scan()

        self.assertEqual(scan_store.save_results(scan, []), (0, 0))
        scan.refresh_from_db()
        self.assertEqual(scan.status, 'completed')

    def test_results_saved_only_once(self):
        scan = running_scan()
        scan_store.save_results(scan, SCANNER_HOSTS)

        with self.assertRaises(ScanStateError):
            scan_store.save_results(scan, SCANNER_HOSTS)
        self.assertEqual(Host.objects.count(), 2)

    def test_pending_scan_cannot_take_results(self):
        scan = scan_store.create_scan('192.168.1.1')

        with self.assertRaises(ScanStateError):
            scan_store.save_results(scan, SCANNER_HOSTS)
        self.assertEqual(Host.objects.count(), 0)

    def test_bad_row_rolls_back_everything(self):
        scan = running_scan()
        bad = [SCANNER_HOSTS[1], {'ip': '192.168.1.30', 'hostname': '', 'services': [
            {'port': 70000, 'protocol': 'tcp', 'service': '', 'product': '', 'version': ''}]}]

        with self.assertRaises(Exception):
            scan_store.save_results(scan, bad)

        scan.refresh_from_db()
        self.assertEqual((scan.status, Host.objects.count()), ('running', 0))


class QueryTests(TestCase):
    """Each query function returns what Matt's matching .sql file returns."""

    def setUp(self):
        self.user = get_user_model().objects.create_user('matt')
        self.scan = running_scan(user=self.user)
        scan_store.save_results(self.scan, SCANNER_HOSTS)
        http = Service.objects.get(port=80)
        dns = Service.objects.get(port=53, protocol='udp')
        Finding.objects.create(service=dns, severity='low', description='DNS answers queries.')
        Finding.objects.create(service=http, severity='high', title='Unencrypted web admin',
                               description='The admin page is served over HTTP.')
        Finding.objects.create(service=http, severity='medium', description='Server version is visible.')
        failed = scan_store.create_scan('192.168.2.1', user=self.user)
        scan_store.fail_scan(failed, 'Nmap was not found.')

    def sql_rows(self, name, params):
        with connection.cursor() as cursor:
            cursor.execute((DATABASE_DIR / name).read_text(), params)
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def assertMatchesSql(self, rows, sql_rows, normalize=lambda key, value: value):
        self.assertTrue(sql_rows)
        trimmed = [{key: normalize(key, row[key]) for key in sql_row} for row, sql_row in zip(rows, sql_rows)]
        self.assertEqual(trimmed, sql_rows)
        self.assertEqual(len(rows), len(sql_rows))

    def test_history_matches_sql(self):
        def as_naive_utc(key, value):
            # Raw SQL rows come back as naive UTC datetimes; the ORM's are aware.
            if key in ('timestamp', 'finished_at') and value is not None:
                return value.replace(tzinfo=None)
            return value

        rows = scan_store.scan_history(self.user)

        self.assertMatchesSql(rows, self.sql_rows('history_results.sql', {'user_id': self.user.pk}), as_naive_utc)
        self.assertEqual([(r['status'], r['devices_found'], r['findings_found']) for r in rows],
                         [('Failed', 0, 0), ('Completed', 2, 3)])
        self.assertEqual(rows[0]['error_message'], 'Nmap was not found.')

    def test_history_without_user_lists_owner_less_scans(self):
        scan_store.create_scan('192.168.3.1')

        self.assertEqual(len(scan_store.scan_history()), 3)
        self.assertEqual(len(scan_store.scan_history(self.user)), 2)

    def test_devices_match_sql(self):
        rows = scan_store.scan_devices(self.scan.pk)

        self.assertMatchesSql(rows, self.sql_rows('service_results.sql', {'scan_id': self.scan.pk}))
        self.assertEqual([(r['ip_address'], r['port'], r['protocol']) for r in rows], [
            ('192.168.1.1', 53, 'tcp'), ('192.168.1.1', 53, 'udp'), ('192.168.1.1', 80, 'tcp'),
            ('192.168.1.20', None, None),
        ])

    def test_findings_match_sql(self):
        rows = scan_store.scan_findings(self.scan.pk)

        self.assertMatchesSql(rows, self.sql_rows('finding_results.sql', {'scan_id': self.scan.pk}))
        self.assertEqual([(r['severity'], r['finding']) for r in rows], [
            ('high', 'Unencrypted web admin'), ('medium', 'Untitled finding'), ('low', 'Untitled finding'),
        ])

    def test_unknown_scan_has_no_rows(self):
        self.assertEqual((scan_store.scan_devices(999), scan_store.scan_findings(999)), ([], []))
