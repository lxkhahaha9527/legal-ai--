"""
记忆模块 - 长期记忆管理
"""
import json
import time
import os
from pathlib import Path
from typing import Dict, List, Optional


# 获取项目根目录（兼容本地和 Streamlit Cloud）
# memory/__init__.py 所在目录的上级即为项目根目录
BASE_DIR = Path(__file__).parent.parent
MEMORY_DIR = BASE_DIR / "memory"
USERS_DIR = MEMORY_DIR / "users"
CONVERSATIONS_DIR = MEMORY_DIR / "conversations"

# 确保目录存在
for dir_path in [MEMORY_DIR, USERS_DIR, CONVERSATIONS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)


class MemoryManager:
    """长期记忆管理器"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        # 使用相对路径，兼容 Windows 本地和 Linux/Streamlit Cloud
        self.memory_dir = USERS_DIR / user_id
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        self.memory_file = self.memory_dir / "memory.json"
        self.preferences_file = self.memory_dir / "preferences.json"
        self.facts_file = self.memory_dir / "facts.json"
    
    def _load(self, file_path: Path) -> dict:
        """加载JSON文件"""
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save(self, file_path: Path, data: dict) -> None:
        """保存JSON文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 偏好记忆
    def get_preferences(self) -> dict:
        """获取用户偏好"""
        return self._load(self.preferences_file)
    
    def update_preferences(self, preferences: dict) -> None:
        """更新用户偏好"""
        current = self.get_preferences()
        current.update(preferences)
        current["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        self._save(self.preferences_file, current)
    
    # 事实记忆
    def get_facts(self) -> List[dict]:
        """获取用户相关事实"""
        return self._load(self.facts_file).get("facts", [])
    
    def add_fact(self, fact: str, category: str = "general") -> None:
        """添加事实"""
        data = self._load(self.facts_file)
        facts = data.get("facts", [])
        facts.append({
            "content": fact,
            "category": category,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        data["facts"] = facts
        self._save(self.facts_file, data)
    
    # 对话记忆
    def get_conversation_memory(self) -> dict:
        """获取对话记忆"""
        return self._load(self.memory_file)
    
    def update_conversation_memory(self, key: str, value: any) -> None:
        """更新对话记忆"""
        memory = self.get_conversation_memory()
        memory[key] = value
        memory["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        self._save(self.memory_file, memory)
    
    def get_summary(self) -> str:
        """获取记忆摘要"""
        prefs = self.get_preferences()
        facts = self.get_facts()
        
        summary = f"用户 {self.user_id} 的记忆摘要:\n"
        
        if prefs:
            summary += f"\n偏好设置: {json.dumps(prefs, ensure_ascii=False)}\n"
        
        if facts:
            summary += "\n已知事实:\n"
            for fact in facts[-5:]:  # 最近5条
                summary += f"- [{fact['category']}] {fact['content']}\n"
        
        return summary


class ConversationManager:
    """对话管理器"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        # 使用相对路径，兼容 Windows 本地和 Linux/Streamlit Cloud
        self.conv_dir = CONVERSATIONS_DIR / user_id
        self.conv_dir.mkdir(parents=True, exist_ok=True)
    
    def create_conversation(self, title: str = "新对话") -> str:
        """创建新对话"""
        conv_id = f"conv_{int(time.time())}"
        conv_file = self.conv_dir / f"{conv_id}.json"
        
        data = {
            "id": conv_id,
            "title": title,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "messages": []
        }
        
        with open(conv_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return conv_id
    
    def get_conversation(self, conv_id: str) -> Optional[dict]:
        """获取对话"""
        conv_file = self.conv_dir / f"{conv_id}.json"
        if conv_file.exists():
            with open(conv_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def add_message(self, conv_id: str, role: str, content: str) -> None:
        """添加消息"""
        conv = self.get_conversation(conv_id)
        if conv:
            conv["messages"].append({
                "role": role,
                "content": content,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            })
            
            conv_file = self.conv_dir / f"{conv_id}.json"
            with open(conv_file, 'w', encoding='utf-8') as f:
                json.dump(conv, f, ensure_ascii=False, indent=2)
    
    def get_conversations_list(self) -> List[dict]:
        """获取对话列表"""
        conversations = []
        for conv_file in self.conv_dir.glob("*.json"):
            with open(conv_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                conversations.append({
                    "id": data["id"],
                    "title": data["title"],
                    "created_at": data["created_at"],
                    "message_count": len(data.get("messages", []))
                })
        
        # 按时间排序
        conversations.sort(key=lambda x: x["created_at"], reverse=True)
        return conversations
    
    def delete_conversation(self, conv_id: str) -> bool:
        """删除对话"""
        conv_file = self.conv_dir / f"{conv_id}.json"
        if conv_file.exists():
            conv_file.unlink()
            return True
        return False
    
    def update_title(self, conv_id: str, title: str) -> None:
        """更新对话标题"""
        conv = self.get_conversation(conv_id)
        if conv:
            conv["title"] = title
            conv_file = self.conv_dir / f"{conv_id}.json"
            with open(conv_file, 'w', encoding='utf-8') as f:
                json.dump(conv, f, ensure_ascii=False, indent=2)