import os
from dotenv import load_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel,RunHooks , RunContextWrapper
from agents.run import RunConfig
import asyncio
from dataclasses import dataclass
from typing import Any

# Load the environment variables from the .env file
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

# Check if the API key is present; if not, raise an error
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

#Reference: https://ai.google.dev/gemini-api/docs/openai
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)

@dataclass
class CustomHooks(RunHooks):

    async def on_agent_start(self, ctx : RunContextWrapper , agent : Agent):
        print("agent start ho gaya....")

    async def on_agent_end(self, ctx : RunContextWrapper , agent : Agent , output : Any):
        print("agent end ho gaya....")    

myhooks = CustomHooks()

async def main():
    agent = Agent(
        name="Assistant",
        instructions="You are helpful Assistent.",
        model=model
    )

    result = await Runner.run(agent, "Tell me about recursion in programming.", hooks=myhooks , run_config=config)
    print(result.final_output)
    # Function calls itself,
    # Looping in smaller pieces,
    # Endless by design.


if __name__ == "__main__":
    asyncio.run(main())