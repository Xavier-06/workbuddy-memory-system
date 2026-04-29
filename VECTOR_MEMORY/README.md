# 向量记忆库

> ⚠️ **重要限制**：向量记忆库依赖 WorkBuddy 原生支持，不是所有 WorkBuddy 实例都能用。如果你的 WorkBuddy 没有内置向量记忆功能，此模块不可用，但不影响文件记忆系统正常运行。

## 功能说明

向量记忆库提供**语义搜索**能力。当你说"之前那个项目叫什么来着"而不是具体名字时，向量搜索能帮你找到。

文件记忆系统（`~/.workbuddy/memory/`）是**独立运行的，不需要向量记忆库也能正常工作**。向量搜索只是加速层，不是必选项。

## 前置要求

- WorkBuddy 内置向量记忆功能（`vecmem.py` 存在且可用）
- 一个 embedding 模型 API（如 OpenAI、Cohere、或支持 qwen3-embedding 的服务商）

检查是否可用：

```bash
find ~/.workbuddy -name "vecmem.py" 2>/dev/null
```

如果返回空，说明此模块不可用，跳过本章节即可。

## 目录结构

```
VECTOR_MEMORY/
├── vecmem.py              ← 主脚本（index / sync / search / status）
├── config.json.template   ← API 配置模板
└── README.md              ← 本文件
```

## 如果不可用怎么办

**不用它。** 文件记忆系统本身已经完整，向量搜索只是锦上添花。没有向量记忆库的情况下：

- 用 MEMORY.md 索引 + 关键字搜索
- 文件多了用 `grep` 或 AI 辅助查找
- 等待 WorkBuddy 原生支持

## 如果可用：初始化步骤

### 1. 部署 vecmem.py

```bash
# 从本仓库复制到 WorkBuddy 目录
cp VECTOR_MEMORY/vecmem.py ~/.workbuddy/vector-memory/vecmem.py
```

如果 `~/.workbuddy/vector-memory/` 目录不存在，先创建：

```bash
mkdir -p ~/.workbuddy/vector-memory/chroma_data
```

### 2. 配置 API

```bash
mkdir -p ~/.workbuddy/vector-memory/chroma_data
cp config.json.template ~/.workbuddy/vector-memory/config.json
vim ~/.workbuddy/vector-memory/config.json
```

填入你的 embedding API key。可选 providers：
- **小马算力**：`https://api.tokenpony.cn/v1`（如已配置）
- **OpenAI**：`https://api.openai.com/v1`
- **Cohere**：`https://api.cohere.ai/v1`

### 3. 全量索引

```bash
cd ~/.workbuddy/vector-memory
python3 vecmem.py index --full
```

### 4. 配置自动化同步

参见 `../AUTOMATIONS/vector-memory-sync/SETUP.md`

## vecmem.py 命令

```bash
cd ~/.workbuddy/vector-memory

# 增量同步（每 6 小时自动化）
python3 vecmem.py sync

# 全量重建索引（记忆结构大变时）
python3 vecmem.py index --full

# 语义搜索
python3 vecmem.py search "之前那个项目"

# 状态查看（向量数 vs 文件数）
python3 vecmem.py status
```

## 常见问题

**Q：vecmem.py 报 API key 错误？**

A：检查 `config.json` 里的 API key 是否正确，是否有余额。

**Q：向量数 > 文件数？**

A：可能是幽灵文件。手动删除的文件在 ChromaDB 中残留。解决：运行 `python3 vecmem.py index --full` 全量重建。

**Q：同步太慢？**

A：增量同步每次只处理新增/修改的文件。如果太慢，减少同步频率（如从每 6 小时改为每天）。

**Q：想禁用向量搜索？**

A：不启动自动化任务即可。文件记忆系统不受影响。
