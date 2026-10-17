"""智能客服页面：RAG 问答 + 按用户隔离的会话历史。"""
import re
import uuid

import streamlit as st

from kbrag.history import get_history
from kbrag.rag_service import RagService

WELCOME_MESSAGE = {"role": "assistant", "content": "你好，有什么可以帮助你？"}


def new_session_id() -> str:
    """生成一个随机的用户/会话标识"""
    return uuid.uuid4().hex[:12]


def sanitize_user_id(raw: str) -> str:
    """只保留安全字符，避免用户标识被拼进文件路径"""
    return re.sub(r"[^0-9A-Za-z_-]", "", raw or "")[:32]


def load_page_messages(session_id: str):
    """从历史文件恢复页面消息，刷新/重开页面后仍能看到之前的对话"""
    messages = [WELCOME_MESSAGE.copy()]
    for message in get_history(session_id).messages:
        role = "user" if message.type == "human" else "assistant"
        messages.append({"role": role, "content": message.content})
    return messages


def chat_page():
    # 标题
    st.title("智能客服")
    # 分隔符
    st.divider()

    # 每个用户使用独立的会话 ID：历史记录按 ID 分文件保存，互不干扰
    if "session_id" not in st.session_state:
        # 支持通过 ?user=xxx 指定用户标识，刷新页面后可以接着原来的对话
        url_user_id = sanitize_user_id(st.query_params.get("user", ""))
        st.session_state["session_id"] = url_user_id or new_session_id()
        if not url_user_id:
            st.query_params["user"] = st.session_state["session_id"]

    # 会话 ID 变化时（例如刷新页面、点击“新建会话”），加载对应的历史消息
    if st.session_state.get("message_session_id") != st.session_state["session_id"]:
        st.session_state["message"] = load_page_messages(st.session_state["session_id"])
        st.session_state["message_session_id"] = st.session_state["session_id"]

    # 避免性能压力，session_state 存入对象
    if "rag" not in st.session_state:
        st.session_state["rag"] = RagService()

    with st.sidebar:
        st.subheader("当前会话")
        st.caption("用户标识（历史记录按此隔离）")
        st.code(st.session_state["session_id"], language=None)
        if st.button("新建会话"):
            st.session_state["session_id"] = new_session_id()
            st.session_state["message"] = [WELCOME_MESSAGE.copy()]
            st.session_state["message_session_id"] = st.session_state["session_id"]
            st.query_params["user"] = st.session_state["session_id"]
            st.rerun()

    session_config = {
        "configurable": {
            "session_id": st.session_state["session_id"],
        }
    }

    # 循环输出历史信息，原本只记录但页面不显示
    for message in st.session_state["message"]:
        st.chat_message(message["role"]).write(message["content"])
    # 在页面最下方提供用户输入栏
    prompt = st.chat_input()

    if prompt and prompt.strip():
        # 在页面输出用户的提问
        st.chat_message("user").write(prompt)
        st.session_state["message"].append({"role": "user", "content": prompt})

        ai_res_list = []
        with st.spinner("AI 思考中......."):
            # 流式输出
            res_stream = st.session_state["rag"].chain.stream({"input": prompt}, session_config)

            def capture(generator, cache_list):
                for chunk in generator:
                    cache_list.append(chunk)
                    yield chunk

            st.chat_message("assistant").write_stream(capture(res_stream, ai_res_list))
            st.session_state["message"].append(
                {"role": "assistant", "content": "".join(ai_res_list)}
            )
