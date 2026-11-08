"""
Login, logout, and the current user (WBS 9.0, UC-01).

Uses Django's session authentication: a successful login stores the user in
the session, and the session cookie identifies them on later requests.
Accounts are created by an administrator (`manage.py createsuperuser` or the
Django admin); there is no sign-up endpoint.

Every endpoint here is CSRF-protected like the rest of the API, so the
frontend must send the X-CSRFToken header on POST. Login rotates the CSRF
token, so the login response includes the new one.
"""
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.http import HttpResponse, JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.http import require_GET, require_POST

from .errors import ApiError
from .validation import parse_json_body, require_string

# Django's default username field is at most 150 characters.
MAX_USERNAME_LENGTH = 150
# Generous for any real password; stops very long inputs reaching the hasher.
MAX_PASSWORD_LENGTH = 1024


def user_payload(user):
    """The user fields the frontend sees."""
    return {'id': user.pk, 'username': user.get_username()}


@require_POST
def login(request):
    """
    Log in with a username and password.

    Body: {"username": "...", "password": "..."}

    200 {user, csrfToken}; 400 validation_error if a field is missing or
    blank; 401 invalid_credentials if the username or password is wrong or
    the account is inactive (one message for all, so the response doesn't
    reveal which usernames exist).
    """
    data = parse_json_body(request)
    username = require_string(data, 'username', max_length=MAX_USERNAME_LENGTH)
    password = _require_password(data)

    user = authenticate(request, username=username, password=password)
    if user is None:
        raise ApiError(401, 'invalid_credentials', 'Incorrect username or password.')

    auth_login(request, user)
    return JsonResponse({'user': user_payload(user), 'csrfToken': get_token(request)})


@require_POST
def logout(request):
    """End the session. 204 whether or not anyone was logged in."""
    auth_logout(request)
    return HttpResponse(status=204)


@require_GET
def me(request):
    """200 {user} for the logged-in user; 401 not_authenticated otherwise."""
    if not request.user.is_authenticated:
        raise ApiError(401, 'not_authenticated', 'You are not logged in.')
    return JsonResponse({'user': user_payload(request.user)})


def _require_password(data):
    """
    Like require_string, but the password is used exactly as typed:
    surrounding whitespace is not stripped, since it may be part of it.
    """
    if 'password' not in data:
        raise _password_error('"password" is required.')
    password = data['password']
    if not isinstance(password, str):
        raise _password_error('"password" must be a string.')
    if not password:
        raise _password_error('"password" must not be empty.')
    if len(password) > MAX_PASSWORD_LENGTH:
        raise _password_error(f'"password" must be at most {MAX_PASSWORD_LENGTH} characters.')
    return password


def _password_error(message):
    return ApiError(400, 'validation_error', message, {'field': 'password'})
