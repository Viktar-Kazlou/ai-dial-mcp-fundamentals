import asyncio
import json
import os
from typing import Any

from agent.mcp_client import MCPClient
from agent.dial_client import DialClient
from agent.models.message import Message, Role
from agent.prompts import SYSTEM_PROMPT


# https://remote.mcpservers.org/fetch/mcp
# Pay attention that `fetch` doesn't have resources and prompts

async def main():
    api_key = os.getenv("DIAL_API_KEY")
    endpoint = os.getenv("DIAL_ENDPOINT", "https://ai-proxy.lab.epam.com")
    if not api_key:
        raise ValueError("DIAL_API_KEY is required")

    async with MCPClient(mcp_server_url="http://localhost:8005/mcp") as mcp_client:
        resources: list[Any] = await mcp_client.get_resources()
        print("Available MCP resources:")
        for resource in resources:
            print(f"- {resource}")

        tools = await mcp_client.get_tools()
        print("Available MCP tools:")
        print(json.dumps(tools, indent=2))

        dial_client = DialClient(
            api_key=api_key,
            endpoint=endpoint,
            tools=tools,
            mcp_client=mcp_client,
        )

        messages: list[Message] = [Message(role=Role.SYSTEM, content=SYSTEM_PROMPT)]

        prompts: list[Any] = await mcp_client.get_prompts()
        for prompt in prompts:
            prompt_content = await mcp_client.get_prompt(prompt.name)
            if prompt_content.strip():
                messages.append(Message(role=Role.USER, content=prompt_content))

        while True:
            user_input = input("\n👤: ").strip()
            if user_input.lower() in {"exit", "quit", "q"}:
                print("Chat ended.")
                break
            if not user_input:
                continue

            messages.append(Message(role=Role.USER, content=user_input))
            ai_message = await dial_client.get_completion(messages)
            messages.append(ai_message)


if __name__ == "__main__":
    asyncio.run(main())
