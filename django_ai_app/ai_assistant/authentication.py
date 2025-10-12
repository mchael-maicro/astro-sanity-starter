"""Custom authentication backends for the AI assistant APIs."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from django.conf import settings
from rest_framework import authentication, exceptions


@dataclass
class APIKeyUser:
    """Lightweight user object representing a validated API key."""

    username: str = "api-key-client"
    is_active: bool = True

    @property
    def is_authenticated(self) -> bool:  # pragma: no cover - property access trivial
        return True


class APIKeyAuthentication(authentication.BaseAuthentication):
    """Authenticate requests using a static API key provided via headers."""

    header_name = "X-API-Key"

    def authenticate(self, request):  # type: ignore[override]
        expected_key: Optional[str] = settings.AI_ASSISTANT_SETTINGS.get("API_KEY")
        if not expected_key:
            if settings.DEBUG:
                return None
            raise exceptions.AuthenticationFailed(
                "AI assistant API key is not configured."
            )

        provided_key = request.headers.get(self.header_name)
        if not provided_key:
            raise exceptions.AuthenticationFailed("Missing API key header.")

        if not self._secure_compare(provided_key, expected_key):
            raise exceptions.AuthenticationFailed("Invalid API key provided.")

        return (APIKeyUser(), None)

    @staticmethod
    def _secure_compare(provided: str, expected: str) -> bool:
        if len(provided) != len(expected):
            return False
        result = 0
        for x, y in zip(provided.encode(), expected.encode()):
            result |= x ^ y
        return result == 0
