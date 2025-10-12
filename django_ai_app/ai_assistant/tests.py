from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from django.conf import settings
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Document
from .services import AICommandRouter
from .views import ChatView


class AuthenticatedAPITestCase(APITestCase):
    api_key = "unit-test-api-key"

    def setUp(self) -> None:
        super().setUp()
        settings.AI_ASSISTANT_SETTINGS["API_KEY"] = self.api_key
        self.client.credentials(HTTP_X_API_KEY=self.api_key)


class DocumentAPITests(AuthenticatedAPITestCase):
    def test_create_and_retrieve_documents(self) -> None:
        create_response = self.client.post(
            reverse("document-list"),
            {"title": "Test Doc", "content": "Hello world"},
            format="json",
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        document_id = create_response.data["id"]

        detail_response = self.client.get(reverse("document-detail", args=[document_id]))
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.data["title"], "Test Doc")

        list_response = self.client.get(reverse("document-list"))
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data), 1)

    def test_update_and_delete_document(self) -> None:
        document = Document.objects.create(title="Original", content="Body")

        update_response = self.client.patch(
            reverse("document-detail", args=[document.id]),
            {"title": "Updated"},
            format="json",
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data["title"], "Updated")

        delete_response = self.client.delete(reverse("document-detail", args=[document.id]))
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Document.objects.filter(id=document.id).exists())


class ChatViewHistoryTests(TestCase):
    def setUp(self) -> None:
        self.view = ChatView()

    def test_accepts_valid_history(self) -> None:
        history = [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi"}]
        normalised = self.view._normalise_history(history)
        self.assertEqual(list(normalised or []), history)

    def test_rejects_invalid_history(self) -> None:
        with self.assertRaises(ValueError):
            self.view._normalise_history("invalid")
        with self.assertRaises(ValueError):
            self.view._normalise_history([{"role": "unknown", "content": "Hi"}])

    def test_rejects_overlong_history(self) -> None:
        history = [{"role": "user", "content": str(i)} for i in range(21)]
        with self.assertRaises(ValueError):
            self.view._normalise_history(history)


class AICommandRouterSecurityTests(TestCase):
    def setUp(self) -> None:
        self.tempdir = TemporaryDirectory()
        settings.AI_ASSISTANT_SETTINGS["FILE_ROOT"] = self.tempdir.name
        settings.AI_ASSISTANT_SETTINGS["MAX_FILE_SIZE_BYTES"] = 8
        settings.AI_ASSISTANT_SETTINGS["MAX_MESSAGE_LENGTH"] = 20
        self.router = AICommandRouter(file_root=self.tempdir.name)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_rejects_messages_exceeding_limit(self) -> None:
        result = self.router.handle_message("x" * 50)
        self.assertFalse(result.success)
        self.assertIn("Messages must be", result.message)

    def test_prevents_large_file_reads(self) -> None:
        file_path = Path(self.tempdir.name) / "data.txt"
        file_path.write_text("0123456789", encoding="utf-8")
        with self.assertRaises(ValidationError):
            self.router._read_file({"path": "data.txt"})
