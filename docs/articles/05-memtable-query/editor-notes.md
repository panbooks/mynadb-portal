# 第五篇编辑与发布说明

## 发布文案

- 通用标题：从0到1实现一个分布式时序数据库（五）：让新写入立即可查
- 知乎备选：数据还没写成 Parquet，SQL 如何查询到它？
- 掘金备选：手写时序数据库 05：Memtable、TableProvider 与查询可见性
- 摘要：介绍内存和 Parquet 的统一查询、DataFusion TableProvider、flush 可见性、schema 对齐与缓存失效。
- 建议话题：时序数据库、DataFusion、Rust、Apache Arrow、Parquet。

## 内容定位与事实边界

参考 `v0.4.0` / M5 的查询路径。Memtable、Parquet 和 Union provider 及缓存失效入口存在于该标签；示意的查询版本切换、跨来源 schema 对齐和故障检查是设计目标，不声称该版本已经完整实现事务快照或验证所有并发语义。Union 的同名字段采用第一侧定义，不能据此推断异构类型被正确处理。该版本将时间列由 `timestamp` 改名为 `time`。

参考源码：[Memtable provider](https://github.com/panbooks/mynadb/blob/v0.4.0/src/query/providers/memtable_provider.rs)、[Union provider](https://github.com/panbooks/mynadb/blob/v0.4.0/src/query/providers/union_provider.rs)、[查询引擎](https://github.com/panbooks/mynadb/blob/v0.4.0/src/query/query_engine.rs)、[版本差异](https://github.com/panbooks/mynadb/compare/v0.3.0...v0.4.0)。

文章的测试表为建议方案，未运行历史版本测试、SQL 或基准；不宣称生产可靠性或性能优势。

## 图文交付与发布准备

- `article.md` 和 `preview.html`：中文正文及本地图文预览。
- `figures/`：六张 PNG、SVG、Mermaid 及清单。
- `build_assets.py`：使用 Pillow、Markdown 和 `MYNADB_ARTICLE_FONT` 指定的中文字体生成图文。

发表前检查图片、链接和平台规则；本文尚未对外发表。

## 复制发布与摘要

- [粘贴发布版](article.publish.md)：图片及文章链接使用 GitHub Pages 完整 HTTPS 地址。
- [100 字以内摘要](summary.md)：可直接复制到社区摘要栏。
- 重新运行 `build_assets.py` 会同步生成发布版；整系列可运行 `../publish_support.py` 统一导出。

复制全文后先检查平台预览。外链图片能否自动解析或转存，取决于目标编辑器；公网直链不等于知乎已自动上传图片。
