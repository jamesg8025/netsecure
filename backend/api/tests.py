import os
import subprocess
import sys
from pathlib import Path

from django.core.exceptions import PermissionDenied
from django.core.management import call_command
from django.http import Http404, HttpResponse
from django.test import Client, SimpleTestCase, override_settings
from django.urls import include, path, reverse

from .errors import ApiError

BACKEND_DIR = Path(__file__).resolve().parent.parent


# Views that fail on purpose, routed only while the error-handling tests run.
def _raise_api_error(request):
    raise ApiError(409, 'conflict_example', 'Something conflicted.', {'field': 'x'})


def _raise_http404(request):
    raise Http404('secret detail')


def _raise_permission_denied(request):
    raise PermissionDenied


def _raise_unexpected(request):
    raise RuntimeError('boom')


def _html_error(request):
    response = HttpResponse('<h1>Bad</h1>', status=400)
    response['X-Custom'] = 'kept'
    return response


urlpatterns = [
    path('api/', include('api.urls')),
    path('api/test/api-error/', _raise_api_error),
    path('api/test/http404/', _raise_http404),
    path('api/test/permission-denied/', _raise_permission_denied),
    path('api/test/unexpected/', _raise_unexpected),
    path('api/test/html-error/', _html_error),
    path('outside/unexpected/', _raise_unexpected),
]


class HealthEndpointTests(SimpleTestCase):
    def test_get_returns_ok_json(self):
        response = self.client.get(reverse('api:health'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok'})

    def test_url_is_under_api_prefix(self):
        self.assertEqual(reverse('api:health'), '/api/health/')

    def test_non_get_is_rejected(self):
        response = self.client.post(reverse('api:health'))

        self.assertEqual(response.status_code, 405)


@override_settings(ROOT_URLCONF=__name__)
class ApiErrorResponseTests(SimpleTestCase):
    def assertApiError(self, response, status, code):
        self.assertEqual(response.status_code, status)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertEqual(response.json()['error']['code'], code)

    def test_unknown_api_url_returns_json_404(self):
        response = self.client.get('/api/does-not-exist/')

        self.assertApiError(response, 404, 'not_found')
        self.assertEqual(response.json(), {'error': {'code': 'not_found', 'message': 'Not Found.'}})

    @override_settings(DEBUG=True)
    def test_unknown_api_url_returns_json_404_in_debug(self):
        # DEBUG turns on Django's console logging; capture it to keep test output clean.
        with self.assertLogs('django.request', level='WARNING'):
            response = self.client.get('/api/does-not-exist/')

        self.assertApiError(response, 404, 'not_found')

    def test_wrong_method_returns_json_405_with_allow_header(self):
        response = self.client.post(reverse('api:health'))

        self.assertApiError(response, 405, 'method_not_allowed')
        self.assertEqual(response['Allow'], 'GET')

    def test_csrf_failure_returns_json_403(self):
        client = Client(enforce_csrf_checks=True)

        response = client.post(reverse('api:health'))

        self.assertApiError(response, 403, 'forbidden')

    def test_api_error_uses_its_status_code_message_and_details(self):
        response = self.client.get('/api/test/api-error/')

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json(), {
            'error': {
                'code': 'conflict_example',
                'message': 'Something conflicted.',
                'details': {'field': 'x'},
            },
        })

    def test_http404_does_not_leak_its_message(self):
        response = self.client.get('/api/test/http404/')

        self.assertApiError(response, 404, 'not_found')
        self.assertNotIn('secret detail', response.content.decode())

    def test_permission_denied_returns_json_403(self):
        response = self.client.get('/api/test/permission-denied/')

        self.assertApiError(response, 403, 'forbidden')

    def test_unexpected_exception_returns_generic_json_500_and_logs(self):
        with self.assertLogs('api.errors', level='ERROR') as logs:
            response = self.client.get('/api/test/unexpected/')

        self.assertApiError(response, 500, 'internal_error')
        self.assertNotIn('boom', response.content.decode())
        self.assertIn('RuntimeError: boom', logs.output[0])

    def test_html_error_response_is_rewritten_keeping_headers(self):
        response = self.client.get('/api/test/html-error/')

        self.assertApiError(response, 400, 'bad_request')
        self.assertEqual(response['X-Custom'], 'kept')

    def test_security_headers_still_applied_to_json_errors(self):
        response = self.client.get('/api/does-not-exist/')

        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')

    def test_paths_outside_api_are_untouched(self):
        response = self.client.get('/outside/missing/')

        self.assertEqual(response.status_code, 404)
        self.assertFalse(response['Content-Type'].startswith('application/json'))

    def test_exceptions_outside_api_are_not_caught(self):
        with self.assertRaises(RuntimeError):
            self.client.get('/outside/unexpected/')


class ProjectConfigTests(SimpleTestCase):
    def test_system_checks_pass(self):
        call_command('check', fail_level='WARNING')

    def _import_settings(self, **env):
        """Import config.settings in a fresh interpreter with only the given DJANGO_* vars."""
        clean_env = {k: v for k, v in os.environ.items() if not k.startswith('DJANGO_')}
        clean_env.update(env)
        return subprocess.run(
            [sys.executable, '-c', 'import config.settings'],
            cwd=BACKEND_DIR,
            env=clean_env,
            capture_output=True,
            text=True,
        )

    def test_missing_secret_key_fails_when_debug_off(self):
        result = self._import_settings()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn('DJANGO_SECRET_KEY must be set', result.stderr)

    def test_missing_secret_key_allowed_when_debug_on(self):
        result = self._import_settings(DJANGO_DEBUG='1')

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_secret_key_set_with_debug_off(self):
        result = self._import_settings(DJANGO_SECRET_KEY='test-key')

        self.assertEqual(result.returncode, 0, result.stderr)
