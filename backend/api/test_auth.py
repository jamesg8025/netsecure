"""Tests for login, logout, and the current user (WBS 9.0, UC-01)."""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from .auth_views import MAX_PASSWORD_LENGTH, MAX_USERNAME_LENGTH

PASSWORD = 'correct horse battery staple'


class AuthTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='alice', password=PASSWORD)

    def setUp(self):
        # Failed-login counts live in the cache; don't let them leak between tests.
        cache.clear()
        self.addCleanup(cache.clear)

    def login(self, client=None, ip='127.0.0.1', **body):
        client = client or self.client
        return client.post(
            reverse('api:auth-login'), data=body, content_type='application/json', REMOTE_ADDR=ip
        )

    def assertApiError(self, response, status, code, field=None):
        self.assertEqual(response.status_code, status)
        error = response.json()['error']
        self.assertEqual(error['code'], code)
        if field is not None:
            self.assertEqual(error['details'], {'field': field})
        return error


class LoginTests(AuthTestCase):
    def test_valid_credentials_log_the_user_in(self):
        response = self.login(username='alice', password=PASSWORD)

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body['user'], {'id': self.user.pk, 'username': 'alice'})
        self.assertTrue(body['csrfToken'])
        self.assertEqual(self.client.session['_auth_user_id'], str(self.user.pk))

    def test_response_never_contains_the_password(self):
        response = self.login(username='alice', password=PASSWORD)

        self.assertNotIn(PASSWORD, response.content.decode())

    def test_session_cookie_is_http_only_and_expires(self):
        response = self.login(username='alice', password=PASSWORD)

        cookie = response.cookies[settings.SESSION_COOKIE_NAME]
        self.assertTrue(cookie['httponly'])
        self.assertEqual(cookie['samesite'], 'Lax')
        self.assertEqual(cookie['max-age'], settings.SESSION_COOKIE_AGE)

    def test_login_rotates_the_session_key(self):
        session = self.client.session
        session['before_login'] = True
        session.save()
        old_key = session.session_key

        self.login(username='alice', password=PASSWORD)

        self.assertNotEqual(self.client.session.session_key, old_key)

    def test_username_surrounding_whitespace_is_ignored(self):
        response = self.login(username='  alice  ', password=PASSWORD)

        self.assertEqual(response.status_code, 200)

    def test_password_is_used_exactly_as_typed(self):
        get_user_model().objects.create_user(username='bob', password='  spaced  ')

        self.assertEqual(self.login(username='bob', password='  spaced  ').status_code, 200)
        self.assertApiError(self.login(username='bob', password='spaced'), 401, 'invalid_credentials')

    def test_wrong_password_and_unknown_user_get_the_same_error(self):
        wrong_password = self.login(username='alice', password='nope')
        unknown_user = self.login(username='mallory', password=PASSWORD)

        self.assertApiError(wrong_password, 401, 'invalid_credentials')
        self.assertEqual(wrong_password.json(), unknown_user.json())
        self.assertEqual(unknown_user.status_code, 401)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_inactive_user_cannot_log_in(self):
        get_user_model().objects.create_user(username='carol', password=PASSWORD, is_active=False)

        self.assertApiError(self.login(username='carol', password=PASSWORD), 401, 'invalid_credentials')

    def test_missing_fields_name_the_field(self):
        self.assertApiError(self.login(password=PASSWORD), 400, 'validation_error', 'username')
        self.assertApiError(self.login(username='alice'), 400, 'validation_error', 'password')

    def test_blank_fields_are_rejected(self):
        self.assertApiError(
            self.login(username='   ', password=PASSWORD), 400, 'validation_error', 'username')
        self.assertApiError(
            self.login(username='alice', password=''), 400, 'validation_error', 'password')

    def test_non_string_fields_are_rejected(self):
        self.assertApiError(
            self.login(username=['alice'], password=PASSWORD), 400, 'validation_error', 'username')
        self.assertApiError(
            self.login(username='alice', password=123), 400, 'validation_error', 'password')

    def test_overlong_fields_are_rejected(self):
        self.assertApiError(
            self.login(username='a' * (MAX_USERNAME_LENGTH + 1), password=PASSWORD),
            400, 'validation_error', 'username')
        self.assertApiError(
            self.login(username='alice', password='a' * (MAX_PASSWORD_LENGTH + 1)),
            400, 'validation_error', 'password')

    def test_non_json_body_is_rejected(self):
        response = self.client.post(
            reverse('api:auth-login'), data={'username': 'alice', 'password': PASSWORD})

        self.assertApiError(response, 415, 'unsupported_media_type')

    def test_get_is_not_allowed(self):
        self.assertApiError(self.client.get(reverse('api:auth-login')), 405, 'method_not_allowed')


class LoginCsrfTests(AuthTestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)

    def test_login_without_csrf_token_is_rejected(self):
        response = self.login(username='alice', password=PASSWORD)

        self.assertApiError(response, 403, 'forbidden')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_with_csrf_token_succeeds_and_returns_a_working_new_token(self):
        token = self.client.get(reverse('api:csrf')).json()['csrfToken']

        response = self.client.post(
            reverse('api:auth-login'), data={'username': 'alice', 'password': PASSWORD},
            content_type='application/json', headers={'X-CSRFToken': token})
        self.assertEqual(response.status_code, 200)

        # Login rotates the token; the one it returns must work for the next POST.
        new_token = response.json()['csrfToken']
        logout = self.client.post(reverse('api:auth-logout'), headers={'X-CSRFToken': new_token})
        self.assertEqual(logout.status_code, 204)


class LogoutTests(AuthTestCase):
    def test_logout_ends_the_session(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse('api:auth-logout'))

        self.assertEqual(response.status_code, 204)
        self.assertApiError(self.client.get(reverse('api:auth-me')), 401, 'not_authenticated')

    def test_logout_when_not_logged_in_is_fine(self):
        self.assertEqual(self.client.post(reverse('api:auth-logout')).status_code, 204)

    def test_get_is_not_allowed(self):
        self.assertApiError(self.client.get(reverse('api:auth-logout')), 405, 'method_not_allowed')


class MeTests(AuthTestCase):
    def test_returns_the_logged_in_user(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('api:auth-me'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'user': {'id': self.user.pk, 'username': 'alice'}})

    def test_anonymous_request_is_not_authenticated(self):
        error = self.assertApiError(self.client.get(reverse('api:auth-me')), 401, 'not_authenticated')
        self.assertEqual(error['message'], 'You are not logged in.')

    def test_login_then_me_round_trip(self):
        self.login(username='alice', password=PASSWORD)

        self.assertEqual(self.client.get(reverse('api:auth-me')).json()['user']['username'], 'alice')

    def test_post_is_not_allowed(self):
        self.assertApiError(self.client.post(reverse('api:auth-me')), 405, 'method_not_allowed')
