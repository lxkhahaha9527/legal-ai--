"""
法律助手智能体 - 配置管理
支持多用户、长期记忆、自定义模型
支持平台: 阿里百炼, DeepSeek, 自定义
"""
import os
import json
import time
from pathlib import Path

# 基础路径
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
MEMORY_DIR = BASE_DIR / "memory"
CONVERSATIONS_DIR = MEMORY_DIR / "conversations"
DOCS_DIR = DATA_DIR / "legal_docs"

# 确保目录存在
for dir_path in [DATA_DIR, MEMORY_DIR, CONVERSATIONS_DIR, DOCS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# 配置文件路径
USERS_FILE = MEMORY_DIR / "users.json"
SETTINGS_FILE = MEMORY_DIR / "settings.json"

# 默认配置
DEFAULT_CONFIG = {
    "current_user": None,
    "users": {},
    "global_settings": {
        "default_model": "qwen-turbo",
        "default_model_provider": "alibaba",
        "default_temperature": 0.7,
        "default_max_tokens": 2048,
    }
}

# 支持的模型提供商配置
PROVIDER_CONFIG = {
    "alibaba": {
        "name": "阿里百炼",
        "default_model": "qwen-turbo",
        "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "env_key": "DASHSCOPE_API_KEY"
    },
    "deepseek": {
        "name": "DeepSeek",
        "default_model": "deepseek-chat",
        "api_base": "https://api.deepseek.com/v1",
        "env_key": "DEEPSEEK_API_KEY"
    },
    "custom": {
        "name": "自定义",
        "default_model": "",
        "api_base": "",
        "env_key": ""
    }
}


def load_json(file_path: Path, default=dict) -> dict:
    """加载JSON文件"""
    if file_path.exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return default()
    return default()


def save_json(file_path: Path, data: dict) -> None:
    """保存JSON文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self.users_data = load_json(USERS_FILE, lambda: {"users": {}})
        self.settings_data = load_json(SETTINGS_FILE, lambda: DEFAULT_CONFIG)
    
    def get_users(self) -> dict:
        """获取所有用户"""
        return self.users_data.get("users", {})
    
    def add_user(self, user_id: str, username: str, password: str, api_keys: dict = None) -> bool:
        """添加用户"""
        users = self.get_users()
        if user_id in users:
            return False
        users[user_id] = {
            "username": username,
            "password": password,
            "api_keys": api_keys or {},
            "model_provider": "alibaba",
            "preferred_model": "qwen-turbo",
            "api_base": "",
            "temperature": 0.7,
            "max_tokens": 2048,
            "conversations": [],
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.users_data["users"] = users
        save_json(USERS_FILE, self.users_data)
        return True
    
    def verify_user(self, user_id: str, password: str) -> bool:
        """验证用户"""
        users = self.get_users()
        if user_id not in users:
            return False
        return users[user_id].get("password") == password
    
    def get_user(self, user_id: str) -> dict:
        """获取用户信息"""
        return self.get_users().get(user_id, {})
    
    def update_user(self, user_id: str, updates: dict) -> None:
        """更新用户信息"""
        users = self.get_users()
        if user_id in users:
            users[user_id].update(updates)
            self.users_data["users"] = users
            save_json(USERS_FILE, self.users_data)
    
    def get_user_model_config(self, user_id: str) -> dict:
        """获取用户模型配置"""
        user = self.get_user(user_id)
        provider = user.get("model_provider", "alibaba")
        provider_info = PROVIDER_CONFIG.get(provider, PROVIDER_CONFIG["alibaba"])
        
        # 优先使用用户设置的 API Key，如果没有则尝试环境变量
        user_api_key = user.get("api_keys", {}).get(provider, "")
        env_api_key = os.getenv(provider_info["env_key"], "")
        api_key = user_api_key if user_api_key else env_api_key
        
        return {
            "provider": provider,
            "provider_name": provider_info["name"],
            "model": user.get("preferred_model", provider_info["default_model"]),
            "api_key": api_key,
            "api_base": user.get("api_base", provider_info["api_base"]),
            "temperature": user.get("temperature", 0.7),
            "max_tokens": user.get("max_tokens", 2048),
            "env_key": provider_info["env_key"]
        }
    
    def add_conversation(self, user_id: str, conv_id: str, title: str = "新对话") -> None:
        """添加对话"""
        users = self.get_users()
        if user_id in users:
            convs = users[user_id].get("conversations", [])
            convs.append({"id": conv_id, "title": title})
            users[user_id]["conversations"] = convs
            self.users_data["users"] = users
            save_json(USERS_FILE, self.users_data)
    
    def get_conversations(self, user_id: str) -> list:
        """获取用户对话列表"""
        user = self.get_user(user_id)
        return user.get("conversations", [])
    
    # Settings
    def get_settings(self) -> dict:
        """获取全局设置"""
        return self.settings_data
    
    def update_settings(self, updates: dict) -> None:
        """更新全局设置"""
        self.settings_data.update(updates)
        save_json(SETTINGS_FILE, self.settings_data)
    
    def get_provider_info(self, provider: str) -> dict:
        """获取提供商信息"""
        return PROVIDER_CONFIG.get(provider, PROVIDER_CONFIG["custom"])


# 全局配置实例
config = ConfigManager()