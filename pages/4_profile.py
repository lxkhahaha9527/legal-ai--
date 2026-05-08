"""
Profile Page - Personal information and history
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import config
from memory import MemoryManager, ConversationManager

st.set_page_config(page_title="我的 - 法律助手", page_icon="👤")

# Check login
if not st.session_state.get("user_id"):
    st.warning("请先登录")
    st.stop()

user_id = st.session_state.user_id
user = config.get_user(user_id)
memory = MemoryManager(user_id)
conv_manager = ConversationManager(user_id)

# Provider name mapping
PROVIDER_NAMES = {
    "alibaba": "阿里百炼",
    "deepseek": "DeepSeek",
    "custom": "自定义"
}

st.markdown("## 👤 个人信息")

# Basic info
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📋 基本信息")
    st.markdown(f"**用户ID:** {user_id}")
    st.markdown(f"**用户名:** {user.get('username', '未设置')}")
    st.markdown(f"**创建时间:** {user.get('created_at', '未知')}")
    
    # Stats
    conversations = conv_manager.get_conversations_list()
    st.markdown(f"**对话数量:** {len(conversations)}")

with col2:
    st.markdown("### 🔑 API配置")
    api_keys = user.get("api_keys", {})
    
    if api_keys:
        for provider, key in api_keys.items():
            provider_name = PROVIDER_NAMES.get(provider, provider)
            masked_key = key[:8] + "..." + key[-4:] if len(key) > 12 else "***"
            st.markdown(f"**{provider_name}:** {masked_key}")
    else:
        st.info("未配置API Key")
    
    # Model preference
    model_provider = user.get("model_provider", "未设置")
    provider_name = PROVIDER_NAMES.get(model_provider, model_provider)
    preferred_model = user.get("preferred_model", "未设置")
    
    st.markdown(f"**当前提供商:** {provider_name}")
    st.markdown(f"**首选模型:** {preferred_model}")
    
    # Other config
    temperature = user.get("temperature", "未设置")
    max_tokens = user.get("max_tokens", "未设置")
    st.markdown(f"**Temperature:** {temperature}")
    st.markdown(f"**最大Token数:** {max_tokens}")

# Preferences
st.markdown("---")
st.markdown("### 📝 个人偏好")

preferences = memory.get_preferences()
if preferences:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**专业领域:**")
        specialty = preferences.get("specialty", [])
        if specialty:
            for s in specialty:
                st.markdown(f"- {s}")
        else:
            st.markdown("未设置")
    
    with col2:
        st.markdown("**回复风格:**")
        st.markdown(preferences.get("style", "未设置"))
        
        st.markdown("**通知:**")
        st.markdown("已启用" if preferences.get("notifications", True) else "已禁用")
else:
    st.info("未设置偏好")

# Memory Summary
st.markdown("---")
st.markdown("### 🧠 记忆摘要")

memory_summary = memory.get_summary()
st.text_area("", value=memory_summary, height=200, disabled=True)

# Conversation History
st.markdown("---")
st.markdown("### 💬 对话历史")

conversations = conv_manager.get_conversations_list()

if conversations:
    for conv in conversations:
        with st.expander(f"📝 {conv['title']} ({conv['created_at']})"):
            conv_data = conv_manager.get_conversation(conv["id"])
            if conv_data:
                for msg in conv_data.get("messages", []):
                    role_emoji = "👤" if msg["role"] == "user" else "🤖"
                    st.markdown(f"{role_emoji} **{msg['role']}:** {msg['content'][:100]}...")
                    st.markdown(f"*时间: {msg.get('timestamp', '未知')}*")
                    st.markdown("---")
else:
    st.info("暂无对话记录")

# Export Data
st.markdown("---")
st.markdown("### 📤 数据导出")

if st.button("导出所有对话"):
    import json
    import time
    
    all_conversations = []
    for conv in conversations:
        conv_data = conv_manager.get_conversation(conv["id"])
        if conv_data:
            all_conversations.append(conv_data)
    
    export_data = {
        "user_id": user_id,
        "username": user.get("username", ""),
        "export_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "model_config": {
            "provider": user.get("model_provider", ""),
            "model": user.get("preferred_model", ""),
            "temperature": user.get("temperature", 0.7),
            "max_tokens": user.get("max_tokens", 2048)
        },
        "conversations": all_conversations
    }
    
    st.download_button(
        label="下载JSON",
        data=json.dumps(export_data, ensure_ascii=False, indent=2),
        file_name=f"conversations_{user_id}_{time.strftime('%Y%m%d')}.json",
        mime="application/json"
    )