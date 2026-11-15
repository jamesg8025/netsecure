"""
Throttling for repeated failed logins (WBS 9.0, UC-01).

Failures are counted two ways, each over a window of LOGIN_THROTTLE_WINDOW
seconds that starts at the first failure:

- username + client IP, up to LOGIN_THROTTLE_USER_LIMIT failures. This stops
  password guessing against one account without letting someone elsewhere
  lock its owner out.
- client IP alone, up to LOGIN_THROTTLE_IP_LIMIT failures. This stops one
  machine trying a few passwords against many usernames.

Once either limit is reached, logins are refused with 429 until that window
ends, even with the right password. Refused attempts don't extend the window.
A successful login clears the username + IP count. Unknown usernames are
counted like real ones, so a lockout doesn't reveal which accounts exist.

Counts live in Django's default cache. With the default in-memory cache, each
server process keeps its own counts and a restart clears them. The client IP
is REMOTE_ADDR; behind a reverse proxy every client would share the proxy's.
"""
import hashlib
import math
import time

from django.conf import settings
from django.core.cache import cache

from .errors import ApiError

_KEY_PREFIX = 'login-throttle'


def check(request, username):
    """Raise a 429 ApiError if this username or client IP is locked out."""
    retry_after = max(_seconds_locked(key, limit) for key, limit in _counters(request, username))
    if retry_after:
        minutes = math.ceil(retry_after / 60)
        unit = 'minute' if minutes == 1 else 'minutes'
        raise ApiError(
            429,
            'too_many_login_attempts',
            f'Too many failed login attempts. Try again in {minutes} {unit}.',
            headers={'Retry-After': str(retry_after)},
        )


def record_failure(request, username):
    """Count a failed login against the username + IP and the IP."""
    window = settings.LOGIN_THROTTLE_WINDOW
    for key, _limit in _counters(request, username):
        # add() only sets a key that doesn't exist, so the window runs from
        # the first failure.
        cache.add(_reset_key(key), time.time() + window, window)
        cache.add(key, 0, window)
        try:
            cache.incr(key)
        except ValueError:
            # The window ended between add() and incr(); start a new one.
            cache.set(_reset_key(key), time.time() + window, window)
            cache.set(key, 1, window)


def record_success(request, username):
    """Clear the username + IP count. The IP-only count is kept."""
    key, _limit = _counters(request, username)[0]
    cache.delete_many([key, _reset_key(key)])


def _counters(request, username):
    """(cache key, failure limit) pairs: username + IP first, then IP alone."""
    ip = request.META.get('REMOTE_ADDR', '')
    # Hashed so any username is a safe cache key; lowercased so changing its
    # case doesn't start a fresh count.
    user = hashlib.sha256(username.lower().encode()).hexdigest()
    return [
        (f'{_KEY_PREFIX}:user:{user}:{ip}', settings.LOGIN_THROTTLE_USER_LIMIT),
        (f'{_KEY_PREFIX}:ip:{ip}', settings.LOGIN_THROTTLE_IP_LIMIT),
    ]


def _reset_key(key):
    return f'{key}:reset'


def _seconds_locked(key, limit):
    """Seconds until this counter allows logins again; 0 if it already does."""
    if cache.get(key, 0) < limit:
        return 0
    reset_at = cache.get(_reset_key(key))
    if reset_at is None:
        # The reset time was evicted without the count; stay locked a full window.
        return settings.LOGIN_THROTTLE_WINDOW
    return max(1, math.ceil(reset_at - time.time()))
