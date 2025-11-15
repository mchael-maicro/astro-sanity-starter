from __future__ import annotations

from typing import Iterable, Optional

from rest_framework import status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Document
from .serializers import DocumentSerializer
from .services import AICommandRouter


class DocumentViewSet(viewsets.ModelViewSet):
    """Standard CRUD operations for documents."""

    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    throttle_scope = "documents"
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]


class ChatView(APIView):
    """API endpoint that translates chat messages into assistant actions."""

    router_class = AICommandRouter
    throttle_scope = "chat"

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self.router = self.router_class()

    def post(self, request: Request, *args: object, **kwargs: object) -> Response:  # noqa: D401
        """Handle chat messages directed to the AI assistant."""

        message: Optional[str] = request.data.get("message")
        if not message:
            return Response({"detail": "`message` is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            history = self._normalise_history(request.data.get("history"))
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        result = self.router.handle_message(message, history=history)
        status_code = status.HTTP_200_OK if result.success else status.HTTP_400_BAD_REQUEST
        return Response(
            {
                "success": result.success,
                "message": result.message,
                "payload": result.payload,
            },
            status=status_code,
        )

    def _normalise_history(self, history: object) -> Optional[Iterable[dict[str, str]]]:
        if history is None:
            return None
        if not isinstance(history, list):
            raise ValueError("`history` must be a list of role/content dicts.")
        normalised: list[dict[str, str]] = []
        for index, item in enumerate(history):
            if index >= 20:
                raise ValueError("`history` may contain at most 20 messages.")
            if not isinstance(item, dict):
                raise ValueError("Each history item must be an object with `role` and `content` keys.")
            role = item.get("role")
            content = item.get("content")
            if role not in {"user", "assistant", "system"} or not isinstance(content, str):
                raise ValueError("History items require `role` in {user, assistant, system} and string `content`.")
            normalised.append({"role": role, "content": content})
        return normalised
