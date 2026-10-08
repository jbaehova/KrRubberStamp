"""An opt-in OpenAI-compatible chat-completions adapter.

Constructing this class never makes a request. The benchmark generation and
fake-solver workflows do not call complete() or any model API.
"""

from __future__ import annotations

from typing import Protocol

import httpx


class ChatAdapter(Protocol):
    def complete(self, messages: list[dict], tools: list[dict]) -> dict:
        """Return one assistant message, optionally with function tool calls."""
        ...


class OpenAICompatibleAdapter:
    def __init__(
        self,
        *,
        model: str,
        base_url: str,
        api_key: str | None = None,
        timeout: float = 60,
        client: httpx.Client | None = None,
    ):
        if not model or not base_url.startswith(("https://", "http://")):
            raise ValueError("A model and HTTP(S) base_url are required")
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.client = client

    def complete(self, messages: list[dict], tools: list[dict]) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        body = {"model": self.model, "messages": messages, "tools": tools, "tool_choice": "auto"}
        request = {
            "url": f"{self.base_url}/chat/completions",
            "headers": headers,
            "json": body,
            "timeout": self.timeout,
        }
        if self.client is not None:
            response = self.client.post(**request)
        else:
            with httpx.Client() as client:
                response = client.post(**request)
        response.raise_for_status()
        payload = response.json()
        try:
            message = payload["choices"][0]["message"]
        except (KeyError, IndexError, TypeError) as error:
            raise ValueError("Adapter response has no assistant message") from error
        if not isinstance(message, dict) or message.get("role") != "assistant":
            raise ValueError("Adapter response is not an assistant message")
        return message
