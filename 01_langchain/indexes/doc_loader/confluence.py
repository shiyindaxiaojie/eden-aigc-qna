# pip install atlassian-python-api
import os

from dotenv import load_dotenv
from langchain.document_loaders import ConfluenceLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain.llms import AzureOpenAI

load_dotenv()

# 嵌入模型
EMBED_API_MODEL = os.getenv("EMBED_API_MODEL")
API_TYPE = os.getenv("API_TYPE")
API_BASE = os.getenv("API_BASE")
API_KEY = os.getenv("API_KEY")
GPT_API_MODEL = os.getenv("GPT_API_MODEL")
GPT_API_VERSION = os.getenv("GPT_API_VERSION")
CONFLUENCE_URL = os.getenv("CONFLUENCE_URL")
CONFLUENCE_TOKEN = os.getenv("CONFLUENCE_TOKEN")
embedding = OpenAIEmbeddings(
    deployment=EMBED_API_MODEL,
    openai_api_type=API_TYPE,
    openai_api_base=API_BASE,
    openai_api_key=API_KEY,
    chunk_size=1)

# 加载文档
loader = ConfluenceLoader(
    url=CONFLUENCE_URL,
    token=CONFLUENCE_TOKEN
)

documents = loader.load(page_ids=["17927151", "11338372", "17927957"],  # http://localhost:8090/pages/viewpage.action?pageId=17927151
                        include_attachments=False,
                        limit=50)

# 创建索引
index = VectorstoreIndexCreator(embedding=embedding).from_documents(documents)
print('索引：', index)

# 提问
llm = AzureOpenAI(deployment_name=GPT_API_MODEL, openai_api_version=GPT_API_VERSION, temperature=0)

question = '入职要做什么'
print('提问：', question)
result = index.query(question, llm=llm)
print('回答：', result)