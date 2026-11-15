"""Rule accuracy and scan -> persistence -> API integration."""
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from .models import Finding, Host, Scan, Service
from .rules import evaluate_service


class ServiceRuleTests(SimpleTestCase):
    def test_expected_rules_and_severities(self):
        cases = [(80, 'http', 'HTTP-001', 'low'),
                 (23, 'telnet', 'TELNET-001', 'high'),
                 (21, 'ftp', 'FTP-001', 'medium'),
                 (9100, 'jetdirect', 'PRINT-001', 'medium'),
                 (2222, 'ssh', 'SSH-001', 'info')]
        for port, name, rule_id, severity in cases:
            with self.subTest(port=port, name=name):
                warnings = evaluate_service(port=port, protocol='tcp', service_name=name)
                self.assertEqual(len(warnings), 1)
                self.assertEqual((warnings[0].rule_id, warnings[0].severity), (rule_id, severity))
                self.assertIn(str(port), warnings[0].description)

    def test_tls_unknown_and_mismatched_services_are_not_flagged(self):
        # Scanner currently drops TLS tunnel metadata. Never infer plaintext
        # from `http` on a TLS port, nor a service from an open port alone.
        cases = [(443, 'http'), (8443, 'http'), (80, 'https'),
                 (80, 'ssl/http'), (990, 'ftp'), (992, 'telnet'),
                 (21, 'ftps'), (22, None), (23, ''), (80, 'unknown'),
                 (9100, 'http'), (80, 'jetdirect'), (53, 'domain')]
        for port, name in cases:
            with self.subTest(port=port, name=name):
                self.assertEqual(evaluate_service(port=port, protocol='tcp', service_name=name), [])

    def test_udp_does_not_trigger_tcp_rules(self):
        self.assertEqual(evaluate_service(port=80, protocol='udp', service_name='http'), [])

    def test_normalized_service_name_and_alternate_http_port(self):
        result = evaluate_service(port=8080, protocol='TCP', service_name=' HTTP ')
        self.assertEqual(result[0].rule_id, 'HTTP-001')

    def test_http_warning_does_not_claim_verified_plaintext(self):
        warning = evaluate_service(port=80, protocol='tcp', service_name='http')[0]
        self.assertIn('does not verify TLS', warning.description)
        self.assertIn('redirect', warning.description)


HOSTS = [{'ip': '192.168.56.20', 'hostname': '', 'services': [
    {'port': 22, 'protocol': 'tcp', 'service': 'ssh', 'product': 'OpenSSH', 'version': '9.6'},
    {'port': 80, 'protocol': 'tcp', 'service': 'http', 'product': 'nginx', 'version': '1.24'},
    {'port': 443, 'protocol': 'tcp', 'service': 'http', 'product': 'nginx', 'version': '1.24'},
]}, {'ip': '192.168.56.22', 'hostname': '', 'services': [
    {'port': 9100, 'protocol': 'tcp', 'service': 'jetdirect', 'product': '', 'version': ''},
]}]


class FindingsIntegrationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='scan-reader')
        self.client.force_login(self.user)

    def post_scan(self, hosts=HOSTS):
        with mock.patch('api.views.scan_target', return_value=hosts):
            return self.client.post(reverse('api:scans'),
                                    {'target': '192.168.56.16/28'}, content_type='application/json')

    def test_new_scan_persists_findings_and_exposes_correct_host_port_and_severity(self):
        response = self.post_scan()
        self.assertEqual(response.status_code, 200)
        scan_id = response.json()['scan_id']
        rows = self.client.get(reverse('api:scan-findings', args=[scan_id])).json()['findings']
        self.assertEqual([(r['host'], r['port'], r['severity']) for r in rows], [
            ('192.168.56.22', 9100, 'medium'), ('192.168.56.20', 80, 'low'),
            ('192.168.56.20', 22, 'info'),
        ])
        self.assertTrue(rows[0]['finding'].startswith('PRINT-001:'))
        history = self.client.get(reverse('api:scans')).json()['scans'][0]
        self.assertEqual((history['status'], history['devices_found'], history['findings_found']),
                         ('Completed', 2, 3))
        self.assertEqual(Service.objects.count(), 4)

    def test_repeat_scan_and_reads_do_not_duplicate_or_mix_findings(self):
        first = self.post_scan().json()['scan_id']
        second = self.post_scan().json()['scan_id']
        for scan_id in [first, second, first]:
            rows = self.client.get(reverse('api:scan-findings', args=[scan_id])).json()['findings']
            self.assertEqual(len(rows), 3)
        self.assertEqual(Finding.objects.count(), 6)
        self.assertEqual(Finding.objects.filter(service__host__scan_id=first).count(), 3)

    def test_rule_error_rolls_back_results_and_marks_scan_failed(self):
        with mock.patch('api.scan_store.evaluate_service', side_effect=RuntimeError('rule error')):
            response = self.post_scan()
        self.assertEqual(response.status_code, 500)
        self.assertEqual(Scan.objects.get().status, 'failed')
        self.assertEqual((Host.objects.count(), Service.objects.count(), Finding.objects.count()), (0, 0, 0))

    def test_discovery_and_no_host_results_do_not_invent_findings(self):
        for hosts in [[], [{'ip': '192.168.56.20', 'hostname': '', 'services': []}]]:
            with self.subTest(hosts=hosts):
                response = self.post_scan(hosts)
                self.assertEqual(response.status_code, 200)
        self.assertEqual(Finding.objects.count(), 0)
