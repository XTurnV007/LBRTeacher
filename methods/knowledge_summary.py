import streamlit as st
import networkx as nx
import plotly.graph_objects as go
from zhipuai import ZhipuAI
from config.config import openai_api_key
from utils.context_manager import add_to_chat_history
from knowledge_base.knowledge_base_management import search_local_knowledge_base, get_embeddings_for_long_text
from internet_search.duckduckgo_search import internet_search
import math

client = ZhipuAI(api_key=openai_api_key)

def fetch_knowledge_from_api(notes_input, knowledge_base_result, internet_search_result):
    combined_input = f"{notes_input}\n\n知识库结果:\n{knowledge_base_result}\n\n互联网搜索结果:\n{internet_search_result}"
    prompt = f"根据以下内容生成结构化知识（按层级递增）:\n{combined_input}"
    messages = [
        {'role': 'system', 'content': "你是一名知识管理专家，擅长以markdown格式生成知识框架。"},
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

def format_markdown(response):
    lines = response.split('\n')
    formatted_lines = []
    for line in lines:
        line = line.strip()
        if line:
            formatted_lines.append(line)
    return '\n'.join(formatted_lines)

def create_knowledge_graph(formatted_response, center_node):
    graph = nx.DiGraph()
    graph.add_node(center_node, level=0)

    lines = formatted_response.split('\n')
    current_subtopic = ""
    current_subsubtopic = ""

    for line in lines:
        if line.startswith('## '):
            current_subtopic = line.strip('# ').strip()
            graph.add_node(current_subtopic, level=1)
            graph.add_edge(center_node, current_subtopic)
            current_subsubtopic = ""
        elif line.startswith('### '):
            current_subsubtopic = line.strip('# ').strip()
            graph.add_node(current_subsubtopic, level=2)
            graph.add_edge(current_subtopic, current_subsubtopic)
        elif line.startswith('#### '):
            item = line.strip('# ').strip()
            graph.add_node(item, level=3)
            graph.add_edge(current_subsubtopic, item)
        elif line.startswith('- '):
            item = line.strip('- ').strip()
            graph.add_node(item, level=4)
            if current_subsubtopic:
                graph.add_edge(current_subsubtopic, item)
            elif current_subtopic:
                graph.add_edge(current_subtopic, item)

    return graph

def polar_layout(graph, center=(0, 0), layer_gap=5):
    pos = {}
    levels = {}
    
    for node, data in graph.nodes(data=True):
        level = data['level']
        if level not in levels:
            levels[level] = []
        levels[level].append(node)
    
    for level, nodes in levels.items():
        angle_gap = 2 * math.pi / len(nodes)
        radius = level * layer_gap
        for i, node in enumerate(nodes):
            angle = i * angle_gap
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            pos[node] = (x, y)
    
    return pos

def plot_knowledge_graph(graph):
    pos = polar_layout(graph)  # 使用极坐标布局
    edge_x = []
    edge_y = []
    for edge in graph.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='rgba(50,50,50,0.7)'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    node_text = []
    node_color = []
    node_size = []
    for node in graph.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)
        level = graph.nodes[node]['level']
        if level == 0:
            node_color.append('rgba(217,95,2,0.9)')  # 中心节点颜色
            node_size.append(40)
        elif level == 1:
            node_color.append('rgba(27,158,119,0.8)')  # 第二级节点颜色
            node_size.append(30)
        elif level == 2:
            node_color.append('rgba(117,112,179,0.8)')  # 第三级节点颜色
            node_size.append(20)
        elif level == 3:
            node_color.append('rgba(231,41,138,0.8)')  # 第四级节点颜色
            node_size.append(15)
        else:
            node_color.append('rgba(102,166,30,0.8)')  # 更低级节点颜色
            node_size.append(10)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="top center",
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            size=node_size,
            color=node_color,
            colorbar=dict(
                thickness=15,
                title='Node Level',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title='<br>Knowledge Graph',
                        titlefont_size=20,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=40, l=40, r=40, t=40),
                        annotations=[dict(
                            text="Generated by Knowledge Management System",
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.005, y=-0.002
                        )],
                        xaxis=dict(showgrid=False, zeroline=False),
                        yaxis=dict(showgrid=False, zeroline=False),
                        plot_bgcolor='white',
                        height=860,  # 调整图表高度
                        width=800,   # 保持宽度不变
                    )
                )
    return fig

def knowledge_summary_method():
    st.title("知识总结式教学方法")
    notes_input = st.text_area("请输入你想要学习的知识:")
    if st.button("生成知识图谱"):
        with st.spinner("正在生成知识图谱..."):
            with st.spinner("正在从知识库检索信息..."):
                query_embedding = get_embeddings_for_long_text(notes_input)
                knowledge_base_result = search_local_knowledge_base(query_embedding)

            with st.spinner("正在进行联网搜索..."):
                internet_search_result = internet_search(notes_input)

            combined_knowledge_base_result = '\n'.join([f"文件名: {result[0]}, 相似度: {result[1]}" for result in knowledge_base_result])
            response = fetch_knowledge_from_api(notes_input, combined_knowledge_base_result, internet_search_result)
            
            if response:
                formatted_response = format_markdown(response)
                graph = create_knowledge_graph(formatted_response, notes_input)
                fig = plot_knowledge_graph(graph)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("API 响应为空，请检查 API 请求。")

