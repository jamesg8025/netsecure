"""
JSON error responses for the /api/ endpoints.

Every API error uses one shape so the frontend can handle failures uniformly:

    {"error": {"code": "not_found", "message": "Not found."}}

An optional "details" object carries extra context, such as the request field
that failed validation.
"""
import logging
from http import HTTPStatus

from django.core.exceptions import (
    BadRequest,
    PermissionDenied,
    SuspiciousOperation,
)
from django.http import Http404, JsonResponse

logger = logging.getLogger(__name__)

API_PREFIX = '/api/'

# Error codes for statuses that Django or the API produce directly.
DEFAULT_ERROR_CODES = {
    400: 'bad_request',
    403: 'forbidden',
    404: 'not_found',
    405: 'method_not_allowed',
    413: 'payload_too_large',
    415: 'unsupported_media_type',
    500: 'internal_error',
}

# Headers that describe the original body and must not carry over to the JSON body.
_BODY_HEADERS = {'content-type', 'content-length'}


class ApiError(Exception):
    """Raise from a view to return a JSON error response."""

    def __init__(self, status, code, message, details=None):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message
        self.details = details


def error_response(status, code=None, message=None, details=None):
    """Build a JSON error response in the standard API shape."""
    phrase = HTTPStatus(status).phrase
    error = {
        'code': code or DEFAULT_ERROR_CODES.get(status, phrase.lower().replace(' ', '_')),
        'message': message or f'{phrase}.',
    }
    if details is not None:
        error['details'] = details
    return JsonResponse({'error': error}, status=status)


class ApiErrorMiddleware:
    """
    Return JSON instead of HTML for every error under /api/.

    Converts ApiError and Django's standard exceptions to JSON responses, and
    rewrites non-JSON error responses (404 pages, 405s from require_GET, CSRF
    failures) into the standard shape. Paths outside /api/ are untouched.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if not request.path.startswith(API_PREFIX) or response.status_code < 400:
            return response
        if response.get('Content-Type', '').startswith('application/json'):
            return response
        return self._to_json(response)

    def process_exception(self, request, exception):
        if not request.path.startswith(API_PREFIX):
            return None
        if isinstance(exception, ApiError):
            return error_response(
                exception.status, exception.code, exception.message, exception.details
            )
        if isinstance(exception, Http404):
            return error_response(404)
        if isinstance(exception, PermissionDenied):
            return error_response(403)
        if isinstance(exception, (BadRequest, SuspiciousOperation)):
            return error_response(400)

        logger.exception('Unhandled error on %s %s', request.method, request.path)
        response = error_response(500)
        # Already logged with the traceback; stop Django logging it a second time.
        response._has_been_logged = True
        return response

    def _to_json(self, response):
        json_response = error_response(response.status_code)
        for header, value in response.items():
            if header.lower() not in _BODY_HEADERS:
                json_response[header] = value
        json_response.cookies = response.cookies
        return json_response
