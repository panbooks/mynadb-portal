# 从0到1实现一个分布式时序数据库：文章摘要

每段均不超过 100 个字符，可直接复制到社区摘要栏。

## 从0到1实现一个分布式时序数据库（一）：用 Rust、Arrow 和 Parquet 打通写入与 SQL 查询

从一条指标出发，用 Rust、Arrow、Parquet 和 DataFusion 串起解析、内存批次、刷盘与 SQL 查询，理解分布式时序数据库的单机基础。

[粘贴发布版](01-from-http-to-parquet/article.publish.md) · [图文预览](01-from-http-to-parquet/preview.html)

## 从0到1实现一个分布式时序数据库（二）：写入成功之后，如何用 WAL 找回数据

从内存写入到故障恢复，拆解 WAL 的日志同步、分组提交、刷盘边界、Checkpoint 与启动重放，讲清“写入成功”背后的持久性保证。

[粘贴发布版](02-wal-and-recovery/article.publish.md) · [图文预览](02-wal-and-recovery/preview.html)

## 从0到1实现一个分布式时序数据库（三）：主从复制、故障检测与切换

从单机 WAL 走向主从复制，梳理复制确认、断线追赶、心跳检测、脑裂与安全切换，理解备用节点接管服务所需的数据和授权边界。

[粘贴发布版](03-replication-and-failover/article.publish.md) · [图文预览](03-replication-and-failover/preview.html)

## 从0到1实现一个分布式时序数据库（四）：从本地文件走向对象存储

把本地文件访问抽象为对象存储接口，讲解 Parquet 写入、WAL 分段、文件提交、查询缓存与 Compaction，理解计算与存储分离的设计。

[粘贴发布版](04-object-storage/article.publish.md) · [图文预览](04-object-storage/preview.html)

## 从0到1实现一个分布式时序数据库（五）：让新写入立即可查

通过 Memtable 与 TableProvider，让 SQL 同时读取内存和 Parquet；结合快照、Schema 对齐、数据裁剪与缓存失效，保证新数据及时可见。

[粘贴发布版](05-memtable-query/article.publish.md) · [图文预览](05-memtable-query/preview.html)

## 从0到1实现一个分布式时序数据库（六）：从单机走向 Router、Data、Meta 与 Raft

将单机拆分为 Router、Data 与 Meta，梳理 Arrow Flight 写入、分布式查询与 Raft 元数据协调，理解分布式时序数据库的核心架构。

[粘贴发布版](06-distributed-cluster/article.publish.md) · [图文预览](06-distributed-cluster/preview.html)

## 从0到1实现一个分布式时序数据库（七）：不提升 Standby 的恢复与安全缩容

围绕不提升 Standby 的恢复设计，拆解复制进度、Flush Checkpoint、数据排空和节点退役，理解故障恢复与安全缩容的关键约束。

[粘贴发布版](07-standby-and-scale-in/article.publish.md) · [图文预览](07-standby-and-scale-in/preview.html)

## 从0到1实现一个分布式时序数据库（八）：表所有权、Hive 分区与查询路由

区分表所有权与物理分区，讲解 Hive 路径、分区发现、冷热数据查询、缓存亲和与故障回退，理解分布式读写请求如何找到数据。

[粘贴发布版](08-table-ownership-routing/article.publish.md) · [图文预览](08-table-ownership-routing/preview.html)

## 从0到1实现一个分布式时序数据库（九）：运维控制台、协议接入与时序分析

围绕运维控制台、协议接入、RBAC、TLS、流式查询与时序分析，讲解数据库如何连接采集器、分析工具和管理员，并划清能力边界。

[粘贴发布版](09-operations-and-integrations/article.publish.md) · [图文预览](09-operations-and-integrations/preview.html)

## 从0到1实现一个分布式时序数据库（十）：正确性补课、OTLP 与 Iceberg 初版

从重复文件、异构 Schema 和分布式聚合出发，梳理正确性问题，并介绍 OTLP 接入与 Iceberg 初版，理解功能实现与互操作验证的区别。

[粘贴发布版](10-correctness-and-interop/article.publish.md) · [图文预览](10-correctness-and-interop/preview.html)
