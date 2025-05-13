
# Based on https://github.com/langchain-ai/langchain-mcp-adapters
# Copyright (c) Langchain/Langgraph

import logging
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

logging.basicConfig(level=logging.DEBUG)

load_dotenv()
model = ChatOpenAI(model="gpt-4o")


async def main():
    import agentwatch
    
    async with MultiServerMCPClient(
        {
            "weather": {
                "url": "http://localhost:8001/sse",
                "transport": "sse",
            }
        }
    ) as client:
        agent = create_react_agent(model, client.get_tools())
        weather_response = await agent.ainvoke({"messages": "what is the weather in nyc?"})
        print(weather_response)
        await asyncio.sleep(999999)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())