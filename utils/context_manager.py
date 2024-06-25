from config.config import MAX_HISTORY_LENGTH

chat_history = []  # 用于存储聊天记录
content_topic = ""  # 用于存储用户输入的内容主题
shared_context = {}

def add_to_chat_history(role, content):
    global chat_history
    if len(chat_history) >= MAX_HISTORY_LENGTH:
        chat_history.pop(0)  # 移除最早的记录
    chat_history.append({'role': role, 'content': content})

def update_context(agent, data):
    global shared_context
    shared_context[agent] = data

def get_context(agent):
    return shared_context.get(agent, {})

def build_prompt(user_input, agent):
    global content_topic
    context = " ".join([x['content'] for x in chat_history[-3:]])
    if agent == 'advantage_agent':
        prompt = f"根据用户近期关心的内容主题'{content_topic}'，请严格按照JSON格式（只要JSON格式部分的内容）描述{user_input} 主题下用户可能的优势。"
    elif agent == 'positioning_agent':
        prompt = f"针对'{content_topic}'， 严格按照JSON格式（只要JSON格式部分的内容），生成一个高水准且结构化关于{user_input}的具体小红书人设。人设内容只包括姓名（有趣且惊艳）、性别、年龄、位置、个人情况（使用多个高级短句和emoji表情符号阐述职业、成就、轻松有趣的话语，短句格式参考“时装设计师\n宋朝业余搞笑女\n心理咨询师，情感问题解决\n爱助人｜爱折腾｜爱阅读得00后大学生\n学习资源，成长干货分享\n自律女孩｜成长学习｜书籍分享\n成为更优秀的自己！向更优秀的人学习！”）、兴趣（多字词语）。用中文回答！"
    elif agent == 'chat_agent':
        prompt = " ".join([m['content'] for m in chat_history])

    return prompt
