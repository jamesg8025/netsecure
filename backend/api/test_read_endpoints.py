"""Tests for the read endpoints (WBS 4.0/8.0)."""
from unittest import mock

from django.test import TestCase
from django.urls import reverse

from . import scan_store
from .models import Finding, Service

HOSTS = [
    {
        'ip': '192.168.1.1',
        'hostname': 'router',
        'services': [
            {'port': 23, 'protocol': 'tcp', 'service': 'telnet', 'product': '', 'version': ''},
            {'port': 80, 'protocol': 'tcp', 'service': 'http', 'product': 'lighttpd', 'version': '1.4'},
        ],
    },
    {'ip': '192.168.1.20', 'hostname': '', 'services': []},
]


def completed_scan(hosts=HOSTS, target='192.168.1.0/24'):
    scan = scan_store.create_scan(target)
    scan_store.start_scan(scan)
    scan_store.save_results(scan, hosts)
    return scan


class ScanHistoryEndpointTests(TestCase):
    def test_empty_history(self):
        response = self.client.get(reverse('api:scans'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'scans': []})

    def test_lists_scans_newest_first_with_counts(self):
        first = completed_scan()
        Finding.objects.create(service=Service.objects.get(port=23), severity='high', description='Telnet.')
        failed = scan_store.create_scan('192.168.2.1')
        scan_store.fail_scan(failed, 'Nmap was not found.')

        scans = self.client.get(reverse('api:scans')).json()['scans']

        self.assertEqual([s['scan_id'] for s in scans], [failed.scan_id, first.scan_id])
        self.assertEqual(
            {k: scans[1][k] for k in ('target', 'profile', 'status', 'devices_found', 'findings_found')},
            {'target': '192.168.1.0/24', 'profile': 'basic', 'status': 'Completed',
             'devices_found': 2, 'findings_found': 1},
        )
        self.assertEqual((scans[0]['status'], scans[0]['error_message'], scans[0]['timestamp']),
                         ('Failed', 'Nmap was not found.', None))

    def test_timestamps_are_iso_8601_utc(self):
        completed_scan()

        scan = self.client.get(reverse('api:scans')).json()['scans'][0]

        self.assertRegex(scan['timestamp'], r'^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$')
        self.assertRegex(scan['finished_at'], r'^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$')

    @mock.patch('api.views.scan_target', return_value=HOSTS)
    def test_posted_scan_appears_in_history(self, scan_target):
        scan_id = self.client.post(
            reverse('api:scans'), data={'target': '192.168.1.1'}, content_type='application/json',
        ).json()['scan_id']

        scans = self.client.get(reverse('api:scans')).json()['scans']

        self.assertEqual([(s['scan_id'], s['status']) for s in scans], [(scan_id, 'Completed')])

