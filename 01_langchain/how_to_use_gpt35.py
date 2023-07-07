import os

from dotenv import load_dotenv
from langchain.llms import AzureOpenAI

load_dotenv()
GPT_API_MODEL = os.getenv("GPT_API_MODEL")
GPT_API_VERSION = os.getenv("GPT_API_VERSION")

llm = AzureOpenAI(deployment_name=GPT_API_MODEL, openai_api_version=GPT_API_VERSION, temperature=0)
text = "Langchain 是什么东西？"
print(llm(text))
