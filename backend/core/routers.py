from django.http import JsonResponse
from django.urls import path


def api_root(_request):
    return JsonResponse({"status": "ok", "message": "django_social_media api"})


urlpatterns = [
    path("", api_root, name="api-root"),
]
