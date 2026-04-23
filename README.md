# WorkBuddy 记忆系统

让 AI 记住你是谁、你在做什么、你的偏好和规则。不是聊天机器人，是真正懂你的助理。

---

## 目录

1. [快速开始](#快速开始) — 5 分钟搭建
2. [系统架构](#系统架构) — 理解六套记忆系统
3. [身份配置](#身份配置) — 填模板，建个性
4. [记忆系统初始化](#记忆系统初始化) — 建目录结构
5. [自动化配置](#自动化配置) — 自动整理，不用手动
6. [向量记忆库](#向量记忆库) — 语义搜索（⚠️ 需要 WorkBuddy 原生支持）
7. [上手指南](ONBOARDING.md) — 新手第一周怎么做
8. [使用规则](#使用规则) — 怎么写记忆
9. [进阶：Self-Improving](#进阶-self-improving) — 让 AI 越用越聪明

---

## 快速开始

### 第一步：Clone 仓库（放到任意目录）

```bash
git clone https://github.com/Xavier-06/workbuddy-memory-system.git ~/workbuddy-memory-system
cd ~/workbuddy-memory-system
```

> **重要说明**：clone 到哪里都行，这个 repo 只是"教材"。真正要用的是第三步初始化后复制到 `~/.workbuddy/` 和 `~/self-improving/` 里的文件。初始化完成后，clone 的这个目录可以留着（以后同步更新用），也可以删掉。

### 第二步：运行初始化脚本

```bash
bash SCRIPTS/init-memory-system.sh
```

脚本会把模板文件复制到正确位置：

| 源（repo 内） | 目标（你的电脑） |
|-------------|--------------|
| TEMPLATES/memory/*.md | `~/.workbuddy/memory/` |
| TEMPLATES/SOUL.md.template | `~/.workbuddy/SOUL.md` |
| TEMPLATES/IDENTITY.md.template | `~/.workbuddy/IDENTITY.md` |
| TEMPLATES/USER.md.template | `~/.workbuddy/USER.md` |
| self-improving/*.md | `~/self-improving/` |

**注意**：`~/.workbuddy/` 和 `~/self-improving/` 才是你真正的记忆系统目录，不是 clone 的那个仓库。

### 第三步：填身份模板

init-script 已把模板复制到正确位置，直接编辑：

```bash
vim ~/.workbuddy/SOUL.md
vim ~/.workbuddy/IDENTITY.md
vim ~/.workbuddy/USER.md
```

### 第四步：配置自动化任务

```bash
# 查看可用的自动化任务配置
cat AUTOMATIONS/memory-extract/SETUP.md
cat AUTOMATIONS/session-summary/SETUP.md
```

按 SETUP.md 的说明在 WorkBuddy 里创建自动化任务。

### 第五步：验证

重启一个 WorkBuddy 会话，让 AI 写一点内容，然后问它："你记得我吗？"

---

## 系统架构

六套记忆系统并存，各司其职：

```
┌─────────────────────────────────────────────────────┐
│                     你是谁                            │
│         SOUL.md / IDENTITY.md / USER.md               │
│        （你的风格、名字、偏好、使用习惯）              │
└────────────────────────┬────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────┐
│                  全局主题记忆                          │
│              ~/.workbuddy/memory/                    │
│    MEMORY.md（索引）+ 主题文件（user/profile/reference）│
│           跨项目稳定知识，唯一真相源                    │
└────────────────────────┬────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────┐
│                  项目工作记忆                          │
│      {workspace}/.workbuddy/memory/ → symlink       │
│               当日进展 + 流水账                         │
└────────────────────────┬────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────┐
│               Self-Improving                         │
│              ~/self-improving/                       │
│        犯错纠正 + HOT规则 + 领域经验                   │
└────────────────────────┬────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────┐
│                向量语义索引                            │
│           ~/.workbuddy/vector-memory/                │
│              ChromaDB + embedding                    │
└────────────────────────┬────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────┐
│                 会话摘要                               │
│              session-summary.md                      │
│              接续上次最少需要的信息                     │
└─────────────────────────────────────────────────────┘
```

**核心原则：每个事实只存一处。**

---

## 身份配置

### SOUL.md — 你是谁

定义 AI 的**风格和原则**。不是配置文件，是性格定义。

```markdown
# SOUL.md - Who I Am

_我不是聊天机器人。我是一个有主见的家伙。_

## 核心原则

**有立场。** 别用"看情况"含糊其辞。亮观点，说人话。

**简洁是硬性要求。** 一句话能说清的，就别写一段。

**不知道就不知道。** 别瞎编，给个找到答案的办法。

## 连续性

每次醒来，读这些文件。这就是我持续存在的方式。

**SessionStart 仪式**：每次新会话第一条消息前：
1. 读 MEMORY.md 索引
2. 扫描 memory/ 目录判断相关记忆
3. 读取相关记忆文件

...
```

### IDENTITY.md — 助理身份

```markdown
# IDENTITY.md

- **Name:** 你的助理叫什么
- **Creature:** 你是干什么的
- **Vibe:** 风格描述
- **Emoji:** 一个代表你的 emoji
```

### USER.md — 用户信息

```markdown
# USER.md - About Your Human

- **Name:** 你的名字
- **What to call them:** 怎么称呼你
- **City:** 你在哪个城市
- **Notes:** 其他背景信息

## Context
- 沟通偏好
- 工作风格
- 特殊要求
```

---

## 记忆系统初始化

### 目录结构

```
~/.workbuddy/
├── memory/
│   ├── MEMORY.md              ← 索引（必须）
│   ├── user_profile.md        ← 用户画像
│   ├── project_*.md           ← 项目记忆（按需）
│   ├── reference_*.md         ← 参考指针（按需）
│   └── YYYY-MM-DD.md          ← 每日日志（AI 会话末尾自动写）
└── self-improving/
    ├── corrections.md         ← 犯错纠正
    ├── memory.md              ← HOT 规则
    └── index.md               ← Self-Improving 索引
```

### symlink 机制

项目级工作记忆通过 symlink 指向全局记忆：

```bash
# 对于每个 WorkBuddy 项目 workspace
ln -sf ~/.workbuddy/memory {workspace}/.workbuddy/memory

# 或使用脚本
bash SCRIPTS/ensure-memory-symlink.sh {workspace_path}
```

### 手动创建方法

```bash
mkdir -p ~/.workbuddy/memory
mkdir -p ~/self-improving

# MEMORY.md 索引文件
touch ~/.workbuddy/memory/MEMORY.md

# 在 MEMORY.md 顶部加：
# # Memory Index
# > 记忆索引 — 每条一行，≤150字符，指向主题文件。
```

---

## 自动化配置

### 自动化 1：定期记忆提取（memory-extract）

**作用**：每天扫描每日日志，把有价值的内容蒸馏到主题记忆文件。

**配置方法**：

1. 在 WorkBuddy 创建自动化任务
2. 触发条件：每天固定时间（如早上 9:00）
3. 任务内容：调用 `extractMemories` 脚本，扫描 `~/.workbuddy/memory/` 下的每日日志

**extractMemories 职责**：
- 扫描 `~/.workbuddy/memory/YYYY-MM-DD.md` 每日日志
- 识别新知识、决策、偏好、规则
- 更新对应主题文件（user/profile/reference）
- 更新 MEMORY.md 索引
- 删除已被充分记录的老旧日志
- 静默退出（无实质内容时）

**判断标准**：
- 新记忆？→ 创建或更新主题文件
- 已在主题文件覆盖？→ 静默退出
- 日志超过 30 天？→ 蒸馏到 MEMORY.md，删除原日志

### 自动化 2：会话摘要（session-summary）

**作用**：每次会话结束后更新 session-summary.md，确保下次接上。

**配置方法**：

1. 在 WorkBuddy 创建自动化任务
2. 触发条件：每次会话结束（AI 检测到对话告一段落）
3. 任务内容：
   - 读取 MEMORY.md 和 session-summary.md
   - 验证所有主题文件存在性（无悬空指针）
   - 更新 session-summary.md 的时间戳和关键进展

### 自动化 3：Skills 自动更新（Auto-Updater）

**作用**：每天自动更新 WorkBuddy skills 到最新版本。

**配置方法**：

1. 在 WorkBuddy 创建自动化任务
2. 触发条件：每天晚上 10:00
3. 任务：调用 Auto-Updater Skill

### 自动化 4：每日记忆蒸馏（Dream）

**作用**：每天凌晨自动把旧每日日志蒸馏成主题记忆，保持记忆系统精简。

**配置方法**：

1. 在 WorkBuddy 创建自动化任务
2. 触发条件：每天凌晨 2:00
3. 任务内容：
   - 扫描 `~/.workbuddy/memory/` 下超过 7 天的每日日志
   - 蒸馏精华到对应主题文件
   - 删除已被吸收的原日志
   - 更新 MEMORY.md 索引

**与 extractMemories 的分工**：Dream 负责"减肥"（老日志），extractMemories 负责"吸收"（新日志）。

### 自动化 5：向量记忆库同步（vector-memory-sync）

**作用**：定期把记忆文件同步到向量数据库，支持语义搜索。

**配置方法**：

1. 在 WorkBuddy 创建自动化任务
2. 触发条件：每 6 小时
3. 任务内容：`python3 vecmem.py sync`

详细说明见 [向量记忆库](#向量记忆库) 章节。

---

## 向量记忆库

当记忆文件积累到 50+ 个时，向量语义搜索是唯一的检索出路。文件记忆是精确查找，向量搜索是语义匹配。

### 组件

| 组件 | 路径 | 说明 |
|------|------|------|
| 主脚本 | `~/.workbuddy/vector-memory/vecmem.py` | index / sync / search / status |
| 配置 | `~/.workbuddy/vector-memory/config.json` | embedding API 参数 |
| ChromaDB | `~/.workbuddy/vector-memory/chroma_data/` | 持久化向量存储 |

### 初始化

```bash
# 1. 创建目录
mkdir -p ~/.workbuddy/vector-memory/chroma_data

# 2. 复制配置模板
cp VECTOR_MEMORY/config.json.template ~/.workbuddy/vector-memory/config.json
# 编辑填入你的 API key

# 3. 全量索引
python3 vecmem.py index --full
```

### 命令

```bash
cd ~/.workbuddy/vector-memory

# 增量同步（自动化任务每 6 小时执行）
python3 vecmem.py sync

# 全量重建（记忆结构大变时）
python3 vecmem.py index --full

# 语义搜索
python3 vecmem.py search "之前那个项目"

# 状态查看
python3 vecmem.py status
```

### 向量搜索 vs 文件查找

| 场景 | 用哪种 |
|------|--------|
| "我上次做的那个项目叫什么来着" | 向量搜索 |
| "Xavier 在哪个城市" | 直接读 USER.md |
| 关于 XX 项目 AI 记得什么 | 向量搜索 |
| 精确知道文件名 | 文件查找 |

---

## 使用规则

### 什么时候写记忆

| 场景 | 写入位置 |
|------|---------|
| 了解到用户的任何细节 | user_profile.md |
| 用户纠正你（不要这样/这样做更好） | corrections.md |
| 项目决策、技术选型、进展 | project_*.md |
| 了解到外部系统的位置 | reference_*.md |
| 当天工作记录 | YYYY-MM-DD.md |
| 犯错后学到的教训 | corrections.md |

### 记忆文件格式

```markdown
---
name: {{记忆名称}}
description: {{一行描述——用于判断相关性}}
type: {{user, feedback, project, reference}}
---

{{记忆内容}}

**Why:** 为什么要记这个

**How to apply:** 未来遇到什么情况该调用这条记忆
```

### 不要存什么

- 代码模式（可以从代码推导）
- Git 历史
- 调试过程
- 已在 CLAUDE.md / 项目配置中记录的内容
- 临时任务细节

### 记忆召回优先级

1. **向量搜索**（`vecmem.py search`）— 语义匹配，最准
2. **MEMORY.md 索引** — 关键字匹配
3. **直接读文件** — 当以上都找不到时

---

## 进阶：Self-Improving

### 核心理念

每次被纠正、失败、发现可复用经验时，**立即写入** self-improving 文件。不是事后补，是当下就写。

### corrections.md

用户纠正的记录，格式：

```markdown
## [日期] {{犯错描述}}

**问题：** {{当时怎么理解的}}

**纠正：** {{用户说应该怎么做}}

**规则：** {{抽象成一条可复用的规则}}
```

### HOT Rules

高价值经验，格式：

```markdown
## HOT: {{规则名称}}

**场景：** {{在什么情况下这条规则适用}}

**规则：** {{具体怎么做}}

**Why：** {{为什么这条规则有效}}
```

---

## 常见问题

### Q：记忆文件和每日日志同时存在不会重复吗？

不会。每日日志是原始素材，extractMemories 会判断内容是否已在主题文件覆盖。覆盖了就静默，不重复记录。

### Q：多个项目会串吗？

不会。项目级 `{workspace}/.workbuddy/memory/` 通过 symlink 指向全局 `~/.workbuddy/memory/`，但每日日志文件名带日期，不会混淆。extractMemories 扫描时会按日期过滤。

### Q：向量索引和文件记忆哪个优先？

向量搜索用于**语义匹配**（你说"之前那个项目"而不是具体名字），文件记忆用于**精确查找**。两者互补，不是替代关系。

---

## 更新日志

- 2026-04-23：初版创建
