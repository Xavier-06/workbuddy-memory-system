---
name: memory-recall
description: 智能记忆召回 — SessionStart 三步流程（读文件→向量搜索→蒸馏检查）+ 主动回忆时语义搜索。在每次新对话开始时自动执行。
metadata:
  emoji: 🔍
  triggers:
    - 记忆
    - 记得
    - 之前
    - 上次
    - 回忆
    - remember
    - recall
    - memory
hooks:
  SessionStart:
    - matcher: ""
      hooks:
        - type: prompt
          prompt: "执行记忆召回三步流程：Step1 读 MEMORY.md + 近两天日志 → Step2 用向量语义搜索召回相关长期记忆 → Step3 检查是否有 >30 天的日志需要蒸馏。详见 SKILL.md 的 SessionStart 流程。"
---

# Memory Recall — 智能记忆召回

## 两套流程

1. **SessionStart 流程**：每次新会话自动执行（读文件 → 向量搜索 → 蒸馏检查）
2. **主动回忆流程**：用户提到过去的事时执行（向量搜索 → 读文件）

---

## SessionStart 流程（每次新会话自动执行）

### Step 1 — 确保 symlink + 读基础文件

```bash
bash ~/.workbuddy/scripts/ensure-memory-symlink.sh {workspace}
```

然后读取：
1. `~/.workbuddy/memory/MEMORY.md` — 长期记忆索引
2. 今天 + 昨天的日志文件 `~/.workbuddy/memory/YYYY-MM-DD.md`

### Step 2 — 向量语义搜索

根据当前上下文（用户消息、工作区路径等）构造查询，做一次语义搜索：

```bash
cd ~/.workbuddy/vector-memory && python3 vecmem.py search "与当前上下文相关的查询" --json
```

- 查询文本应概括当前会话可能需要的长期记忆
- 如果是空会话/问候，用"最近工作进展"之类的通用查询
- 读取 similarity ≥ 0.5 的结果对应的完整文件
- 同一文件只读一次，最多读 5 个

### Step 3 — 日志蒸馏检查

扫描 `~/.workbuddy/memory/` 中超过 30 天的日期日志文件：

```bash
# 找出 >30 天的旧日志
find ~/.workbuddy/memory/ -name "[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].md" -mtime +30
```

如果有旧日志：
1. **逐个读取**旧日志，识别其中有价值的信息
2. **蒸馏到对应主题文件**：用户偏好→`feedback_*.md`，项目决策→`project_*.md`，参考指针→`reference_*.md`
3. **删除原日志文件**
4. **更新 MEMORY.md 索引**：删除已删除日志的指针
5. **跑一次向量 sync**：`cd ~/.workbuddy/vector-memory && python3 vecmem.py sync`

蒸馏规则：
- 只保留**结论、决策、偏好、规则**（Why + How to apply）
- 丢弃过程细节、调试步骤、临时状态
- 丢弃纯代码片段（代码从仓库获取，不需要存在记忆里）
- 丢弃已过时的信息（如"正在修复X"，如果X已修复就丢掉）

### Step 4 — 新鲜度检查

对 >1 天的记忆，使用前注意：
- 记忆可能是过时的，需验证当前状态
- "记忆说 X 存在" ≠ "X 现在还存在"
- 引用函数/文件/flag 时，先确认仍存在

---

## 主动回忆流程（用户触发时执行）

### Step 1 — 判断是否需要召回

**触发**：
- 用户提到过去的对话、决策、偏好
- 需要了解项目状态或历史约束
- "之前"、"上次"、"记得"等关键词

**跳过**：
- 纯代码问题（从代码推导即可）
- 简单的通用知识问答
- 当前对话中已有完整上下文

### Step 2 — 向量语义搜索

```bash
cd ~/.workbuddy/vector-memory && python3 vecmem.py search "查询文本" --json
```

- 查询文本应概括当前需要回忆的内容
- 返回 top 5 最相关记忆片段
- 每个结果包含：source_file、source_path、fm_name、fm_type、similarity、content

### Step 3 — 读取完整文件

从 JSON 结果中提取 `source_path`，读取完整文件内容：
- 优先读取 similarity ≥ 0.5 的结果
- 同一文件只读一次
- 最多读 5 个完整文件

### Step 4 — 类型感知排序

向量搜索返回的 `fm_type` 可用于排序优先级：
- 用户偏好/习惯 → `user` 类型优先
- 用户纠正 → `feedback` 类型优先
- 项目状态 → `project` 类型优先
- 外部系统 → `reference` 类型优先

---

## 记忆目录位置

| 位置 | 用途 |
|------|------|
| `~/.workbuddy/memory/` | 全局记忆（唯一真相源），日志+主题文件 |
| `~/.workbuddy/vector-memory/` | ChromaDB 语义索引，每 6h 增量同步 |
| `{workspace}/.workbuddy/memory/` | 项目级，通过 symlink 指向全局 |

## Symlink 机制

项目级 `.workbuddy/memory/` 通过 symlink 指向 `~/.workbuddy/memory/`：
- 系统读项目级 → 自动读到全局
- 系统写项目级 → 自动写到全局

新工作区时：`bash ~/.workbuddy/scripts/ensure-memory-symlink.sh {workspace}`

## 与旧 dream automation 的关系

旧 `memory-dream-daily-consolidation` automation 因超时无法正常运行。蒸馏逻辑已内嵌到本 skill 的 SessionStart Step 3，每次新会话自动检查，不再依赖独立的 dream automation。
