# 第十篇编辑与发布说明

## 发布文案

- 通用标题：从0到1实现一个分布式时序数据库（十）：正确性补课、OTLP 与 Iceberg 初版
- 知乎备选：数据库查询能返回结果，为什么还需要正确性补课？
- 掘金备选：手写时序数据库 10：Compaction 清单、异构 Schema 与协议互通
- 摘要：从合并文件重复读取、schema 对齐和分布式聚合出发，讨论 OTLP、Iceberg 初版及验证边界。
- 建议话题：时序数据库、数据正确性、OpenTelemetry、Apache Iceberg、Rust。

## 内容定位与事实边界

以 `v0.9.0` / M10 为主，补充 `v0.9.1` 的 dashboard 响应和分布式 time 分桶修复，以及 `v0.9.2` 的 README 与依赖锁维护。Compaction manifest 是分区下的 superseded 文件集合；历史实现读取失败回退空集合，不能称为完整事务提交协议。它与 Iceberg manifest 是不同机制。Iceberg 初版的 manifest 和 manifest list 使用 JSON，不能声称与外部引擎完整互通。OTLP 与 Iceberg 的顶层开关在该标签默认关闭。

参考源码：[Compaction manifest](https://github.com/panbooks/mynadb/blob/v0.9.0/src/storage/manifest.rs)、[OTLP 服务](https://github.com/panbooks/mynadb/blob/v0.9.0/src/services/otlp/mod.rs)、[Iceberg manifest](https://github.com/panbooks/mynadb/blob/v0.9.0/src/iceberg/metadata/manifest.rs)、[v0.9.1 聚合](https://github.com/panbooks/mynadb/blob/v0.9.1/src/router/query_coordinator/aggregation.rs)、[v0.9.1 到 v0.9.2 差异](https://github.com/panbooks/mynadb/compare/v0.9.1...v0.9.2)。

文中测试矩阵是建议方案；未重新运行历史版本测试、外部引擎兼容性或性能测试。历史测试和 benchmark 文件不构成生产保证。

## 图文交付与发布准备

- `article.md`、`preview.html`：中文正文与本地图文预览。
- `figures/`：六张 PNG、SVG、Mermaid 源文件及清单。
- `build_assets.py`：使用 Pillow、Markdown 和 `MYNADB_ARTICLE_FONT` 指定的中文字体生成。

发表前检查图片、链接和平台规则；本文尚未对外发表。

## 复制发布与摘要

- [粘贴发布版](article.publish.md)：图片及文章链接使用 GitHub Pages 完整 HTTPS 地址。
- [100 字以内摘要](summary.md)：可直接复制到社区摘要栏。
- 重新运行 `build_assets.py` 会同步生成发布版；整系列可运行 `../publish_support.py` 统一导出。

复制全文后先检查平台预览。外链图片能否自动解析或转存，取决于目标编辑器；公网直链不等于知乎已自动上传图片。
