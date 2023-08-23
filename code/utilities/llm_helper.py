import hashlib
import os
import re
import urllib

import openai
import pandas as pd
from dotenv import load_dotenv
from fake_useragent import UserAgent
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.chat_vector_db.prompts import CONDENSE_QUESTION_PROMPT
from langchain.chains.llm import LLMChain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import WebBaseLoader
from langchain.document_loaders.base import BaseLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import AzureOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from langchain.text_splitter import TokenTextSplitter, TextSplitter
from langchain.vectorstores import Milvus
from langchain.vectorstores.base import VectorStore

from utilities.custom_prompt import PROMPT
from utilities.logger import Logger
from utilities.redis_client import RedisClient

load_dotenv()
logger = Logger().get_logger()


class LLMHelper:
    def __init__(self,
                 llm: AzureOpenAI = None,
                 embeddings: OpenAIEmbeddings = None,
                 temperature: float = None,
                 document_loaders: BaseLoader = None,
                 text_splitter: TextSplitter = None,
                 max_tokens: int = None,
                 custom_prompt: str = "",
                 vector_store: VectorStore = None,
                 k: int = None):

        openai.api_type = os.getenv("OPENAI_API_TYPE", "azure")
        openai.api_base = os.getenv("OPENAI_API_BASE")
        openai.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_version = os.getenv("OPENAI_API_VERSION", "2023-05-15")

        # Azure OpenAI
        self.api_base = openai.api_base
        self.api_version = openai.api_version
        self.deployment_name: str = os.getenv("OPENAI_ENGINE", "gpt-35-turbo")
        self.model: str = os.getenv("OPENAI_EMBEDDINGS_ENGINE", "text-embedding-ada-002")
        # 控制 OpenAI 模型输出的多样性。数值越高，输出结果的多样性越大
        self.temperature: float = float(os.getenv("OPENAI_TEMPERATURE", 0.7)) if temperature is None else temperature
        # 限制 OpenAI 模型生成的最大令牌数量，如果未设置，默认值为 -1，表示不限制最大令牌数量
        self.max_tokens: int = int(os.getenv("OPENAI_MAX_TOKENS", -1)) if max_tokens is None else max_tokens
        # 提示词模板
        self.prompt = PROMPT if custom_prompt == "" else PromptTemplate(template=custom_prompt,
                                                                        input_variables=["summaries", "question"])

        # 文档嵌入
        self.document_loaders: BaseLoader = WebBaseLoader if document_loaders is None else document_loaders
        # 指定在相似性搜索时返回的文档数量
        self.k: int = 3 if k is None else k

        # 文本切割器
        self.chunk_size = int(os.getenv("OPENAI_CHUNK_SIZE", 500))
        self.chunk_overlap = int(os.getenv("OPENAI_CHUNK_OVERLAP", 100))
        self.text_splitter: TextSplitter = TokenTextSplitter(chunk_size=self.chunk_size,
                                                             chunk_overlap=self.chunk_overlap) if text_splitter is None else text_splitter

        self.index_name: str = "embeddings"
        self.embeddings: OpenAIEmbeddings = OpenAIEmbeddings(model=self.model,
                                                             chunk_size=1) if embeddings is None else embeddings

        # 部署类型
        self.deployment_type: str = os.getenv("OPENAI_DEPLOYMENT_TYPE", "Text")
        if self.deployment_type == "Text":  # 文本
            self.llm: AzureOpenAI = AzureOpenAI(deployment_name=self.deployment_name, temperature=self.temperature,
                                                max_tokens=self.max_tokens) if llm is None else llm
        else:  # 聊天
            self.llm: ChatOpenAI = ChatOpenAI(model_name=self.deployment_name, engine=self.deployment_name,
                                              temperature=self.temperature,
                                              max_tokens=self.max_tokens if self.max_tokens != -1 else None) if llm is None else llm

        # 向量存储
        self.vector_store_type = os.getenv("VECTOR_STORE_TYPE")
        if self.vector_store_type == "Milvus":
            self.vector_store_host: str = os.getenv("MILVUS_HOST", "localhost")
            self.vector_store_port: int = int(os.getenv("MILVUS_PORT", 19530))
            self.vector_store_username: str = os.getenv("MILVUS_USERNAME")
            self.vector_store_password: str = os.getenv("MILVUS_PASSWORD", None)
            self.vector_store: Milvus = Milvus(
                connection_args={"host": self.vector_store_host, "port": self.vector_store_port},
                embedding_function=self.embeddings)
        else:
            self.vector_store_host: str = os.getenv("REDIS_HOST", "localhost")
            self.vector_store_port: int = int(os.getenv("REDIS_PORT", 6379))
            self.vector_store_protocol: str = os.getenv("REDIS_PROTOCOL", "redis://")
            self.vector_store_password: str = os.getenv("REDIS_PASSWORD", None)
            if self.vector_store_password:
                self.vector_store_full_address = f"{self.vector_store_protocol}:{self.vector_store_password}@{self.vector_store_host}:{self.vector_store_port}"
            else:
                self.vector_store_full_address = f"{self.vector_store_protocol}{self.vector_store_host}:{self.vector_store_port}"
            self.vector_store: RedisClient = RedisClient(redis_url=self.vector_store_full_address,
                                                         index_name=self.index_name,
                                                         embedding_function=self.embeddings.embed_query) if vector_store is None else vector_store

        self.user_agent: UserAgent() = UserAgent()
        self.user_agent.random

    # 调用 LLM 返回内容
    def get_completion(self, prompt, **kwargs):
        if self.deployment_type == "Text":
            return self.llm(prompt)
        else:
            return self.llm([HumanMessage(content=prompt)]).content

    # 获取自然语言处理问题的回答
    def get_semantic_answer(self, question, chat_history):
        # 创建问题语言链，简化用户的提问。
        question_generator = LLMChain(llm=self.llm, prompt=CONDENSE_QUESTION_PROMPT, verbose=True)
        # 创建文档语言链，从文档中获取问题答案的信息。
        doc_chain = load_qa_with_sources_chain(self.llm, chain_type="stuff", verbose=True, prompt=self.prompt)
        # 创建回答生成链，获取给模型生成回答所需的文档，然后生成回答解释。
        chain = ConversationalRetrievalChain(
            retriever=self.vector_store.as_retriever(),
            question_generator=question_generator,
            combine_docs_chain=doc_chain,
            return_source_documents=True
        )

        # 调用链处理用户问题，返回处理结果。
        result = chain({"question": question, "chat_history": chat_history})

        print("历史记录：", chat_history)
        print("完整结果：", result)

        # 对返回结果的源文档进行处理，得到答案的来源。
        sources = "\n".join(set(map(lambda x: x.metadata["source"], result["source_documents"])))

        # 根据相关文档生成上下文，以便获得给定问题的答案。
        contextDict = {}
        for res in result["source_documents"]:
            source_key = self.filter_sources_links(res.metadata["source"]).replace("\n", "").replace(" ", "")
            if source_key not in contextDict:
                contextDict[source_key] = []
            myPageContent = self.clean_encoding(res.page_content)
            contextDict[source_key].append(myPageContent)

        # 清洗和处理生成的答案
        result['answer'] = \
            result['answer'].split('SOURCES:')[0].split('Sources:')[0].split('SOURCE:')[0].split('Source:')[0]
        result['answer'] = self.clean_encoding(result['answer'])

        return question, result["answer"], contextDict, sources

    # 解析后续问题
    def extract_followup_questions(self, answer):
        followupTag = answer.find("Follow-up Questions")
        followupQuestions = answer.find("<<")

        followupTag = min(followupTag, followupQuestions) if followupTag != -1 and followupQuestions != -1 else max(
            followupTag, followupQuestions)
        answer_without_followup_questions = answer[:followupTag] if followupTag != -1 else answer
        followup_questions = answer[followupTag:].strip() if followupTag != -1 else ""

        pattern = r"\<\<(.*?)\>\>"
        match = re.search(pattern, followup_questions)
        followup_questions_list = []
        while match:
            followup_questions_list.append(followup_questions[match.start() + 2:match.end() - 2])
            followup_questions = followup_questions[match.end():]
            match = re.search(pattern, followup_questions)

        if followup_questions_list != "":
            pattern = r"\d. (.*)"
            match = re.search(pattern, followup_questions)
            while match:
                followup_questions_list.append(followup_questions[match.start() + 3:match.end()])
                followup_questions = followup_questions[match.end():]
                match = re.search(pattern, followup_questions)

        if followup_questions_list != "":
            pattern = r"Follow-up Question: (.*)"
            match = re.search(pattern, followup_questions)
            while match:
                followup_questions_list.append(followup_questions[match.start() + 19:match.end()])
                followup_questions = followup_questions[match.end():]
                match = re.search(pattern, followup_questions)

        followupTag = answer_without_followup_questions.lower().find("follow-up questions")
        if followupTag != -1:
            answer_without_followup_questions = answer_without_followup_questions[:followupTag]
        followupTag = answer_without_followup_questions.lower().find("follow up questions")
        if followupTag != -1:
            answer_without_followup_questions = answer_without_followup_questions[:followupTag]

        return answer_without_followup_questions, followup_questions_list

    # 获取文档连接
    def filter_sources_links(self, sources):
        pattern = r"\[[^\]]*?/([^/\]]*?)\]"
        match = re.search(pattern, sources)
        while match:
            withoutExtensions = match.group(1).split(".")[0]
            sources = sources[:match.start()] + f"[{withoutExtensions}]" + sources[match.end():]
            match = re.search(pattern, sources)

        sources = "  \n " + sources.replace("\n", "  \n ")
        return sources

    # 获取文件链接
    def get_links_filenames(self, answer, sources):
        split_sources = sources.split("  \n ")
        return answer.replace("可能的后续问题：", "").replace("\n", ""), split_sources


    # 清除编码问题
    def clean_encoding(self, text):
        try:
            encoding = "ISO-8859-1"
            encoded_text = text.encode(encoding)
            encoded_text = encoded_text.decode("utf-8")
        except Exception as e:
            encoded_text = text
        return encoded_text

    # 添加文档
    def add_document(self, documents, name, source):
        try:
            # 编码处理
            for (document) in documents:
                try:
                    if document.page_content.encode("iso-8859-1") == document.page_content.encode("latin-1"):
                        document.page_content = document.page_content.encode("iso-8859-1").decode("utf-8",
                                                                                                  errors="ignore")
                except:
                    pass

            # 文档切割处理
            docs = self.text_splitter.split_documents(documents)

            # 移除 half non-ascii 字符
            pattern = re.compile(r'[\x00-\x09\x0b\x0c\x0e-\x1f\x7f\u0080-\u00a0\u2000-\u3000\ufff0-\uffff]')
            for (doc) in docs:
                doc.page_content = re.sub(pattern, '', doc.page_content)
                if doc.page_content == '':
                    docs.remove(doc)

            # 遍历文档并保存到向量数据库
            keys = []
            for i, doc in enumerate(docs):
                hash_key = hashlib.sha1(f"{name}_{i}".encode('utf-8')).hexdigest()
                hash_key = f"doc:{self.index_name}:{hash_key}"
                keys.append(hash_key)
                doc.metadata = {"filename": name, "source": f"{source}", "chunk": i, "key": hash_key}

            if self.vector_store_type == 'Redis':
                self.vector_store.add_documents(documents=docs, redis_url=self.vector_store_full_address,
                                                index_name=self.index_name, keys=keys)
            else:
                self.vector_store.add_documents(documents=docs, keys=keys)

            logger.error(f"Add document {source} success")

        except Exception as e:
            logger.error(f"Add document {source} failed: {e}")
            raise e

    # 获取 Top K 的文档列表
    def get_all_documents(self, k: int = None):
        result = self.vector_store.similarity_search(query="*", k=k if k else self.k)
        dataFrame = pd.DataFrame(list(map(lambda x: {
            'filename': x.metadata['filename'],
            'content': x.page_content,
            'source': urllib.parse.unquote(x.metadata['source']),
            'key': x.metadata['key'],
            'metadata': x.metadata,
        }, result)))
        if dataFrame.empty is False:
            dataFrame = dataFrame.sort_values(by='filename')
        return dataFrame
