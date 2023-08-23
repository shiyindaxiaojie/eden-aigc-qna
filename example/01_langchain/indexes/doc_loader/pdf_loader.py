# pip install pymupdf faiss-gpu faiss-cpu
# streamlit run ~/pdf_loader.pdf
import os

import streamlit as st
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from langchain.chains import ConversationalRetrievalChain
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

    file = st.file_uploader("上传 PDF", type="pdf")
    if file is not None:
        reader = PdfReader(file)

        text = ""
        for page in reader.pages:
            text += page.extract_text()

        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text)
        vectors = FAISS.from_texts(chunks, embedding)

        llm = AzureOpenAI(deployment_name=GPT_API_MODEL,
                          openai_api_version=GPT_API_VERSION,
                          temperature=0,
                          max_tokens=150)
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
                user_input = st.text_input("Query:", placeholder="Talk about your data here (:", key='input')
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
