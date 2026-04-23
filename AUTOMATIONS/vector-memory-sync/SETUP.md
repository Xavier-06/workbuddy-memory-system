# 自动化：向量记忆库同步

**作用**：定期把记忆文件同步到向量数据库，支持语义搜索。当你说"之前那个项目"而不是具体名字时，向量搜索能帮你找到。

## 向量记忆库是什么

文件记忆是精确查找（你知道要找什么）。
向量记忆是语义搜索（你知道大概意思，但说不清楚）。

当记忆文件积累到 50+ 个时，向量搜索是唯一的检索出路。

## 组件

| 组件 | 路径 | 说明 |
|------|------|------|
| 主脚本 | `~/.workbuddy/vector-memory/vecmem.py` | index / sync / search / status 四合一 |
| 配置 | `~/.workbuddy/vector-memory/config.json` | embedding 模型、API 参数 |
| ChromaDB 数据 | `~/.workbuddy/vector-memory/chroma_data/` | 持久化向量存储 |
| 同步状态 | `~/.workbuddy/vector-memory/.sync_state.json` | 增量同步跟踪 |

## API 配置

需要一个 embedding 模型 API，模板使用通用配置：

```json
{
  "embedding": {
    "model": "qwen3-embedding-8b",
    "api_url": "https://api.example.com/v1",
    "api_key": "your-api-key",
    "dimensions": 1024
  }
}
```

可选 providers：
- 小马算力（如果你有 token）
- OpenAI embedding API
- 本地部署的 embedding 模型

## 在 WorkBuddy 中配置

### 自动化 1：增量同步（每 6 小时）

1. 创建自动化任务
2. 触发条件：定时，每 6 小时
3. 任务内容：

```bash
cd ~/.workbuddy/vector-memory && python3 vecmem.py sync
```

### 自动化 2：全量重建（按需）

当记忆结构发生重大变化时（如大量新增/删除文件），手动触发全量重建：

```bash
cd ~/.workbuddy/vector-memory && python3 vecmem.py index --full
```

## vecmem.py 命令

```bash
# 语义搜索（人类可读）
python3 vecmem.py search "查询文本"

# 语义搜索（JSON 输出，供脚本解析）
python3 vecmem.py search "查询文本" --json

# 增量同步
python3 vecmem.py sync

# 全量重建索引
python3 vecmem.py index --full

# 查看状态
python3 vecmem.py status
```

## 向量搜索使用场景

什么时候用向量搜索而不是文件查找？

| 场景 | 用哪种 |
|------|--------|
| "我上次做的那个项目叫什么来着" | 向量搜索 |
| "Xavier 在哪个城市" | 直接读 USER.md |
| "关于 XX 项目，AI 记得什么" | 向量搜索 |
| 精确知道文件名 | 文件查找 |

## 与 memory-recall 的关系

`memory-recall` skill 已升级：核心召回流程从 LLM frontmatter 匹配 → **向量语义搜索**。

召回流程：
1. 用户发起需要回忆上下文的请求
2. 调用 `vecmem.py search --json`
3. 根据返回的 source_path 读取完整文件
4. 注入相关记忆到上下文

## 踩坑经验

- **幽灵文件**：手动删除的文件可能在 ChromaDB 中残留，导致向量数 > 文件数。解决：手动清理 `chroma_data/` 中对应 collection 的记录，并清理 `.sync_state.json`。
- **增量同步失败**：检查 API key 是否有效，网络是否通畅。
- **向量数 vs 文件数不一致**：运行 `vecmem.py status` 对比，差距大则执行全量重建。
