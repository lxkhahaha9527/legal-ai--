# ⚖️ 法律助手智能体

基于 LangChain + Streamlit 的智能法律咨询系统。

## ✨ 功能特性

- **💬 智能对话** - 基于RAG的法律问答，支持上下文理解
- **📁 文档管理** - 支持 .txt, .pdf, .doc, .docx 多格式导入
- **🔍 语义检索** - 基于向量数据库的法律条文检索
- **👥 多用户支持** - 独立的用户空间和数据隔离
- **🧠 长期记忆** - 记住用户偏好和设置
- **⚙️ 自定义模型** - 支持阿里百炼/DeepSeek及自定义API Key

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动应用

```bash
streamlit run app.py
```

### 3. 访问应用

打开浏览器访问: http://localhost:8501

## 📁 项目结构

```
D:\AI_agent\
├── app.py                  # 主应用入口
├── requirements.txt       # 依赖包
├── config.py              # 配置管理
├── README.md              # 项目说明
├── data/                 # 文档数据目录
│   └── legal_docs/       # 法律条文存储
├── memory/               # 记忆存储
│   ├── users/           # 用户记忆
│   └── conversations/   # 对话历史
├── Rag/                  # RAG模块
│   ├── __init__.py
│   ├── loader.py        # 文档加载器
│   └── retriever.py     # 检索器
└── pages/                # Streamlit页面
    ├── 1_chat.py        # 主对话页面
    ├── 2_documents.py   # 文档上传/管理
    ├── 3_settings.py    # 模型和API设置
    └── 4_profile.py     # 用户信息/历史
```

## 🔧 配置说明

### API Key设置
1. 在设置页面选择模型提供商
2. 输入您的API Key
3. 选择模型和温度参数

### 文档上传
1. 进入文档管理页面
2. 上传法律文档（支持多格式）
3. 点击"构建向量索引"

### 开始对话
1. 点击"新建对话"
2. 输入法律问题
3. 系统会自动检索相关法律条文并回答

## 🛠️ 技术栈

- **后端**: LangChain, Python
- **前端**: Streamlit
- **向量存储**: ChromaDB
- **文档处理**: PyPDF, python-docx
- **API clients**: 阿里百炼 (DashScope)
- **记忆存储**: JSON文件

## 📝 注意事项

1. API Key仅存储在本地，不会上传到服务器
2. 文档和对话数据按用户隔离存储
3. 向量索引需要API Key才能构建
4. 建议定期备份重要对话数据

## 🔒 隐私说明

- 所有数据存储在本地
- 用户数据相互隔离
- API Key本地加密存储
- 支持数据导出和清除