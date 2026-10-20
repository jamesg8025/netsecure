"""
Request-shape validation for API views.

These helpers check that a request body is well-formed JSON with the expected
fields and types, raising ApiError (rendered as a JSON 4xx) when it is not.
They do not decide whether a scan target is allowed; that is the scanner's
validator (FR-02), reached through api.targets.
"""
import json

from django.core.exceptions import RequestDataTooBig

from .errors import ApiError


def parse_json_body(request):
    """Return the request body as a dict, or raise ApiError if it is not a JSON object."""
    if request.content_type != 'application/json':
        raise ApiError(415, 'unsupported_media_type', 'Request body must be JSON (Content-Type: application/json).')
    try:
        body = request.body
    except RequestDataTooBig:
        raise ApiError(413, 'payload_too_large', 'Request body is too large.')
    try:
        data = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ApiError(400, 'invalid_json', 'Request body is not valid JSON.')
    if not isinstance(data, dict):
        raise ApiError(400, 'invalid_json', 'Request body must be a JSON object.')
    return data


def require_string(data, field, max_length):
    """Return data[field] with surrounding whitespace removed, or raise ApiError if it is missing or invalid."""
    if field not in data:
        raise _field_error(field, f'"{field}" is required.')
    value = data[field]
    if not isinstance(value, str):
        raise _field_error(field, f'"{field}" must be a string.')
    value = value.strip()
    if not value:
        raise _field_error(field, f'"{field}" must not be empty.')
    if len(value) > max_length:
        raise _field_error(field, f'"{field}" must be at most {max_length} characters.')
    return value


def _field_error(field, message):
    return ApiError(400, 'validation_error', message, {'field': field})
