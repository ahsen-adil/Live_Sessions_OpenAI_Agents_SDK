import asyncio
import os
from typing import Any
from pydantic import BaseModel
from agents import (
    Agent,
    AgentHooks,
    RunContextWrapper,
    Runner,
    Tool,
    function_tool,
    RunConfig,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    set_default_openai_client,
    set_tracing_disabled,
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file!")

# Gemini Client Setup
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
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

# Pydantic model for task output
class TaskOutput(BaseModel):
    task_id: str
    description: str
    assigned_to: str
    status: str

# Custom Hook for Task Manager
class TaskManagerHook(AgentHooks):
    def __init__(self, agent_name):
        self.agent_name = agent_name
        self.step_count = 0

    async def on_start(self, context: RunContextWrapper, agent: Agent):
        self.step_count += 1
        print(f"🚀 {self.agent_name} Step {self.step_count}: {agent.name} shuru hua!")

    async def on_end(self, context: RunContextWrapper, agent: Agent, output: Any):
        self.step_count += 1
        print(f"🎯 {self.agent_name} Step {self.step_count}: {agent.name} khatam, Output: {output}")

# Tools
@function_tool
def create_task(description: str, assigned_to: str) -> str:
    """Create a new task with a unique ID."""
    task_id = f"TASK-{hash(description + assigned_to) % 1000}"
    return f"Task {task_id} created for {assigned_to}: {description}"

@function_tool
def check_status(task_id: str) -> str:
    """Check the status of a task (simulated)."""
    return f"Task {task_id} status: In Progress"  # Dummy response

# Agents
task_creator = Agent(
    name="Task Creator",
    instructions="Create a new task based on user input and assign it to someone.",
    tools=[create_task],
    hooks=TaskManagerHook(agent_name="TaskCreator"),
    model=model
)

task_checker = Agent(
    name="Task Checker",
    instructions="Check the status of a task using its ID.",
    tools=[check_status],
    hooks=TaskManagerHook(agent_name="TaskChecker"),
    model=model
)

# Main function
async def main():
    # Create a task
    create_result = await Runner.run(task_creator, input="Create a task: Build a website, assign to Ali",run_config=config)
    task_id = create_result.final_output.split()[1]  # Extract TASK-XXX

    # Check status
    check_result = await Runner.run(task_checker, input=f"Check status of {task_id}",run_config=config)
    print(f"Final Status: {check_result.final_output}")

# Run the bot
if __name__ == "__main__":
    asyncio.run(main())