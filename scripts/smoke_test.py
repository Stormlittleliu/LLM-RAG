# -*- coding: utf-8 -*-
"""端到端冒烟测试:导入示例知识库 -> 检索验证 -> RAG 问答验证。

用法: python scripts/smoke_test.py   (需先设置环境变量 DASHSCOPE_API_KEY)
验证通过后即可用 streamlit 启动网页端。此文件可删除,不影响项目本身。
"""
import sys
from pathlib import Path

# 项目模块位于 src/ 下，这里把 src/ 加入 sys.path；示例素材位于 scripts/assets/
ROOT = Path(__file__).resolve().parent.parent
SRC_ROOT = ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))
ASSET_DIR = ROOT / "scripts" / "assets"

# Windows 控制台默认 GBK，模型回答里若含 emoji 会触发 UnicodeEncodeError
try:
    sys.stdout.reconfigure(errors="replace")
except (AttributeError, OSError):
    pass

from kbrag.history import get_history
from kbrag.knowledge_base import KnowledgeBaseService
from kbrag.rag_service import RagService
from kbrag.vector_store import VectorStoreService

ASSETS = ["尺码推荐.txt", "洗涤养护.txt", "颜色推荐.txt"]
TEST_SESSION_ID = "smoke_test"


def step1_ingest():
    print("[1/3] 导入示例知识库(会逐块调用嵌入 API)...")
    service = KnowledgeBaseService()
    for name in ASSETS:
        path = ASSET_DIR / name
        with open(path, encoding="utf-8") as f:
            text = f.read()
        print(f"  {name}: {len(text)} 字符 -> {service.upload_by_str(text, name)}")


def step2_retrieve():
    print("[2/3] 检索验证: '我的身高180，体重165斤，穿什么尺码'")
    retriever = VectorStoreService().get_retriever()
    docs = retriever.invoke("我的身高180，体重165斤，穿什么尺码")
    for i, doc in enumerate(docs):
        print(f"  命中{i + 1}: {doc.page_content.strip()[:100]}")
        print(f"  元数据: {doc.metadata}")


def step3_rag():
    print("[3/3] RAG 问答验证(检索 -> Prompt -> qwen-plus)...")
    # 冒烟测试使用独立会话，避免污染真实用户历史；每次从空历史开始
    get_history(TEST_SESSION_ID).clear()
    session_config = {"configurable": {"session_id": TEST_SESSION_ID}}
    rag = RagService()
    res = rag.chain.invoke(
        {"input": "我的身高180，体重165斤，穿什么尺码？"},
        session_config,
    )
    print("  回答:", res)


if __name__ == "__main__":
    step1_ingest()
    step2_retrieve()
    step3_rag()
    print("全部通过")
