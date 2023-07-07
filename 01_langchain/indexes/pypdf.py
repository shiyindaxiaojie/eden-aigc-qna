# pip install pymupdf faiss-gpu faiss-cpu
import os

from dotenv import load_dotenv
from langchain import FAISS
from langchain.document_loaders import PyMuPDFLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import AzureOpenAI

load_dotenv()

# 嵌入模型
EMBED_API_MODEL = os.getenv("EMBED_API_MODEL")
API_TYPE = os.getenv("API_TYPE")
API_BASE = os.getenv("API_BASE")
API_KEY = os.getenv("API_KEY")
GPT_API_MODEL = os.getenv("GPT_API_MODEL")
GPT_API_VERSION = os.getenv("GPT_API_VERSION")
embedding = OpenAIEmbeddings(
    deployment=EMBED_API_MODEL,
    openai_api_type=API_TYPE,
    openai_api_base=API_BASE,
    openai_api_key=API_KEY,
    chunk_size=1)

# 源文件
file = '../data/JRT0059-2010.pdf'
loader = PyMuPDFLoader(file)
pages = loader.load_and_split()

# 创建索引
index = FAISS.from_documents(pages, embedding)
documents = index.similarity_search("说说这份文档讲了哪些术语和定义", k=2)
print('索引：', index)

# 提问
question = '总结这篇文章'
print('提问：', question)
llm = AzureOpenAI(deployment_name=GPT_API_MODEL, openai_api_version=GPT_API_VERSION, temperature=0)

# result = index.query(question, llm=llm)
# print('回答：', result)
