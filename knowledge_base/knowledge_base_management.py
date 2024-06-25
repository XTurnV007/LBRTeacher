import os
import requests
import json
import numpy as np
import streamlit as st
import faiss
import chardet
import fitz  # PyMuPDF
from typing import List, Tuple
from config.config import openai_api_key

API_KEY = openai_api_key
EMBEDDING_MODEL = "embedding-2"
EMBEDDING_API_URL = "https://open.bigmodel.cn/api/paas/v4/embeddings"
VECTOR_DIMENSION = 1024
EMBEDDING_FILE = "embeddings.txt"

def get_embedding(text: str) -> List[float]:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    payload = {
        "model": EMBEDDING_MODEL,
        "input": text
    }
    response = requests.post(EMBEDDING_API_URL, headers=headers, data=json.dumps(payload))
    response.raise_for_status()
    data = response.json()
    return data["data"][0]["embedding"]

def get_embeddings_for_long_text(text: str) -> List[float]:
    max_length = 512
    segments = [text[i:i+max_length] for i in range(0, len(text), max_length)]
    embeddings = []
    for segment in segments:
        embedding = get_embedding(segment)
        embeddings.append(embedding)
    avg_embedding = np.mean(embeddings, axis=0).tolist()
    return avg_embedding

def store_embeddings_to_file(embeddings: List[Tuple[str, List[float]]], file_path: str):
    with open(file_path, 'w', encoding='utf-8') as f:
        for text, embedding in embeddings:
            f.write(f"{text}\t{json.dumps(embedding)}\n")

def load_embeddings_from_file(file_path: str) -> List[Tuple[str, List[float]]]:
    embeddings = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            text, embedding = line.strip().split('\t')
            embeddings.append((text, json.loads(embedding)))
    return embeddings

def build_faiss_index(embeddings: List[Tuple[str, List[float]]]) -> faiss.IndexFlatL2:
    index = faiss.IndexFlatL2(VECTOR_DIMENSION)
    vectors = np.array([embedding for _, embedding in embeddings]).astype('float32')
    index.add(vectors)
    return index

def search_similar_texts(query_embedding: List[float], embeddings: List[Tuple[str, List[float]]], index: faiss.IndexFlatL2, top_k: int = 5) -> List[Tuple[str, float]]:
    query_vector = np.array(query_embedding).reshape(1, -1).astype('float32')
    distances, indices = index.search(query_vector, top_k)
    return [(embeddings[idx][0], distances[0][i]) for i, idx in enumerate(indices[0])]

def read_file_content(uploaded_file):
    raw_data = uploaded_file.read()
    result = chardet.detect(raw_data)
    encoding = result['encoding'] if result['encoding'] else 'utf-8'
    return raw_data.decode(encoding, errors='ignore')

def read_pdf_content(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    content = ""
    for page in doc:
        content += page.get_text()
    return content

def knowledge_base_management_method():
    st.title("知识库管理")
    option = st.selectbox("选择操作", ["上传文件", "搜索文件", "查看知识库"])
    
    if option == "上传文件":
        uploaded_files = st.file_uploader("选择文件上传", accept_multiple_files=True, type=["txt", "pdf"])
        if st.button("处理文件"):
            if uploaded_files:
                embeddings = []
                with st.spinner("正在处理文件..."):
                    for uploaded_file in uploaded_files:
                        try:
                            if uploaded_file.name.endswith(".pdf"):
                                content = read_pdf_content(uploaded_file)
                            else:
                                content = read_file_content(uploaded_file)
                            embedding = get_embeddings_for_long_text(content)
                            embeddings.append((uploaded_file.name, embedding))
                            st.success(f"文件 {uploaded_file.name} 已处理。")
                        except Exception as e:
                            st.error(f"处理文件 {uploaded_file.name} 时发生错误: {str(e)}")
                if embeddings:
                    store_embeddings_to_file(embeddings, EMBEDDING_FILE)
                    st.success("所有文件已处理并存储嵌入向量。")
            else:
                st.warning("请上传文件。")
    
    elif option == "搜索文件":
        query_text = st.text_input("输入查询文本:")
        if st.button("搜索"):
            if query_text:
                with st.spinner("正在搜索..."):
                    embeddings = load_embeddings_from_file(EMBEDDING_FILE)
                    index = build_faiss_index(embeddings)
                    query_embedding = get_embeddings_for_long_text(query_text)
                    results = search_similar_texts(query_embedding, embeddings, index)
                    st.write("搜索结果:")
                    for result in results:
                        st.write(f"文件名: {result[0]}, 相似度: {result[1]}")
            else:
                st.warning("请输入查询文本。")
    
    elif option == "查看知识库":
        embeddings = load_embeddings_from_file(EMBEDDING_FILE)
        st.write("现有知识库内容:")
        for text, _ in embeddings:
            st.write(f"文件名: {text}")

def search_local_knowledge_base(query_embedding: List[float], top_k: int = 5) -> List[Tuple[str, float]]:
    embeddings = load_embeddings_from_file(EMBEDDING_FILE)
    index = build_faiss_index(embeddings)
    return search_similar_texts(query_embedding, embeddings, index, top_k)

