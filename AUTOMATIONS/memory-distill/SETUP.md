# 自动化：每周日志蒸馏（Memory Distill）

**作用**：每周日凌晨 3:00 自动把 >30 天的旧日志蒸馏到主题文件，保持记忆系统精简。

## 工作流程

```
每周日 03:00 自动触发
    │
    ▼
find ~/.workbuddy/memory/ -name "YYYY-MM-DD.md" -mtime +30
    │
    ▼
逐个读取旧日志，识别有价值信息
    │
    ▼
蒸馏到对应主题文件（feedback/project/reference/user_profile）
    │
    ▼
删除原日志 → 更新 MEMORY.md 索引 → 向量库 sync
```

## 在 WorkBuddy 中配置

### 创建自动化任务

1. 打开 WorkBuddy → Automations
2. 创建新自动化任务，名称：`Memory Distill - 日志蒸馏`
3. 设置：
   - 类型：定时触发（recurring）
   - 规则：`FREQ=WEEKLY;BYDAY=SU;BYHOUR=3;BYMINUTE=0`
   - 工作目录：`/Users/xavier/WorkBuddy`
   - 状态：ACTIVE

### 蒸馏 Prompt（复制到自动化任务）

```
你是记忆蒸馏 agent。你的任务是对 >30 天的旧日志做蒸馏整理。

⚠️ 你的 cwds 可能指向任意工作间。记忆目录始终是全局路径：~/.workbuddy/memory/ — 不要依赖 cwds 下的 .workbuddy/memory/。

## 流程

### Step 1 — 找旧日志

扫描 ~/.workbuddy/memory/ 中日期格式 YYYY-MM-DD.md 的文件，找出修改时间 >30 天的：

find ~/.workbuddy/memory/ -name "[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].md" -mtime +30

如果没有旧日志，输出"无需蒸馏"后退出。

### Step 2 — 逐个蒸馏

对每个旧日志：
1. 读取内容，识别有价值的信息
2. 按类型蒸馏到对应主题文件：
   - 用户偏好/纠正 → feedback_*.md 或 ~/self-improving/corrections.md
   - 项目决策/状态 → project_*.md
   - 外部系统参考 → reference_*.md
   - 用户画像 → user_profile.md
3. 如果没有对应的主题文件，创建新的（带 frontmatter）
4. 蒸馏完成后，删除原日志文件

蒸馏规则：
- ✅ 保留：结论、决策、偏好、规则（Why + How to apply）
- ❌ 丢弃：过程细节、调试步骤、临时状态、纯代码片段、已过时信息

### Step 3 — 更新索引

1. 更新 ~/.workbuddy/memory/MEMORY.md 索引：删除已删除日志的指针，添加新主题文件指针
2. 运行 cd ~/.workbuddy/vector-memory && python3 vecmem.py sync 同步向量库

完成后输出简短总结：蒸馏了几个文件、合并到哪些主题、删除了什么。
```

## 与旧 dream 的区别

| | 旧 Dream | 新 Distill |
|---|---|---|
| 阈值 | >7 天 | >30 天 |
| 频率 | 每天凌晨 2:00 | 每周日凌晨 3:00 |
| 触发方式 | 独立 automation（经常超时） | 独立 automation + memory-recall SessionStart 双保险 |
| 向量同步 | 不涉及 | 蒸馏后自动 sync |

阈值从 7 天改到 30 天的原因：7 天太激进，经常把还没 extractMemories 处理完的日志就删了。30 天确保 extract 有足够时间处理，distill 只处理真正"冷"的日志。

## 静默退出原则

- 没有超过 30 天的日志 → 输出"无需蒸馏"后退出
- 日志内容已被现有主题文件覆盖 → 跳过，删除原日志

## 注意事项

- **双保险**：即使这个 automation 没跑，memory-recall skill 的 SessionStart Step 3 也会在每次新会话时检查旧日志
- **不并发**：不要与 extractMemories 同时运行，两者处理不同年龄的日志（extract 处理新日志，distill 处理旧日志）
- **增量进行**：每次只处理 >30 天的那批，不要试图一次蒸馏所有历史
