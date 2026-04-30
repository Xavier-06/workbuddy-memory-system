# ⚠️ 已废弃 — 迁移到 memory-distill

此自动化已被 `../memory-distill/SETUP.md` 替代。

主要变更：
- 阈值从 7 天改为 30 天（避免误删未处理的日志）
- 频率从每天改为每周日
- 新增蒸馏后向量库 sync
- 蒸馏逻辑合并到 memory-recall skill 作为双保险

请使用 `AUTOMATIONS/memory-distill/` 下的新配置。
