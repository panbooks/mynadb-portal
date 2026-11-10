# 第七篇编辑与发布说明

## 发布文案

- 通用标题：从零实现一个时序数据库（七）：不提升 Standby 的恢复与安全缩容
- 知乎备选：数据库节点故障后，不提升备用节点也能恢复吗？
- 掘金备选：手写时序数据库 07：Standby、Flush Checkpoint 与缩容
- 摘要：介绍不提升备用节点的恢复思路、复制 checkpoint、节点退役与故障验证。
- 建议话题：时序数据库、分布式系统、高可用、Rust。

## 内容定位与事实边界

参考 `v0.6.0` / M7 的恢复、备用节点与缩容路径。历史恢复管理器在触发 Standby flush 后，`wait_for_flush_completion` 仍以短暂等待和假定完成作为占位，并注明需要真实状态跟踪；不能宣称严格等待 flush 完成。checkpoint 连续性、写入隔离、可重试的缩容状态机和故障表是设计检查项，不代表该标签已完整验证。

参考源码：[恢复管理器](https://github.com/panbooks/mynadb/blob/v0.6.0/src/meta/recovery/mod.rs)、[缩容执行器](https://github.com/panbooks/mynadb/blob/v0.6.0/src/meta/scale_in/executor.rs)、[复制类型](https://github.com/panbooks/mynadb/blob/v0.6.0/src/data/replication/types.rs)、[节点退役 API](https://github.com/panbooks/mynadb/blob/v0.6.0/src/data/server/api.rs)、[版本差异](https://github.com/panbooks/mynadb/compare/v0.5.0...v0.6.0)。

未运行历史集群或故障测试；不宣称无损恢复、零停机或生产就绪。

## 图文交付与发布准备

- `article.md`、`preview.html`：中文正文与本地图文预览。
- `figures/`：六张 PNG、SVG、Mermaid 源文件及清单。
- `build_assets.py`：使用 Pillow、Markdown 和 `MYNADB_ARTICLE_FONT` 指定的中文字体生成。

发表前检查图片、链接和平台规则；本文尚未对外发表。
