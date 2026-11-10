# 第九篇编辑与发布说明

## 发布文案

- 通用标题：从零实现一个时序数据库（九）：运维控制台、协议接入与时序分析
- 知乎备选：数据库内核之外，还需要哪些接入和运维能力？
- 掘金备选：手写时序数据库 09：控制台、Prometheus、权限和流式查询
- 摘要：介绍控制台、协议映射、权限、流式查询、降采样和功能验证边界。
- 建议话题：时序数据库、可观测性、Prometheus、Rust。

## 内容定位与事实边界

参考 `v0.8.0` / M9。该阶段包含 React 管理界面、Prometheus remote read/write、InfluxQL、Grafana 插件源码、RBAC/TLS、流式查询和分析组件。流式更新以写入通知后重新执行查询为主，不宣称增量计算。自动降采样改写器只记录候选 tier，仍返回原计划；独立 continuous aggregate 执行器为占位。Router MySQL 尚未实现。OTLP 与 Iceberg 属于下一里程碑。

源码参考：[降采样改写器](https://github.com/panbooks/mynadb/blob/v0.8.0/src/query/analyzers/downsampling_rewriter.rs)、[流式查询](https://github.com/panbooks/mynadb/blob/v0.8.0/src/query/streaming.rs)、[Prometheus 服务](https://github.com/panbooks/mynadb/blob/v0.8.0/src/services/prometheus/mod.rs)、[Router 启动](https://github.com/panbooks/mynadb/blob/v0.8.0/src/node/router.rs)、[版本差异](https://github.com/panbooks/mynadb/compare/v0.7.0...v0.8.0)。

测试表是建议计划；未运行历史版本的真实客户端、安全、前端或性能测试，也不声称插件签名或商店发布。

## 图文交付与发布准备

- `article.md`、`preview.html`：中文正文与本地图文预览。
- `figures/`：六张 PNG、SVG、Mermaid 源文件及清单。
- `build_assets.py`：使用 Pillow、Markdown 和 `MYNADB_ARTICLE_FONT` 指定的中文字体生成。

发表前检查图片、链接和平台规则；本文尚未对外发表。
