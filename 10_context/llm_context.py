import asyncio
from agents import Agent, RunConfig,AsyncOpenAI,OpenAIChatCompletionsModel, Runner
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get Gemini API Key from .env
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please check your .env file.")

# Create OpenAI-compatible Gemini client
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Create model object
model = OpenAIChatCompletionsModel(
    model="gemini-1.5-flash",
    openai_client=external_client
)

# Create config for running the agent
config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)

# Step 1: Define a basic agent with a custom system prompt
agent = Agent(
    name="GreetingAgent",
    instructions="""
You are talking to a user named Ahsen. Be polite and greet him by name.
""",
)

# Step 2: Run the agent with user input
async def main():
    result = await Runner.run(
        starting_agent=agent,
        input="Say hello to me!",  # 🔸 This input will be seen by LLM
        run_config=config  
    )
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())