import asyncio
from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
    output_guardrail,
    AsyncOpenAI,OpenAIChatCompletionsModel,RunConfig,set_tracing_disabled
)
from dotenv import load_dotenv
import os
import asyncio

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
    model="gemini-2.0-flash",
    openai_client=external_client
)

# Create config for running the agent
config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)

set_tracing_disabled(disabled=True)  # Disable tracing for cleaner output

# Pydantic model for agent output
class SupportResponse(BaseModel):
    response: str

# Pydantic model for input guardrail output
class InputCheck(BaseModel):
    is_abusive: bool
    reasoning: str

# Pydantic model for output guardrail output
class OutputCheck(BaseModel):
    is_negative: bool
    reasoning: str

# Input guardrail agent to check for abusive words
input_guardrail_agent = Agent(
    name="InputAbuseCheck",
    instructions="Check if the user input contains abusive words like 'stupid' or 'idiot'.",
    output_type=InputCheck,
)

# Output guardrail agent to check for negative words
output_guardrail_agent = Agent(
    name="OutputPositiveCheck",
    instructions="Check if the output contains negative words like 'bad' or 'hate'.",
    output_type=OutputCheck,
)

# Input guardrail function
@input_guardrail
async def abusive_input_guardrail(
    ctx: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    result = await Runner.run(input_guardrail_agent, input, context=ctx.context,run_config=config)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_abusive,
    )

# Output guardrail function
@output_guardrail
async def negative_output_guardrail(
    ctx: RunContextWrapper, agent: Agent, output: SupportResponse
) -> GuardrailFunctionOutput:
    result = await Runner.run(output_guardrail_agent, output.response, context=ctx.context,run_config=config)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_negative,
    )

# Main customer support agent
support_agent = Agent(
    name="CustomerSupportBot",
    instructions="You are a polite customer support agent. Answer customer questions professionally and positively.",
    input_guardrails=[abusive_input_guardrail],
    output_guardrails=[negative_output_guardrail],
    output_type=SupportResponse,
)

# Main function to run the chatbot
async def main():
    try:
        result = await Runner.run(support_agent, "you'r service is stupid", run_config=config)
        print(f"Response: {result.final_output.response}")
    except InputGuardrailTripwireTriggered:
        print("Error: Input contains abusive words!")
    except OutputGuardrailTripwireTriggered:
        print("Error: Output contains negative words!")

# Execute the async function
if __name__ == "__main__":
    asyncio.run(main())