import streamlit as st
import requests

# ========== 配置 ==========
API_URL = "http://127.0.0.1:5000/ask"  # 改为你的后端API地址（如云服务器公网IP）

# ========== 多语言支持 ==========
LANGS = {
    "English": {
        "title": "Building Code Professional Q&A",
        "input": "Enter your question:",
        "submit": "Submit",
        "answer": "AI Answer:",
        "placeholder": "e.g. What is the fire separation distance for residential buildings?"
    },
    "中文": {
        "title": "建筑规范专业问答",
        "input": "请输入你的问题：",
        "submit": "提交",
        "answer": "AI专业回答：",
        "placeholder": "例如：住宅楼的防火间距要求是多少？"
    }
}

# ========== Streamlit 页面 ==========
st.set_page_config(page_title="Building Code Q&A", layout="centered")
lang = st.selectbox("Language / 语言", ["English", "中文"])
labels = LANGS[lang]

st.title(labels["title"])
question = st.text_input(labels["input"], placeholder=labels["placeholder"])

if st.button(labels["submit"]) and question.strip():
    with st.spinner("AI is thinking..." if lang == "English" else "AI思考中..."):
        try:
            resp = requests.post(API_URL, json={"question": question})
            if resp.status_code == 200:
                answer = resp.json().get("answer", "")
                st.markdown(f"**{labels['answer']}**")
                st.write(answer)
            else:
                st.error("API error, please check your backend." if lang == "English" else "API错误，请检查后端服务。")
        except Exception as e:
            st.error(str(e)) 