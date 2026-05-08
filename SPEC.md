# 法律助手智能体 - 项目规范

## 📋 项目需求

### 核心功能
1. **长期记忆** - 记住用户偏好和设置
2. **多用户支持** - 区分不同用户身份
3. **对话管理** - 新建对话、查看历史对话
4. **RAG检索** - 基于法律条文进行语义检索
5. **多格式文档支持** - .txt, .pdf, .doc, .docx
6. **自定义模型** - 用户可选模型 + 输入API Key
7. **前端** - Streamlit

### 技术栈
- **后端**: Langchain + Python
- **前端**: Streamlit
- **向量存储**: Chroma / FAISS
- **文档加载**: langchain.document_loaders
- **记忆存储**: JSON文件 (长期记忆)

### 目录结构
```
D:\AI_agent\
├── app.py                  # 主应用入口
├── requirements.txt       # 依赖包
├── config.py              # 配置管理
├── data/                 # 文档数据目录
│   └── legal_docs/       # 法律条文存储
├── memory/               # 记忆存储
│   ├── users.json       # 用户信息
│   └── conversations/   # 对话历史
├── Rag/
│   ├── __init__.py
│   ├── loader.py        # 文档加载器
│   └── retriever.py     # 检索器
└── pages/
    ├── 1_对话.py        # 主对话页面
    ├── 2_文档管理.py    # 文档上传/管理
    ├── 3_设置.py        # 模型和API设置
    └── 4_我的.py       # 用户信息/历史
```

## 🎯 功能模块

### 1. 用户系统
- 用户注册/登录
- 用户偏好存储
- API Key管理

### 2. 对话系统
- 新建对话
- 历史对话列表
- 对话历史存储

### 3. RAG系统
- 文档上传 (多格式)
- 向量索引构建
- 语义检索

### 4. 模型系统
- 模型选择 (OpenAI/Anthropic/本地模型)
- API Key输入
- 模型配置