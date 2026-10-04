import os
import subprocess
import sys
from pathlib import Path

from django.core.management import call_command
from django.test import SimpleTestCase
from django.urls import reverse

BACKEND_DIR = Path(__file__).resolve().parent.parent


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
