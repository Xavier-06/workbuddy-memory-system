#!/bin/bash
# ensure-memory-symlink.sh
# 确保项目目录的 memory 指向全局 memory

set -e

WORKSPACE="$1"

if [ -z "$WORKSPACE" ]; then
    echo "Usage: ensure-memory-symlink.sh <workspace_path>"
    exit 1
fi

MEMORY_DIR="$WORKSPACE/.workbuddy/memory"
GLOBAL_MEMORY="$HOME/.workbuddy/memory"

mkdir -p "$WORKSPACE/.workbuddy"

if [ -L "$MEMORY_DIR" ]; then
    TARGET=$(readlink "$MEMORY_DIR")
    if [ "$TARGET" = "$GLOBAL_MEMORY" ]; then
        echo "symlink already correct"
        exit 0
    else
        rm "$MEMORY_DIR"
    fi
elif [ -d "$MEMORY_DIR" ]; then
    echo "Warning: $MEMORY_DIR is a real directory, not a symlink. Moving aside."
    mv "$MEMORY_DIR" "$MEMORY_DIR.bak.$(date +%s)"
fi

ln -sf "$GLOBAL_MEMORY" "$MEMORY_DIR"
echo "symlink created: $MEMORY_DIR -> $GLOBAL_MEMORY"
