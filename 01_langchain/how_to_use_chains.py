import os

from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.llms import AzureOpenAI
from langchain.chains import LLMChain

load_dotenv()
GPT_API_MODEL = os.getenv("GPT_API_MODEL")
GPT_API_VERSION = os.getenv("GPT_API_VERSION")

llm = AzureOpenAI(deployment_name=GPT_API_MODEL, openai_api_version=GPT_API_VERSION, temperature=0)
prompt = PromptTemplate(
    input_variables=["product"],
    template="哪些公司生产{product}?",
)

chain = LLMChain(llm=llm, prompt=prompt)
print(chain.run("iphone"))
