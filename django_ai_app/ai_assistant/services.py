from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from .models import Document
from .serializers import DocumentSerializer

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - dependency is optional during code analysis
    OpenAI = None  # type: ignore


SYSTEM_PROMPT = (
    "You are Michael, an operations assistant that can manage a knowledge base of documents within "
    "a Django application. You can also read files from the project to help answer questions.\n\n"
    "Always introduce yourself as Michael and include the phrase 'How can I assist you today?' when you "
    "greet the user directly.\n\n"
    "Follow these rules:\n"
    "1. Only respond with a valid JSON object containing the keys `action`, `arguments`, and `response_template`.\n"
    "2. Choose one of the actions: `list_documents`, `create_document`, `read_document`, `update_document`, `delete_document`, `read_file`, or `respond`.\n"
    "3. `arguments` must be a JSON object with the parameters required for the action.\n"
    "4. Use the `respond` action when you can answer the user directly without calling the database or filesystem.\n"
    "5. Never attempt to read files outside of the configured project directory.\n"
)


@dataclass
class AICommandResult:
    """Standardised structure returned by the AI router."""

    success: bool
    message: str
    payload: Optional[Dict[str, Any]] = None


class AICommandRouter:
    """Routes AI-generated commands to concrete actions in the Django backend."""

    def __init__(self, *, file_root: Optional[str] = None) -> None:
        self.file_root = Path(file_root or settings.AI_ASSISTANT_SETTINGS["FILE_ROOT"]).resolve()
        self.allowed_extensions = settings.AI_ASSISTANT_SETTINGS["ALLOWED_EXTENSIONS"]

    def _client(self) -> OpenAI:
        if OpenAI is None:
            raise RuntimeError(
                "openai package is not installed. Install dependencies defined in requirements.txt."
            )
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY environment variable is not configured.")
        return OpenAI(api_key=settings.OPENAI_API_KEY)

    def build_messages(self, user_message: str, history: Optional[Iterable[Dict[str, str]]] = None) -> List[Dict[str, str]]:
        messages: List[Dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_message})
        return messages

    def call_openai(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        client = self._client()
        response = client.responses.create(
            model=settings.OPENAI_MODEL,
            input=messages,
            response_format={"type": "json_object"},
        )
        raw_text = response.output[0].content[0].text  # type: ignore[index]
        return json.loads(raw_text)

    def handle_message(
        self, user_message: str, *, history: Optional[Iterable[Dict[str, str]]] = None
    ) -> AICommandResult:
        plan = self.call_openai(self.build_messages(user_message, history=history))
        action = plan.get("action")
        arguments = plan.get("arguments", {})

        if action == "respond":
            return AICommandResult(True, plan.get("response_template", ""))

        executor = {
            "list_documents": self._list_documents,
            "create_document": self._create_document,
            "read_document": self._read_document,
            "update_document": self._update_document,
            "delete_document": self._delete_document,
            "read_file": self._read_file,
        }.get(action)

        if not executor:
            return AICommandResult(False, f"Unsupported action requested by AI: {action}")

        try:
            result = executor(arguments)
        except (ValidationError, ValueError, ObjectDoesNotExist) as exc:
            return AICommandResult(False, str(exc))

        response_template = plan.get(
            "response_template",
            "Action `{action}` completed successfully.",
        )
        return AICommandResult(True, response_template.format(action=action, **result), payload=result)

    def _list_documents(self, _: Dict[str, Any]) -> Dict[str, Any]:
        documents = Document.objects.all()
        return {"documents": DocumentSerializer(documents, many=True).data}

    def _create_document(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        serializer = DocumentSerializer(data=arguments)
        serializer.is_valid(raise_exception=True)
        document = serializer.save()
        return {"document": DocumentSerializer(document).data}

    def _read_document(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        document_id = arguments.get("id")
        if document_id is None:
            raise ValidationError("`id` is required to read a document.")
        document = Document.objects.get(pk=document_id)
        return {"document": DocumentSerializer(document).data}

    def _update_document(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        document_id = arguments.get("id")
        if document_id is None:
            raise ValidationError("`id` is required to update a document.")
        document = Document.objects.get(pk=document_id)
        serializer = DocumentSerializer(document, data=arguments, partial=True)
        serializer.is_valid(raise_exception=True)
        document = serializer.save()
        return {"document": DocumentSerializer(document).data}

    def _delete_document(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        document_id = arguments.get("id")
        if document_id is None:
            raise ValidationError("`id` is required to delete a document.")
        document = Document.objects.get(pk=document_id)
        document.delete()
        return {"deleted": document_id}

    def _read_file(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        relative_path = arguments.get("path")
        if not relative_path:
            raise ValidationError("`path` is required to read a file.")

        resolved_path = (self.file_root / relative_path).resolve()
        if not str(resolved_path).startswith(str(self.file_root)):
            raise ValidationError("Attempted to access a file outside of the allowed directory.")

        extension = resolved_path.suffix.lower()
        if extension not in self.allowed_extensions:
            raise ValidationError(
                f"Files with extension '{extension}' are not allowed. Allowed extensions: {sorted(self.allowed_extensions)}."
            )

        if not resolved_path.exists() or not resolved_path.is_file():
            raise ValidationError("Requested file does not exist.")

        content = resolved_path.read_text(encoding="utf-8")
        return {"path": str(resolved_path), "content": content}
