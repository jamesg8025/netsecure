"""
The single point where the backend checks a scan target before scanning.

Any code path that passes a user-supplied target toward Nmap must call
validate_scan_target() first (SRS FR-02, AGENTS.md Critical Safety Rule).

The scanner's validator (scanner/validator.py, WBS 3.0) does not exist yet, so
this placeholder rejects every target rather than letting any through
unchecked. During integration, replace the body with a call to the scanner's
validate_target() and convert its rejection into:

    ApiError(400, 'invalid_target', <reason from the validator>, {'field': 'target'})
"""
from .errors import ApiError

# Hostnames top out at 253 characters, and IP, subnet, and range formats are
# far shorter, so anything longer is rejected before reaching the validator.
MAX_TARGET_LENGTH = 255


def validate_scan_target(target):
    """Return the target if it is safe to scan; otherwise raise ApiError."""
    raise ApiError(
        503,
        'target_validation_unavailable',
        'Scan target validation is not available yet, so scans cannot be started.',
    )
