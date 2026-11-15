"""API authorization independent of frontend routing and CSRF (WBS 9.0)."""
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from . import scan_store
from .models import Scan


class ScanAuthorizationTests(TestCase):
    def setUp(self):
        users = get_user_model().objects
        self.alice = users.create_user('alice', password='test-only-secret')
        self.bob = users.create_user('bob')
        self.owned = scan_store.create_scan('192.168.56.20', user=self.alice)
        scan_store.start_scan(self.owned)
        scan_store.save_results(self.owned, [{'ip': '192.168.56.20', 'services': [
            {'port': 80, 'protocol': 'tcp', 'service': 'http'},
        ]}])
        self.other = scan_store.create_scan('192.168.56.21', user=self.bob)
        self.legacy = scan_store.create_scan('192.168.56.22')

    def test_anonymous_reads_require_login_even_for_existing_ids(self):
        for path in ['/api/scans/', f'/api/scans/{self.owned.pk}/devices/',
                     f'/api/scans/{self.owned.pk}/findings/']:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.json()['error']['code'], 'not_authenticated')

    @mock.patch('api.views.scan_target')
    def test_valid_csrf_alone_cannot_start_scan_or_create_history(self, scanner):
        client = Client(enforce_csrf_checks=True)
        token = client.get('/api/csrf/').json()['csrfToken']
        before = Scan.objects.count()
        response = client.post('/api/scans/', {'target': '192.168.56.20'},
                               content_type='application/json', HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 401)
        scanner.assert_not_called()
        self.assertEqual(Scan.objects.count(), before)

    def test_history_contains_only_current_users_scans(self):
        for user, expected in [(self.alice, self.owned), (self.bob, self.other)]:
            self.client.force_login(user)
            rows = self.client.get('/api/scans/').json()['scans']
            self.assertEqual([row['scan_id'] for row in rows], [expected.pk])

    def test_foreign_unowned_and_missing_details_have_identical_404(self):
        self.client.force_login(self.alice)
        for endpoint in ['devices', 'findings']:
            missing = self.client.get(f'/api/scans/999999/{endpoint}/')
            self.assertEqual(missing.status_code, 404)
            for scan in [self.other, self.legacy]:
                response = self.client.get(f'/api/scans/{scan.pk}/{endpoint}/')
                self.assertEqual(response.status_code, 404)
                self.assertEqual(response.json(), missing.json())

    def test_owner_can_read_real_devices_and_findings(self):
        self.client.force_login(self.alice)
        for endpoint in ['devices', 'findings']:
            response = self.client.get(f'/api/scans/{self.owned.pk}/{endpoint}/')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json()[endpoint]), 1)

    @mock.patch('api.views.scan_target', return_value=[])
    def test_new_scan_uses_session_owner_not_submitted_owner(self, scanner):
        self.client.force_login(self.alice)
        response = self.client.post('/api/scans/',
            {'target': '192.168.56.30', 'user': self.bob.pk, 'user_id': self.bob.pk},
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Scan.objects.get(pk=response.json()['scan_id']).user, self.alice)

    @mock.patch('api.views.scan_target')
    def test_authenticated_post_still_requires_csrf(self, scanner):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.alice)
        response = client.post('/api/scans/', {'target': '192.168.56.20'},
                               content_type='application/json')
        self.assertEqual(response.status_code, 403)
        scanner.assert_not_called()

    def test_logout_revokes_scan_access(self):
        self.client.force_login(self.alice)
        self.assertEqual(self.client.post(reverse('api:auth-logout')).status_code, 204)
        self.assertEqual(self.client.get('/api/scans/').status_code, 401)

    def test_staff_does_not_bypass_ownership_in_scan_api(self):
        self.alice.is_staff = self.alice.is_superuser = True
        self.alice.save()
        self.client.force_login(self.alice)
        self.assertEqual(self.client.get(f'/api/scans/{self.other.pk}/findings/').status_code, 404)
