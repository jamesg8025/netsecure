import os
import subprocess
import sys
from pathlib import Path
from unittest import mock

from django.core.exceptions import PermissionDenied
from django.core.management import call_command
from django.http import Http404, HttpResponse
from django.test import Client, RequestFactory, SimpleTestCase, override_settings
from django.urls import include, path, reverse

from scanner.scanner import ScanError

from .errors import ApiError
from .targets import MAX_TARGET_LENGTH, validate_scan_target
from .validation import parse_json_body, require_string

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


def _require_target(request):
    require_string(parse_json_body(request), 'target', max_length=MAX_TARGET_LENGTH)
    return HttpResponse(status=204)


def _validate_target(request):
    target = require_string(parse_json_body(request), 'target', max_length=MAX_TARGET_LENGTH)
    validate_scan_target(target)
    return HttpResponse(status=204)


urlpatterns = [
    path('api/', include('api.urls')),
    path('api/test/api-error/', _raise_api_error),
    path('api/test/http404/', _raise_http404),
    path('api/test/permission-denied/', _raise_permission_denied),
    path('api/test/unexpected/', _raise_unexpected),
    path('api/test/html-error/', _html_error),
    path('api/test/require-target/', _require_target),
    path('api/test/validate-target/', _validate_target),
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


class ParseJsonBodyTests(SimpleTestCase):
    def _post(self, body, content_type='application/json'):
        # CONTENT_TYPE is passed explicitly because RequestFactory omits it for empty bodies.
        return RequestFactory().post('/api/scan/', data=body, content_type=content_type, CONTENT_TYPE=content_type)

    def assertRaisesApiError(self, status, code, func, *args):
        with self.assertRaises(ApiError) as ctx:
            func(*args)
        self.assertEqual((ctx.exception.status, ctx.exception.code), (status, code))
        return ctx.exception

    def test_returns_json_object_as_dict(self):
        request = self._post('{"target": "192.168.1.0/24"}')

        self.assertEqual(parse_json_body(request), {'target': '192.168.1.0/24'})

    def test_accepts_content_type_with_charset(self):
        request = self._post('{}', content_type='application/json; charset=utf-8')

        self.assertEqual(parse_json_body(request), {})

    def test_rejects_non_json_content_type(self):
        request = self._post('target=10.0.0.1', content_type='application/x-www-form-urlencoded')

        self.assertRaisesApiError(415, 'unsupported_media_type', parse_json_body, request)

    def test_rejects_malformed_json(self):
        self.assertRaisesApiError(400, 'invalid_json', parse_json_body, self._post('{"target": '))

    def test_rejects_empty_body(self):
        self.assertRaisesApiError(400, 'invalid_json', parse_json_body, self._post(''))

    def test_rejects_non_utf8_body(self):
        self.assertRaisesApiError(400, 'invalid_json', parse_json_body, self._post(b'\xff\xfe'))

    def test_rejects_json_that_is_not_an_object(self):
        for body in ('[]', '"10.0.0.1"', '42', 'null'):
            with self.subTest(body=body):
                self.assertRaisesApiError(400, 'invalid_json', parse_json_body, self._post(body))

    @override_settings(DATA_UPLOAD_MAX_MEMORY_SIZE=10)
    def test_rejects_oversized_body(self):
        request = self._post('{"target": "192.168.1.0/24"}')

        self.assertRaisesApiError(413, 'payload_too_large', parse_json_body, request)


class RequireStringTests(SimpleTestCase):
    def assertFieldError(self, data, message):
        with self.assertRaises(ApiError) as ctx:
            require_string(data, 'target', max_length=10)
        error = ctx.exception
        self.assertEqual((error.status, error.code), (400, 'validation_error'))
        self.assertEqual(error.details, {'field': 'target'})
        self.assertEqual(error.message, message)

    def test_returns_stripped_value(self):
        self.assertEqual(require_string({'target': '  10.0.0.1 '}, 'target', max_length=10), '10.0.0.1')

    def test_value_at_max_length_is_allowed(self):
        self.assertEqual(require_string({'target': 'a' * 10}, 'target', max_length=10), 'a' * 10)

    def test_missing_field(self):
        self.assertFieldError({}, '"target" is required.')

    def test_wrong_type(self):
        for value in (None, 42, ['10.0.0.1'], {'ip': '10.0.0.1'}, True):
            with self.subTest(value=value):
                self.assertFieldError({'target': value}, '"target" must be a string.')

    def test_blank_value(self):
        for value in ('', '   ', '\t\n'):
            with self.subTest(value=value):
                self.assertFieldError({'target': value}, '"target" must not be empty.')

    def test_too_long(self):
        self.assertFieldError({'target': 'a' * 11}, '"target" must be at most 10 characters.')


@override_settings(ROOT_URLCONF=__name__)
class ValidationErrorResponseTests(SimpleTestCase):
    def test_validation_error_reaches_client_as_json(self):
        response = self.client.post('/api/test/require-target/', data={}, content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            'error': {
                'code': 'validation_error',
                'message': '"target" is required.',
                'details': {'field': 'target'},
            },
        })


class ScanTargetValidationTests(SimpleTestCase):
    def test_allowed_targets_are_normalized(self):
        cases = {
            '192.168.1.10': '192.168.1.10',
            '192.168.1.0/24': '192.168.1.0/24',
            '192.168.1.7/24': '192.168.1.0/24',
            '127.0.0.1': '127.0.0.1',
        }
        for target, expected in cases.items():
            with self.subTest(target=target):
                self.assertEqual(validate_scan_target(target), expected)

    def test_rejects_unsafe_targets_as_400(self):
        targets = [
            '8.8.8.8',
            '10.0.0.0/8',
            'scanme.nmap.org',
            '10.0.0.1; rm -rf /',
            '-oN /tmp/out 10.0.0.1',
            '::1',
        ]
        for target in targets:
            with self.subTest(target=target):
                with self.assertRaises(ApiError) as ctx:
                    validate_scan_target(target)
                self.assertEqual(ctx.exception.status, 400)
                self.assertEqual(ctx.exception.code, 'invalid_target')
                self.assertEqual(ctx.exception.details, {'field': 'target'})


@override_settings(ROOT_URLCONF=__name__)
class ScanTargetResponseTests(SimpleTestCase):
    def test_rejection_reaches_client_as_json_400(self):
        response = self.client.post(
            '/api/test/validate-target/', data={'target': '8.8.8.8'}, content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error']['code'], 'invalid_target')

    def test_allowed_target_passes(self):
        response = self.client.post(
            '/api/test/validate-target/', data={'target': '192.168.1.0/24'}, content_type='application/json'
        )

        self.assertEqual(response.status_code, 204)

    def test_request_shape_is_checked_before_target_validation(self):
        response = self.client.post(
            '/api/test/validate-target/', data={'target': 'a' * (MAX_TARGET_LENGTH + 1)}, content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error']['code'], 'validation_error')


class CsrfEndpointTests(SimpleTestCase):
    def test_returns_token_and_sets_cookie(self):
        response = self.client.get(reverse('api:csrf'))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['csrfToken'])
        self.assertIn('csrftoken', response.cookies)

    def test_token_allows_post_with_csrf_enforced(self):
        client = Client(enforce_csrf_checks=True)
        token = client.get(reverse('api:csrf')).json()['csrfToken']

        with mock.patch('api.views.scan_target', return_value=[]):
            response = client.post(
                reverse('api:scans'), data={'target': '127.0.0.1'},
                content_type='application/json', HTTP_X_CSRFTOKEN=token,
            )

        self.assertEqual(response.status_code, 200)


class ScanEndpointTests(SimpleTestCase):
    HOSTS = [{
        'ip': '192.168.1.1',
        'hostname': 'router',
        'services': [{'port': 80, 'protocol': 'tcp', 'service': 'http', 'product': '', 'version': ''}],
    }]

    def _post(self, data):
        return self.client.post(reverse('api:scans'), data=data, content_type='application/json')

    def test_url_is_under_api_prefix(self):
        self.assertEqual(reverse('api:scans'), '/api/scans/')

    @mock.patch('api.views.scan_target')
    def test_returns_scanner_results(self, scan_target):
        scan_target.return_value = self.HOSTS

        response = self._post({'target': ' 192.168.1.1 '})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'target': '192.168.1.1', 'profile': 'basic', 'hosts': self.HOSTS})
        scan_target.assert_called_once_with('192.168.1.1', profile='basic')

    @mock.patch('api.views.scan_target', return_value=[])
    def test_passes_normalized_target_and_profile(self, scan_target):
        response = self._post({'target': '192.168.1.7/24', 'profile': 'discovery'})

        self.assertEqual(response.status_code, 200)
        scan_target.assert_called_once_with('192.168.1.0/24', profile='discovery')

    @mock.patch('api.views.scan_target')
    def test_rejected_target_never_reaches_scanner(self, scan_target):
        for target in ('8.8.8.8', '10.0.0.1; rm -rf /', '-oN /tmp/out 10.0.0.1', 'scanme.nmap.org'):
            with self.subTest(target=target):
                response = self._post({'target': target})

                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json()['error']['code'], 'invalid_target')
        scan_target.assert_not_called()

    @mock.patch('api.views.scan_target')
    def test_missing_target_is_400(self, scan_target):
        response = self._post({})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error']['code'], 'validation_error')
        scan_target.assert_not_called()

    @mock.patch('api.views.scan_target')
    def test_unknown_profile_is_400(self, scan_target):
        for profile in ('aggressive', '-sS', None, 1, ['basic']):
            with self.subTest(profile=profile):
                response = self._post({'target': '192.168.1.1', 'profile': profile})

                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json()['error']['details'], {'field': 'profile'})
        scan_target.assert_not_called()

    @mock.patch('api.views.scan_target', side_effect=ScanError('Nmap was not found. Install Nmap and add it to PATH.'))
    def test_scan_failure_is_502_with_reason(self, scan_target):
        response = self._post({'target': '192.168.1.1'})

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json(), {
            'error': {'code': 'scan_failed', 'message': 'Nmap was not found. Install Nmap and add it to PATH.'},
        })

    def test_get_is_rejected(self):
        response = self.client.get(reverse('api:scans'))

        self.assertEqual(response.status_code, 405)


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
