"""
The single point where the backend checks a scan target before scanning.

Any code path that passes a user-supplied target toward Nmap must call
validate_scan_target() first (SRS FR-02, AGENTS.md Critical Safety Rule).
The decision itself belongs to the scanner's validator (scanner/validator.py,
WBS 3.0); this module only converts its rejection into an API error.
"""
from scanner.validator import InvalidTargetError, validate_target

from .errors import ApiError

# Hostnames top out at 253 characters, and IP, subnet, and range formats are
# far shorter, so anything longer is rejected before reaching the validator.
MAX_TARGET_LENGTH = 255


def validate_scan_target(target):
    """Return the normalized target if it is safe to scan; otherwise raise ApiError."""
    try:
        return validate_target(target)
    except InvalidTargetError as error:
        raise ApiError(400, 'invalid_target', str(error), {'field': 'target'}) from error
