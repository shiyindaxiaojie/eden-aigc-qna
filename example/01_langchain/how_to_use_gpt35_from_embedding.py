import os

import chardet
from dotenv import load_dotenv
from langchain.document_loaders import TextLoader
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
embedding = OpenAIEmbeddings(
    deployment=EMBED_API_MODEL,
    openai_api_type=API_TYPE,
    openai_api_base=API_BASE,
    openai_api_key=API_KEY,
    chunk_size=1)

# 源文件
file = 'data/sample.txt'

# 自动检测编码
with open(file, 'rb') as f:
    result = chardet.detect(f.read())
    encoding = result['encoding']

# 加载文件
loader = TextLoader(file, encoding=encoding)

# 创建索引
index = VectorstoreIndexCreator(embedding=embedding).from_loaders([loader])
print('索引：', index)

# 提问
question = '这篇文章主要介绍了什么?'
print('提问：', question)
llm = AzureOpenAI(deployment_name=GPT_API_MODEL, openai_api_version=GPT_API_VERSION, temperature=0)
result = index.query(question, llm=llm)
print('回答：', result)

# 如果提示安装 chromadb，请下载 Visual Studio Install 安装 C++，然后执行 pip install numpy cmake scipy setuptools-rust chromadb
# 代码有坑，识别不了变量，详见源码：langchain.embeddings.openai.OpenAIEmbeddings._get_len_safe_embeddings
# 建议设置 chunk_size=1 限制默认并发：https://go.microsoft.com/fwlink/?linkid=2213926
