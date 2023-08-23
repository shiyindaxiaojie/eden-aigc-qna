import streamlit as st
import os
import traceback
from utilities.llm_helper import LLMHelper


# 删除指定索引
def delete_embedding():
    llm_helper.vector_store.delete_keys([f"{st.session_state['embedding_to_drop']}"])
    if 'data_embeddings' in st.session_state:
        del st.session_state['data_embeddings'] 

# 删除文档内所有索引
def delete_file_embeddings():
    if st.session_state['data_embeddings'].shape[0] != 0:
        file_to_delete = st.session_state['file_to_drop']
        embeddings_to_delete = st.session_state['data_embeddings'][st.session_state['data_embeddings']['filename'] == file_to_delete]['key'].tolist()
        embeddings_to_delete = list(map(lambda x: f"{x}", embeddings_to_delete))
        if len(embeddings_to_delete) > 0:
            llm_helper.vector_store.delete_keys(embeddings_to_delete)
            st.session_state['data_embeddings'] = st.session_state['data_embeddings'].drop(st.session_state['data_embeddings'][st.session_state['data_embeddings']['filename'] == file_to_delete].index)

# 清空所有索引
def delete_all():
    embeddings_to_delete = st.session_state['data_embeddings'].key.tolist()
    embeddings_to_delete = list(map(lambda x: f"{x}", embeddings_to_delete))
    llm_helper.vector_store.delete_keys(embeddings_to_delete)   


try:
    # 页面设置
    menu_items = {
	'Get help': None,
	'Report a bug': None,
	'About': '''
	 ## Embeddings App
	 Embedding testing application.
	'''
    }
    st.set_page_config(layout="wide", menu_items=menu_items)

    llm_helper = LLMHelper()

    st.session_state['data_embeddings'] = llm_helper.get_all_documents(k=1000)

    nb_embeddings = len(st.session_state['data_embeddings'])

    if nb_embeddings == 0:
        st.warning("找不到索引记录，请添加文档！")
    else:
        col1, col2 = st.columns([3, 12])
        with col1:
            st.selectbox("文档", set(st.session_state['data_embeddings'].get('filename', [])),
                         key="file_to_drop")
        with col2:
            st.selectbox("索引", st.session_state['data_embeddings'].get('key', []), key="embedding_to_drop")

        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 6])
        with col1:
            st.button("删除文档内所有索引", on_click=delete_file_embeddings)
        with col2:
            st.button("删除指定索引", on_click=delete_embedding)
        with col3:
            st.button("清空所有索引", type="secondary", on_click=delete_all)
        with col4:
            st.download_button("下载数据", st.session_state['data_embeddings'].to_csv(index=False).encode('utf-8'),
                               "embeddings.csv", "text/csv", key='download-embeddings')
        with col5:
            st.write("")

        st.dataframe(st.session_state['data_embeddings'], use_container_width=True)
 
except Exception as e:
    st.error(traceback.format_exc())
