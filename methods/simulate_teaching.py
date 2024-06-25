import json
import streamlit as st
from zhipuai import ZhipuAI
from config.config import openai_api_key
from utils.chat_helpers import add_to_chat_history, build_prompt, clean_api_response, generate_image_url, generate_content
from utils.css_styles import persona_card_styles

client = ZhipuAI(api_key=openai_api_key)

def generate_persona(user_input):
    prompt = build_prompt(user_input)
    response = client.chat.completions.create(
        # model="glm-3-turbo",
        model="glm-4-0520",
        messages=[{'role': 'user', 'content': prompt}]
    )

    result = ""
    try:
        if hasattr(response, 'choices'):
            for choice in response.choices:
                if hasattr(choice, 'message'):
                    cleaned_content = clean_api_response(choice.message.content)
                    result += cleaned_content
    except Exception as e:
        st.error(f"Error processing response: {e}")

    add_to_chat_history('assistant', result)
    return result

def generate_notes(persona, topic):
    prompt = f"基于以下人设生成关于'{topic}'的笔记：{persona}"
    response = client.chat.completions.create(
        # model="glm-3-turbo",
        model="glm-4-0520",
        messages=[{'role': 'user', 'content': prompt}]
    )

    result = ""
    try:
        if hasattr(response, 'choices'):
            for choice in response.choices:
                if hasattr(choice, 'message'):
                    cleaned_content = clean_api_response(choice.message.content)
                    result += cleaned_content
    except Exception as e:
        st.error(f"Error processing response: {e}")

    return result

def sync_session_state():
    if 'personas' not in st.session_state:
        st.session_state.personas = []
    if 'show_input' not in st.session_state:
        st.session_state.show_input = []
    if 'notes' not in st.session_state:
        st.session_state.notes = []

    # Ensure lengths are the same
    while len(st.session_state.show_input) < len(st.session_state.personas):
        st.session_state.show_input.append(False)
    while len(st.session_state.notes) < len(st.session_state.personas):
        st.session_state.notes.append("")

    # In case the lists are longer than personas (which shouldn't happen but just in case)
    while len(st.session_state.show_input) > len(st.session_state.personas):
        st.session_state.show_input.pop()
    while len(st.session_state.notes) > len(st.session_state.personas):
        st.session_state.notes.pop()

def simulate_teaching_method():
    st.title("模拟教学方法")

    global content_topic

    st.markdown("<div style='background-color: #fafafa; padding: 10px; border-radius: 10px;'>", unsafe_allow_html=True)
    st.write("请输入内容主题：")
    content_topic_input = st.text_input("内容主题", key="content_topic_input")

    if st.button("生成人设"):
        content_topic = content_topic_input
        with st.spinner("正在生成人设..."):
            persona = generate_persona(content_topic_input)
            image_url = generate_image_url(persona)
            if 'personas' not in st.session_state:
                st.session_state.personas = []
            st.session_state.personas.append((persona, image_url))
            sync_session_state()

    if 'personas' in st.session_state:
        st.markdown(persona_card_styles, unsafe_allow_html=True)
        st.markdown("<div class='persona-container'>", unsafe_allow_html=True)
        for idx, (persona, image_url) in enumerate(st.session_state.personas):
            create_persona_card(persona, image_url, idx)
        st.markdown("</div>", unsafe_allow_html=True)

def create_persona_card(description, image_url, idx):
    def build_html_content(data):
        def generate_list(data):
            if isinstance(data, dict):
                items = ""
                for key, value in data.items():
                    if isinstance(value, (dict, list)):
                        items += f"<li><strong>{key}:</strong>{generate_list(value)}</li>"
                    else:
                        items += f"<li><strong>{key}:</strong> {value}</li>"
                return f"<ul>{items}</ul>"
            elif isinstance(data, list):
                items = ""
                for item in data:
                    items += f"<li>{generate_list(item)}</li>"
                return f"<ul>{items}</ul>"
            else:
                return f"<li>{data}</li>"

        return generate_list(data)

    try:
        persona_data = json.loads(description)
    except json.JSONDecodeError:
        persona_data = {"description": description}

    card_html_content = build_html_content(persona_data)

    st.markdown(
        f"""
        <div class="persona-card">
            <h5>人设卡片</h5>
            <img src="{image_url}" class="persona-avatar" alt="Avatar">
            <div style="height: 300px; overflow: hidden; text-overflow: ellipsis;">
                {card_html_content}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("生成笔记", key=f"show_input_{idx}"):
        st.session_state.show_input[idx] = not st.session_state.show_input[idx]
        st.experimental_rerun()

    if st.session_state.show_input[idx]:
        note_topic = st.text_input("请输入主题词", key=f"note_topic_{idx}")
        if st.button("开始生成", key=f"generate_{idx}"):
            with st.spinner("正在生成笔记..."):
                notes = generate_content(description, note_topic)
                st.session_state.notes[idx] = notes
                st.experimental_rerun()

    if st.session_state.notes[idx]:
        st.write(st.session_state.notes[idx])

    if st.button("✕", key=f"delete_{idx}"):
        delete_persona(idx)

def delete_persona(idx):
    if 'personas' in st.session_state:
        st.session_state.personas.pop(idx)
    sync_session_state()
    st.experimental_rerun()
