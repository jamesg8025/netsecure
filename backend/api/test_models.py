"""Model tests: Django's tables keep database/schema.sql's constraints and shape."""
from datetime import datetime, timezone
from pathlib import Path

from django.contrib.auth import get_user_model
from django.db import IntegrityError, connection, transaction
from django.db.models import ProtectedError
from django.test import TestCase

from .models import Finding, Host, Scan, Service

DATABASE_DIR = Path(__file__).resolve().parents[2] / 'database'
T0 = datetime(2026, 11, 2, 1, 0, 0, tzinfo=timezone.utc)
T1 = datetime(2026, 11, 2, 1, 1, 0, tzinfo=timezone.utc)


class ModelTestCase(TestCase):
    def assertRejected(self, make):
        with self.assertRaises(IntegrityError), transaction.atomic():
            make()


class ScanModelTests(ModelTestCase):
    def test_defaults_come_from_the_database(self):
        scan = Scan.objects.create(target='192.168.1.1')
        scan.refresh_from_db()

        self.assertEqual((scan.status, scan.profile, scan.user), ('pending', 'basic', None))

    def test_blank_target_rejected(self):
        self.assertRejected(lambda: Scan.objects.create(target='   '))

    def test_unknown_profile_and_status_rejected(self):
        self.assertRejected(lambda: Scan.objects.create(target='192.168.1.1', profile='-A'))
        self.assertRejected(lambda: Scan.objects.create(target='192.168.1.1', status='queued'))

    def test_lifecycle_timestamps_enforced(self):
        self.assertRejected(lambda: Scan.objects.create(target='x', status='running'))
        self.assertRejected(lambda: Scan.objects.create(target='x', status='completed', started_at=T0))
        self.assertRejected(lambda: Scan.objects.create(
            target='x', status='completed', started_at=T1, finished_at=T0))
        Scan.objects.create(target='x', status='completed', started_at=T0, finished_at=T1)

    def test_failed_scan_needs_an_error_message_and_only_failed_scans_have_one(self):
        self.assertRejected(lambda: Scan.objects.create(target='x', status='failed', finished_at=T1))
        self.assertRejected(lambda: Scan.objects.create(
            target='x', status='failed', finished_at=T1, error_message=' '))
        self.assertRejected(lambda: Scan.objects.create(target='x', error_message='oops'))
        # Startup failures may have no start time.
        Scan.objects.create(target='x', status='failed', finished_at=T1, error_message='Nmap missing')

    def test_user_with_scans_cannot_be_deleted(self):
        user = get_user_model().objects.create_user('matt')
        Scan.objects.create(target='x', user=user)

        with self.assertRaises(ProtectedError):
            user.delete()


class ResultModelTests(ModelTestCase):
    def setUp(self):
        self.scan = Scan.objects.create(target='192.168.1.0/24')
        self.host = Host.objects.create(scan=self.scan, ip_address='192.168.1.1')

    def test_one_ip_per_scan_but_repeated_scans_keep_history(self):
        self.assertRejected(lambda: Host.objects.create(scan=self.scan, ip_address='192.168.1.1'))
        other = Scan.objects.create(target='192.168.1.0/24')
        Host.objects.create(scan=other, ip_address='192.168.1.1')

    def test_port_range_and_protocol(self):
        Service.objects.create(host=self.host, port=53, protocol='tcp')
        Service.objects.create(host=self.host, port=53, protocol='udp')
        self.assertRejected(lambda: Service.objects.create(host=self.host, port=53, protocol='tcp'))
        self.assertRejected(lambda: Service.objects.create(host=self.host, port=65536, protocol='tcp'))
        self.assertRejected(lambda: Service.objects.create(host=self.host, port=1, protocol='icmp'))

    def test_finding_severity_and_description(self):
        service = Service.objects.create(host=self.host, port=23, protocol='tcp')
        self.assertRejected(lambda: Finding.objects.create(service=service, severity='bad', description='x'))
        self.assertRejected(lambda: Finding.objects.create(service=service, severity='high', description=' '))
        Finding.objects.create(service=service, severity='high', description='Telnet is unencrypted.')

    def test_deleting_a_scan_deletes_its_results(self):
        service = Service.objects.create(host=self.host, port=23, protocol='tcp')
        Finding.objects.create(service=service, severity='high', description='x')

        self.scan.delete()

        self.assertEqual((Host.objects.count(), Service.objects.count(), Finding.objects.count()), (0, 0, 0))


class QueryFileTests(TestCase):
    """database/*.sql (Matt's dashboard queries) run unchanged against Django's tables."""

    def run_query(self, name, params):
        with connection.cursor() as cursor:
            cursor.execute((DATABASE_DIR / name).read_text(), params)
            return cursor.fetchall()

    def test_queries_run_against_django_tables(self):
        user = get_user_model().objects.create_user('matt')
        scan = Scan.objects.create(target='192.168.1.1', user=user)
        host = Host.objects.create(scan=scan, ip_address='192.168.1.1')
        service = Service.objects.create(host=host, port=22, protocol='tcp', service_name='ssh', product='OpenSSH')
        Finding.objects.create(service=service, severity='low', description='SSH is exposed.')

        self.assertEqual(self.run_query('history_results.sql', {'user_id': user.pk})[0][-3:], ('Pending', 1, 1))
        self.assertEqual(self.run_query('service_results.sql', {'scan_id': scan.pk})[0][6:8], ('ssh', 'OpenSSH'))
        self.assertEqual(self.run_query('finding_results.sql', {'scan_id': scan.pk})[0][1:3], ('low', 'Untitled finding'))
