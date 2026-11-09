# MynaDB 开源推广逐项检查记录

执行日期：2026-11-09。对应
[原计划](2026-11-09-open-source-promotion-plan.md)。

源码基线：`panbooks/mynadb` 的 `d603624`；保留远程更新后的品牌 README，
只追加状态、贡献和验证入口。文档站基线：`panbooks/mynadb-portal` 的 `f03625e`。
暂停前的修改保留在主仓库 stash 中；本次恢复有效准备文件；原 portal URL 修正仍可从 stash 取回，
独立文档站已使用正确仓库地址。没有恢复原先的 `git-log-main.txt`、`log.txt` 和 Python 缓存。

状态含义：**完成**表示有检查证据；**已准备**表示内容已写好，正式发布或运营动作仍未执行；
**待确认**表示缺少负责人决定或外部证据；**未验证**表示没有实际运行该场景。
草稿、源码存在、一次成功请求均不自动计为正式发布或全面兼容。

## 1. 目标与原则

- [x] 采用“先让陌生开发者理解、运行和评价”的定位，未以 Star 作为唯一成功指标。
- [x] 将实际验证、源码存在和计划目标分开记录。
- [x] README 与功能状态文档说明仍在开发，不作生产就绪声明。
- [x] 宣传材料包含具体工程取舍、运行边界及反馈问题。
- [ ] 持续反馈处理：尚无真实用户反馈样本，不能标记完成。

## 2. 定位与目标用户

- [x] 中英文一句话和段落介绍已准备，见 [首发素材包](2026-11-09-launch-kit.md)。
- [x] 重点对象为 Rust/数据库开发者，其次是遥测和可观测性使用者。
- [x] 不将所有集成实现描述为已经过真实客户端测试。

## 3.1 许可证与版权

| 原计划步骤 | 状态 | 检查结果 / 后续动作 |
| --- | --- | --- |
| 1. 确认代码、公司资产、外部贡献权属 | 待确认 | 需要维护者确认；提交姓名不是权属证明，本次未代作声明 |
| 2. 第三方代码和依赖许可证 | 部分完成 | 主仓库 `docs/promotion/dependency-licenses.csv` 记录 602 个 Cargo metadata 包；`dependency-license-review.md` 记录特殊项；另有 401 个 admin UI npm 包元数据，7 项缺失许可字段。Grafana 没有 npm lockfile；字体、素材和完整 notice 收集仍待完成 |
| 3. 选择根许可证 | 待确认 | 已发现 portal LICENSE 与插件元数据为 Apache-2.0；主项目未据此自动授权 |
| 4. 添加根 LICENSE | 待确认 | 主仓库没有根 LICENSE，待明确授权意愿后添加完整文本 |
| 5. 更新 Cargo 与 README 许可证 | 部分准备 | README 明确当前缺口；Cargo license 未擅自填写 |
| 6. 主子项目声明一致 | 待确认 | 当前不一致已记录，待根许可证决定后处理 |

初查发现 `inferno 0.11.21` 的 CDDL-1.0 表述，以及 `arima`、旧 `ring`、
`webpki` 的 license-file 情况。这里仅记录实际文件和元数据，尚未完成发行物
授权义务审核，不将本次清单当成法律兼容性结论。

## 3.2 GitHub About

证据：[公开 API 快照](promotion-evidence/github-public-snapshot.json)。
浏览器页面可能缓存了旧 About 内容，本次以带观察时间的 API 响应为准。

- [x] Description 已设置，内容与项目定位一致；原计划中的“尚未填写”已过时。
- [x] Website 已设置为 `https://panbooks.github.io/mynadb-portal/`；实际 HTTP 检查首页、中文首页和 Quick Start 均为 200，见 [站点检查](promotion-evidence/live-site-check.json)。
- [ ] Topics 仍为空；建议设置以下 8 个相关主题：

```text
time-series-database tsdb rust datafusion apache-arrow parquet observability influxdb
```

本环境可用 SSH 同步源码，但没有 `gh` 或已配置的 GitHub 管理 API 凭据；未假装
完成 Topics 设置。维护者可以在 About 齿轮中设置，或使用已认证的管理客户端。

## 3.3 安装与 Quick Start

原 README 已被远程更新，本次以该版本为基础，不恢复 stash 中的旧全文替换。
新增主仓库 `examples/quickstart.toml`（回环地址、关闭 MySQL、WAL 和认证）、
`scripts/validation/quickstart_smoke.py`（临时目录和端口、检查实际结果、清理进程）。

| 原计划步骤 | 当前状态 | 证据 / 范围 |
| --- | --- | --- |
| 1. 依赖与克隆 | 完成 | 独立 Git checkout `/tmp/mynadb-promotion-20261109`；不是干净容器；工具链和系统信息见验证记录 |
| 2. 构建并记录平台/工具链/耗时 | 完成 | Oracle Linux 9.5 x86_64 / WSL2，Rust/Cargo 1.92.0、protoc 29.3；构建成功。续跑 890.13 秒，使用此前中断构建的缓存，不当作干净容器或冷构建 benchmark |
| 3. 文档配置启动 | 完成 | README 原始开发配置、新 examples/quickstart.toml 和临时端口 smoke 配置均已启动；数据均放在隔离临时工作目录 |
| 4. 健康检查 | 完成 | 两个流程都收到实际 `/health` 成功响应 |
| 5. 写入与 SQL | 完成 | README 单点返回 204，SQL 核对字段；smoke 两行结果精确匹配 host 和 usage，flush 前后均验证 |
| 6. flush、重启、再次查询 | 完成（限定范围） | 显式 flush 生成 Parquet；两个流程重启后结果正确；WAL 关闭，不是 WAL crash recovery |
| 7. 停止并清理 | 完成 | README 的 CLI stop 和 smoke 的 SIGTERM 均完成，进程已退出，临时数据目录已清理 |
| 8. 独立陌生用户复测 | 未完成 | 自动化运行不能替代外部开发者；需要独立试用记录 |

已修正独立文档站的中英文 Quick Start：移除未经确认的 Rust 1.70
和“60 秒安装”表述，增加构建前提，显式传入本地配置，并解释 WAL 和 flush 边界。
安装页移除不存在的 Release 下载包和未经验证的官方容器拉取指令。
主仓库 `web/portal` 镜像在并行工作中已恢复为 HEAD，本次保留该状态，不覆盖其他操作。

验证证据：

- [构建环境](promotion-evidence/validation-environment.json) · [构建结果](promotion-evidence/build-result.json) · [构建完整输出](promotion-evidence/build-output.txt)
- [README 原配置端到端结果](promotion-evidence/readme-quickstart-result.json) · [新示例配置端到端结果](promotion-evidence/example-config-result.json)
- [两行 smoke 实际请求与响应](promotion-evidence/quickstart-smoke-transcript.json) · [执行结果](promotion-evidence/quickstart-smoke-result.json)
- [本地二进制版本和校验值](promotion-evidence/binary-provenance.json)（仅本地验证产物，未发布）
- [核心测试摘要](promotion-evidence/core-test-summary.json) · [精确命令与耗时](promotion-evidence/core-test-results.json)
- [Parser 完整输出：22 通过](promotion-evidence/unit-parser.txt) · [WAL entry/checksum：2 通过](promotion-evidence/unit-wal.txt) · [InfluxQL：66 通过](promotion-evidence/unit-influxql.txt)

## 3.4 功能状态与限制

- [x] 主仓库 `docs/project-status.md` 已准备能力表：line protocol、SQL、Prometheus、
  OTLP、WAL、集群、Grafana、Iceberg；每项区分源码证据与实际验证范围。
- [x] README 加入开发状态、验证范围和配置说明，保留远程品牌页头与主体内容。
- [x] 明确本地开发配置关闭 WAL；默认 WAL 同步策略与示例设置分别说明。
- [x] 未认证 Prometheus/OTLP 客户端版本、Grafana 安装、集群故障恢复和完整 SQL 兼容性。
- [x] 文档站安装页将硬件表标成规划参考，未把 ARM64 或未经测试的系统当成已支持平台。

## 3.5 可识别的版本

| 原计划步骤 | 状态 | 检查结果 |
| --- | --- | --- |
| 1. 版本号与平台 | 待统一 | 公共 Release 为 `v0.0.1`，Cargo 为 0.1.0，历史标签另有 v0.1.0/v0.1.1；需统一命名和支持平台 |
| 2. 构建与核心测试 | 完成（限定范围） | 构建通过；parser 22、WAL entry/checksum 2、InfluxQL 66，共 90 个选定库单元测试通过；不是完整测试套件或 crash recovery 认证 |
| 3. 标签和 GitHub Release | 已存在，未新增 | v0.0.1 已发布；本次未创建标签或新 Release |
| 4. 摘要、安装、变化、已知问题 | 已准备 | 主仓库 `docs/promotion/release-checklist.md` 有可审核的发布说明模板和验收项 |
| 5. 二进制与校验值 | 未完成 | 现有 Release assets 为空；未制造下载链接或发布未测二进制 |

## 4. 贡献入口

- [x] 已准备主仓库 `CONTRIBUTING.md`，包含依赖、构建、单元测试、忽略的 HTTP 集成测试、PR 与文档流程。
- [x] 已准备 Bug / Feature YAML Issue 表单，以及 Discussions 联系入口。
- [x] 已准备 10 个任务草稿，均写明背景、相关文件、验收标准和测试方法：
  `docs/promotion/contributor-tasks.md`。涉及架构和数据安全的任务未标为 good first issue。
- [ ] 未发布 GitHub Issues 或设置标签；没有管理 API 会话，不将本地草稿算作已创建 Issues。
- [x] 公开 API 显示 Issues 和 Discussions 已启用，Release 已存在。
- [ ] 尚无真实 Issue/PR 需要回应；不编造响应记录。

## 5.1 首发故事

- [x] 中英文文章草稿已准备，见 [首发素材包](2026-11-09-launch-kit.md)。
- [x] 文章围绕小批次写入、Parquet、schema 对齐、DataFusion 查询及 WAL/flush 区别展开。
- [x] 没有代维护者编造个人经历或性能成绩；发布前由作者确认动机和事实。
- [ ] 尚未发布到社区，最终运行证据和许可证仍是发布前置条件。

## 5.2 基础素材

- [x] 中英文短介绍已准备。
- [x] 原生 SVG 封面：[`images/promotion-cover.svg`](../../images/promotion-cover.svg)，复用现有项目 Logo，无性能领先声明。
- [x] 素材包包含与源码路径对应的单机 Mermaid 架构图，不将集群或恢复当成已验证。
- [ ] 真实写入查询截图待采集；不将拼接终端文字当成实际截图。
- [ ] 60–120 秒实录待完成；已准备 90 秒分镜，自动 transcript 不冒充视频。

## 5.3 系列文章

- [x] 在素材包中准备了总览、写入、查询、Compaction、WAL、集群的六篇顺序与范围。
- [ ] 目前只有总览中英文草稿，其余不计为已撰写或已发表。

## 6. 渠道与发布

- [x] 准备中文先行、反馈修复、英文独立试用后再考虑 Show HN 的顺序。
- [x] 已复查 [Show HN 官方规则](https://news.ycombinator.com/showhn.html)：需可供试用，不组织刷票评论。
- [x] 英文介绍和反馈邀请已准备；不提前声称通过所有验证。
- [ ] 掘金、知乎、V2EX、Bilibili、Reddit、周刊等渠道的现行投稿规则要在实际发布前分别复查。
- [ ] 没有登录或向上述社区发帖、私信、评论，也没有替作者作公开承诺。

## 7. Benchmark 与可信度

- [x] 已准备主仓库 `docs/promotion/benchmark-protocol.md`：硬件、配置、WAL、数据、重复次数、正确性和原始输出要求。
- [x] 明确已有 `benchmarks/` 是历史实验，本次不据此宣称当前领先。
- [ ] 本次没有执行新的吞吐/延迟基准，不能用小规模 smoke 耗时当 benchmark。
- [ ] 未运行 TSBS 或跨系统比较；实际适配、持久化条件和查询语义仍待验证。

## 8–9. 30 天与 90 天计划

- [x] [周报与阶段安排](2026-11-09-promotion-weekly-log.md) 已准备每阶段进入条件、行动和完成证据。
- [x] 第 1 周仍有许可证和独立试用前置项，未为了排期提前进入正式推广。
- [ ] 后续发布、修复、月度更新、真实案例均是待执行目标，不能一次检查就标记完成。

## 10. 指标与每周复盘

- [x] 保存公开 API 基线：Star 0、Fork 0、Open Issues 0；附带真实观察时间。
- [x] 准备每周日志模板，包含试用成功率、问题类型、贡献和渠道来源。
- [ ] 私有 Traffic 的访客、clone 和来源未获取；公开 API 快照不冒充 Traffic 数据。
- [ ] 尚无外部试用样本，不计算无依据的转化率或成功率。

## 11. 文案草稿

- [x] 完成可审核的中英文短介绍及技术文章草稿，链接指向 `panbooks/mynadb`。
- [x] 文字区分开发状态、实现存在、未验证兼容性与实际运行结果。
- [ ] 正式发布前需将运行证据和最终许可证核对一遍。

## 12. 三项优先行动的当前结论

1. **许可证与 Quick Start**：权属和许可证等待维护者决定；源码构建、README 运行、smoke 和 90 个选定核心单元测试已通过，独立用户复测尚无样本。
2. **技术文章**：中英文草稿和架构图已准备，尚未发表。
3. **真实演示**：分镜及自动化检查工具已准备，截图和视频需要实际录制。

本记录是逐项检查及准备工作的结果，不表示 30/90 天运营动作已经发生。


## 本次工作收尾状态

- 所有本次启动的构建、选定测试与临时数据库进程均已结束，没有继续后台编译。
- 本记录描述验证与准备结果；提交、推送和文档站部署状态以 Git 历史及 GitHub Actions 为准。没有发布社区帖子或 GitHub Issues。
- 主仓库 README 的远程品牌页头保留；`web/portal` 镜像保持 HEAD。
- 另一路工作新建的 `docs/analysis/development-commit-*` 和 development-milestones 文件未由本次任务修改或清理。
- 原 stash 保留；旧导出的日志和 Python 缓存没有恢复到工作目录。
