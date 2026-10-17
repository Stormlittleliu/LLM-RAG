"""模型工厂：集中创建 embedding 和聊天模型。

业务代码不直接实例化具体模型，换模型/换供应商时只改这里。
本次仍默认使用 DashScope；将来接入本地模型（如 bge、Ollama）时，
在下面的函数里按 config 增加分支即可，调用方无需改动。
"""
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings

from kbrag import config

_embedding = None
_embedding_model_name = None
_chat_model = None
_chat_model_name = None


def get_embedding():
    """获取 embedding 模型实例；配置中的模型名变化时自动重建。"""
    global _embedding, _embedding_model_name
    if _embedding is None or _embedding_model_name != config.embedding_model_name:
        # 扩展点：例如 if config.embedding_provider == "local": 返回本地 embedding
        _embedding = DashScopeEmbeddings(model=config.embedding_model_name)
        _embedding_model_name = config.embedding_model_name
    return _embedding


def get_chat_model():
    """获取聊天模型实例；配置中的模型名变化时自动重建。"""
    global _chat_model, _chat_model_name
    if _chat_model is None or _chat_model_name != config.chat_model_name:
        # 扩展点：例如 if config.chat_provider == "ollama": 返回 ChatOllama
        _chat_model = ChatTongyi(model=config.chat_model_name)
        _chat_model_name = config.chat_model_name
    return _chat_model
