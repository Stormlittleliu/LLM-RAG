"""项目配置。

所有路径都以项目根目录为基准，因此从任意工作目录启动都能找到数据文件。
"""
from pathlib import Path

from dotenv import load_dotenv

# src/kbrag/config.py 往上三级是项目根目录（config.py -> kbrag -> src -> 项目根）
PROJECT_ROOT = Path(__file__).resolve().parents[2]
# 运行时数据统一放在项目根目录的 data/ 下（向量库、去重记录、会话历史、对比记录）
DATA_DIR = PROJECT_ROOT / "data"

# 加载项目根目录 .env 文件中的环境变量(如 DASHSCOPE_API_KEY)
load_dotenv(str(PROJECT_ROOT / ".env"))

md5_path = str(DATA_DIR / "md5.text")
history_dir = str(DATA_DIR / "chat_history")
compare_history_path = str(DATA_DIR / "compare_history.json")

# Chroma
collection_name = "rag"
persist_directory = str(DATA_DIR / "chroma_db")

# splitter
chunk_size = 1000
chunk_overlap = 100
separators = ["\n\n", "\n", ".", "!", "?", "。", "！", "？", " ", ""]

max_split_char_number = 1000  # 文本分割阈值

# 检索返回的文档数量(top-k)
retrieval_k = 4

embedding_model_name = "text-embedding-v4"
chat_model_name = "qwen-plus"
