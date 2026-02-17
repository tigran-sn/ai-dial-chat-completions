from aidial_client import Dial, AsyncDial

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role


class DialClient(BaseClient):

    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)
        self._client = Dial(api_key=self._api_key, base_url=DIAL_ENDPOINT)
        self._async_client = AsyncDial(api_key=self._api_key, base_url=DIAL_ENDPOINT)

    def get_completion(self, messages: list[Message]) -> Message:
        completion = self._client.chat.completions.create(
            deployment_name=self._deployment_name,
            stream=False,
            messages=[msg.to_dict() for msg in messages],
        )

        if not completion.choices:
            raise Exception("No choices in response found")

        content = completion.choices[0].message.content
        print(content)
        return Message(Role.AI, content)

    async def stream_completion(self, messages: list[Message]) -> Message:
        chunks = await self._async_client.chat.completions.create(
            deployment_name=self._deployment_name,
            stream=True,
            messages=[msg.to_dict() for msg in messages],
        )

        contents = []
        async for chunk in chunks:
            if chunk.choices and chunk.choices[0].delta.content:
                snippet = chunk.choices[0].delta.content
                print(snippet, end="", flush=True)
                contents.append(snippet)

        print()
        return Message(Role.AI, "".join(contents))
