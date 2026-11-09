# MynaDB 开源推广分析与执行计划

> 制定日期：2026-11-09
> 项目：[GitHub](https://github.com/panbooks/mynadb) · [中文官网](https://panbooks.github.io/mynadb-portal/zh/index.html)

执行进度：[逐项检查记录](2026-11-09-open-source-promotion-checklist.md) · [首发素材草稿](2026-11-09-launch-kit.md) · [周报与阶段安排](2026-11-09-promotion-weekly-log.md)

## 1. 目标与原则

推广的首要目标是让第一批对时序数据库、Rust 和可观测性感兴趣的开发者，能够理解、运行和评价 MynaDB，进而积累真实用户、贡献者和持续关注。Star 是一个结果指标，应与试用、反馈和贡献一起观察。

推广遵循以下原则：

- **先验证，再宣传**：只宣传实际测试过的能力和适用范围。
- **降低试用门槛**：让陌生用户通过清晰的文档完成启动、写入和查询。
- **公开项目状态**：说明已知限制、数据持久化设置和当前成熟度。
- **以技术内容建立信任**：分享具体设计、取舍、测试和问题，而不是只请求 Star。
- **持续回应反馈**：把真实问题转化为文档、测试和产品改进。

## 2. 项目定位与目标用户

### 2.1 推荐定位

> MynaDB 是一个用 Rust 构建的时序数据库项目，基于 Apache Arrow、Parquet 和 DataFusion，支持 SQL 查询及多种遥测数据接入方式。

English:

> MynaDB is a time-series database written in Rust, built with Apache Arrow, Parquet, and DataFusion. It supports SQL queries and ingestion through InfluxDB line protocol and other telemetry protocols.

建议同时说明项目仍在开发，并根据实际测试结果描述功能边界。未充分验证前，避免使用“生产级”“全面兼容”“性能领先”等表述。

### 2.2 初期重点用户

| 用户 | 关注点 | 可能的参与方式 |
| --- | --- | --- |
| Rust、数据库和系统开发者 | 存储引擎、DataFusion、WAL、Compaction、Raft | 阅读源码、讨论架构、提交 Issue 和 PR |
| 监控与可观测性工程师 | 数据接入、SQL、Grafana、部署和稳定性 | 试用、反馈需求、验证集成 |
| 时序数据使用者 | 数据模型、查询、保留策略和维护成本 | 提供场景、试用和分享使用经验 |

初期建议以技术开发者为主要传播对象，同时邀请有真实时序数据需求的工程师试用。

## 3. 推广前的准备

### 3.1 明确许可证与版权

截至本分析制定时，仓库根目录未发现明确的项目级 `LICENSE` 文件；Grafana 插件中的许可证说明不能自动代表整个仓库。应先确认当前仓库状态和所有代码的版权归属，再决定项目许可证。

执行步骤：

1. 确认代码、公司资产和外部贡献的版权归属。
2. 检查第三方代码与依赖的许可证及所需声明。
3. 根据项目实际授权意愿选择许可证。
4. 在根目录添加完整的许可证文件。
5. 更新 `Cargo.toml` 和 README 的许可证说明。
6. 检查主项目与子项目的许可证表述是否一致。

参考：[GitHub：为仓库选择许可证](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)。许可证选择应结合实际权属与授权需求。

### 3.2 完善 GitHub 仓库信息

分析时仓库页面显示 About 信息尚未填写；执行前请再次确认当前状态。

在仓库首页 **About → 齿轮** 中设置：

- Description：`A Rust time-series database with SQL, Arrow, Parquet, and InfluxDB line protocol.`
- Website：`https://panbooks.github.io/mynadb-portal/zh/index.html`
- Topics：`time-series-database`、`tsdb`、`rust`、`datafusion`、`apache-arrow`、`parquet`、`observability`、`influxdb`。

只使用与项目实际能力相关的主题。

### 3.3 验证安装与 Quick Start

当前 README 提供源码构建和单机运行说明，但此前构建验证未完整结束。正式推广前应在干净环境中完成一次端到端验证：

1. 安装依赖并克隆仓库。
2. 构建项目，记录平台、工具链与构建时间。
3. 使用文档中的配置启动服务。
4. 检查健康接口。
5. 写入样例数据并执行 SQL 查询。
6. 手动 flush，重启服务后再次查询。
7. 按文档停止进程并清理示例数据。
8. 由未参与项目的开发者独立重复上述步骤。

当前本地示例配置关闭了 WAL。重启验证前应确认数据已经 flush，并按照实际配置解释持久化结果。记录并修复安装、权限、端口和文档问题。

后续可考虑提供经过验证的预编译二进制、Docker 镜像或自动化示例脚本。只有实际可用后才将其写入 Quick Start。

### 3.4 说明功能状态和限制

在 README 或单独文档中维护一张能力表，基于测试结果填写：

| 能力 | 需要记录的信息 |
| --- | --- |
| Line protocol | 已测试语法、字段类型、时间戳精度、已知不支持项 |
| SQL | 支持的查询和已知限制 |
| Prometheus / OTLP | 已测试的客户端、版本和兼容性范围 |
| WAL | 开启方式、同步策略、恢复行为和测试范围 |
| 集群 | 测试拓扑、故障恢复能力和已知限制 |
| Grafana | 插件构建、安装和发布状态 |

说明当前适合的使用场景、数据安全配置和不适用场景。代码中存在某项实现并不等于该能力已经全面验证。

### 3.5 发布可识别的版本

准备首个版本时：

1. 确定版本号和支持的平台。
2. 构建并运行核心测试。
3. 创建版本标签和 GitHub Release。
4. 编写功能摘要、安装方法、兼容性变化和已知问题。
5. 如提供二进制，附带平台信息和校验值。

## 4. 建立贡献入口

- 添加 `CONTRIBUTING.md`，说明开发环境、构建、测试、分支和 PR 流程。
- 添加 Bug 和功能请求 Issue 模板。
- 创建 5–10 个范围清晰的任务，并在适用时标记 `good first issue`、`help wanted` 或 `documentation`。
- 对每个任务写清背景、相关文件、验收标准和测试方法。
- 使用 Issues 跟踪问题，Discussions 讨论想法，Releases 发布版本。
- 及时确认收到 Issue 和 PR；对不接受的建议说明原因。

## 5. 内容与素材准备

### 5.1 首发故事

使用“问题—设计—结果—反馈”的结构：

1. 为什么开发 MynaDB。
2. 项目面向哪些场景。
3. 目前实现了什么。
4. 一两个具体的技术问题和设计取舍。
5. 当前限制与后续计划。
6. 如何试用，以及希望获得什么反馈。

中文标题示例：

- 我用 Rust 构建了一个时序数据库：从 Line Protocol 到 Parquet 和 SQL
- 从零实现时序数据库：MynaDB 的架构与设计
- 基于 Arrow、Parquet 和 DataFusion，我做了一个 Rust 时序数据库

英文标题示例：

- Building MynaDB: a time-series database in Rust with Arrow, Parquet, and DataFusion
- Show HN: MynaDB – a time-series database in Rust

### 5.2 基础素材

准备：

- 一句话和一段话的中英文介绍。
- 项目封面：Logo、名称、定位、项目地址。
- 一张与当前实现一致的架构图。
- 一张真实的写入和查询截图。
- 一个 60–120 秒演示：启动、写入、查询、展示结果和反馈入口。

技术文章应解释具体问题，例如：缓存如何减少 Parquet 小文件，WAL 和 flush 的配置如何影响故障恢复。避免把未经验证的设计画成已完成的能力。

### 5.3 系列文章

| 顺序 | 主题 | 建议内容 |
| --- | --- | --- |
| 1 | MynaDB 总体介绍 | 目标、架构、运行方式和限制 |
| 2 | 写入路径 | Line protocol、schema 映射、缓存、WAL 和 flush |
| 3 | 查询路径 | 表发现、内存数据、Parquet 和 DataFusion |
| 4 | Compaction | 小文件、触发条件、资源消耗和并发 |
| 5 | WAL 与恢复 | 同步策略、恢复过程和验证方法 |
| 6 | 集群设计 | Router、Data、Meta、路由和故障场景 |

所有文章均应基于真实代码和可复现结果。

## 6. 渠道与发布方式

### 6.1 中文渠道

| 渠道 | 内容 | 执行动作 |
| --- | --- | --- |
| 掘金 | 带架构图、代码和运行步骤的技术文章 | 先发项目总览，再连载技术细节；回应评论 |
| 知乎 | 技术背景和设计取舍 | 解释为什么选择 Rust、Arrow、Parquet、DataFusion |
| V2EX | 项目展示和具体问题征求 | 说明项目状态，提出希望获得的架构或使用反馈 |
| Bilibili | 实际操作演示 | 展示启动、写入、查询和结果，附项目及反馈链接 |
| Rust / 数据库社区活动 | 技术分享 | 分享具体工程问题与解决过程 |

发布前查看各平台及社区当时的规则。避免短时间重复发布相同广告或只要求 Star。

### 6.2 英文渠道

| 渠道 | 内容与注意事项 |
| --- | --- |
| Hacker News Show HN | 项目应可让读者直接试用；发布当天准备回答设计、可靠性和兼容性问题 |
| Reddit 的 Rust、数据库和开源社区 | 根据每个社区当前规则发布有技术细节的介绍和具体问题 |
| Rust 周刊、数据库和可观测性社区 | 投稿技术文章或经过验证的重要版本更新 |
| GitHub Discussions 和个人技术博客 | 长期沉淀设计、路线图、FAQ 和项目进展 |

[Show HN 指南](https://news.ycombinator.com/showhn.html)要求提交可供体验的作品，并禁止组织朋友刷投票或评论。

### 6.3 建议的英文首发评论

```text
Hi HN, I’m the author of MynaDB.

I started this project to explore how Rust, Apache Arrow, Parquet,
and DataFusion can be used to build a time-series database.

The project is still under development. I would especially appreciate
feedback on the architecture, data model, and getting-started experience.

GitHub: https://github.com/panbooks/mynadb
```

发布时可补充经过验证的功能，并明确已知限制。

## 7. Benchmark 与可信度

### 7.1 先建立自身基线

优先测量写入吞吐、查询延迟、内存和 CPU 占用、磁盘使用、不同批量与数据规模的影响、flush 前后表现及重启恢复时间。

记录并公开：

- CPU、内存、磁盘、操作系统。
- MynaDB 和 Rust 版本，以及完整配置。
- WAL 是否开启、是否同步写入。
- 数据生成方式、规模、批量大小。
- 查询语句、测试次数和结果。
- 已知限制以及如何复现。

### 7.2 再考虑标准基准和横向比较

可研究 [Time Series Benchmark Suite（TSBS）](https://github.com/timescale/tsbs)，并说明工具及适配方式的测试范围和限制。

比较不同系统时，应尽量统一硬件、数据、持久化条件和查询语义，校验结果正确性，并公开所有版本与配置。没有充分证据时，不作性能领先或倍数优势的结论。

## 8. 30 天执行计划

| 时间 | 目标 | 具体行动 |
| --- | --- | --- |
| 第 1 周 | 完成推广基础 | 定位、License、GitHub About、干净环境 Quick Start 验证、项目状态和素材 |
| 第 2 周 | 中文首发 | 掘金文章、开发者社区反馈、短视频；将高频问题整理为 Issue |
| 第 3 周 | 英文传播准备 | 根据反馈修正文档，完成英文文章和外部试运行；准备就绪后考虑 Show HN |
| 第 4 周 | 修复与复盘 | 解决最影响试用的 3 个问题，发布项目进展、FAQ 和后续计划 |

不要为了赶首发日期跳过可运行性和许可证检查。

## 9. 90 天计划

| 时间 | 目标 | 重点 |
| --- | --- | --- |
| 第 1–30 天 | 让用户理解并运行 | License、Quick Start、项目状态、首发文章和演示 |
| 第 31–60 天 | 建立技术可信度 | 兼容性测试、WAL 与恢复文档、架构文章、初步 benchmark |
| 第 61–90 天 | 培育持续社区 | Release、贡献指南、Roadmap、月度更新、试用案例 |

建议维护公开 Roadmap 和简短的月度更新：已完成事项、用户反馈、下月计划及欢迎贡献的任务。计划应区分目标和已经验证的结果。

## 10. 数据指标与每周复盘

除 Star 外，记录以下指标：

| 指标 | 用途 |
| --- | --- |
| Star 增量 | 了解关注趋势 |
| 仓库独立访客与完整 clone | 了解访问和获取代码的情况 |
| Issue 和问题类型 | 发现试用障碍及真实需求 |
| 外部贡献者和 PR | 了解参与情况 |
| Quick Start 成功率 | 衡量安装与文档体验 |
| 真实试用者和使用场景 | 衡量实际使用价值 |
| 流量来源和内容表现 | 判断渠道效果 |

GitHub **Insights → Traffic** 提供最近 14 天的访客、完整 clone、部分来源和热门内容；建议每周记录一次。[GitHub Traffic 文档](https://docs.github.com/en/repositories/viewing-activity-and-data-for-your-repository/viewing-traffic-to-a-repository)

每周记录模板：

```text
日期：
Star 总数 / 本周增量：
仓库独立访客：
完整 clone：
新增 Issue / 外部贡献者：
本周发布渠道：
最常见反馈：
下周改进：
```

访问多但试用少时，检查定位和入门门槛；安装问题集中时，优先修复 Quick Start；具体原因需要结合实际反馈判断。

## 11. 推广文案草稿

### 中文

> 最近我在用 Rust 开发一个时序数据库项目 **MynaDB**。
>
> 它使用 Apache Arrow 和 Parquet 处理与存储数据，并基于 Apache DataFusion 提供 SQL 查询能力。项目包含 InfluxDB line protocol 写入、内存缓存、WAL、后台 flush 和 compaction 等实现，也在探索集群架构。
>
> 项目仍在开发中，我正在持续完善运行体验、测试和文档。如果你对 Rust、数据库内核或可观测性感兴趣，欢迎试用并提出建议。
>
> GitHub：https://github.com/panbooks/mynadb
> 官网：https://panbooks.github.io/mynadb-portal/zh/index.html

### English

> I’m building **MynaDB**, a time-series database written in Rust.
>
> It uses Apache Arrow and Parquet for data processing and storage, and Apache DataFusion for SQL queries. The project includes line protocol ingestion, an in-memory cache, WAL, background flushing, and compaction, with cluster components under development.
>
> MynaDB is still evolving. I’d appreciate feedback on the architecture, documentation, and getting-started experience.
>
> GitHub: https://github.com/panbooks/mynadb

发布前根据最新测试结果核对功能、兼容性和成熟度描述。

## 12. 最优先的三项行动

1. **明确许可证，并完成干净环境下的 Quick Start 验证。**
2. **写一篇技术文章，解释项目动机、架构、具体设计问题与当前限制。**
3. **录制真实的启动、写入和查询演示，先收集反馈并修复问题，再扩大传播。**
