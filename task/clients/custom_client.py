import json
import aiohttp
import requests

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role


class CustomDialClient(BaseClient):

    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)
        self._endpoint = DIAL_ENDPOINT + f"/openai/deployments/{deployment_name}/chat/completions"

    def get_completion(self, messages: list[Message]) -> Message:
        headers = {
            "api-key": self._api_key,
            "Content-Type": "application/json",
        }
        request_data = {
            "messages": [msg.to_dict() for msg in messages],
        }

        response = requests.post(self._endpoint, headers=headers, json=request_data)

        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}: {response.text}")

        data = response.json()
        content = data["choices"][0]["message"]["content"]
        print(content)
        return Message(Role.AI, content)

    async def stream_completion(self, messages: list[Message]) -> Message:
        headers = {
            "api-key": self._api_key,
            "Content-Type": "application/json",
        }
        request_data = {
            "stream": True,
            "messages": [msg.to_dict() for msg in messages],
        }

        contents = []
        async with aiohttp.ClientSession() as session:
            async with session.post(self._endpoint, json=request_data, headers=headers) as response:
                async for line in response.content:
                    decoded = line.decode("utf-8").strip()
                    if not decoded or not decoded.startswith("data: "):
                        continue

                    payload = decoded[6:]
                    if payload == "[DONE]":
                        break

                    snippet = self._get_content_snippet(payload)
                    if snippet:
                        print(snippet, end="", flush=True)
                        contents.append(snippet)

        print()
        return Message(Role.AI, "".join(contents))

    @staticmethod
    def _get_content_snippet(payload: str) -> str | None:
        chunk = json.loads(payload)
        delta = chunk["choices"][0].get("delta", {})
        return delta.get("content")

