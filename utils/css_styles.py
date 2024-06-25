import streamlit as st

persona_card_styles = """
<style>
    .persona-container {
        display: flex;
        flex-wrap: nowrap;
        overflow-x: auto;
        gap: 100px;
        padding: 20px 0;
    }
    .persona-card {
        flex: 0 0 300px;
        height: 340px;
        background: #fff;
        padding: 15px;
        border-radius: 10px;
        margin-top: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        position: relative;
        overflow: hidden;
        transition: transform 0.3s, box-shadow 0.3s;
    }
    .persona-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }
    .persona-card h5 {
        margin-top: 0;
        font-size: 18px;
        font-weight: bold;
        color: #007bff;
    }
    .persona-card p {
        font-size: 14px;
        line-height: 1.5;
        color: #333;
    }
    .persona-avatar {
        width: calc(260px);  /* 占据卡片高度的三分之二 */
        height: calc(260px); /* 保持宽高一致 */
        border-radius: 50%;
        position: absolute;
        top: calc(340px / 2 - 260px / 2);  /* 垂直居中 */
        right: 60px;
    }
</style>
"""
def apply_css_styles():
    css_styles = """
    <style>
    .css-1aumxhk {
        background: #f0f0f0;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 20px;
    }
    .stRadio > div > label {
        display: flex;
        justify-content: left;
        align-items: left;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #e1e1e1;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stRadio > div > label:hover {
        background-color: #f0f0f0;
    }
    .stRadio > div > label > div {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
    }
    .stRadio > div > label > div > span {
        margin-top: 5px;
    }
    </style>
    """
    st.markdown(css_styles, unsafe_allow_html=True)
