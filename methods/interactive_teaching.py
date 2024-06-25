import streamlit as st
from zhipuai import ZhipuAI
from config.config import openai_api_key
from utils.context_manager import add_to_chat_history

client = ZhipuAI(api_key=openai_api_key)

def fetch_response_from_api(user_input, chat_history):
    messages = chat_history + [
        {'role': 'user', 'content': user_input}
    ]

    response = client.chat.completions.create(
        # model="glm-3-turbo",
        model="glm-4-0520",
        messages=messages
    )

    result = response.choices[0].message.content  # Correctly access response content

    add_to_chat_history('assistant', result)
    return result

def render_chat_bubble(chat, role):
    if role == 'user':
        st.markdown(
            f"""
            <div style='background-color: #DCF8C6; padding: 10px; border-radius: 10px; margin: 5px 0; text-align: right;'>
                <strong>你:</strong> {chat}
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div style='background-color: #E6E6E6; padding: 10px; border-radius: 10px; margin: 5px 0;'>
                <strong>导师:</strong> {chat}
            </div>
            """,
            unsafe_allow_html=True
        )

def interactive_teaching_method():
    st.title("互动式教学方法")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        st.session_state.started = False

    if not st.session_state.started:
        if st.button("开始"):
            with st.spinner("正在获取初始回复..."):
                initial_prompt = "为用户拟定一个小红书角色（包括背景、内容方向、目标受众以及营销策略），并根据角色，需要提出一个易于回答的且与小红书运营相关的问题。"
                st.session_state.chat_history = [
                    {'role': 'system', 'content': "你是一个小红书博主教学专家，用户现在要通过角色扮演的方式——互动式教学方法来学习小红书博主。"}
                ]
                initial_response = fetch_response_from_api(initial_prompt, st.session_state.chat_history)
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': initial_response
                })
                st.session_state.started = True
                st.experimental_rerun()  # Rerun to update the interface

    if st.session_state.started:
        for chat in st.session_state.chat_history:
            if chat["role"] == "user":
                render_chat_bubble(chat["content"], "user")
            else:
                render_chat_bubble(chat["content"], "assistant")

        user_input = st.text_area("请输入你的问题或描述你的情况:", "")
        
        if st.button("发送"):
            if user_input:
                with st.spinner("正在生成回复..."):
                    chat_history = st.session_state.chat_history
                    response = fetch_response_from_api(user_input, chat_history)
                    if response:
                        chat_history.append({"role": "user", "content": user_input})
                        chat_history.append({"role": "assistant", "content": response})
                        st.session_state.chat_history = chat_history
                        st.experimental_rerun()  # Rerun to update the interface

