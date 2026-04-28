# Self-Improving Index

> Self-Improving 系统索引，记录目录结构和文件职责。

## 文件清单

| 文件 | 职责 | 读写频率 |
|------|------|---------|
| memory.md | HOT 规则 + 偏好 + 模式（每次任务前读） | 高频读写 |
| corrections.md | 犯错纠正日志 | 犯错时写入 |
| index.md | 本文件，系统索引 | 低频更新 |

## 与全局记忆的关系

- **Self-Improving 是纠正/教训的唯一源**——被纠正时写这里，不在全局 memory 重复建 feedback 文件
- **全局 memory 是跨会话稳定知识源**——Self-Improving 的规则成熟后可以迁入全局 memory 的主题文件
- **update_memory 不要重复存 Self-Improving 已有的内容**
