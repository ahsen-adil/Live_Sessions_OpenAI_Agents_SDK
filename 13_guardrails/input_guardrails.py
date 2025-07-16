from agents import AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig
from dotenv import load_dotenv
from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
)
from pydantic import BaseModel
import os
import asyncio

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set in the environment variables.")


#Reference: https://ai.google.dev/gemini-api/docs/openai
extarnal_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
    
model = OpenAIChatCompletionsModel(
    openai_client=extarnal_client,
    model="gemini-2.0-flash",    
)

config = RunConfig(
    model=model,
    model_provider=extarnal_client,
    tracing_disabled=True
)

class MathHomeworkOutput(BaseModel):
    is_math_homework: bool
    reasoning: str

guardrail_agent = Agent( 
    name="Guardrail check",
    instructions="Check if the user is asking you to do their math homework.",
    output_type=MathHomeworkOutput,
)


@input_guardrail
async def math_guardrail( 
    ctx: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, input, context=ctx.context,run_config=config)

    return GuardrailFunctionOutput(
        output_info=result.final_output, 
        tripwire_triggered=result.final_output.is_math_homework,
    )


agent = Agent(  
    name="Customer support agent",
    instructions="You are a customer support agent. You help customers with their questions.",
    input_guardrails=[math_guardrail],
)

async def main():
    # This should trip the guardrail
    try:
        res = await Runner.run(agent, "what is 2 + 2 = ?",run_config=config)
        print(res.final_output)

    except InputGuardrailTripwireTriggered:
        print("Math homework guardrail tripped")

if __name__ == "__main__":
    asyncio.run(main())    




































    

