from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_http_methods

from scanner.scanner import SCAN_PROFILES, ScanError, scan_target

from . import scan_store
from .errors import ApiError
from .models import Scan
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


@require_http_methods(['GET', 'POST'])
def scans(request):
    """GET lists saved scans (history); POST runs a new scan."""
    _require_user(request)
    if request.method == 'GET':
        return _list_scans(request)
    return _start_scan(request)


def _list_scans(request):
    """
    Scan history, newest first (UC-05).

    Each scan has its target, profile, status, start/finish times, error
    message (failed scans), and device and finding counts. Only the signed-in
    user's scans are included.
    """
    return JsonResponse({'scans': scan_store.scan_history(user=request.user)})


def _start_scan(request):
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

    scan = scan_store.create_scan(target, profile, user=request.user)
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


def _require_user(request):
    if not request.user.is_authenticated:
        raise ApiError(401, 'not_authenticated', 'You are not logged in.')


def _require_scan(request, scan_id):
    """Hide missing, unowned and other users' scans behind the same 404."""
    _require_user(request)
    if not Scan.objects.filter(pk=scan_id, user=request.user).exists():
        raise ApiError(404, 'scan_not_found', 'Scan not found.')


@require_GET
def scan_devices(request, scan_id):
    """
    Devices found by one scan (UC-03): one row per open service, plus one row
    for each host with no open services (all service fields null).
    """
    _require_scan(request, scan_id)
    return JsonResponse({'scan_id': scan_id, 'devices': scan_store.scan_devices(scan_id)})


@require_GET
def scan_findings(request, scan_id):
    """Security findings for one scan, most severe first (UC-04, FR-05, FR-06)."""
    _require_scan(request, scan_id)
    return JsonResponse({'scan_id': scan_id, 'findings': scan_store.scan_findings(scan_id)})
