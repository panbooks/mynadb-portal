# 从0到1实现一个分布式时序数据库

面向 Rust、数据库和可观测性系统开发者。围绕十个开发里程碑，从单机读写逐步走向复制、共享存储、分布式协调、路由与运维。

[在线技术专栏](https://panbooks.github.io/mynadb-portal/docs/articles/index.html) · [本地栏目首页](index.html)

## 全系列发布材料

每篇均包含正文、PNG/SVG/Mermaid 配图、图文预览、粘贴发布版 Markdown 和 100 字以内摘要。

| 篇次 | 主题与正文 | 参考版本 / 里程碑 | 粘贴发布版 | 图文预览 | 摘要 |
| --- | --- | --- | --- | --- | --- |
| 一 | [用 Rust、Arrow 和 Parquet 打通写入与 SQL 查询](01-from-http-to-parquet/article.md) | `v0.0.0` / M1 | [复制](01-from-http-to-parquet/article.publish.md) | [预览](01-from-http-to-parquet/preview.html) | [摘要](01-from-http-to-parquet/summary.md) |
| 二 | [写入成功之后，如何用 WAL 找回数据](02-wal-and-recovery/article.md) | `v0.1.0` / M2 | [复制](02-wal-and-recovery/article.publish.md) | [预览](02-wal-and-recovery/preview.html) | [摘要](02-wal-and-recovery/summary.md) |
| 三 | [主从复制、故障检测与切换](03-replication-and-failover/article.md) | `v0.2.0` / M3 | [复制](03-replication-and-failover/article.publish.md) | [预览](03-replication-and-failover/preview.html) | [摘要](03-replication-and-failover/summary.md) |
| 四 | [从本地文件走向对象存储](04-object-storage/article.md) | `v0.3.0` / M4 | [复制](04-object-storage/article.publish.md) | [预览](04-object-storage/preview.html) | [摘要](04-object-storage/summary.md) |
| 五 | [让新写入立即可查](05-memtable-query/article.md) | `v0.4.0` / M5 | [复制](05-memtable-query/article.publish.md) | [预览](05-memtable-query/preview.html) | [摘要](05-memtable-query/summary.md) |
| 六 | [从单机走向 Router、Data、Meta 与 Raft](06-distributed-cluster/article.md) | `v0.5.0` / M6 | [复制](06-distributed-cluster/article.publish.md) | [预览](06-distributed-cluster/preview.html) | [摘要](06-distributed-cluster/summary.md) |
| 七 | [不提升 Standby 的恢复与安全缩容](07-standby-and-scale-in/article.md) | `v0.6.0` / M7 | [复制](07-standby-and-scale-in/article.publish.md) | [预览](07-standby-and-scale-in/preview.html) | [摘要](07-standby-and-scale-in/summary.md) |
| 八 | [表所有权、Hive 分区与查询路由](08-table-ownership-routing/article.md) | `v0.7.0` / M8 | [复制](08-table-ownership-routing/article.publish.md) | [预览](08-table-ownership-routing/preview.html) | [摘要](08-table-ownership-routing/summary.md) |
| 九 | [运维控制台、协议接入与时序分析](09-operations-and-integrations/article.md) | `v0.8.0` / M9 | [复制](09-operations-and-integrations/article.publish.md) | [预览](09-operations-and-integrations/preview.html) | [摘要](09-operations-and-integrations/summary.md) |
| 十 | [正确性补课、OTLP 与 Iceberg 初版](10-correctness-and-interop/article.md) | `v0.9.0` / M10，补充 `.1/.2` | [复制](10-correctness-and-interop/article.publish.md) | [预览](10-correctness-and-interop/preview.html) | [摘要](10-correctness-and-interop/summary.md) |

[一次查看十篇摘要](summaries.md)。篇次参考开发里程碑，正文优先讲清设计，不要求逐标签复现；已有实现、设计示意与验证范围在各篇中分别说明。

## 如何复制到社区

1. 打开对应的 `article.publish.md`，复制全文到支持 Markdown 的编辑器。
2. 从 `summary.md` 复制摘要，单独填写摘要栏。
3. 检查标题、图片、代码块和表格的预览效果。

发布版中的图片使用 `https://panbooks.github.io/mynadb-portal/docs/articles/` 下的完整 HTTPS 地址，跨篇链接指向在线预览，无需逐张替换本地图片路径。知乎等平台能否自动解析或转存外链，以实际编辑器为准；公网链接不等于平台已上传图片。

## 后续更新

- 编辑 `article.md` 和 `summary.md`，摘要保持单段且不超过 100 个字符。
- 在本目录执行 `python3 publish_support.py`，统一更新十篇发布版和摘要汇总；此步骤只依赖 Python 标准库。
- 编辑正文或摘要后执行 `python3 site_support.py`，更新栏目首页、篇章导航和十篇正式阅读页；此步骤需要 Python Markdown 包。
- 修改配图后运行对应目录的 `build_assets.py`，重新生成图片、阅读页、栏目首页与发布版。绘图依赖 Pillow、Markdown 和中文字体，通过 `MYNADB_ARTICLE_FONT` 指定字体路径。

代码仓库的提交、推送与社区发表分别记录；材料准备完成不代表已经向社区投稿。
