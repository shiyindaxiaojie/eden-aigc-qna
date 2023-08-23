import traceback

import streamlit as st
from streamlit_chat import message
from utilities.llm_helper import LLMHelper
import regex as re
import os
from random import randint


# 清空聊天变量信息
def clear_chat_data():
    st.session_state['chat_history'] = []
    st.session_state['chat_source_documents'] = []
    st.session_state['chat_asked_question'] = ''
    st.session_state['chat_question'] = ''
    st.session_state['chat_followup_questions'] = []
    answer_with_citations = ""


# 输入问题离开焦点触发事件，保存问题信息
def question_asked():
    st.session_state.chat_asked_question = st.session_state["input" + str(st.session_state['input_message_key'])]
    st.session_state.chat_question = st.session_state.chat_asked_question


# 回复问题
def ask_followup_question(followup_question):
    st.session_state.chat_asked_question = followup_question
    st.session_state['input_message_key'] = st.session_state['input_message_key'] + 1


try:
    llm_helper = LLMHelper()

    # 初始化变量信息
    if 'chat_question' not in st.session_state:
        st.session_state['chat_question'] = ''
    if 'chat_asked_question' not in st.session_state:
        st.session_state.chat_asked_question = ''
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    if 'chat_source_documents' not in st.session_state:
        st.session_state['chat_source_documents'] = []
    if 'chat_followup_questions' not in st.session_state:
        st.session_state['chat_followup_questions'] = []
    if 'input_message_key' not in st.session_state:
        st.session_state['input_message_key'] = 1

    # 初始化聊天头像
    ai_avatar_style = os.getenv("CHAT_AI_AVATAR_STYLE", "thumbs")
    ai_seed = os.getenv("CHAT_AI_SEED", "Lucy")
    user_avatar_style = os.getenv("CHAT_USER_AVATAR_STYLE", "thumbs")
    user_seed = os.getenv("CHAT_USER_SEED", "Bubba")

    # 聊天窗口
    clear_chat = st.button("清空聊天记录", key="clear_chat", on_click=clear_chat_data)
    input_text = st.text_input("**请发起提问**", placeholder="输入您的问题", value=st.session_state.chat_asked_question,
                               key="input" + str(st.session_state['input_message_key']), on_change=question_asked)

    # 获取结果、上下文、来源、后续问题
    if st.session_state.chat_asked_question:
        st.session_state['chat_question'] = st.session_state.chat_asked_question
        st.session_state.chat_asked_question = ""
        st.session_state['chat_question'], result, context, sources = llm_helper.get_semantic_answer(
            st.session_state['chat_question'], st.session_state['chat_history'])
        result, chat_followup_questions_list = llm_helper.extract_followup_questions(result)
        st.session_state['chat_history'].append((st.session_state['chat_question'], result))
        st.session_state['chat_source_documents'].append(sources)
        st.session_state['chat_followup_questions'] = chat_followup_questions_list

    # 显示聊天历史记录
    if st.session_state['chat_history']:
        history_range = range(len(st.session_state['chat_history']) - 1, -1, -1)
        for i in range(len(st.session_state['chat_history']) - 1, -1, -1):

            if i == history_range.start:
                answer_with_citations, sourceList = llm_helper.get_links_filenames(
                    st.session_state['chat_history'][i][1], st.session_state['chat_source_documents'][i])
                st.session_state['chat_history'][i] = st.session_state['chat_history'][i][:1] + (answer_with_citations,)

                answer_with_citations = re.sub(r'\$\^\{(.*?)\}\$', r'(\1)', st.session_state['chat_history'][i][
                    1]).strip()

                if len(st.session_state['chat_followup_questions']) > 0:
                    st.markdown('**您还可以继续追问**')
                with st.container():
                    for questionId, followup_question in enumerate(st.session_state['chat_followup_questions']):
                        if followup_question:
                            str_followup_question = re.sub(r"(^|[^\\\\])'", r"\1\\'", followup_question)
                            st.button(str_followup_question, key=randint(1000, 99999), on_click=ask_followup_question,
                                      args=(followup_question,))

                for questionId, followup_question in enumerate(st.session_state['chat_followup_questions']):
                    if followup_question:
                        str_followup_question = re.sub(r"(^|[^\\\\])'", r"\1\\'", followup_question)

            answer_with_citations = re.sub(r'\$\^\{(.*?)\}\$', r'(\1)', st.session_state['chat_history'][i][
                1])
            message(answer_with_citations, key=str(i) + 'answers', avatar_style=ai_avatar_style, seed=ai_seed)
            st.markdown(f'\n\n参考来源：{st.session_state["chat_source_documents"][i]}')
            message(st.session_state['chat_history'][i][0], is_user=True, key=str(i) + 'user' + '_user',
                    avatar_style=user_avatar_style, seed=user_seed)

except Exception:
    st.error(traceback.format_exc())
