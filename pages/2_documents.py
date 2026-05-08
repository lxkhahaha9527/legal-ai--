"""
Document Management Page - Upload and manage legal documents
"""
import streamlit as st
import sys
from pathlib import Path
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import config
from Rag.loader import LegalDocLoader
from Rag.retriever import LegalRetriever

st.set_page_config(page_title="文档管理 - 法律助手", page_icon="📁")

# Check login
if not st.session_state.get("user_id"):
    st.warning("请先登录")
    st.stop()

user_id = st.session_state.user_id

# User documents directory (兼容本地和 Streamlit Cloud)
BASE_DIR = Path(__file__).parent.parent
user_docs_dir = BASE_DIR / "data" / "legal_docs" / user_id
user_docs_dir.mkdir(parents=True, exist_ok=True)

st.markdown("## 📁 法律文档管理")

# Document upload
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📤 上传文档")
    uploaded_files = st.file_uploader(
        "选择文件",
        type=['txt', 'pdf', 'doc', 'docx'],
        accept_multiple_files=True,
        help="支持 .txt, .pdf, .doc, .docx 格式"
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_path = user_docs_dir / uploaded_file.name
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getvalue())
        
        st.success(f"成功上传 {len(uploaded_files)} 个文件")
        
        # Build index
        if st.session_state.get("api_key"):
            if st.button("🔍 构建向量索引"):
                with st.spinner("正在构建索引..."):
                    try:
                        retriever = LegalRetriever(user_id, str(user_docs_dir))
                        # 获取用户配置的 provider，默认使用阿里百炼
                        user_config = config.get_user_model_config(user_id)
                        provider = user_config.get("provider", "alibaba")
                        api_key = user_config.get("api_key", st.session_state.get("api_key", ""))
                        
                        if not api_key:
                            st.error("❌ 未配置 API Key，请在设置页面配置")
                            st.stop()
                        
                        retriever.set_api_key(api_key)
                        
                        loader = LegalDocLoader(str(user_docs_dir))
                        docs = loader.load_directory(str(user_docs_dir))
                        
                        if docs:
                            retriever.build_index(documents=docs, regenerate=True)
                            st.success(f"🎉 索引构建完成！共 {len(docs)} 个文档片段")
                        else:
                            st.warning("⚠️ 没有找到可索引的文档")
                    except Exception as e:
                        st.error(f"❌ 索引构建失败: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
        else:
            st.warning("请先设置API Key")

with col2:
    st.markdown("### 📋 文档列表")
    
    files = list(user_docs_dir.glob("*"))
    supported_exts = ['.txt', '.pdf', '.doc', '.docx']
    legal_files = [f for f in files if f.suffix.lower() in supported_exts]
    
    if legal_files:
        for file in legal_files:
            col_name, col_size, col_action = st.columns([3, 1, 1])
            with col_name:
                st.text(file.name)
            with col_size:
                size = file.stat().st_size
                if size < 1024:
                    st.text(f"{size}B")
                elif size < 1024*1024:
                    st.text(f"{size/1024:.1f}KB")
                else:
                    st.text(f"{size/(1024*1024):.1f}MB")
            with col_action:
                if st.button("🗑️", key=f"del_doc_{file.name}"):
                    file.unlink()
                    st.rerun()
    else:
        st.info("暂无文档")

# Index status
st.markdown("---")
st.markdown("### 📊 索引状态")

if st.session_state.get("api_key"):
    try:
        retriever = LegalRetriever(user_id, str(user_docs_dir))
        retriever.set_api_key(st.session_state.api_key)
        count = retriever.get_document_count()
        if count > 0:
            st.success(f"✅ 当前索引文档数: {count}")
        else:
            st.info("ℹ️ 尚未构建索引，请上传文档后点击「构建向量索引」")
    except Exception as e:
        st.info(f"ℹ️ 索引状态: 未初始化")
else:
    st.warning("⚠️ 请先设置API Key以查看索引状态")