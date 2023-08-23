import os

from dotenv import load_dotenv
from langchain.agents import AgentType
from langchain.agents import initialize_agent
from langchain.agents import load_tools
from langchain.llms import AzureOpenAI

load_dotenv()
GPT_API_MODEL = os.getenv("GPT_API_MODEL")
GPT_API_VERSION = os.getenv("GPT_API_VERSION")

# First, let's load the language model we're going to use to control the agent.
llm = AzureOpenAI(deployment_name=GPT_API_MODEL, openai_api_version=GPT_API_VERSION, temperature=0)

# Next, let's load some tools to use. Note that the `llm-math` tool uses an LLM, so we need to pass that in.
tools = load_tools(["serpapi", "llm-math"], llm=llm)

# Finally, let's initialize an agent with the tools, the language model, and the type of agent we want to use.
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

# Now let's test it out!
agent.run("iphone的价格是多少")
