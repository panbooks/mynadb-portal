# 第四篇编辑与发布说明

## 发布文案

- 通用标题：从零实现一个时序数据库（四）：从本地文件走向对象存储
- 知乎备选：数据库把文件放进对象存储之后，还需要解决哪些问题？
- 掘金备选：手写时序数据库 04：存储抽象、Parquet、WAL 与查询缓存
- 摘要：从本地文件抽象出发，讲解对象存储写入、WAL 分段、查询缓存和 compaction，并讨论多对象提交与故障恢复边界。
- 建议话题：时序数据库、对象存储、Rust、Parquet、数据库。

## 内容定位与事实边界

以 `v0.3.0` / M4 为线索，介绍存储抽象、数据路径和查询优化。正文中的唯一 key、条件发布 manifest、文件集切换和垃圾回收是设计讨论，不表示该历史版本提供事务性 manifest 或已实现相应安全协议。对象存储具体行为依赖服务和配置，需要单独测试。

历史代码表明：`Storage` 封装本地与 S3 兼容后端；WAL 缓冲分段并通过 `put` 写入完整缓冲；缓存分片、字段类型、查询缓存和读取优化在该阶段出现。查询内存与持久化数据的整合是下一阶段的主题；旧 HA 子系统在该阶段移除。本文不宣称所有 S3 兼容服务、同步持久化或故障恢复已经验证。

源码参考：

- [存储抽象](https://github.com/panbooks/mynadb/blob/v0.3.0/src/storage.rs)
- [WAL](https://github.com/panbooks/mynadb/blob/v0.3.0/src/wal.rs)
- [写入缓存](https://github.com/panbooks/mynadb/blob/v0.3.0/src/cache.rs)
- [Parquet 写入器](https://github.com/panbooks/mynadb/blob/v0.3.0/src/parquet_writer.rs)
- [查询缓存](https://github.com/panbooks/mynadb/blob/v0.3.0/src/query_cache.rs)
- [版本差异](https://github.com/panbooks/mynadb/compare/v0.2.0...v0.3.0)

文中故障验证是建议方案；未运行该历史版本的构建、端到端、对象存储兼容性或容错测试，未提供性能结果。

## 图文交付

- `article.md`：中文正文和六张配图。
- `preview.html`：沿用前文风格的本地图文预览。
- `figures/`：PNG、SVG、Mermaid 源文件及清单。
- `build_assets.py`：使用 Pillow、Markdown 和 `MYNADB_ARTICLE_FONT` 指定的中文字体生成图片和预览。

## 发布准备

发表前检查图片、链接、术语、平台排版及当前规则；可将 PNG 上传至社区图片服务并替换正文相对路径。本文是草稿，尚未向社区发表；仓库提交推送与社区发布分别记录。
