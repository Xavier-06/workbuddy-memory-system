# 向量记忆库

## 目录结构

```
VECTOR_MEMORY/
├── config.json.template    ← API 配置模板
└── vecmem.py               ← 主脚本（从 WorkBuddy 官方获取）
```

## 初始化步骤

### 1. 获取 vecmem.py

vecmem.py 是 WorkBuddy 向量记忆系统的核心脚本。在支持向量记忆的 WorkBuddy 实例中：

```bash
# 找到 vecmem.py
find ~/.workbuddy -name "vecmem.py" 2>/dev/null
```

如果没有，可以参考以下接口实现：

```bash
# 创建目录
mkdir -p ~/.workbuddy/vector-memory/chroma_data

# vecmem.py 需要支持以下命令：
# python3 vecmem.py sync       — 增量同步
# python3 vecmem.py index --full — 全量索引
# python3 vecmem.py search "query" — 语义搜索
# python3 vecmem.py status    — 查看状态
```

### 2. 配置 API

```bash
cp config.json.template ~/.workbuddy/vector-memory/config.json
vim ~/.workbuddy/vector-memory/config.json
```

填入你的 embedding API key。

### 3. 创建自动化任务

参见 `../AUTOMATIONS/vector-memory-sync/SETUP.md`

## 快速测试

```bash
cd ~/.workbuddy/vector-memory

# 查看状态
python3 vecmem.py status

# 全量索引
python3 vecmem.py index --full

# 语义搜索
python3 vecmem.py search "我的项目"
```
