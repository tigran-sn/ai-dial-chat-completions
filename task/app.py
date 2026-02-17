import asyncio

from task.clients.client import DialClient
from task.constants import DEFAULT_SYSTEM_PROMPT
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role


async def start(stream: bool) -> None:
    # 1.1 Create DialClient (swap with CustomDialClient to test step 9)
    client = DialClient("gpt-4o")

    # 2. Create Conversation object
    conversation = Conversation()

    # 3. Get system prompt or use default
    system_prompt = input("Provide System prompt or press 'enter' to continue.\n> ").strip()
    if not system_prompt:
        system_prompt = DEFAULT_SYSTEM_PROMPT
    conversation.add_message(Message(Role.SYSTEM, system_prompt))

    # 4. Infinite loop for user input
    print("\nType your question or 'exit' to quit.")
    while True:
        user_input = input("> ").strip()

        # 5. Exit condition
        if user_input.lower() == "exit":
            print("Exiting the chat. Goodbye!")
            break

        # 6. Add user message to conversation history
        conversation.add_message(Message(Role.USER, user_input))

        # 7. Stream or regular completion
        if stream:
            response = await client.stream_completion(conversation.get_messages())
        else:
            response = client.get_completion(conversation.get_messages())

        # 8. Add AI response to conversation history
        conversation.add_message(response)


asyncio.run(
    start(True)
)
