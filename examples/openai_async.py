import asyncio

from openai import AsyncOpenAI

import agentwatch


async def main():
    client = AsyncOpenAI()

    completion = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": "Write a one-sentence bedtime story about a unicorn."
            }
        ]
    )

    print(completion.choices[0].message.content)



if __name__ == "__main__":
    asyncio.run(main())