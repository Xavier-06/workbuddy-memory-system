#!/usr/bin/env python3
"""
init-memory-system.py
初始化 WorkBuddy 记忆系统
跨平台支持：Windows / macOS / Linux
"""

import os
import shutil
from pathlib import Path

def main():
    home = Path.home()
    repo_dir = Path(__file__).parent.parent.resolve()
    workbuddy_dir = home / ".workbuddy"
    self_improving_dir = home / "self-improving"

    print("=== WorkBuddy 记忆系统初始化 ===")

    # 创建目录
    (workbuddy_dir / "memory").mkdir(parents=True, exist_ok=True)
    (workbuddy_dir / "logs").mkdir(parents=True, exist_ok=True)
    self_improving_dir.mkdir(parents=True, exist_ok=True)

    templates = {
        workbuddy_dir / "SOUL.md": repo_dir / "TEMPLATES" / "SOUL.md.template",
        workbuddy_dir / "IDENTITY.md": repo_dir / "TEMPLATES" / "IDENTITY.md.template",
        workbuddy_dir / "USER.md": repo_dir / "TEMPLATES" / "USER.md.template",
        workbuddy_dir / "memory" / "MEMORY.md": repo_dir / "TEMPLATES" / "MEMORY.md",
    }

    for dest, src in templates.items():
        if not dest.exists():
            shutil.copy2(src, dest)
            print(f"  created: {dest.relative_to(home)}")
        else:
            print(f"  exists:  {dest.relative_to(home)}")

    # 复制 skeleton 文件
    skeletons_dir = repo_dir / "TEMPLATES" / "memory" / "SKELETONS"
    if skeletons_dir.exists():
        for skel in skeletons_dir.glob("*.skeleton"):
            dest = workbuddy_dir / "memory" / skel.name
            if not dest.exists():
                shutil.copy2(skel, dest)
                print(f"  created: {dest.relative_to(home)}")

    # 复制 self-improving 文件
    si_files = ["corrections.md", "memory.md", "index.md"]
    for fname in si_files:
        src = repo_dir / "self-improving" / fname
        dest = self_improving_dir / fname
        if not dest.exists():
            shutil.copy2(src, dest)
            print(f"  created: {dest.relative_to(home)}")

    print("")
    print("=== 初始化完成 ===")
    print("")
    print("请完成以下步骤：")
    print("1. 编辑 ~/.workbuddy/SOUL.md       — 填入你的风格")
    print("2. 编辑 ~/.workbuddy/IDENTITY.md   — 填入你的助理身份")
    print("3. 编辑 ~/.workbuddy/USER.md       — 填入你的用户信息")
    print("4. 参考 AUTOMATIONS/ 目录配置自动化任务")
    print("")
    print("详细说明请阅读 README.md")

if __name__ == "__main__":
    main()
