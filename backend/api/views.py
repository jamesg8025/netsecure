from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from scanner.scanner import SCAN_PROFILES, ScanError, scan_target

from . import scan_store
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
    Run a scan, save it, and return its results.

    Body: {"target": "<private IPv4 or CIDR>", "profile": "basic" | "discovery"}

    The target is validated before anything is stored or scanned (FR-02).
    The scan is recorded as running, Nmap runs outside any database
    transaction, then the results are saved and the scan marked completed
    (FR-03). A failed scan is kept with its reason (NFR-04). The scan still
    runs synchronously (up to the scanner's 300-second limit); background
    jobs are later work.
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

    # No owner until login exists (WBS 9.0).
    scan = scan_store.create_scan(target, profile)
    scan_store.start_scan(scan)
    try:
        hosts = scan_target(target, profile=profile)
    except ScanError as error:
        scan_store.fail_scan(scan, str(error))
        raise ApiError(502, 'scan_failed', str(error)) from error
    except Exception:
        scan_store.fail_scan(scan, 'Unexpected error while running the scan.')
        raise

    try:
        scan_store.save_results(scan, hosts)
    except Exception:
        scan_store.fail_scan(scan, 'The scan finished but its results could not be saved.')
        raise

    return JsonResponse({'scan_id': scan.scan_id, 'target': target, 'profile': profile, 'hosts': hosts})
