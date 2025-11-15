from __future__ import annotations

from django.db import models


class Document(models.Model):
    """Simple knowledge base entry managed by the AI assistant."""

    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self) -> str:  # pragma: no cover - representational helper
        return self.title
