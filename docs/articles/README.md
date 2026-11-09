# MynaDB 从零实现系列

面向 Rust、数据库和可观测性系统开发者。围绕开发里程碑讲解实现顺序、核心架构和工程取舍；文章准备不代表已向社区发布。

## 系列选题与参考里程碑

| 篇次 | 参考版本 / 里程碑 | 选题 | 状态 |
| --- | --- | --- | --- |
| 1 | `v0.0.0` / M1 | [从 HTTP 到 Parquet，打通写入与 SQL 查询](01-from-http-to-parquet/article.md) | 首稿及配图已准备 |
| 2 | `v0.1.0` / M2 | [写入成功之后，如何用 WAL 找回数据](02-wal-and-recovery/article.md) | 首稿及配图已准备 |
| 3 | `v0.2.0` / M3 | 主从复制：故障检测与切换设计 | 待写 |
| 4 | `v0.3.0` / M4 | 对象存储：重构存储接口、写入与缓存 | 待写 |
| 5 | `v0.4.0` / M5 | 让新写入立即可查：Memtable、TableProvider 与查询优化 | 待写 |
| 6 | `v0.5.0` / M6 | 从单机走向集群：Router、Data、Meta 与 Raft | 待写 |
| 7 | `v0.6.0` / M7 | 不提升 Standby 的恢复方案与安全缩容 | 待写 |
| 8 | `v0.7.0` / M8 | 表所有权、Hive 分区和查询路由怎样配合 | 待写 |
| 9 | `v0.8.0` / M9 | 运维控制台、协议接入与时序分析能力 | 待写 |
| 10 | `v0.9.0` / M10，补充 `.1/.2` | 正确性补课：合并清单、异构 schema、OTLP 与 Iceberg 初版 | 待写 |

篇次参考开发里程碑，正文优先讲清设计，不要求逐标签复现。篇次不等同于发布时间承诺。

## 第一篇交付

- [正文 Markdown](01-from-http-to-parquet/article.md)：带八张架构/流程图，可作为知乎、掘金的共同正文。
- [本地浏览版](01-from-http-to-parquet/preview.html)：浏览器打开，便于通读图文。
- `01-from-http-to-parquet/figures/`：PNG 上传版、SVG 矢量版和 Mermaid 源文件。
- [编辑与发布说明](01-from-http-to-parquet/editor-notes.md)：标题、摘要、内容定位与发布准备。

## 第二篇交付

- [正文 Markdown](02-wal-and-recovery/article.md)：写入确认、同步策略、日志格式、刷盘边界与启动恢复。
- [图文预览](02-wal-and-recovery/preview.html)：包含六张配图，与第一篇采用统一样式。
- `02-wal-and-recovery/figures/`：PNG 上传版、SVG 矢量版与 Mermaid 源文件。
- [编辑与发布说明](02-wal-and-recovery/editor-notes.md)：标题、摘要、设计范围和发布准备。

代码仓库的提交、推送与社区发表分别记录；草稿准备完成不代表已向社区投稿。
