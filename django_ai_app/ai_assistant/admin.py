from __future__ import annotations

from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "updated_at", "created_at")
    search_fields = ("title", "content")
    ordering = ("-updated_at",)
