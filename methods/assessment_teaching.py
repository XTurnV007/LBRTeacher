import streamlit as st
from zhipuai import ZhipuAI
from config.config import openai_api_key
from utils.context_manager import add_to_chat_history

client = ZhipuAI(api_key=openai_api_key)

def assess_content(content):
    prompt = f"请评估以下内容，并为其打分（1到10分），指出不足之处并提供改进方向：\n\n{content}"
    messages = [
        {'role': 'system', 'content': "你是一名经验丰富的老师，擅长评估和改进学生的写作内容。"},
        {'role': 'user', 'content': prompt}
    ]

    response = client.chat.completions.create(
        # model="glm-3-turbo",
        model="glm-4-0520",
        messages=messages,
        stream=True,
    )

    result = ""
    for chunk in response:
        if hasattr(chunk.choices[0], 'delta'):
            result += chunk.choices[0].delta.content

    add_to_chat_history('assistant', result)
    return result

def extract_score(assessment_result):
    import re
    match = re.search(r"评分：(\d+)/10", assessment_result)
    if match:
        return int(match.group(1))
    return None

def display_stars(score):
    stars = "⭐" * score + "☆" * (10 - score)
    return stars

def assessment_teaching_method():
    st.title("评估式教学方法")
    st.write("请输入您要评估的内容：")
    content_input = st.text_area("撰写内容")

    if st.button("评估内容"):
        with st.spinner("正在评估..."):
            assessment_result = assess_content(content_input)
            st.write("评估结果：")
            score = extract_score(assessment_result)
            if score is not None:
                stars = display_stars(score)
                st.markdown(f"**评分：** {stars} ({score}/10)")
            st.write(assessment_result)

