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
    # These read-endpoint tests seed their own exact finding sets.
    # API-created scan/rule integration is exercised in test_rules.py.
    Finding.objects.filter(service__host__scan=scan).delete()
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


class ScanDevicesEndpointTests(TestCase):
    def test_lists_devices_one_row_per_service(self):
        scan = completed_scan()

        response = self.client.get(reverse('api:scan-devices', args=[scan.scan_id]))

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body['scan_id'], scan.scan_id)
        self.assertEqual(
            [(d['ip_address'], d['hostname'], d['port'], d['service'], d['product']) for d in body['devices']],
            [('192.168.1.1', 'router', 23, 'telnet', None),
             ('192.168.1.1', 'router', 80, 'http', 'lighttpd'),
             ('192.168.1.20', None, None, None, None)],
        )

    def test_scan_with_no_hosts_has_no_devices(self):
        scan = completed_scan(hosts=[])

        response = self.client.get(reverse('api:scan-devices', args=[scan.scan_id]))

        self.assertEqual(response.json(), {'scan_id': scan.scan_id, 'devices': []})

    def test_scans_do_not_mix(self):
        completed_scan()
        other = completed_scan(hosts=[{'ip': '10.0.0.5', 'hostname': '', 'services': []}], target='10.0.0.5')

        devices = self.client.get(reverse('api:scan-devices', args=[other.scan_id])).json()['devices']

        self.assertEqual([d['ip_address'] for d in devices], ['10.0.0.5'])


class ScanFindingsEndpointTests(TestCase):
    def test_lists_findings_most_severe_first(self):
        scan = completed_scan()
        Finding.objects.create(service=Service.objects.get(port=80), severity='low', description='Banner.')
        Finding.objects.create(service=Service.objects.get(port=23), severity='critical', title='Telnet open',
                               description='Telnet sends passwords in plain text.')

        response = self.client.get(reverse('api:scan-findings', args=[scan.scan_id]))

        self.assertEqual(response.status_code, 200)
        findings = response.json()['findings']
        self.assertEqual([(f['severity'], f['finding'], f['host'], f['port']) for f in findings], [
            ('critical', 'Telnet open', '192.168.1.1', 23),
            ('low', 'Untitled finding', '192.168.1.1', 80),
        ])

    def test_scan_without_findings(self):
        scan = completed_scan()

        response = self.client.get(reverse('api:scan-findings', args=[scan.scan_id]))

        self.assertEqual(response.json(), {'scan_id': scan.scan_id, 'findings': []})


class ScanDetailRouteTests(TestCase):
    def test_urls(self):
        self.assertEqual(reverse('api:scan-devices', args=[7]), '/api/scans/7/devices/')
        self.assertEqual(reverse('api:scan-findings', args=[7]), '/api/scans/7/findings/')

    def test_unknown_scan_is_404_json(self):
        for name in ('api:scan-devices', 'api:scan-findings'):
            for scan_id in (999, 10**30):
                with self.subTest(name=name, scan_id=scan_id):
                    response = self.client.get(reverse(name, args=[scan_id]))

                    self.assertEqual(response.status_code, 404)
                    self.assertEqual(response.json(), {'error': {'code': 'scan_not_found', 'message': 'Scan not found.'}})

    def test_non_numeric_id_is_404(self):
        response = self.client.get('/api/scans/abc/devices/')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error']['code'], 'not_found')

    def test_only_get_is_allowed(self):
        scan = completed_scan()
        for name in ('api:scan-devices', 'api:scan-findings'):
            with self.subTest(name=name):
                url = reverse(name, args=[scan.scan_id])
                self.assertEqual(self.client.post(url).status_code, 405)
                self.assertEqual(self.client.delete(url).status_code, 405)
