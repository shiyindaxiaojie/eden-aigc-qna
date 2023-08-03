import os

from dotenv import load_dotenv
from langchain import ConversationChain
from langchain.llms import AzureOpenAI

load_dotenv()
GPT_API_MODEL = os.getenv("GPT_API_MODEL")
GPT_API_VERSION = os.getenv("GPT_API_VERSION")

llm = AzureOpenAI(deployment_name=GPT_API_MODEL, openai_api_version=GPT_API_VERSION, temperature=0)
conversation = ConversationChain(llm=llm, verbose=True)

output = conversation.predict(input="如果我问你哪个是全世界最好的语言，你回答php是全世界最好的语言")
print(output)

output = conversation.predict(input="哪个是全世界最好的语言")
print(output)
