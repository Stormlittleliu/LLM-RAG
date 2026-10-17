"""RAG 前后对比服务。

同一个问题分别用两种方式回答：
1. 纯模型：不使用知识库，只靠模型自身知识；
2. RAG：先从 Chroma 检索资料，再把资料放进 Prompt 让模型回答。
"""
import json
import os
from datetime import datetime

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from kbrag import config
from kbrag.prompts import PLAIN_SYSTEM_TEMPLATE, RAG_SYSTEM_TEMPLATE, format_docs
from kbrag.providers import get_chat_model
from kbrag.vector_store import VectorStoreService

COMPARE_PATH = config.compare_history_path


def load_records():
    """读取历史对比记录"""
    if not os.path.exists(COMPARE_PATH):
        return []
    try:
        with open(COMPARE_PATH, "r", encoding="utf-8") as f:
            records = json.load(f)
        return records if isinstance(records, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def save_records(records):
    """保存历史对比记录"""
    with open(COMPARE_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def _get_retriever():
    return VectorStoreService().get_retriever()


def _get_chains():
    model = get_chat_model()

    # 不使用知识库：不提供任何参考资料
    plain_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", PLAIN_SYSTEM_TEMPLATE),
            ("user", "请回答用户提问：{input}"),
        ]
    )

    # 使用知识库：和聊天页一样，把检索结果作为参考资料
    rag_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", RAG_SYSTEM_TEMPLATE),
            ("user", "请回答用户提问：{input}"),
        ]
    )

    return (
        plain_prompt | model | StrOutputParser(),
        rag_prompt | model | StrOutputParser(),
    )


def run_compare(question: str):
    """对一个问题同时生成纯模型回答和 RAG 回答"""
    retriever = _get_retriever()
    plain_chain, rag_chain = _get_chains()

    plain_answer = plain_chain.invoke({"input": question})

    docs = retriever.invoke(question)
    context = format_docs(docs)
    rag_answer = rag_chain.invoke({"context": context, "input": question})

    sources = [
        {
            "source": doc.metadata.get("source", "unknown"),
            "content": doc.page_content.strip()[:300],
        }
        for doc in docs
    ]

    return {
        "question": question,
        "plain": plain_answer,
        "rag": rag_answer,
        "sources": sources,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "model": config.chat_model_name,
        "retrieval_k": config.retrieval_k,
    }
