# 自动化：Skills 自动更新

**作用**：每天自动检查并更新 WorkBuddy skills 到最新版本，确保 AI 始终有最新工具可用。

## 为什么要自动化

WorkBuddy 的 skills 市场更新频繁：新技能发布、已有技能改进、bug 修复。手动更新麻烦且容易忘，配置好后每天自动跑，省心。

## 在 WorkBuddy 中配置

### 使用 Auto-Updater Skill（推荐）

WorkBuddy 内置了 Auto-Updater Skill，直接启用：

1. 在 WorkBuddy 中搜索 "Auto-Updater Skill"
2. 启用该 skill
3. 配置触发时间：每天晚上 10:00

### 自定义 cron（高级）

```bash
# 每天晚上 10 点更新 skills
0 22 * * * /usr/bin/python3 ~/self-improving/scripts/update-skills.py >> ~/.workbuddy/logs/skills-update.log 2>&1
```

## 更新机制

1. 检查本地已安装的 skills
2. 对比 skill marketplace 最新版本
3. 下载并安装更新
4. 记录更新日志
5. 如果有重大更新，通知用户

## 验证是否正常运行

```bash
cat ~/.workbuddy/logs/skills-update.log
```

## 注意事项

- 网络要求：自动更新需要能访问 WorkBuddy marketplace
- 排除：某些 skill 不想自动更新可以在配置中排除
- 回滚：如果更新后有问题，检查日志回滚到上一版本
