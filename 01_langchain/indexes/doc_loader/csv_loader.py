# pip install faiss-gpu faiss-cpu message
# streamlit run ~/pdf_loader.pdf
import os
import tempfile

import streamlit as st
from dotenv import load_dotenv
from langchain.chains import ConversationalRetrievalChain
from langchain.document_loaders import CSVLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import AzureOpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from streamlit_chat import message


def main():
    load_dotenv()

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

    st.set_page_config(page_title="聊天")
    st.header("聊天 💬")

    file = st.file_uploader("上传 CSV", type="csv")
    if file is not None:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(file.getvalue())
            tmp_file_path = tmp_file.name

        loader = CSVLoader(file_path=tmp_file_path, encoding="utf-8")
        data = loader.load()

        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=8000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_documents(data)

        vectors = FAISS.from_documents(chunks, embedding)
        # print('索引：', vectors)
        #
        # question = st.text_input("请进行提问:")
        # print('提问：', question)
        # if question:
        #     docs = vectors.similarity_search(question)
        #
        #     llm = AzureOpenAI(deployment_name=GPT_API_MODEL, openai_api_version=GPT_API_VERSION, temperature=0)
        #     chain = load_qa_chain(llm, chain_type="stuff")
        #     with get_openai_callback() as cb:
        #         response = chain.run(input_documents=docs, question=question)
        #         print(cb)
        #
        #     st.write(response)

        llm = AzureOpenAI(deployment_name=GPT_API_MODEL,
                          openai_api_version=GPT_API_VERSION,
                          temperature=0,
                          max_tokens=150)
        vectors = FAISS.from_documents(chunks, embedding)
        chain = ConversationalRetrievalChain.from_llm(llm, retriever=vectors.as_retriever())
        def conversational_chat(query):
            result = chain({"question": query,
                            "chat_history": st.session_state['history']})
            st.session_state['history'].append((query, result["answer"]))

            return result["answer"]

        if 'history' not in st.session_state:
            st.session_state['history'] = []

        if 'generated' not in st.session_state:
            st.session_state['generated'] = ["可以问我关于 " + file.name + " 的内容哦 🤗"]

        if 'past' not in st.session_state:
            st.session_state['past'] = ["你好 👋"]

        response_container = st.container()

        container = st.container()

        with container:
            with st.form(key='my_form', clear_on_submit=True):
                user_input = st.text_input("Query:", placeholder="Talk about your csv data here (:", key='input')
                submit_button = st.form_submit_button(label='Send')

            if submit_button and user_input:
                output = conversational_chat(user_input)

                st.session_state['past'].append(user_input)
                st.session_state['generated'].append(output)

        if st.session_state['generated']:
            with response_container:
                for i in range(len(st.session_state['generated'])):
                    message(st.session_state["past"][i], is_user=True, key=str(i) + '_user',
                            avatar_style="big-smile")
                    message(st.session_state["generated"][i], key=str(i), avatar_style="thumbs")


if __name__ == '__main__':
    main()
