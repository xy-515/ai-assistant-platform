"""URL Routing"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from assistant.views import (
    AuthViewSet, UserViewSet,
    PaperHistoryViewSet, CodeHistoryViewSet,
    UploadedFileViewSet,
)

router = DefaultRouter()
router.register(r"auth", AuthViewSet, basename="auth")
router.register(r"user", UserViewSet, basename="user")
router.register(r"history/paper", PaperHistoryViewSet, basename="paper-history")
router.register(r"history/code", CodeHistoryViewSet, basename="code-history")
router.register(r"files", UploadedFileViewSet, basename="files")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
