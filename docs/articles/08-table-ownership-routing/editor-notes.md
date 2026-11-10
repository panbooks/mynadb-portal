# 第八篇编辑与发布说明

## 发布文案

- 通用标题：从零实现一个时序数据库（八）：表所有权、Hive 分区与查询路由
- 知乎备选：时序数据库如何知道一张表的数据在哪些节点？
- 掘金备选：手写时序数据库 08：表级 Owner、分区发现与缓存亲和
- 摘要：区分 Meta 表级所有权与物理分区，讲解多 owner、冷热数据发现、查询回退和迟到数据风险。
- 建议话题：时序数据库、分布式查询、对象存储、Rust。

## 内容定位与事实边界

参考 `v0.7.0` / M8。表级所有权是 Meta 的主要模型，`date=.../node_id=...` 是物理布局与读路由层；不将后者描述为旧分区副本注册机制。历史路由中对近期查询采用时间阈值等启发式，代码注释与具体分支不完全等价；旧日期迟到数据仍在内存的发现需要测试，不能宣称已保证。TTL、缓存亲和和节点回退不证明 fencing 或所有查询语义正确。

参考源码：[表元数据](https://github.com/panbooks/mynadb/blob/v0.7.0/src/meta/types/table.rs)、[查询路由](https://github.com/panbooks/mynadb/blob/v0.7.0/src/router/query_coordinator/routing.rs)、[SQL 重写](https://github.com/panbooks/mynadb/blob/v0.7.0/src/router/query_coordinator/sql_rewrite.rs)、[Parquet 写入器](https://github.com/panbooks/mynadb/blob/v0.7.0/src/storage/parquet_writer.rs)、[版本差异](https://github.com/panbooks/mynadb/compare/v0.6.0...v0.7.0)。

故障与查询表为建议验证计划；未运行历史多节点、迁移或性能测试。旧布局迁移未获得自动兼容保证。

## 图文交付与发布准备

- `article.md`、`preview.html`：中文正文与本地图文预览。
- `figures/`：六张 PNG、SVG、Mermaid 源文件及清单。
- `build_assets.py`：使用 Pillow、Markdown 和 `MYNADB_ARTICLE_FONT` 指定的中文字体生成。

发表前检查图片、链接和平台规则；本文尚未对外发表。
