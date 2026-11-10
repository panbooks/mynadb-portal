# 第六篇编辑与发布说明

## 发布文案

- 通用标题：从零实现一个时序数据库（六）：从单机走向 Router、Data、Meta 与 Raft
- 知乎备选：时序数据库如何从单机走向集群？
- 掘金备选：手写时序数据库 06：路由、Arrow Flight 与 Raft 元数据
- 摘要：介绍集群角色、写入路由、查询 fan-out、Raft 元数据与故障边界。
- 建议话题：时序数据库、分布式系统、Rust、Raft、Apache Arrow。

## 内容定位与事实边界

参考 `v0.5.0` / M6：Router、Data 和内置 Raft Meta，以及共享存储、Flight、早期副本和 fencing 组件。Raft 协调元数据，不代表指标数据都由 Meta 复制；写入确认、查询汇总、租约、故障隔离与恢复均需按实际路径和配置验证。初始 etcd 方案在标签端点前被移除；Router 模式的 MySQL 服务在该标签尚未实现。后续版本调整了 standby、fencing、缩容及文件布局。

参考源码：[写入路由](https://github.com/panbooks/mynadb/blob/v0.5.0/src/router/routing/write_router.rs)、[查询协调](https://github.com/panbooks/mynadb/blob/v0.5.0/src/router/routing/query_coordinator.rs)、[Raft](https://github.com/panbooks/mynadb/blob/v0.5.0/src/meta/raft/mod.rs)、[Router 启动](https://github.com/panbooks/mynadb/blob/v0.5.0/src/node/router.rs)、[版本差异](https://github.com/panbooks/mynadb/compare/v0.4.0...v0.5.0)。

故障矩阵是建议的测试计划；未运行历史多节点集群或容错测试，不宣称零停机、无损切换或生产就绪。

## 图文交付与发布准备

- `article.md` 和 `preview.html`：中文正文及本地图文预览。
- `figures/`：六张 PNG、SVG、Mermaid 及清单。
- `build_assets.py`：使用 Pillow、Markdown 和 `MYNADB_ARTICLE_FONT` 指定的中文字体生成图文。

发表前检查图片、链接和平台规则；本文尚未对外发表。
