"""URL Configuration"""
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
from assistant.paper_views import (
    PaperOutlineView, PaperPolishView, PaperFeedbackView,
    PaperStreamOutlineView, PaperStreamPolishView, PaperStreamFeedbackView,
)
from assistant.code_views import (
    CodeDebugView, CodeGenerateView, CodeReviewView,
    CodeStreamDebugView, CodeStreamGenerateView, CodeStreamReviewView,
)

router = DefaultRouter()
router.register(r"auth", AuthViewSet, basename="auth")
router.register(r"user", UserViewSet, basename="user")
router.register(r"history/paper", PaperHistoryViewSet, basename="paper")
router.register(r"history/code", CodeHistoryViewSet, basename="code")
router.register(r"files", UploadedFileViewSet, basename="files")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    # Async paper endpoints
    path("api/paper/outline",  PaperOutlineView.as_view(),  name="paper-outline"),
    path("api/paper/polish",   PaperPolishView.as_view(),   name="paper-polish"),
    path("api/paper/feedback", PaperFeedbackView.as_view(), name="paper-feedback"),
    # Async code endpoints
    path("api/code/debug",    CodeDebugView.as_view(),    name="code-debug"),
    path("api/code/generate", CodeGenerateView.as_view(), name="code-generate"),
    path("api/code/review",   CodeReviewView.as_view(),   name="code-review"),
    # SSE Streaming endpoints
    path("api/paper/stream/outline",  PaperStreamOutlineView.as_view(),  name="paper-stream-outline"),
    path("api/paper/stream/polish",   PaperStreamPolishView.as_view(),   name="paper-stream-polish"),
    path("api/paper/stream/feedback", PaperStreamFeedbackView.as_view(), name="paper-stream-feedback"),
    path("api/code/stream/debug",    CodeStreamDebugView.as_view(),    name="code-stream-debug"),
    path("api/code/stream/generate", CodeStreamGenerateView.as_view(), name="code-stream-generate"),
    path("api/code/stream/review",   CodeStreamReviewView.as_view(),   name="code-stream-review"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
