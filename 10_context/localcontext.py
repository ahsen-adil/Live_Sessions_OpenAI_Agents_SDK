import os
from dotenv import load_dotenv
from agents import Agent, Runner,RunContextWrapper,function_tool, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig
import asyncio
from dataclasses import dataclass

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
class  UserInfo:  
    name: str
    uid: int

@function_tool
async def fetch_info(ctx: RunContextWrapper[UserInfo]):
    return f"hello {ctx.context.name} your id is {ctx.context.uid}"


async def main():
    user_info = UserInfo(name="ahsen", uid=123)

    agent = Agent[UserInfo](  
        name="Assistant",
        instructions="""You are a helpful assistant that uses local context to provide personalized responses.
        Use the available tools to retrieve user information and provide tailored assistance.""",
        tools=[fetch_info],
    )

    result = await Runner.run(  
        starting_agent=agent,
        input="What is my name ? ",
        context=user_info,
        run_config=config
    )

    print(result.final_output)  
    # The user John is 47 years old.

if __name__ == "__main__":
    asyncio.run(main())


    
    













