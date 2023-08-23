import traceback
from urllib import parse

import streamlit as st

from utilities.blob_client import BlobClient
from utilities.llm_helper import LLMHelper


# 删除文档关联的向量数据
def delete_embeddings_of_file(file_to_delete):
    if 'data_files_embeddings' not in st.session_state:
        st.session_state['data_files_embeddings'] = llm_helper.get_all_documents(k=1000)

    if st.session_state['data_files_embeddings'].shape[0] == 0:
        return

    embeddings_to_delete = st.session_state['data_files_embeddings'][st.session_state['data_files_embeddings']['filename'] == file_to_delete]['key'].tolist()
    embeddings_to_delete = list(map(lambda x: f"{x}", embeddings_to_delete))
    if len(embeddings_to_delete) > 0:
        llm_helper.vector_store.delete_keys(embeddings_to_delete)
        st.session_state['data_files_embeddings'] = st.session_state['data_files_embeddings'].drop(
            st.session_state['data_files_embeddings'][
                st.session_state['data_files_embeddings']['filename'] == file_to_delete].index)


# 删除指定文档和数据
def delete_file_and_embeddings(filename=''):
    if 'data_files_embeddings' not in st.session_state:
        st.session_state['data_files_embeddings'] = llm_helper.get_all_documents(k=1000)

    if filename == '':
        filename = st.session_state['file_and_embeddings_to_drop']

    file_dict = next((d for d in st.session_state['data_files'] if d['filename'] == filename), None)

    if len(file_dict) > 0:
        source_file = file_dict['filename']
        try:
            blob_client.delete_file(source_file)
        except Exception as e:
            st.error(f"删除文件 {source_file} 失败: {e}")

        delete_embeddings_of_file(parse.quote(filename))

    st.session_state['data_files'] = [d for d in st.session_state['data_files'] if d['filename'] != '{filename}']


# 删除所有文档和数据
def delete_all_files_and_embeddings():
    files_list = st.session_state['data_files']
    for filename_dict in files_list:
        delete_file_and_embeddings(filename_dict['filename'])


try:
    llm_helper = LLMHelper()
    blob_client = BlobClient()

    # 页面设置
    menu_items = {
	'Get help': None,
	'Report a bug': None,
	'About': '''
	 ## 文档管理
	'''
    }
    st.set_page_config(layout="wide", menu_items=menu_items)

    hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    # 初始化变量信息，并加载文档
    st.session_state['data_files'] = blob_client.get_all_files()

    if len(st.session_state['data_files']) == 0:
        st.warning("找不到文档记录，请添加文档！")

    else:
        filenames_list = [d['filename'] for d in st.session_state['data_files']]

        st.selectbox("文档", filenames_list, key="file_and_embeddings_to_drop")

        col1, col2 = st.columns([1, 13])
        with col1:
            st.button("删除", on_click=delete_file_and_embeddings)
        with col2:
            if len(st.session_state['data_files']) > 1:
                st.button("全部删除", type="secondary", on_click=delete_all_files_and_embeddings, args=None, kwargs=None)

        st.dataframe(st.session_state['data_files'], use_container_width=True)

except Exception as e:
    st.error(traceback.format_exc())
