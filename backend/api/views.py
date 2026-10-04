from django.http import JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def health(request):
    """Liveness check for the frontend and integration tests."""
    return JsonResponse({'status': 'ok'})
