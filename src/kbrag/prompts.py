"""Prompt 模板与上下文格式化，聊天页和对比页共用。"""
from langchain_core.documents import Document

# 聊天页：结合参考资料回答
CHAT_SYSTEM_TEMPLATE = (
    "以我提供的已知参考资料为主，简洁和专业的回答用户问题。参考资料:{context}。"
)
# 聊天页：说明接下来是历史消息
HISTORY_SYSTEM_TEMPLATE = "并且我提供用户的对话历史记录，如下："
# 对比页：纯模型回答（不使用知识库）
PLAIN_SYSTEM_TEMPLATE = "你是一个乐于助人的助手，请简洁和专业的回答用户问题。"
# 对比页：RAG 回答（使用知识库）
RAG_SYSTEM_TEMPLATE = (
    "以我提供的已知参考资料为主，简洁和专业的回答用户问题。参考资料:{context}。"
)


def format_docs(docs: list[Document]) -> str:
    """把检索到的文档拼接成上下文；没有检索结果时给出明确提示。"""
    if not docs:
        return "无相关参考资料"
    return "\n\n".join(doc.page_content for doc in docs)
