"""单一入口：streamlit run app.py

通过 st.navigation 把四个页面组装成一个多页面应用。
"""
import sys
from pathlib import Path

# 保证从任意工作目录运行 streamlit run <绝对路径>/app.py 都能 import 到 src/ 下的 kbrag/ui_pages
PROJECT_ROOT = Path(__file__).resolve().parent
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import streamlit as st

from ui_pages.chat_page import chat_page
from ui_pages.compare_page import compare_page
from ui_pages.manage_page import manage_page
from ui_pages.upload_page import upload_page

st.set_page_config(page_title="本地知识库 RAG 系统", page_icon="📚", layout="wide")

pg = st.navigation(
    [
        st.Page(chat_page, title="智能客服", icon="💬", default=True),
        st.Page(upload_page, title="知识库上传", icon="📤"),
        st.Page(manage_page, title="向量库管理", icon="🗂️"),
        st.Page(compare_page, title="RAG 前后对比", icon="⚖️"),
    ]
)
pg.run()
