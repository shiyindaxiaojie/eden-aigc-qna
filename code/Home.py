from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import traceback
from utilities.llm_helper import LLMHelper
import regex as re

from utilities.logger import Logger

logger = Logger().get_logger()

# 检查模型部署
def check_deployment():
    # 检查 LLM
    try:
        llm_helper = LLMHelper()
        llm_helper.get_completion("Generate a joke!")
        st.success(f"""LLM 检测正常，部署名称为 {llm_helper.deployment_name}""")
    except Exception as e:
        st.error(
            f"""LLM 检测异常，请检查 "{llm_helper.deployment_name}" 是否已经部署到 {llm_helper.api_base}""")
        st.error(traceback.format_exc())

    # 检查 Embeddings
    try:
        llm_helper = LLMHelper()
        llm_helper.embeddings.embed_documents(texts=["测试"])
        st.success(f"""Embedding Model 检测正常，部署名称为 {llm_helper.model}""")
    except Exception as e:
        st.error(
            f"""Embedding Model 检测异常，请检查 "{llm_helper.model}" 是否已经部署到 {llm_helper.api_base}。""")
        st.error(traceback.format_exc())

    # 检查 Vectors
    try:
        llm_helper = LLMHelper()
        if llm_helper.vector_store_type == "Redis":
            if llm_helper.vector_store.check_existing_index("embeddings-index"):
                st.warning("""Vectors Database 索引已存在，您可能用的是 Redis 历史数据
                    """)
            else:
                st.success("Vectors Database 检测正常，使用 Redis 向量数据库")
        else:
            if llm_helper.vector_store.check_existing_index("embeddings-index"):
                st.warning("""Vectors Database 检测异常，请检查 Milvus 的配置是否正确
                    """)
            else:
                st.success("Vectors Database 检测正常，使用 Milvus 向量数据库")
    except Exception as e:
        st.error(f"""Vectors Database 检测异常，请检查配置是否正确""")
        st.error(traceback.format_exc())

# 检查提示词是否包含指定的变量，否则按默认内容返回
def check_variables_in_prompt():
    if "{summaries}" not in st.session_state.custom_prompt:
        st.warning("""你的提示词不包含变量 "{summaries} 关键字""")
        st.session_state.custom_prompt = ""
    if "{question}" not in st.session_state.custom_prompt:
        st.warning("""你的提示词不包含变量 "{question} 关键字""")
        st.session_state.custom_prompt = ""


# 保存用户的提问内容
def ask_followup_question(followup_question):
    st.session_state.asked_question = followup_question
    st.session_state["input_message_key"] = st.session_state["input_message_key"] + 1


# 保存用户的提问内容，用于后续的语义搜索
def question_asked():
    st.session_state.asked_question = st.session_state["input" + str(st.session_state["input_message_key"])]


try:

    # 会话管理
    default_prompt = ""
    default_question = ""
    default_answer = ""
    if "question" not in st.session_state:
        st.session_state["question"] = default_question
    if "response" not in st.session_state:
        st.session_state["response"] = default_answer
    if "context" not in st.session_state:
        st.session_state["context"] = ""
    if "custom_prompt" not in st.session_state:
        st.session_state["custom_prompt"] = ""
    if "custom_temperature" not in st.session_state:
        st.session_state["custom_temperature"] = float(os.getenv("OPENAI_TEMPERATURE", 0.7))
    if 'sources' not in st.session_state:
        st.session_state['sources'] = ""
    if 'followup_questions' not in st.session_state:
        st.session_state['followup_questions'] = []
    if 'input_message_key' not in st.session_state:
        st.session_state ['input_message_key'] = 1
    if 'asked_question' not in st.session_state:
        st.session_state.asked_question = default_question

    # 侧栏菜单
    menu_items = {
        "Get help": None,
        "Report a bug": None,
        "About": """
         ## Embeddings App
         Embedding testing application.
        """
    }
    st.set_page_config(
        page_title="普益AI知识库",
        page_icon = "🧊",
        layout = "wide",
        initial_sidebar_state = "expanded",
        menu_items=menu_items)

    llm_helper = LLMHelper(custom_prompt=st.session_state.custom_prompt,
                           temperature=st.session_state.custom_temperature)

    # 自定义提示词变量
    custom_prompt_placeholder = """{summaries}  
    Question: {question}  
    Answer:"""

    custom_prompt_help = """You can configure a custom prompt by adding the variables {summaries} and {question} to the prompt.  
    {summaries} will be replaced with the content of the documents retrieved from the VectorStore.  
    {question} will be replaced with the user's question.
    """

    # 设置页面布局
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.image(os.path.join('images', 'logo.png'))

    st.write("<br>", unsafe_allow_html=True)

    col4, col5, col6 = st.columns([2, 2, 2])
    with col4:
        st.button("检查模型部署", on_click=check_deployment)
    with col6:
        with st.expander("设置"):
            st.slider("Temperature", min_value=0.0, max_value=1.0, step=0.1, key='custom_temperature')
            st.text_area("Custom Prompt", key='custom_prompt', on_change=check_variables_in_prompt,
                         placeholder=custom_prompt_placeholder, help=custom_prompt_help, height=150)

    # 提问输入框
    question = st.text_input("**请在下方输入你的问题**", value=st.session_state['asked_question'],
                             key="input" + str(st.session_state['input_message_key']), on_change=question_asked)
    if st.session_state.asked_question != '':
        st.session_state['question'] = st.session_state.asked_question
        st.session_state.asked_question = ""
        st.session_state['question'], \
            st.session_state['response'], \
            st.session_state['context'], \
            st.session_state['sources'] = llm_helper.get_semantic_answer(st.session_state['question'], [])

        st.session_state['response'], followup_questions_list = llm_helper.extract_followup_questions(
            st.session_state['response'])

        st.session_state['followup_questions'] = followup_questions_list

    sourceList = []

    if st.session_state['sources'] or st.session_state['context']:
        st.session_state['response'], sourceList = llm_helper.get_links_filenames(
            st.session_state['response'], st.session_state['sources'])

    st.write("<br>", unsafe_allow_html=True)

    if st.session_state['response']:
        st.write("**回答** <br>", unsafe_allow_html=True)
        st.markdown(st.session_state['response'].split("\n")[0])

    st.write("<br>", unsafe_allow_html=True)

    if st.session_state['sources'] or st.session_state['context']:
        st.markdown('**信息来源**')
        for id in range(len(sourceList)):
            st.markdown(f"[{id + 1}] {sourceList[id]}")

        with st.expander("相关问题上下文"):
            if not st.session_state['context'] is None and st.session_state['context'] != []:
                for content_source in st.session_state['context'].keys():
                    st.markdown(f"#### {content_source}")
                    for context_text in st.session_state['context'][content_source]:
                        st.markdown(f"{context_text}")

            st.markdown(f"来源: {st.session_state['sources']}")

    st.write("<br>", unsafe_allow_html=True)

    if len(st.session_state['followup_questions']) > 0:
        st.markdown('**您还可以继续提问**')
    with st.container():
        for questionId, followup_question in enumerate(st.session_state['followup_questions']):
            if followup_question:
                str_followup_question = re.sub(r"(^|[^\\\\])'", r"\1\\'", followup_question)
                st.button(str_followup_question, key=1000 + questionId, on_click=ask_followup_question,
                          args=(followup_question,))

    for questionId, followup_question in enumerate(st.session_state['followup_questions']):
        if followup_question:
            str_followup_question = re.sub(r"(^|[^\\\\])'", r"\1\\'", followup_question)


except Exception:
    st.error(traceback.format_exc())
