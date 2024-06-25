import streamlit as st
from methods.simulate_teaching import simulate_teaching_method
from methods.interactive_teaching import interactive_teaching_method
from methods.exercise_teaching import exercise_teaching_method
from methods.knowledge_summary import knowledge_summary_method
from methods.assessment_teaching import assessment_teaching_method
from knowledge_base.knowledge_base_management import knowledge_base_management_method
from utils.css_styles import apply_css_styles

# 设置页面配置
st.set_page_config(
    page_title="LRBTeacher",  # 设置浏览器标签标题
    page_icon="📚",  # 设置浏览器标签图标，可以是路径、URL或emoji
    layout="wide",  # 设置页面布局为宽屏模式
    initial_sidebar_state="expanded"  # 设置侧边栏初始状态为展开
)

def main():
    apply_css_styles()
    
    st.sidebar.title("LRBTeacher")
    st.sidebar.markdown("一个由大语言模型驱动的小红书博主学习教育平台")
    
    section = st.sidebar.radio(
        "选择一个功能",
        [
            "教学模式",
            "知识库管理"
        ],
        format_func=lambda x: f"⚙️ {x}"  # 添加图标
    )

    if section == "教学模式":
        method = st.sidebar.selectbox(
            "请选择一种教学方法",
            [
                "模拟教学方法",
                "互动式教学方法",
                "练习式教学方法",
                "知识总结式教学方法",
                "评估式教学方法"
            ],
            format_func=lambda x: f"📘 {x}"  # 添加图标
        )

        if method == "模拟教学方法":
            simulate_teaching_method()
        elif method == "互动式教学方法":
            interactive_teaching_method()
        elif method == "练习式教学方法":
            exercise_teaching_method()
        elif method == "知识总结式教学方法":
            knowledge_summary_method()
        elif method == "评估式教学方法":
            assessment_teaching_method()
    elif section == "知识库管理":
        knowledge_base_management_method()

if __name__ == "__main__":
    main()
