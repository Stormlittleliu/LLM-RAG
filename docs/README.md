# KnowledgeBase-RAG-LLM-System

**基于 Streamlit 的本地知识库上传与 RAG 问答学习项目**

[中文](README.md) | [English](README.en.md)

适合作为本地知识库问答与检索增强（RAG）的入门实践：

- 单一入口多页面：一个 Streamlit 服务包含知识库上传、RAG 问答、向量库管理、前后对比四个页面
- 在网页端上传 `txt` 文件，自动切分后写入 Chroma 向量库
- 在网页端以聊天形式提问，基于知识库内容进行检索增强回答（RAG）
- 支持「纯模型 vs RAG」同题对比，直观查看知识库带来的差异
- 支持会话历史查看、按用户隔离历史、流式输出
- 技术栈：Python / Streamlit / LangChain / Chroma / Embeddings / Qwen ChatModel

---

## ✨ 功能一览

### 1) 知识库上传（Upload）

- Streamlit 页面上传文件并显示基本格式
- 自动读取文本内容
- 根据配置进行分段（`RecursiveCharacterTextSplitter`）
- 写入 Chroma 向量库（本地持久化）
- 使用 **MD5 去重**：同一文件内容未变化时不重复入库
- 文件内容更新后重新上传，会自动替换该文件的旧分块，不会新旧内容并存

### 2) 智能客服（RAG Chat）

- Streamlit Chat UI，支持流式输出
- 显示历史消息（`session_state`）
- LangChain 链式调用：`Retrieval -> Prompt -> LLM -> Output`
- 消息历史文件存储（`FileChatMessageHistory`）
- 每个用户使用独立的会话 ID（浏览器会话自动生成，也可用 `?user=xxx` 指定），历史记录分文件保存、互不干扰
- 侧边栏可查看当前用户标识，或点击“新建会话”开启一段新对话
- 注意：用户标识仅用于隔离历史文件，项目没有登录/鉴权；如需多租户部署，请自行接入认证

### 3) RAG 前后对比（Compare）

- 同一个问题分别用「纯模型」和「使用知识库（RAG）」回答
- 同时展示检索到的参考资料（来源文件 + 片段）
- 对比记录保存在 `data/compare_history.json`，可在侧边栏清空

### 4) 向量库管理（Manage）

- 查看向量库总分块数、文档数、去重记录数和存储位置
- 按来源文件汇总展示分块数量、最近入库时间、操作人
- 可展开查看每个分块的原文、ID、入库时间与操作人
- 按文档删除：删除该来源的全部分块，并同步清理对应的 MD5 去重记录，之后可重新上传同一文件
- 清空向量库：清空全部分块和去重记录（不可撤销，需二次确认）
- 删除操作只影响向量库与去重记录，不会删除会话历史或对比记录

### 5) 效果预览

<!-- 智能客服示例图 -->
<div align="left">
  <img src="./images/chat_demo1.png" width="750" alt="智能客服聊天界面示例 1">
</div>

- 本地知识库预存了衣物尺码推荐表、材质维护、穿衣搭配等示例内容（示例文本见 `scripts/assets/`）
- 对标电商场景，可按个人需求替换为自己的业务文本

<div align="left">
  <img src="./images/chat_demo2.png" width="750" alt="智能客服聊天界面示例 2">
</div>

- 支持结合历史消息进行连续问答

---

## 🧩 项目结构

```text
KnowledgeBase-RAG-LLM-System/
├─ app.py                      # 单一入口：st.navigation 组装四个页面
├─ README.md                   # 双语短指针
├─ requirements.txt            # 项目依赖（核心版本精确锁定）
├─ .env                        # 本地密钥配置（需自行创建，勿提交）
├─ src/
│  ├─ kbrag/                   # 业务服务包（不依赖 Streamlit）
│  │  ├─ config.py             # 模型、路径、chunk 等参数配置
│  │  ├─ providers.py          # embedding / LLM 统一工厂
│  │  ├─ vector_store.py       # 向量库检索封装（持久化）
│  │  ├─ knowledge_base.py     # 知识库处理：读取、切分、写库、去重
│  │  ├─ history.py            # 会话历史存储
│  │  ├─ prompts.py            # Prompt 模板与上下文格式化
│  │  ├─ rag_service.py        # RAG 链组装
│  │  └─ compare_service.py    # 纯模型 vs RAG 对比服务
│  └─ ui_pages/                # Streamlit 页面层（只放 UI）
│     ├─ chat_page.py          # 智能客服
│     ├─ upload_page.py        # 知识库上传
│     ├─ manage_page.py        # 向量库管理
│     └─ compare_page.py       # RAG 前后对比
├─ docs/
│  ├─ README.md                # 中文完整文档（本文件）
│  ├─ README.en.md             # English full documentation
│  └─ images/                  # README 演示截图
├─ scripts/
│  ├─ smoke_test.py            # 端到端冒烟测试
│  └─ assets/                  # 示例知识文本（4 个 txt）
├─ data/                       # 运行时数据（gitignore，首次运行自动创建）
│  ├─ chroma_db/               # 本地向量库
│  ├─ chat_history/            # 按用户保存的会话历史
│  ├─ md5.text                 # 文件去重记录
│  └─ compare_history.json     # 前后对比记录
└─ logs/                       # 服务日志（gitignore）
```

设计说明：

- `src/kbrag/` 只放业务逻辑，不依赖 Streamlit；`src/ui_pages/` 只放页面 UI
- 模型统一从 `src/kbrag/providers.py` 获取，将来接入本地 embedding/LLM 只需改工厂
- 运行时数据全部集中在 `data/`，代码、文档、脚本、数据、日志分目录管理
- 从任意工作目录启动 `streamlit run <项目路径>/app.py` 都能正确找到数据文件

### 数据流

```text
上传:  txt 文件 -> 读取文本 -> MD5 去重 -> 文本切分 -> DashScope Embedding -> Chroma(data/chroma_db)
问答:  用户问题 -> Chroma 检索 top-k -> Prompt 拼接上下文 -> qwen-plus -> 流式回答 -> 历史文件
对比:  同一问题 -> 纯模型回答  vs  检索 + qwen-plus 回答 -> data/compare_history.json
```

---

## ✅ 环境准备

### 1) 环境要求

- Python 3.10（实测 3.10.21）
- 可访问阿里云 DashScope 服务的网络
- 有效的 `DASHSCOPE_API_KEY`

### 2) 安装依赖

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

建议在虚拟环境（conda / venv）中安装，清华镜像源可加速下载。`requirements.txt` 中核心依赖已按实测版本用 `==` 锁定，避免上游版本漂移导致不兼容。

### 3) 配置 API Key

在项目根目录创建 `.env` 文件：

```dotenv
DASHSCOPE_API_KEY=sk-你的密钥
```

`.env` 已被 `.gitignore` 忽略，请勿提交到仓库，也不要写进代码。

---

## 🚀 快速运行

```bash
streamlit run app.py
```

打开 `http://localhost:8501`，通过左侧导航切换四个页面：

- **智能客服**：输入问题后，先检索知识库，再结合检索内容由模型综合回答
- **知识库上传**：上传 `.txt` 文件后写入本地向量库
- **向量库管理**：查看已入库分块，按文档删除或清空向量库
- **RAG 前后对比**：同一问题对比纯模型与 RAG 的回答

想接着指定用户的历史对话，可在地址后加 `?user=xxx`，例如：

```text
http://localhost:8501/?user=demo
```

---

## 🧪 冒烟测试（可选）

```bash
python scripts/smoke_test.py
```

脚本会依次验证：

1. 导入 `scripts/assets/` 下的三个示例文档（逐块调用嵌入 API）
2. 用尺码问题做检索验证
3. 走一次完整的 RAG 问答

测试使用独立会话 `smoke_test`，不会污染真实用户历史。若示例文档此前已入库，导入步骤会显示 `[Repeat]`，属于 MD5 去重的正常行为。

---

## ⚙️ 配置说明

核心配置位于 `src/kbrag/config.py`：

- `PROJECT_ROOT`：项目根目录（自动推导）
- `DATA_DIR`：运行时数据目录，固定为 `data/`
- `chunk_size` / `chunk_overlap` / `separators`：文本切分参数
- `retrieval_k`：检索返回的文档数量（top-k）
- `embedding_model_name`：默认 `text-embedding-v4`
- `chat_model_name`：默认 `qwen-plus`

模型创建集中在 `src/kbrag/providers.py`；将来接入本地 embedding / LLM 时，在该文件增加分支即可。

---

## 📂 数据与日志

| 路径 | 内容 | 是否入库 |
| --- | --- | --- |
| `data/chroma_db/` | Chroma 向量库 | 否（gitignore） |
| `data/md5.text` | 文件 MD5 去重记录 | 否（gitignore） |
| `data/chat_history/` | 按用户标识分文件的会话历史 | 否（gitignore） |
| `data/compare_history.json` | 前后对比记录 | 否（gitignore） |
| `logs/` | 服务运行日志 | 否（gitignore） |

- 首次运行会自动创建所需目录与文件
- 已有项目升级到当前目录结构时，只需把原来的运行时数据整体移动到 `data/`，无需重新入库
- 清空知识库：停止服务后删除 `data/chroma_db/` 与 `data/md5.text`（会丢失全部已入库内容，操作前请备份）
- 清空会话历史 / 对比记录：删除 `data/chat_history/` 或 `data/compare_history.json`

---

## 🛠 常见问题

### Q1：上传文件后，聊天问答仍然像“没有检索到资料”？

可能原因：

- 上传与问答使用了不同的向量库目录（检查 `src/kbrag/config.py` 的 `DATA_DIR`）
- `collection_name` 配置不一致
- 文件内容与已入库内容完全相同，被 MD5 去重跳过（上传页会显示 `[Repeat]`）
- 文件内容更新后没有重新上传，旧分块仍在库中

### Q2：上传文件后，回答较慢或没有正常输出？

可能原因：

- 文本切分参数或检索参数不合适，可调整 `chunk_size`、`retrieval_k`
- 模型接口或网络请求响应较慢
- 本地向量库未正确初始化

### Q3：项目运行报路径或配置错误怎么办？

优先检查：

- `src/kbrag/config.py` 中的路径、模型配置是否正确
- `data/` 目录是否存在（首次运行会自动创建）
- 项目根目录 `.env` 中的 `DASHSCOPE_API_KEY` 是否已配置
- 是否在项目根目录执行 `streamlit run app.py`（也支持带绝对路径从其他目录启动）

### Q4：启动时出现 LangChain 弃用警告？

`RunnableWithMessageHistory is deprecated...` 属于框架提示，不影响当前功能运行。后续可迁移到 LangGraph 的持久化机制。

---

## 🧭 已测试环境

- 操作系统：Windows 10
- Python：3.10.21
- 关键依赖版本（详见 `requirements.txt`）：

| 依赖 | 版本 |
| --- | --- |
| streamlit | 1.40.1 |
| langchain | 1.4.2 |
| langchain-core | 1.6.4 |
| langchain-community | 0.4.2 |
| langchain-chroma | 1.1.0 |
| langchain-text-splitters | 1.1.2 |
| chromadb | 1.5.9 |
| numpy | 1.26.4 |
| dashscope | 1.27.6 |
| pydantic | 2.13.5 |
| python-dotenv | 1.2.3 |

---

## ✨ 优化方向（仅供参考）

- 增加深度 Rerank，提升检索结果质量（如 LangChain 提供的相关 rerank 模块）
- 优化 Streamlit 页面交互与展示
- 支持更多文件类型（PDF / Markdown / Word），增加对应解析器即可
- 单模型 -> 多模型混合输出
- Chroma -> FAISS：Chroma 轻量适合个人复现，FAISS 更适合大规模检索
- 扩展升级：企业级 RAG -> 功能插件 -> Agent -> AI 产品

---

## ⚠️ 使用限制

- 当前仅支持纯文本（`.txt`）上传
- 项目没有登录/鉴权，`?user=xxx` 只用于隔离历史文件，不能作为安全边界
- 示例知识文本仅用于学习演示

---

## 📄 License

本项目仅用于学习与交流，如需商用请自行补全安全、合规与授权相关内容。详见根目录 [LICENSE](../LICENSE)。

---

## 🙌 致谢

- Black Horse
- Streamlit
- LangChain
- Chroma / chromadb
- Aliyun Bailian / Qwen
