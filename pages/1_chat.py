"""
Chat Page - Main conversation interface
Supports multiple platforms: Alibaba, DeepSeek, Custom
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import config
from memory import MemoryManager, ConversationManager
from Rag.retriever import LegalRetriever
from langchain_core.prompts import ChatPromptTemplate

st.set_page_config(page_title="对话 - 法律助手", page_icon="💬")

# Check login
if not st.session_state.get("user_id"):
    st.warning("请先登录")
    st.stop()

user_id = st.session_state.user_id
memory = MemoryManager(user_id)
conv_manager = ConversationManager(user_id)

# Get user config
user = config.get_user(user_id)
user_config = {
    "api_key": st.session_state.get("api_key", ""),
    "model_provider": st.session_state.get("model_provider", "alibaba"),
    "current_model": st.session_state.get("current_model", "qwen-turbo"),
    "api_base": user.get("api_base", ""),
    "temperature": user.get("temperature", 0.7),
    "max_tokens": user.get("max_tokens", 2048)
}

# Initialize retriever
retriever = None
if user_config["api_key"]:
    retriever = LegalRetriever(user_id)
    retriever.set_api_key(user_config["api_key"])


def get_llm():
    """Get LLM instance based on configuration - 使用阿里百炼 ChatTongyi"""
    provider = user_config["model_provider"]
    model = user_config["current_model"]
    api_key = user_config["api_key"]
    api_base = user_config["api_base"]
    temperature = user_config["temperature"]
    max_tokens = user_config["max_tokens"]
    
    if not api_key:
        return None
    
    try:
        if provider == "alibaba":
            # 使用阿里百炼 ChatTongyi
            from langchain_community.chat_models.tongyi import ChatTongyi
            return ChatTongyi(
                model=model or "qwen-turbo",
                dashscope_api_key=api_key,
                temperature=temperature,
                max_tokens=max_tokens
            )
        
        elif provider == "deepseek":
            # DeepSeek 使用 OpenAI 兼容接口
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=model,
                api_key=api_key,
                base_url=api_base or "https://api.deepseek.com/v1",
                temperature=temperature,
                max_tokens=max_tokens
            )
        
        elif provider == "custom":
            # 自定义提供商使用 OpenAI 兼容接口
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=model,
                api_key=api_key,
                base_url=api_base,
                temperature=temperature,
                max_tokens=max_tokens
            )
        
        else:
            # 默认使用阿里百炼
            from langchain_community.chat_models.tongyi import ChatTongyi
            return ChatTongyi(
                model="qwen-turbo",
                dashscope_api_key=api_key,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
    except Exception as e:
        st.error(f"初始化模型失败: {str(e)}")
        return None


# Sidebar - Conversation list
with st.sidebar:
    st.markdown("### 💬 对话列表")
    
    if st.button("➕ 新建对话", use_container_width=True):
        conv_id = conv_manager.create_conversation()
        st.session_state.current_conv = conv_id
        st.rerun()
    
    st.markdown("---")
    
    conversations = conv_manager.get_conversations_list()
    for conv in conversations:
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(f"📝 {conv['title']}", key=f"conv_{conv['id']}", use_container_width=True):
                st.session_state.current_conv = conv["id"]
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{conv['id']}"):
                conv_manager.delete_conversation(conv["id"])
                if st.session_state.get("current_conv") == conv["id"]:
                    st.session_state.current_conv = None
                st.rerun()
    
    # Show current model info
    st.markdown("---")
    st.markdown("### 🤖 当前模型")
    provider_name = {
        "alibaba": "阿里百炼",
        "deepseek": "DeepSeek",
        "custom": "自定义"
    }.get(user_config["model_provider"], "阿里百炼")
    
    st.text(f"提供商: {provider_name}")
    st.text(f"模型: {user_config['current_model']}")
    
    if not user_config["api_key"]:
        st.warning("⚠️ 未配置API Key")

# Main interface
st.markdown("## 💬 法律咨询")

# Current conversation
if not st.session_state.get("current_conv"):
    st.info('👈 点击左侧"新建对话"开始')
    st.stop()

conv_id = st.session_state.current_conv
conv = conv_manager.get_conversation(conv_id)

if not conv:
    st.error("对话不存在")
    st.stop()

# Show conversation title
st.markdown(f"### {conv['title']}")

# Show history messages
for msg in conv.get("messages", []):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
user_input = st.chat_input("请输入您的问题...")

if user_input:
    # Show user message
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Save user message
    conv_manager.add_message(conv_id, "user", user_input)
    
    # Build context
    context = ""
    
    # RAG retrieval
    if retriever:
        try:
            docs = retriever.search(user_input, k=3)
            if docs:
                context = "\n\n".join([f"[来源{i+1}] {doc.page_content[:500]}" for i, doc in enumerate(docs)])
        except Exception as e:
            st.warning(f"检索失败: {e}")
    
    # Get memory
    memory_summary = memory.get_summary()
    
    # Build prompt template
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", """您是一位专业的法律顾问。请根据以下信息回答用户的问题：

用户记忆：
{memory}

相关法律条款：
{context}

请用中文回答，保持专业性和准确性。如果引用法律条款，请注明来源。"""),
        ("human", "{question}")
    ])
    
    # Generate response
    llm = get_llm()
    
    if llm:
        try:
            prompt = prompt_template.format(
                memory=memory_summary,
                context=context or "未找到相关法律条款",
                question=user_input
            )
            
            # Stream output
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                
                for chunk in llm.stream(prompt):
                    if hasattr(chunk, 'content'):
                        full_response += chunk.content
                    else:
                        full_response += str(chunk)
                    message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                answer = full_response
                
        except Exception as e:
            answer = f"抱歉，生成回复时出错: {str(e)}"
            with st.chat_message("assistant"):
                st.markdown(answer)
    else:
        answer = "请先设置API Key（在设置页面）"
        with st.chat_message("assistant"):
            st.markdown(answer)
    
    # Save assistant message
    conv_manager.add_message(conv_id, "assistant", answer)
    
    # Update conversation title (if first message)
    if len(conv.get("messages", [])) <= 2:
        title = user_input[:20] + "..." if len(user_input) > 20 else user_input
        conv_manager.update_title(conv_id, title)
    
    st.rerun()