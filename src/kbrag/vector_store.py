"""向量库封装：统一创建 Chroma 实例并提供检索器。"""
from langchain_chroma import Chroma

from kbrag import config
from kbrag.providers import get_embedding


class VectorStoreService(object):
    def __init__(self, embedding=None):
        """
        :param embedding: 嵌入模型；不传时使用模型工厂的默认实现
        """
        self.embedding = embedding if embedding is not None else get_embedding()
        self.vector_store = Chroma(
            collection_name=config.collection_name,
            embedding_function=self.embedding,
            persist_directory=config.persist_directory,
        )

    def get_retriever(self):
        """返回向量检索器，方便加入 chain"""
        return self.vector_store.as_retriever(
            search_kwargs={"k": config.retrieval_k}
        )
