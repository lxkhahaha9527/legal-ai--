"""
RAG模块 - 向量检索器
支持多种嵌入模型：阿里百炼(DashScope)
"""
import os
import json
from pathlib import Path
from typing import List, Optional
import chromadb
from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from .loader import LegalDocLoader


class LegalRetriever:
    """法律文档检索器"""
    
    def __init__(
        self,
        user_id: str,
        docs_dir: str = None,
        collection_name: str = None
    ):
        self.user_id = user_id
        self.docs_dir = Path(docs_dir) if docs_dir else None
        self.collection_name = collection_name or f"legal_docs_{user_id}"
        self.embeddings = None
        self.vectorstore = None
        self.embedding_provider = "alibaba"  # 默认使用阿里百炼
    
    def set_api_key(self, api_key: str = None, provider: str = "alibaba") -> None:
        """设置API Key和嵌入模型 - 默认使用阿里百炼 DashScope"""
        self.embedding_provider = provider
        
        # 优先使用阿里百炼 DashScope 嵌入模型
        try:
            from langchain_community.embeddings import DashScopeEmbeddings
            self.embeddings = DashScopeEmbeddings(
                model="text-embedding-v2",
                dashscope_api_key=api_key
            )
        except ImportError:
            raise
        except Exception as e:
            raise RuntimeError(f"加载 DashScope 嵌入模型失败: {e}")
            raise
    
    def build_index(
        self,
        documents: List[Document] = None,
        docs_dir: str = None,
        regenerate: bool = False
    ) -> bool:
        """构建向量索引"""
        if self.embeddings is None:
            return False
            
        if documents is None:
            docs_dir = docs_dir or self.docs_dir
            if not docs_dir:
                return False
            
            loader = LegalDocLoader(docs_dir)
            documents = loader.load_directory(docs_dir)
        
        if not documents:
            return False
        
        # 创建向量存储
        persist_dir = self._get_persist_dir()
        persist_dir.mkdir(parents=True, exist_ok=True)
        
        if regenerate:
            self._delete_collection()
        
        try:
            self.vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                collection_name=self.collection_name,
                persist_directory=str(persist_dir)
            )
            
            # 持久化到磁盘
            self.vectorstore.persist()
            return True
        except Exception as e:
            raise RuntimeError(f"索引构建失败: {e}")
    
    def search(
        self,
        query: str,
        k: int = 4,
        filter: dict = None
    ) -> List[Document]:
        """相似度检索"""
        if not self.vectorstore:
            self._load_index()
        
        if not self.vectorstore:
            return []
        
        results = self.vectorstore.similarity_search(
            query,
            k=k,
            filter=filter
        )
        
        return results
    
    def search_with_score(
        self,
        query: str,
        k: int = 4,
        filter: dict = None
    ) -> List[tuple]:
        """带相似度分数的检索"""
        if not self.vectorstore:
            self._load_index()
        
        if not self.vectorstore:
            return []
        
        results = self.vectorstore.similarity_search_with_score(
            query,
            k=k,
            filter=filter
        )
        
        return results

    def _get_persist_dir(self) -> Path:
        """获取向量存储持久化目录（兼容Streamlit Cloud）"""
        import os
        # Streamlit Cloud使用/tmp作为可写目录
        if os.environ.get("STREAMLIT_SHARING") or not os.access(".", os.W_OK):
            base = Path("/tmp") / "legal_assistant_vectorstore"
        else:
            base = Path(__file__).parent.parent / "data" / "vectorstore"
        return base / self.user_id
    
    def _load_index(self) -> bool:
        """加载已有索引"""
        persist_dir = self._get_persist_dir()
        
        if not persist_dir.exists():
            return False
        
        if self.embeddings is None:
            return False
        
        try:
            self.vectorstore = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=str(persist_dir)
            )
            return True
        except Exception as e:
            return False
    
    def _delete_collection(self) -> None:
        """删除向量集合"""
        try:
            client = chromadb.PersistentClient(path=str(self._get_persist_dir().parent))
            client.delete_collection(name=self.collection_name)
        except:
            pass
        
        persist_dir = self._get_persist_dir()
        if persist_dir.exists():
            import shutil
            shutil.rmtree(persist_dir)
    
    def get_document_count(self) -> int:
        """获取索引文档数量"""
        # 确保 embedding 已初始化
        if not self.embeddings:
            return 0
        
        if not self.vectorstore:
            self._load_index()
        
        if self.vectorstore:
            return self.vectorstore._collection.count()
        return 0
