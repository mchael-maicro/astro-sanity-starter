from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ChatView, DocumentViewSet

router = DefaultRouter()
router.register(r"documents", DocumentViewSet, basename="document")

urlpatterns = [
    path("", include(router.urls)),
    path("chat/", ChatView.as_view(), name="ai-chat"),
]
