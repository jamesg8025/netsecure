from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from scanner.scanner import SCAN_PROFILES, ScanError, scan_target

from .errors import ApiError
from .targets import MAX_TARGET_LENGTH, validate_scan_target
from .validation import parse_json_body, require_string


@require_GET
def health(request):
    """Liveness check for the frontend and integration tests."""
    return JsonResponse({'status': 'ok'})


@require_GET
@ensure_csrf_cookie
def csrf(request):
    """Return a CSRF token for the frontend to send on POST requests."""
    return JsonResponse({'csrfToken': get_token(request)})


@require_POST
def scans(request):
    """
    Run a scan and return its results.

    Body: {"target": "<private IPv4 or CIDR>", "profile": "basic" | "discovery"}

    The target is validated before the scanner is called (FR-02). The scan runs
    synchronously for now (up to the scanner's 300-second limit); persistence
    and background jobs come with the database work (WBS 5.0).
    """
    data = parse_json_body(request)
    target = require_string(data, 'target', max_length=MAX_TARGET_LENGTH)
    target = validate_scan_target(target)

    profile = data.get('profile', 'basic')
    if not isinstance(profile, str) or profile not in SCAN_PROFILES:
        raise ApiError(
            400,
            'validation_error',
            f'"profile" must be one of: {", ".join(SCAN_PROFILES)}.',
            {'field': 'profile'},
        )

    try:
        hosts = scan_target(target, profile=profile)
    except ScanError as error:
        raise ApiError(502, 'scan_failed', str(error)) from error

    return JsonResponse({'target': target, 'profile': profile, 'hosts': hosts})
