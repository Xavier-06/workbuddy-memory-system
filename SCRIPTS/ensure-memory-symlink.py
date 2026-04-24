#!/usr/bin/env python3
"""
ensure-memory-symlink.py
确保项目目录的 memory 指向全局 memory
跨平台支持：Windows / macOS / Linux
"""

import os
import sys
import shutil
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("Usage: ensure-memory-symlink.py <workspace_path>")
        sys.exit(1)

    workspace = Path(sys.argv[1]).resolve()
    memory_dir = workspace / ".workbuddy" / "memory"
    global_memory = Path.home() / ".workbuddy" / "memory"

    memory_dir.mkdir(parents=True, exist_ok=True)

    if memory_dir.is_symlink():
        target = memory_dir.resolve()
        if target == global_memory:
            print("symlink already correct")
            return
        else:
            memory_dir.unlink()
    elif memory_dir.exists():
        backup = Path(str(memory_dir) + f".bak.{int(os.path.getmtime(memory_dir))}")
        shutil.move(memory_dir, backup)
        print(f"Warning: moved existing directory to {backup}")
    memory_dir.symlink_to(global_memory, target_is_directory=True)
    print(f"symlink created: {memory_dir} -> {global_memory}")

if __name__ == "__main__":
    main()
