import os
import asyncio
import streamlit as st
from dotenv import load_dotenv

from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig

# Load environment variables
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Streamlit page setup
st.set_page_config(page_title="Gemini Q&A Agent", layout="centered", page_icon="🤖")
st.markdown("""
    <style>
    body {
        background-color: #0e1117;
        color: white;
    }
    .stTextInput>div>div>input {
        background-color: #1e1e1e;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 Gemini Agent")
st.subheader("Ask me anything!")

# Check for missing API key
if not gemini_api_key:
    st.error("❌ GEMINI_API_KEY is missing. Please set it in a `.env` file.")
    st.stop()

# Set up Gemini as OpenAI-compatible client
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    openai_client=external_client,
    model="gemini-2.0-flash",
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)

agent = Agent(
    name="Simple Agent",
    instructions="A simple agent that can answer questions.",
)

# Streamlit input
query = st.text_input("Type your question here...")

if st.button("Submit") and query:
    with st.spinner("Thinking..."):
        try:
            result = asyncio.run(Runner.run(agent, query, run_config=config))
            st.success("✅ Answer:")
            st.markdown(f"**{result.final_output}**")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
