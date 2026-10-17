"""RAG 前后对比页面：同一问题，纯模型 vs 使用知识库。"""
import streamlit as st

from kbrag.compare_service import load_records, run_compare, save_records


def compare_page():
    st.title("RAG 前后对比")
    st.caption(
        "同一个问题，分别用纯模型（不使用知识库）和 RAG（检索知识库）回答，"
        "直观看出录入知识库前后的区别。"
    )

    if "comparisons" not in st.session_state:
        st.session_state["comparisons"] = load_records()

    with st.form("compare_form", clear_on_submit=True):
        question = st.text_input(
            "输入要对比的问题",
            placeholder="例如：根据文档，蔡徐坤2026年发行了什么专辑？",
        )
        submitted = st.form_submit_button("生成对比")

    if submitted and question.strip():
        with st.spinner("两种模式生成中，请稍候..."):
            try:
                record = run_compare(question.strip())
                st.session_state["comparisons"].insert(0, record)
                save_records(st.session_state["comparisons"])
                st.rerun()
            except Exception as exc:
                st.error(f"生成失败：{exc}")

    if not st.session_state["comparisons"]:
        st.info("还没有对比记录，输入一个问题开始。")

    for record in st.session_state["comparisons"]:
        st.divider()
        st.subheader(f"Q：{record['question']}")
        st.caption(
            f"{record.get('time', '')} | 模型：{record.get('model', '')} | "
            f"top-k：{record.get('retrieval_k', '')}"
        )

        left, right = st.columns(2)
        with left:
            st.markdown("#### 未使用知识库（纯模型）")
            st.write(record["plain"])
        with right:
            st.markdown("#### 使用知识库（RAG）")
            st.write(record["rag"])

            sources = record.get("sources") or []
            with st.expander(f"检索到的参考资料（{len(sources)} 条）"):
                if not sources:
                    st.write("未检索到相关内容")
                for source in sources:
                    st.markdown(f"**{source['source']}**")
                    st.text(source["content"])

    with st.sidebar:
        st.subheader("对比记录")
        st.caption(f"共 {len(st.session_state['comparisons'])} 条")
        if st.button("清空对比记录"):
            save_records([])
            st.session_state["comparisons"] = []
            st.rerun()
