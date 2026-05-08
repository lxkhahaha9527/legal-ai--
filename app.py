"""
Legal Assistant - Main Application Entry
"""
import streamlit as st
import sys
from pathlib import Path

# Add project path
sys.path.insert(0, str(Path(__file__).parent))

from config import config

import os

# ========== 自动创建必要目录 ==========
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def ensure_dirs():
 """确保所有必要目录存在"""
 dirs = [
 os.path.join(BASE_DIR, "memory"),
 os.path.join(BASE_DIR, "memory", "users"),
 os.path.join(BASE_DIR, "memory", "conversations"),
 os.path.join(BASE_DIR, "data"),
 ]
 for d in dirs:
     os.makedirs(d, exist_ok=True)

ensure_dirs()
# =====================================


# Page config
st.set_page_config(
    page_title="法律助手",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f4788;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 3rem;
    }
    .login-box {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        border-radius: 10px;
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f4788;
        color: white;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #2a5aa0;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state"""
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "username" not in st.session_state:
        st.session_state.username = None
    if "current_conv" not in st.session_state:
        st.session_state.current_conv = None
    if "api_key" not in st.session_state:
        st.session_state.api_key = None
    if "model_provider" not in st.session_state:
        st.session_state.model_provider = "alibaba"


def login_page():
    """Login page"""
    st.markdown('<div class="main-header">⚖️ 法律助手</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">您的智能法律顾问</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["登录", "注册"])
        
        with tab1:
            with st.form("login_form"):
                user_id = st.text_input("用户ID", placeholder="请输入用户ID")
                password = st.text_input("密码", type="password", placeholder="请输入密码")
                submit = st.form_submit_button("登录")
                
                if submit:
                    if config.verify_user(user_id, password):
                        st.session_state.user_id = user_id
                        user = config.get_user(user_id)
                        st.session_state.username = user.get("username", user_id)
                        
                        # 读取用户配置的 provider 和对应的 API Key
                        provider = user.get("model_provider", "alibaba")
                        st.session_state.model_provider = provider
                        api_keys = user.get("api_keys", {})
                        st.session_state.api_key = api_keys.get(provider, api_keys.get("alibaba", ""))
                        st.session_state.current_model = user.get("preferred_model", "qwen-turbo")
                        
                        st.success("登录成功！")
                        st.rerun()
                    else:
                        st.error("用户ID或密码错误")
        
        with tab2:
            with st.form("register_form"):
                new_user_id = st.text_input("用户ID", placeholder="设置用户ID")
                new_username = st.text_input("用户名", placeholder="设置用户名")
                new_password = st.text_input("密码", type="password", placeholder="设置密码")
                confirm_password = st.text_input("确认密码", type="password", placeholder="再次输入密码")
                submit = st.form_submit_button("注册")
                
                if submit:
                    if not all([new_user_id, new_username, new_password]):
                        st.error("请填写所有字段")
                    elif new_password != confirm_password:
                        st.error("两次输入的密码不一致")
                    elif config.add_user(new_user_id, new_username, new_password):
                        st.success("注册成功！请登录")
                    else:
                        st.error("用户ID已存在")
        
        st.markdown('</div>', unsafe_allow_html=True)


def sidebar():
    """Sidebar"""
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.username}")
        st.markdown("---")
        
        # Navigation
        st.markdown("### 📋 导航")
        
        if st.button("💬 开始对话", use_container_width=True):
            st.switch_page("pages/1_chat.py")
        
        if st.button("📁 文档管理", use_container_width=True):
            st.switch_page("pages/2_documents.py")
        
        if st.button("⚙️ 设置", use_container_width=True):
            st.switch_page("pages/3_settings.py")
        
        if st.button("👤 我的", use_container_width=True):
            st.switch_page("pages/4_profile.py")
        
        st.markdown("---")
        
        # Logout
        if st.button("🚪 退出登录", use_container_width=True):
            for key in ["user_id", "username", "current_conv", "api_key", "model_provider"]:
                st.session_state[key] = None
            st.rerun()


def main():
    """Main function"""
    init_session_state()
    
    if not st.session_state.user_id:
        login_page()
    else:
        sidebar()
        
        # Welcome page
        st.markdown('<div class="main-header">⚖️ 法律助手</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">欢迎使用智能法律顾问系统</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### 💬 智能对话
            - 基于RAG的法律问答
            - 多轮对话上下文理解
            - 引用法律条文来源
            """)
        
        with col2:
            st.markdown("""
            ### 📁 文档管理
            - 支持多种格式导入
            - 自动构建向量索引
            - 语义检索法律条文
            """)
        
        with col3:
            st.markdown("""
            ### ⚙️ 个性化设置
            - 自定义AI模型
            - 管理API密钥
            - 用户偏好记忆
            """)
        
        st.markdown("---")
        st.info("👈 请从左侧导航栏选择功能开始使用")


if __name__ == "__main__":
    main()