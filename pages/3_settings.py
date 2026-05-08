"""
Settings Page - Model and API Configuration
Supports: Alibaba Bailian, DeepSeek, Custom
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import config
from memory import MemoryManager

st.set_page_config(page_title="设置 - 法律助手", page_icon="⚙️")

# Check login
if not st.session_state.get("user_id"):
    st.warning("请先登录")
    st.stop()

user_id = st.session_state.user_id
memory = MemoryManager(user_id)

# Model configuration - 默认使用阿里百炼，移除 OpenAI/Anthropic
PROVIDERS = {
    "alibaba": {
        "name": "阿里百炼",
        "models": [
            "qwen-turbo",
            "qwen-plus",
            "qwen-max",
            "qwen-max-longcontext",
            "qwen-coder-plus",
            "qwen3-max"
        ],
        "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "key_hint": "sk-..."
    },
    "deepseek": {
        "name": "DeepSeek",
        "models": ["deepseek-chat", "deepseek-coder", "deepseek-reasoner"],
        "api_base": "https://api.deepseek.com/v1",
        "key_hint": "sk-..."
    },
    "custom": {
        "name": "自定义",
        "models": [],
        "api_base": "",
        "key_hint": "your-api-key"
    }
}

st.markdown("## ⚙️ 系统设置")

# Provider selection outside form to update model list dynamically
st.markdown("### 🔑 API配置")

provider_list = list(PROVIDERS.keys())
current_provider = st.session_state.get("model_provider", "alibaba")
try:
    current_index = provider_list.index(current_provider)
except ValueError:
    current_index = 0

# Provider selection
provider = st.selectbox(
    "选择模型提供商",
    options=provider_list,
    format_func=lambda x: PROVIDERS[x]["name"],
    index=current_index,
    key="provider_select"
)

# Update session state when provider changes
if provider != st.session_state.get("model_provider"):
    st.session_state.model_provider = provider
    # Reset model to first available for new provider
    st.session_state.current_model = PROVIDERS[provider]["models"][0] if PROVIDERS[provider]["models"] else ""
    st.rerun()

provider_info = PROVIDERS[provider]

with st.form("api_settings"):
    # API Key input
    api_key = st.text_input(
        f"API Key ({provider_info['key_hint']})",
        value=st.session_state.get("api_key", ""),
        type="password",
        placeholder=f"请输入{provider_info['name']} API Key",
        help="您的API Key仅存储在本地"
    )
    
    # API Base
    if provider == "custom":
        api_base = st.text_input(
            "API Base URL",
            value=provider_info["api_base"],
            placeholder="https://api.example.com/v1"
        )
    else:
        api_base = provider_info["api_base"]
        st.text(f"API Base: {api_base}")
    
    # Model selection - dynamically based on provider
    if provider == "custom":
        model = st.text_input("自定义模型名称", placeholder="例如: gpt-3.5-turbo")
    else:
        models = provider_info["models"]
        current_model = st.session_state.get("current_model", models[0] if models else "")
        try:
            model_index = models.index(current_model) if current_model in models else 0
        except ValueError:
            model_index = 0
        
        model = st.selectbox(
            "选择模型",
            options=models,
            index=model_index,
            key="model_select"
        )
    
    # Temperature
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1,
        help="越低越确定，越高越随机"
    )
    
    # Max Tokens
    max_tokens = st.number_input(
        "最大Token数",
        min_value=256,
        max_value=8192,
        value=2048,
        step=256,
        help="生成文本的最大长度"
    )
    
    submit = st.form_submit_button("💾 保存设置")
    
    if submit:
        st.session_state.api_key = api_key
        st.session_state.model_provider = provider
        st.session_state.current_model = model
        
        user = config.get_user(user_id)
        api_keys = user.get("api_keys", {})
        api_keys[provider] = api_key
        
        config.update_user(user_id, {
            "api_keys": api_keys,
            "preferred_model": model,
            "model_provider": provider,
            "api_base": api_base,
            "temperature": temperature,
            "max_tokens": max_tokens
        })
        
        memory.update_preferences({
            "model_provider": provider,
            "model": model,
            "api_base": api_base,
            "temperature": temperature,
            "max_tokens": max_tokens
        })
        
        st.success("✅ 设置已保存！")
        
        st.markdown("---")
        st.markdown("### 📋 当前配置")
        st.json({
            "提供商": PROVIDERS[provider]["name"],
            "模型": model,
            "API Base": api_base,
            "Temperature": temperature,
            "最大Token数": max_tokens
        })

# Model Description
st.markdown("---")
st.markdown("### 📖 模型说明")

with st.expander("查看平台详情"):
    st.markdown("""
    #### 阿里百炼
    - **qwen-turbo**: 快速响应，低成本
    - **qwen-plus**: 性能均衡
    - **qwen-max**: 能力最强，复杂任务
    - **qwen-max-longcontext**: 长文本支持（1M tokens）
    - **qwen-coder-plus**: 代码相关任务
    - **qwen3-max**: 最新旗舰模型，综合能力最强
    
    #### DeepSeek
    - **deepseek-chat**: 通用对话模型
    - **deepseek-coder**: 代码生成与理解
    - **deepseek-reasoner**: 增强推理能力
    """)

# User Preferences
st.markdown("---")
st.markdown("### 📝 个人偏好")

with st.form("preferences"):
    specialty = st.multiselect(
        "关注领域",
        options=["民法", "刑法", "商法", "劳动法", 
                "知识产权", "合同法", "房地产", 
                "婚姻家庭", "行政法", "诉讼法"],
        default=memory.get_preferences().get("specialty", [])
    )
    
    style = st.selectbox(
        "回复风格",
        options=["详细解释", "简洁明了", "案例分析", "法条引用", "通俗易懂"],
        index=0
    )
    
    notifications = st.checkbox("启用通知", 
                               value=memory.get_preferences().get("notifications", True))
    
    submit_pref = st.form_submit_button("💾 保存偏好")
    
    if submit_pref:
        memory.update_preferences({
            "specialty": specialty,
            "style": style,
            "notifications": notifications
        })
        st.success("✅ 偏好已保存！")

# Danger Zone
st.markdown("---")
st.markdown("### ⚠️ 危险区域")

if st.button("🗑️ 清除所有数据", type="secondary"):
    confirm = st.checkbox("我确认要清除所有数据，此操作不可撤销！")
    if confirm:
        import shutil
        BASE_DIR = Path(__file__).parent.parent
        
        user_dir = BASE_DIR / "memory" / "users" / user_id
        if user_dir.exists():
            shutil.rmtree(user_dir)
        
        conv_dir = BASE_DIR / "memory" / "conversations" / user_id
        if conv_dir.exists():
            shutil.rmtree(conv_dir)
        
        docs_dir = BASE_DIR / "data" / "legal_docs" / user_id
        if docs_dir.exists():
            shutil.rmtree(docs_dir)
        
        st.success("数据已清除")
        st.rerun()