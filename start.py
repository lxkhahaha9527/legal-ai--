#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
启动脚本 - 确保UTF-8编码，使用虚拟环境
"""
import os
import sys
import subprocess
from pathlib import Path

# 设置UTF-8环境
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["LANG"] = "zh_CN.UTF-8"

# 添加项目路径
project_dir = Path(__file__).parent.resolve()
os.chdir(project_dir)

# 优先使用虚拟环境的 Python
venv_python = project_dir / ".venv" / "Scripts" / "python.exe"
if venv_python.exists():
    python_exe = str(venv_python)
else:
    python_exe = sys.executable

# 启动Streamlit
cmd = [
    python_exe, "-m", "streamlit", "run", "app.py",
    "--server.headless=true",
    "--server.fileWatcherType=none"
]

subprocess.run(cmd)