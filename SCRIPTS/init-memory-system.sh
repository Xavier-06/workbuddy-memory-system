#!/bin/bash
# init-memory-system.sh
# 初始化 WorkBuddy 记忆系统

set -e

WORKBUDDY_DIR="$HOME/.workbuddy"
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== WorkBuddy 记忆系统初始化 ==="

mkdir -p "$WORKBUDDY_DIR/memory"
mkdir -p "$HOME/self-improving"
mkdir -p "$WORKBUDDY_DIR/logs"

if [ ! -f "$WORKBUDDY_DIR/SOUL.md" ]; then
    cp "$REPO_DIR/TEMPLATES/SOUL.md.template" "$WORKBUDDY_DIR/SOUL.md"
    echo "SOUL.md created"
fi

if [ ! -f "$WORKBUDDY_DIR/IDENTITY.md" ]; then
    cp "$REPO_DIR/TEMPLATES/IDENTITY.md.template" "$WORKBUDDY_DIR/IDENTITY.md"
    echo "IDENTITY.md created"
fi

if [ ! -f "$WORKBUDDY_DIR/USER.md" ]; then
    cp "$REPO_DIR/TEMPLATES/USER.md.template" "$WORKBUDDY_DIR/USER.md"
    echo "USER.md created"
fi

if [ ! -f "$WORKBUDDY_DIR/memory/MEMORY.md" ]; then
    cp "$REPO_DIR/TEMPLATES/MEMORY.md" "$WORKBUDDY_DIR/memory/MEMORY.md"
    echo "MEMORY.md created"
fi

cp "$REPO_DIR/TEMPLATES/memory/SKELETONS/"*.skeleton "$WORKBUDDY_DIR/memory/" 2>/dev/null || true

if [ ! -f "$HOME/self-improving/corrections.md" ]; then
    cp "$REPO_DIR/self-improving/corrections.md" "$HOME/self-improving/corrections.md"
fi

if [ ! -f "$HOME/self-improving/memory.md" ]; then
    cp "$REPO_DIR/self-improving/memory.md" "$HOME/self-improving/memory.md"
fi

echo "Done. Edit SOUL.md, IDENTITY.md, USER.md to customize."
