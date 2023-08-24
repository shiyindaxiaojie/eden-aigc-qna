from dotenv import load_dotenv
load_dotenv()

import tempfile
import traceback

import streamlit as st
from langchain.document_loaders import CSVLoader, PyPDFLoader, TextLoader

from utilities.blob_client import BlobClient
from utilities.llm_helper import LLMHelper


# 上传文件
def upload_file(uploaded_file):
    file_name = uploaded_file.name
    file_url = blob_client.upload_file(uploaded_file.getvalue(), file_name)
    st.session_state["file_name"] = file_name
    st.session_state["file_url"] = file_url
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name
    if file_name.endswith(".pdf"):
        loader = PyPDFLoader(file_path=tmp_file_path)
    elif file_name.endswith(".csv"):
        loader = CSVLoader(file_path=tmp_file_path, encoding="utf-8")
    elif file_name.endswith(".txt"):
        loader = TextLoader(file_path=tmp_file_path, encoding="utf-8")
    else:
        st.error("不支持的文件格式")
        return
    documents = loader.load()
    llm_helper.add_document(documents, file_name, file_url)

try:
    llm_helper = LLMHelper()
    blob_client = BlobClient()

    # 页面设置
    menu_items = {
        "Get help": None,
        "Report a bug": None,
        "About": """
	## 上传文档
	"""
    }
    st.set_page_config(layout="wide", menu_items=menu_items)

    # 上传单个文档
    with st.expander("上传单个文档", expanded=True):
        uploaded_file = st.file_uploader("支持 PDF/CSV/TXT 格式", type=["pdf", "csv", "txt"])
        if uploaded_file is not None:
            if st.session_state.get("file_name", "") != uploaded_file.name:
                upload_file(uploaded_file)
                st.success(f"上传文档 {uploaded_file.name} 成功添加到知识库。")

    # 批量上传文档
    with st.expander("批量上传文档", expanded=True):
        uploaded_files = st.file_uploader("支持 PDF/CSV/TXT 格式", type=["pdf", "csv", "txt"], accept_multiple_files=True)
        if uploaded_files is not None:
            for up_file in uploaded_files:
                if st.session_state.get('filename', '') != up_file.name:
                    upload_file(up_file)
                    st.success(f"上传文档 {up_file.name} 成功添加到知识库。")


except Exception as e:
    st.error(traceback.format_exc())
