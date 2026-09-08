import base64
import json
from pathlib import Path
from typing import Generator

import requests

from core import config_loader


class OpenRouterClient:
    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self, cfg: dict):
        self.api_key = cfg["api"]["openrouter_key"]
        self.vision_model = cfg["models"]["vision"]
        self.reasoning_model = cfg["models"]["reasoning"]
        self.summary_model = cfg["models"]["summarization"]

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/ash1407/hermes_vision",
            "X-Title": "Hermes Assistant",
        }

    def chat(self, messages: list, model: str = None, tools: list = None, stream: bool = False) -> dict | Generator:
        payload = {
            "model": model or self.reasoning_model,
            "messages": messages,
            "stream": stream,
        }
        if tools:
            payload["tools"] = tools

        resp = requests.post(
            f"{self.BASE_URL}/chat/completions",
            headers=self._headers(),
            json=payload,
            stream=stream,
            timeout=60,
        )
        resp.raise_for_status()

        if stream:
            return self._stream_chunks(resp)
        return resp.json()

    def _stream_chunks(self, resp) -> Generator:
        for line in resp.iter_lines():
            if line and line.startswith(b"data: "):
                data = line[6:]
                if data == b"[DONE]":
                    break
                try:
                    yield json.loads(data)
                except json.JSONDecodeError:
                    continue

    def vision(self, image_bytes: bytes, prompt: str, stream: bool = False) -> dict | Generator:
        encoded = base64.b64encode(image_bytes).decode("utf-8")
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded}",
                            "detail": "auto",
                        },
                    },
                ],
            }
        ]
        return self.chat(messages, model=self.vision_model, stream=stream)

    def extract_text(self, response: dict) -> str:
        try:
            return response["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError):
            return ""

    def extract_tool_calls(self, response: dict) -> list:
        try:
            return response["choices"][0]["message"].get("tool_calls", [])
        except (KeyError, IndexError):
            return []


class OllamaClient:
    def __init__(self, cfg: dict):
        self.base_url = cfg["api"]["ollama_base_url"]
        self.vision_model = cfg["models"]["local_vision"]
        self.reasoning_model = cfg["models"]["local_reasoning"]

    def chat(self, messages: list, model: str = None, tools: list = None, stream: bool = False) -> dict:
        payload = {
            "model": model or self.reasoning_model,
            "messages": messages,
            "stream": False,
        }
        resp = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()

    def vision(self, image_bytes: bytes, prompt: str) -> dict:
        encoded = base64.b64encode(image_bytes).decode("utf-8")
        payload = {
            "model": self.vision_model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                    "images": [encoded],
                }
            ],
            "stream": False,
        }
        resp = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()

    def extract_text(self, response: dict) -> str:
        try:
            return response["message"]["content"] or ""
        except KeyError:
            return ""

    def extract_tool_calls(self, response: dict) -> list:
        return []


def get_client():
    cfg = config_loader.load()
    mode = cfg.get("mode", "local")
    if mode == "api":
        return OpenRouterClient(cfg)
    return OllamaClient(cfg)
