from __future__ import annotations

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Document
from .views import ChatView


class DocumentAPITests(APITestCase):
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
