# 第三篇编辑与发布说明

## 发布文案

- 通用标题：从0到1实现一个分布式时序数据库（三）：主从复制、故障检测与切换
- 知乎备选：有了两份数据就安全吗？聊聊数据库复制、心跳和脑裂
- 掘金备选：手写时序数据库 03：复制确认、故障检测与安全切换
- 摘要：从单机 WAL 的故障边界出发，讨论主从复制、ACK、断线追赶、心跳超时、脑裂和 fencing，并用六张图展示设计边界及故障验证场景。
- 建议话题：时序数据库、分布式系统、数据库、Rust、高可用。

## 内容定位与事实边界

参考 `v0.2.0` / M3：历史代码引入主从角色、复制消息、心跳检测和提升原型。正文的复制确认策略、补发、快照、选主与 fencing 是讲解设计所需的检查项，不表示该标签已经实现完整协议。该 HA 子系统在 `v0.3.0` 被移除，不应与后续集群或不提升 standby 的方案混同。

历史代码检查要点：接收端校验后将记录送入队列即发送 ACK；`replicate_write` 使用排队发送；握手报告 `last_sequence`，但发送端未实现基于此的历史补发；文件同步为 TODO；提升器主要切换本地角色和状态，其他关键步骤列为后续工作。正文不声称零停机、无数据丢失或网络分区安全。

源码参考：

- [复制协议](https://github.com/panbooks/mynadb/blob/v0.2.0/src/ha/replication/protocol.rs)
- [发送端](https://github.com/panbooks/mynadb/blob/v0.2.0/src/ha/replication/sender.rs)
- [接收端](https://github.com/panbooks/mynadb/blob/v0.2.0/src/ha/replication/receiver.rs)
- [HA 管理器](https://github.com/panbooks/mynadb/blob/v0.2.0/src/ha/mod.rs)
- [故障检测](https://github.com/panbooks/mynadb/blob/v0.2.0/src/ha/failover/detector.rs)
- [提升器](https://github.com/panbooks/mynadb/blob/v0.2.0/src/ha/failover/promoter.rs)

文中故障测试是建议方案，并非已执行的结果；未编译或运行该历史版本，也未进行基准或容错验证。

## 图文交付

- `article.md`：中文正文和六张图片。
- `preview.html`：与前两篇统一风格的本地图文预览。
- `figures/`：六张图的 PNG、SVG、Mermaid 源文件及清单。
- `build_assets.py`：使用 Pillow、Markdown 和 `MYNADB_ARTICLE_FONT` 指定的中文字体重新生成图片和预览。

## 发布准备

发表前应检查图片、链接、术语、平台排版和平台当前规则；PNG 可上传至社区图片服务并替换正文相对链接。本文是草稿，尚未向社区发表；仓库提交推送与社区发布分别记录。

## 复制发布与摘要

- [粘贴发布版](article.publish.md)：图片及文章链接使用 GitHub Pages 完整 HTTPS 地址。
- [100 字以内摘要](summary.md)：可直接复制到社区摘要栏。
- 重新运行 `build_assets.py` 会同步生成发布版；整系列可运行 `../publish_support.py` 统一导出。

复制全文后先检查平台预览。外链图片能否自动解析或转存，取决于目标编辑器；公网直链不等于知乎已自动上传图片。
