import json
import os
import urllib.error
import urllib.request
from types import SimpleNamespace


class OllamaClient:
    """Small adapter for calling a local Ollama server with the same interface as the old OpenAI client."""

    def __init__(self, base_url: str | None = None, model: str | None = None) -> None:
        self.base_url = (base_url or os.getenv("OLLAMA_HOST") or "http://localhost:11434").rstrip("/")
        self.model = (model or os.getenv("OLLAMA_MODEL") or "llama3.2:3b").strip()

    def is_available(self) -> tuple[bool, str]:
        try:
            request = urllib.request.Request(f"{self.base_url}/api/models", method="GET")
            with urllib.request.urlopen(request, timeout=5) as response:
                data = json.loads(response.read().decode("utf-8"))
                if isinstance(data, list) and len(data) > 0:
                    models = ", ".join(str(item.get("name", "unknown")) for item in data[:3])
                    return True, f"Local Ollama available ({len(data)} models, sample: {models})"
                return False, "Connected to Ollama but no models found"
        except Exception as exc:
            return False, str(exc)

    def _request(self, prompt: str, *, system_prompt: str = "", max_tokens: int = 180, temperature: float = 0.5) -> str | None:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
            },
        }

        request = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                data = json.loads(response.read().decode("utf-8"))
                return (data.get("message", {}).get("content") or "").strip()
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
            print(f"Ollama request failed: {exc}")
            return None

    class _Completions:
        def __init__(self, parent: "OllamaClient") -> None:
            self._parent = parent

        def create(self, *, model: str | None = None, messages: list[dict] | None = None, max_tokens: int = 180, temperature: float = 0.5):
            if not messages:
                raise ValueError("Messages are required for Ollama chat completions.")

            system_prompt = ""
            user_prompt = ""
            for message in messages:
                role = message.get("role", "")
                content = message.get("content", "")
                if role == "system":
                    system_prompt = content
                elif role == "user":
                    user_prompt = content

            reply = self._parent._request(
                user_prompt,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            if reply is None:
                raise RuntimeError("Ollama did not return a reply.")

            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(content=reply),
                    )
                ]
            )

    @property
    def chat(self) -> SimpleNamespace:
        return SimpleNamespace(completions=self._Completions(self))
