"""Tests for failed-login throttling (WBS 9.0, UC-01)."""
import time
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import override_settings

from .test_auth import PASSWORD, AuthTestCase

WINDOW = 15 * 60


@override_settings(
    LOGIN_THROTTLE_WINDOW=WINDOW,
    LOGIN_THROTTLE_USER_LIMIT=5,
    LOGIN_THROTTLE_IP_LIMIT=20,
)
class LoginThrottleTests(AuthTestCase):
    def fail_logins(self, times, username='alice', ip='127.0.0.1'):
        for _ in range(times):
            response = self.login(username=username, password='wrong', ip=ip)
            self.assertEqual(response.status_code, 401)

    def assertLockedOut(self, response):
        error = self.assertApiError(response, 429, 'too_many_login_attempts')
        self.assertIn('Too many failed login attempts', error['message'])
        self.assertTrue(0 < int(response['Retry-After']) <= WINDOW)

    def test_failures_below_the_limit_still_allow_login(self):
        self.fail_logins(4)

        response = self.login(username='alice', password=PASSWORD)

        self.assertEqual(response.status_code, 200)

    def test_reaching_the_limit_locks_out_even_the_right_password(self):
        self.fail_logins(5)

        response = self.login(username='alice', password=PASSWORD)

        self.assertLockedOut(response)
        self.assertIn('Try again in 15 minutes.', response.json()['error']['message'])
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_locked_out_attempt_never_checks_the_password(self):
        self.fail_logins(5)

        with mock.patch('api.auth_views.authenticate') as authenticate:
            self.login(username='alice', password=PASSWORD)

        authenticate.assert_not_called()

    def test_username_case_does_not_reset_the_count(self):
        self.fail_logins(5, username='ALICE')

        self.assertLockedOut(self.login(username='alice', password=PASSWORD))

    def test_lockout_does_not_reveal_whether_the_account_exists(self):
        self.fail_logins(5, username='nobody')

        response = self.login(username='nobody', password='wrong')

        self.assertLockedOut(response)

    def test_lockout_does_not_block_another_user_from_the_same_ip(self):
        get_user_model().objects.create_user(username='bob', password=PASSWORD)
        self.fail_logins(5)

        response = self.login(username='bob', password=PASSWORD)

        self.assertEqual(response.status_code, 200)

    def test_lockout_does_not_block_the_same_user_from_another_ip(self):
        self.fail_logins(5, ip='10.0.0.5')

        response = self.login(username='alice', password=PASSWORD, ip='10.0.0.6')

        self.assertEqual(response.status_code, 200)

    @override_settings(LOGIN_THROTTLE_IP_LIMIT=6)
    def test_one_ip_trying_many_usernames_is_locked_out(self):
        for name in ('u1', 'u2', 'u3'):
            self.fail_logins(2, username=name)

        self.assertLockedOut(self.login(username='alice', password=PASSWORD))
        # Another IP is unaffected.
        response = self.login(username='alice', password=PASSWORD, ip='10.0.0.6')
        self.assertEqual(response.status_code, 200)

    def test_successful_login_resets_the_count(self):
        self.fail_logins(4)
        self.assertEqual(self.login(username='alice', password=PASSWORD).status_code, 200)

        self.fail_logins(4)

        self.assertEqual(self.login(username='alice', password=PASSWORD).status_code, 200)

    def test_invalid_requests_are_not_counted(self):
        for _ in range(10):
            response = self.login(username='alice', password='')
            self.assertEqual(response.status_code, 400)

        self.assertEqual(self.login(username='alice', password=PASSWORD).status_code, 200)

    def test_lockout_ends_after_the_window_and_refusals_do_not_extend_it(self):
        start = time.time()
        with mock.patch('time.time', return_value=start):
            self.fail_logins(5)
        with mock.patch('time.time', return_value=start + WINDOW - 60):
            response = self.login(username='alice', password=PASSWORD)
            self.assertLockedOut(response)
            self.assertEqual(response['Retry-After'], '60')
            self.assertIn('Try again in 1 minute.', response.json()['error']['message'])

        with mock.patch('time.time', return_value=start + WINDOW + 1):
            response = self.login(username='alice', password=PASSWORD)

        self.assertEqual(response.status_code, 200)

    def test_locked_out_response_is_json(self):
        self.fail_logins(5)

        response = self.login(username='alice', password=PASSWORD)

        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertIn('Retry-After', response)
