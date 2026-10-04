# PsychTalk Hub — 架构记录

日期：2026-10-04｜最后验收步骤：08｜状态：用户确认本地验收通过；GitHub CI 待验证，第 09 步未开始

本文记录当前仓库事实与后续计划的架构边界，不代表完整应用、接口或部署已经实现。测试由用户执行；用户已分别确认第 01–08 步“通过”。第 08 步按用户确认记录本地验收，未提供逐项输出；GitHub CI 和 Linux 兼容性仍待验证。收到本步确认后已先请求打开并更新 [progress.md](progress.md)，再补充本文件的文件职责、验收与洞察；助手未代运行检查或测试，第 09 步未开始。

## 1. 当前仓库状态

仓库已初始化 Git，已有本地提交及 GitHub 远程；本次不提交或推送。当前复用功能分支 `docs/clarify-implementation-plan`，保留此前文档的未提交修改，不覆盖或撤销这些改动。

第 03 步已在 backend 建立 Django config 项目和唯一的 events 业务应用，并移除 backend/.gitkeep。第 04 步已加入环境配置、独立 PostgreSQL 17、健康检查、基础测试与 backend CI 工作流，移除工作流占位文件；frontend 仍只有占位文件。第 05 步的 Event 模型、初始迁移和 9 个模型测试已由用户确认本地验收。第 06 步增加 Resource、0002_resource 迁移及 14 个测试，已由用户确认本地验收；助手只生成迁移，未应用迁移或代运行验收。第 07 步增加 EventResource、0003_event_resource 和 13 个测试，已由用户确认本地验收；助手只生成迁移，未应用迁移或运行检查/测试。第 08 步增加基础 Admin、三份确认模板和 21 个测试，已由用户确认本地验收，累计 69 个测试方法；助手未代运行验收，无逐项输出。活动 API、React、DOI 导入及演示数据尚未实现。新增文件均未暂存或提交，本次没有 GitHub 更新，CI 线上运行仍未验证。

独立 CPython 3.13.16 安装于项目内被忽略的 .tools/python313，项目虚拟环境位于 backend/.venv，不读取系统 site-packages。安装未修改 PATH、文件关联或启动器，未替换 Anaconda 3.11.5 或既有 Python 3.10。后端直接与传递依赖已按精确版本锁定并安装到该虚拟环境；Gunicorn 限定 Linux 安装，未在 Windows 安装或运行。环境准备日志不等同于用户验收通过。

## 2. 已有文件与目录职责

以下路径相对仓库根目录；本表是当前文件说明，不是代码目录已建立的声明。

| 文件或目录 | 当前作用 |
| --- | --- |
| `.gitignore` | 排除环境变量文件、虚拟环境、依赖、缓存和构建产物；第 03 步新增 .tools/ 排除本机解释器、安装包与依赖解析报告；允许提交无真实值的环境变量示例 |
| `AGENTS.md` | 贡献者规则：必读资料、计划目录、风格、测试、分支、权限及配置边界；其中开发命令仅在脚手架建立后可用 |
| `memory-bank/` | 产品、技术与分步执行依据，以及实施过程中的架构和进度交接记录 |
| `memory-bank/design-document.md` | 英文产品与交互规范，规定两页公开体验、管理流程、内容规则、视觉及验收 |
| `memory-bank/design-document.zh-CN.md` | 相同产品规范的中文对应版本，两种语言需同步维护 |
| `memory-bank/tech-stack.md` | 技术选型、部署边界、数据一致性、预览会话与权限要求；Public API contract 为字段与类型的唯一详细规范 |
| `memory-bank/implementation-plan.md` | 40 个依赖有序的实施步骤；第 01–08 步已按用户确认本地验收，第 09 步未开始；GitHub CI 待验证 |
| `memory-bank/architecture.md` | 本文件，记录初始事实、计划职责及验收后洞察，后续随实际功能更新，不把设计目标写成已有代码 |
| `memory-bank/progress.md` | 第 01–08 步的改动、用户验收来源、未验证边界与下一步交接；区分本地通过和 GitHub CI 未验证 |
| `frontend/.gitkeep` | 保留前端目录骨架的占位文件，无 React 项目或依赖配置；实际脚手架留到第 13 步 |
| `.python-version` | 记录独立 CPython 的准确版本 3.13.16，供后续开发、CI 与部署统一运行时；不会自动切换系统解释器 |
| `backend/requirements.in` | 直接依赖约束与平台条件的维护来源；更新时需要重新解析，不能当作锁定安装文件 |
| `backend/requirements.txt` | 可移植的精确版本锁，覆盖直接与传递依赖；Gunicorn 仅在 Linux 安装，无本机路径或凭据 |
| `backend/README.md` | 当前环境、独立数据库启停/初始化、环境配置、用户验证指令及未验证边界；不是完整应用部署指南 |
| `backend/manage.py` | Django 管理入口，加载 config.settings；第 04 步已在新开发库执行基础迁移 |
| `backend/config/__init__.py` | Django 项目配置包标识 |
| `backend/config/settings.py` | 公共设置，加载环境配置，保留英文、伦敦时区，启用数据库会话和隔离测试运行器；生产安全 Cookie/HTTPS 已准备，静态集成及部署未完成 |
| `backend/config/urls.py` | 原生 Admin 与 /healthz/ 路由；没有活动 API 或 React 页面，用户已确认本地步骤验收，无独立浏览器日志 |
| `backend/config/wsgi.py` | WSGI application 入口，供未来 Gunicorn 使用，当前没有运行生产服务器 |
| `backend/config/asgi.py` | Django 默认生成的 ASGI 入口，保留但未配置对应服务器；生产设计仍使用 WSGI |
| `backend/events/__init__.py` | 唯一业务应用的 Python 包标识 |
| `backend/events/apps.py` | EventsConfig 应用注册与默认主键类型 |
| `backend/events/models.py` | 用户确认本地验收的 Event、Resource 和 EventResource；普通保存前 full_clean，书目标识规范化及字段约束；关联保存活动语境，定义组合唯一、确定排序与外键删除策略 |
| `backend/events/admin.py` | 第 08 步注册三个模型，定义伦敦时间输入/控件、活动公开地址/保存消息、手动书目、已有资料关联与不可更改的关联身份；活动确认及双模型删除权限、全部资源删除拒绝；用户确认本地验收 |
| `backend/events/templates/admin/events/event/delete_confirmation.html` | 单条活动删除确认文案；继承原生模板，保留权限、受保护对象、删除清单、CSRF 与确认/取消控件 |
| `backend/events/templates/admin/events/event/delete_selected_confirmation.html` | 批量活动删除确认文案；继承原生模板，保留选择记录、原生权限/确认和 CSRF，不重写删除收集器 |
| `backend/events/templates/admin/events/eventresource/delete_confirmation.html` | 单条阅读关联移除确认文案，保留原生确认路径；不删除共享书目 |
| `backend/events/tests/test_admin.py` | 第 08 步 21 个真实 Admin 请求测试：增改、字段错误、伦敦时间/DST、公开地址、手动来源/空值、关联复用/身份、权限、确认/删除保留、资源全局禁删及真实 CSRF；用户确认本地验收，无逐项输出，助手未代运行；测试账号仅在隔离库创建 |
| `backend/events/views.py` | 只读 API 视图位置占位；接口留到第 10–12 步 |
| `backend/events/migrations/__init__.py` | 迁移包标识 |
| `backend/events/migrations/0001_initial.py` | Django 生成的初始 Event 表迁移，含默认值、非空字段、可空唯一 seed_key 和检查约束；用户确认本步迁移验收，助手只生成，未代应用 |
| `backend/events/tests/test_event.py` | 第 05 步 9 个模型测试，覆盖存取、默认值、输入拒绝、NULL/唯一约束、绕过模型校验的数据库保护、UTC 时间及空测试库迁移；用户确认本地验收，无逐项输出 |
| `backend/events/migrations/0002_resource.py` | Django 生成的 Resource 表迁移，依赖 0001_initial；包括唯一 DOI/seed_key、必填字段、年份/类型/来源及标准化 DOI 检查；用户确认迁移验收，助手只生成、未代应用 |
| `backend/events/tests/test_resource.py` | 14 个测试，覆盖书目存取、校验、规范化、数据库保护、手动资料独立保存及迁移；用户确认本地验收，无逐项日志；包含仅供测试的 DRF 书目序列化探针，不是公开 API |
| `backend/events/migrations/0003_event_resource.py` | Django 生成的关联表迁移，依赖 0002_resource；整数主键、必填外键、推荐理由/顺序默认值、活动/资源组合唯一和默认排序；用户确认本地迁移验收，助手只生成、未代应用 |
| `backend/events/tests/test_event_resource.py` | 13 个测试：关联存取、独立活动语境、唯一性、负数及同值排序、字段/外键约束、移除与删除保留规则，以及空 PostgreSQL 测试库迁移；用户确认本地验收，无逐项输出；Admin 权限测试位于 test_admin.py，API 仍未实现 |
| `backend/events/tests/__init__.py` | 后端测试包标识 |
| `.tools/`、`backend/.venv/` | 被忽略的本机解释器、下载/解析中间产物和隔离依赖；不随 Git 克隆分发，另一台机器需独立重建 |
| `.github/workflows/backend.yml` | Linux 使用锁定 Python、PostgreSQL 17.11，检查依赖、系统、迁移和测试；尚未提交/推送或线上运行 |
| `backend/config/environment.py` | django-environ 配置入口：开发/测试读取对应私有文件，生产仅读进程变量；校验密钥、PostgreSQL、隔离测试库及生产 TLS/主机/DEBUG |
| `backend/config/test_runner.py` | 标准 DiscoverRunner 的保护层，数据库测试初始化前拒绝生产配置 |
| `backend/config/health.py` | GET/HEAD readiness probe：SELECT 1，成功 200，故障安全 JSON 503，不缓存、不访问 Crossref，其他方法 405 |
| `backend/events/tests/test_infrastructure.py` | 5 个方法，覆盖真实 PostgreSQL 17/隔离库/会话迁移、健康检查/故障/方法及 Admin 登录页；用户确认本地验收，无逐项输出 |
| `backend/events/tests/test_environment.py` | 7 个方法，覆盖错误配置、库隔离、生产缺项/TLS/DEBUG、环境优先级和生产测试拒绝；用户确认本地验收，无逐项输出 |
| `backend/.env.example` | 密钥和数据库 URL 留空的配置示例，无真实凭据，可随 Git 提交 |
| `backend/scripts/local_database.py` | Windows 本机初始化/启停/状态工具，仅操作 .tools/postgres17；初始化拒绝已有数据或环境文件，使用 SCRAM、随机凭据和非超级用户，不注册服务或修改旧安装 |
| `backend/.env、backend/.env.test` | 被忽略的开发/测试持久随机密钥与本机连接；测试运行器另用 test_psychtalk；不打印、提交或推送 |
| `.tools/postgres17/` | 被忽略的 PostgreSQL 17.11 二进制、独立数据目录、日志与私有管理员连接文件；不随 Git 分发 |

## 3. 计划架构与实现边界

backend/config 已有环境配置与健康检查，backend/events 的三个业务模型与基础 Admin 已由用户确认本地验收；公开 API、DOI 服务与 frontend/src 尚不存在。工作流文件已准备但没有线上运行结果。下表描述完整产品的未来职责，不表示对应功能已运行或验证。

| 计划位置 | 计划职责 |
| --- | --- |
| `backend/` | Django 项目配置与管理入口；负责 API、Admin、生产页面入口和静态集成 |
| `backend/events/` | 唯一业务应用；管理 Event、Resource、EventResource，包含序列化、Admin 表单、Crossref 服务与后端测试 |
| `frontend/src/` | React 首页与活动详情、只读请求模块、当前活动标题搜索、普通 CSS 和可访问性状态 |
| `.github/workflows/` | GitHub Actions，使用 PostgreSQL 执行后端测试与迁移检查，并执行前端 lint 和构建 |

计划中的浏览器通过同域 Django 服务读取已保存活动和资料；管理员通过 Django Admin、会话和 CSRF 管理内容。PostgreSQL 保存业务数据与数据库会话；Crossref 仅由管理流程触发。Node.js 用于开发与前端构建，生产请求由 Django、Gunicorn 和 WhiteNoise 处理。上述业务路径均为设计目标，尚无运行验证。

## 4. 后续实现必须保持的边界

- React 只有两个公开页面，管理使用 Django Admin；不增加会员、支付、聊天、AI 推荐或多租户。
- Event 负责活动；Resource 的书目共享；EventResource 单独保存每场活动的推荐理由和顺序。删除活动仅删除关联，保留资源；禁用共享资源删除。
- 公开 API 只读，字段与空值按技术栈契约；搜索在当前活动已加载资料中执行，不增加搜索写入入口。
- DOI 预览可写受保护的数据库会话，不创建或修改 Resource、EventResource；固定 15 分钟有效，各标签页独立。最终确认验证权限，短事务保存并保证重复或并发操作不产生重复关联。
- 独立使用 Python 3.13、PostgreSQL 17，保留已有环境，开发、测试、生产数据库分开；版本锁定和 CI 按实施计划提前建立，不能把规划写成已配置。
- 免费 Render 单 Web Service 与同区域数据库是部署目标；启动先迁移，初始化管理员和示例数据单独执行。账号、免费资源及线上可用性仍需后续实际验证。

## 5. 验收交接点

2026-10-03，用户回复“通过”，确认第 01 步文档验收。验收范围为文件可读、初始架构事实准确、中英文产品规则一致、文档链接有效，以及不存在带 @ 前缀或额外复制的设计文件。用户未提供逐项输出或日志，助手未代为运行测试，不据此声明应用运行、数据库、CI 或部署通过。

第 01–08 步按用户确认先记录进度，再更新架构。验收依据为用户回复“通过”，无逐项日志，助手未代运行验收测试。此确认记录为本地步骤通过，不涵盖 GitHub CI、Linux 兼容性、实际生产连接或部署。第 08 步确认后已先请求打开并更新进度，再补充本文件的验收洞察；实施与验收记录见第 19 节。未推进第 09 步，等待用户新指令。

## 6. 第 01 步验收后的架构洞察

- **文档分工需要保持明确。** 两份 design-document 文件负责同一套产品行为，tech-stack.md 的 Public API contract 负责详细接口字段，implementation-plan.md 负责执行顺序；本文件解释实际结构，progress.md 记录推进与验收证据。实现时引用已有依据，不另建相互竞争的设计或接口副本。
- **文件职责与计划目录不是同一种状态。** 第 01 步验收时，只有根目录文件及 memory-bank 文件已存在，后端、前端和工作流目录尚未建立。第 02 步只增加基础目录与占位文件；后续创建实际模块后逐一记录文件用途，不能提前填入假设中的 models、services 或测试文件。
- **共享书目与活动语境必须分开。** 计划中的 Resource 保存共享书目，EventResource 保存各活动理由和排序，这解释了已有 DOI 的复用，以及移除关联、删除活动时保留资源的规则；数据库约束与事务仍待实现。
- **预览状态不等同于已发布资源。** 数据库会话允许保存临时预览，Resource/EventResource 只在确认时写入。这两个保存边界需在后续文件职责和测试中分别说明，不能把会话写入误报为资料已公开。
- **公开阅读应独立于外部查询。** 访客读取已保存资料，Crossref 只由后台获取动作使用；服务调用应与最终保存事务分开。前端不直接查询 Crossref，也不需要独立 Node.js 后端。
- **第 01 步通过仅确立准备工作的交接点。** 当时依赖安装、目录骨架、代码、自动化检查与部署都没有实施。本文件和进度记录必须继续区分计划、已实现和用户验证结果。

## 7. 第 02 步验收交接

- 已复用现有 Git 仓库与功能分支，不重新初始化、不切换分支、不提交或推送；保留所有现有文档。
- 新增三个 .gitkeep 文件，仅用于让基础目录可随未来提交保留；目前尚未提交，不能宣称 GitHub 已包含这些目录。建立实际项目后可移除相应占位文件。
- 沿用现有 .gitignore：环境变量文件、虚拟环境、Python 缓存、node_modules、dist 与 staticfiles 均有排除规则，.env.example 例外保留。用户已确认本步验证通过；没有逐项输出，不将配置阅读当作助手执行测试的证据。
- 用户验证期间遇到 Git 所有权检查，已提供仅信任本项目路径的处理说明；助手未修改用户全局 Git 配置。后续开发者使用不同账号时仍可能需要在自己的用户配置中处理信任，不能由沙箱中 Git 可用推断用户终端也可用。
- 第 02 步时未代用户执行验证，也未建立运行环境、Django/React 项目或 CI。该步验收后已先更新进度，再补充本文件；当时第 03 步未开始，后续实际状态见第 9 节。

## 8. 第 02 步验收后的架构洞察

- **目录可保留不等于已实现或已发布。** 三个 .gitkeep 使基础目录可随未来 Git 提交保留，但当前仍未跟踪、未提交；GitHub 没有因此收到目录。后端入口、React 源码与 CI 工作流分别留到对应步骤，不能把占位文件当作运行能力。
- **文件用途随脚手架建立更新。** backend/.gitkeep、frontend/.gitkeep 与 .github/workflows/.gitkeep 仅占位；后续加入真实文件后可移除它们，并逐一记录新增配置、入口、业务模块和测试文件的作用。
- **本机配置与仓库配置分别交接。** .gitignore 是随仓库维护的文件，safe.directory 是用户 Git 配置；处理账号信任无需改动产品架构，也不应使用信任全部路径的设置。相关故障与验证来源保留在进度记录中。
- **基础骨架验收不覆盖后续环境验证。** 本次通过只确认第 02 步范围。独立解释器、依赖锁定、Django 系统检查仍在第 03 步；数据库、迁移、Admin 登录与初始 CI 留到第 04 步。

## 9. 第 03 步验收交接

- 最小项目已使用官方 Django 脚手架生成，并注册唯一的 events 应用。原始空 tests.py 改为 tests 包，便于后续按行为组织测试；没有新增认证框架、第二个后端或业务功能。
- 锁定核心版本为 Django 5.2.17、DRF 3.16.1、Psycopg/Psycopg binary 3.3.6；Gunicorn 26.2.0 仅供 Linux。其他直接及传递依赖的准确版本以 requirements.txt 为准，解析报告和安装包不进入仓库。
- 数据库配置明确留空，Django 只会使用 dummy backend，不生成 SQLite 数据库。没有运行 migrate、数据库测试、开发服务器或 Admin 登录验证，也没有检查或改动 PostgreSQL。
- settings 的临时密钥每个进程不同，只服务当前脚手架检查。第 04 步须以 django-environ 配置持久密钥与分离的开发、测试、生产数据库，并替换当前本地调试配置；当前脚手架不能部署。
- 用户验证说明位于 backend/README.md：解释器版本与隔离、pip 依赖一致性、Django 系统检查、应用清单和 dummy backend。用户随后回复“通过”，据此确认第 03 步验收；无逐项输出，不编造日志。助手未代用户执行验收检查；Linux 实际安装与兼容性留到后续 CI，不宣称已验证。
- 已先在 progress.md 记录第 03 步完成、改动和验收来源，再补充本文件，并同步 README 与 AGENTS 的状态。第 04 步未开始，本次只有文档交接，没有提交或推送 Git。

## 10. 第 03 步验收后的架构洞察

- **项目配置与业务应用分工明确。** config 负责设置、根路由和服务器入口，events 是唯一业务应用。models、admin、views 和测试包目前只是占位；后续功能应填入这些职责范围，避免新增第二套后端或认证系统。
- **隔离环境与版本锁承担不同职责。** .tools/python313 和 backend/.venv 提供本机隔离，不随 Git 分发；.python-version 指明运行时，requirements.in 记录更新约束，requirements.txt 固定实际安装版本。未来 CI 必须从锁重建，不能依赖这台机器已有的安装。
- **跨平台锁不等于跨平台验收。** Gunicorn 的 Linux 标记避免 Windows 安装运行它；Linux 安装、启动和依赖兼容性仍需后续验证。Windows 脚手架通过不能代替 Linux CI 或生产验证。
- **当前数据库空缺是有意的步骤边界。** dummy backend 允许系统检查准备，但不提供持久化。临时进程密钥也不支持稳定的会话；第 04 步必须配置 PostgreSQL、分离数据库与持久密钥，再验证 Admin 登录和数据库行为。
- **测试包存在不表示测试覆盖已建立。** events/tests/__init__.py 只定义包，当前验收来自用户执行的环境与系统检查。业务测试需随后续模型、接口、事务和权限实现增加，不用空测试套件的成功退出宣称覆盖。

## 11. 第 04 步实施与验收交接

- 已完整阅读六份 memory-bank 文档和 AGENTS，复用现有分支，保留全部先前修改。
- 只读确认旧 postgresql-x64-11 服务运行于 D:/Program Files/PostgreSQL/11，监听 5432；未修改、迁移或停止。从 PostgreSQL 官方 Windows 页面指向的 EDB 下载 17.11 ZIP，在 .tools/postgres17 解压为独立实例，未改 PATH 或注册新服务。
- 新实例仅监听 127.0.0.1:5433，使用 SCRAM，开发库为 psych_talk_dev。应用角色 psychtalk_dev 可以在本机创建测试库，但不是超级用户且不能创建角色；凭据只保存在被忽略的私有本机文件。测试运行器管理 test_psychtalk 的创建/销毁，生产地址须另行提供。
- 已执行 Django 基础迁移，18 项 admin/auth/contenttypes/sessions 迁移输出成功。这是实施操作的结果，不代表验收测试通过。未创建业务模型、业务迁移或 Django 管理员账号。
- 环境加载器替换了 dummy backend 和临时密钥：开发读 .env，测试读 .env.test，生产仅读进程变量。没有数据库或生成密钥的默认值；本机地址和测试库名有隔离保护，生产强制密钥、明确主机、关闭 DEBUG 和数据库 TLS。
- 已写健康检查和 12 个测试方法。用户在收到命令和 README 验收说明后回复“通过”，据此记录本地验收通过；无逐项输出或独立浏览器日志，不编造运行结果。助手未运行测试套件或浏览器验收，验证指令仍保存在 backend/README.md 供复现。
- CI 文件已配置 PostgreSQL 17.11 service container、锁定依赖、系统检查、基础迁移、迁移遗漏检查与测试。没有提交/推送；GitHub CI 与 Linux 兼容性未验证，不宣称 CI 已通过。
- 已读取新旧监听状态和 Git 忽略结果：新实例仅本机 5433，旧服务仍 5432；.env、.env.test、数据库数据与私有连接文件均被忽略，.env.example 可提交。只读核对不替代用户测试。
- PostgreSQL 17 未注册自动启动服务，重启机器后须用本项目工具启动；不同 Windows 账号控制已启动进程可能受限，不因此停止旧服务或重置/删除旧数据。
- 用户确认后已先打开并更新 progress.md，再补充本文件的验收来源、文件职责与新洞察，并同步 README 和 AGENTS。第 04 步验收交接仅改文档，无应用、数据库、测试或 Git 发布操作；当时第 05 步未开始。随后实施状态见第 13 节。

## 12. 第 04 步验收后的架构洞察

- **实例隔离与测试库隔离各有职责。** 独立 .tools/postgres17 实例和 5433 避免修改旧 5432 服务；同一新实例中的 psych_talk_dev 与 test_psychtalk 再分离开发数据和测试生命周期。生产 URL 不进入本机配置或 CI，测试运行器拒绝生产模式。
- **环境配置校验是应用启动边界。** environment.py 负责读取和校验，settings.py 消费结果；生产不读开发文件，也不生成默认密钥。配置测试验证失败条件，不代表真实生产数据库、HTTPS 代理和 Cookie 已在线验收。
- **数据库会话现在有基础持久化，但 DOI 预览仍未实现。** 标准 sessions 迁移及 SESSION_ENGINE 为后续预览提供存储基础；多标签页合并、会话行锁、15 分钟期限和幂等确认须在第 24–25 步实现及验证，不能用基础迁移替代这些业务要求。
- **健康检查独立于活动与外部书目服务。** config/health.py 查询数据库但不访问 Crossref，不需要业务模型即可检查应用能否访问持久化层；错误只返回通用信息，后续 API 或导入异常不能直接暴露数据库异常。
- **本机管理工具不属于生产发布流程。** scripts/local_database.py 只管理 Windows 项目内实例，初始化拒绝已有文件，运行时启停不导入业务数据。生产迁移、种子和私有管理员初始化仍按后续受控流程处理。
- **验证证据分开交接。** 12 个本地测试方法的验收来源是用户确认，未提供逐项日志；backend.yml 只是可执行工作流文件，未推送便没有 Actions 运行结果。后续需要真实 CI 运行证据，不能因本地通过就标记 Linux 或线上部署完成。

## 13. 第 05 步实施与验收交接

- 已完整阅读六份 memory-bank 文件、AGENTS、已有实现与进度，仅实施活动模型，不提前实现第 06 步。
- Event 使用整数主键；title 最长 255，description 为可空白文本，topic 最长 100，speaker 最长 255；可选展示文字默认空字符串而不是 NULL。starts_at 必填，is_example 默认 false，无结束时间或发布审批字段。
- seed_key 最长 100、可空且唯一；模型 clean 去掉两端空白，空值转为 NULL。普通活动可不填写，多个 NULL 不冲突。规范化后的非空值仍受唯一校验与数据库唯一约束保护。
- Event.save 调用 full_clean，ORM 普通保存也拒绝空白标题、缺失开始时间和无时区时间；未来 Admin 表单沿用模型规则。PostgreSQL 的 NOT NULL 与标题/标识检查约束保护绕过 save 的写入，数据库唯一约束是最终去重边界，不能只依赖提前查询。
- bulk_create、QuerySet.update 不调用模型 save/full_clean。后续种子导入使用普通保存，若使用批量路径必须先规范化标识并验证有时区时间；数据库不能复原输入原本是否包含时区。保存既有活动的部分字段时仍会校验完整模型实例。
- 已使用安装的 Django 生成 0001_initial，仅包含 Event；生成命令成功不是验收。助手未应用新迁移、运行系统检查或测试，未创建示例活动、管理员账号或业务接口。
- 新增 9 个测试方法与后端 README 验收指引，包含数据库层约束与冬夏 London 同一时刻的 UTC 存取。标准测试运行器从空测试库执行迁移，验证初始 schema 可重建；此前 12 个基础测试也纳入回归，总计 21 个方法。用户收到指引后于 2026-10-04 回复“通过”，据此记录本地验收，不编造逐项日志或数据库查询证据。
- 已按约定先打开并更新 progress.md，再补充本文件的验收来源和洞察，同步 README 与 AGENTS。此次验收交接仅改文档，没有运行测试、修改代码或数据库。
- 公开页面上的示例标签、Admin 的伦敦时区文案留到对应步骤；本步仅验证 is_example 默认值与时间持久化，不宣称页面效果或管理功能已实现。第 05 步交接时第 06 步未开始，后续实现见第 15 节；未提交或推送 Git。

## 14. 第 05 步验收后的架构洞察

- **输入校验与数据库约束分别保护不同入口。** models.py 的 full_clean 提供字段错误并检查有时区时间；0001_initial.py 将必填、非空白检查和 seed_key 唯一性固化为 schema。bulk_create、QuerySet.update 绕过 save，不能依赖普通保存的规范化；唯一性提前校验也不能替代数据库处理并发冲突。
- **导入身份与示例标记承担不同职责。** seed_key 用于后续可重复导入，is_example 用于访客标识；普通活动默认 false 和 NULL，不自动变为示例。无标识规范化为 NULL，避免多个普通活动共享空字符串而发生唯一冲突；后续导入仍需保证不覆盖人工修改。
- **时间模型保存时刻，展示层负责伦敦文案。** starts_at 必须带时区，PostgreSQL/ORM 存取保持相同时刻并返回 UTC；冬夏 London 测试覆盖偏移变化。Admin 时区说明、GMT/BST 标签与 Upcoming/Past 分组属于后续表单和页面职责，不能从模型通过推断已实现。
- **迁移与测试文件共同提供可重建依据。** 0001_initial.py 创建 Event schema；test_event.py 验证实际 PostgreSQL 下的存取、规则与约束，已有 test_infrastructure.py/test_environment.py 继续覆盖环境和数据库边界。21 个方法的本地验收来源是用户确认，GitHub CI 未运行仍需另行记录。
- **活动模型先建立，不提前接入共享阅读。** 第 05 步时 models.py 只包含 Event；Resource 的共享书目与 EventResource 的推荐理由/顺序分别安排在第 06–07 步。admin.py、views.py 仍为占位，保存后的公开展示与删除权限待对应步骤验证。

## 15. 第 06 步实施与验收交接

- 已完整阅读六份 memory-bank 文档、AGENTS、已有代码和此前进度，仅实施共享 Resource，保留所有未提交工作；第 07 步未开始。
- Resource 使用整数主键；title 最长 500 且不能空白，authors 为默认空字符串的展示文本，year 可空并限定为 1–9999，original_url 最长 2048 且必须是有效 HTTP(S) URL。两种 resource_type 为 research_paper/article，metadata_source 为 crossref/manual；默认 article/manual，作者、年份和 DOI 缺失分别保存为字符串空值、NULL、NULL。
- doi 最长 2048、可空且唯一，普通保存去掉两端空白并转小写，校验 10.、4–9 位注册者数字和非空无空白后缀，保留后缀标点。仅保存纯标识；doi.org 链接解析仍在第 19 步实现，模型不访问 Crossref。seed_key 最长 100、可空唯一，去掉两端空白；两个字段无内容时都转为 NULL，多个缺失值可以共存。
- Resource.save 与 Event 一样在普通保存前 full_clean，包括部分字段保存。数据库唯一约束拒绝非空 DOI/标识重复；额外检查约束保护标题、年份、HTTP(S) 前缀与空白、标准化 DOI、类型、来源和非空标识。数据库 URL 检查仅保护基础格式，不等价于 Django URLValidator 的完整 URL 校验。批量写入不执行 save/full_clean，调用方必须保持规范化和完整字段校验。
- 标题和原文链接没有唯一约束，也没有自动合并逻辑；手动同标题或同链接资料可独立创建，后续 Admin 通过整数 ID 选择已有记录。编辑标题等书目不会自动更改来源；后续表单仍需维护来源不变规则。没有新增推荐理由、顺序、活动外键、后台注册或删除权限，这些均属于后续步骤。
- 已使用安装的 Django 生成 0002_resource，依赖初始 Event 迁移且只创建 Resource。生成成功不代表迁移已应用或测试通过；助手未运行 migrate、check 或测试，不改开发业务数据。
- 新增 test_resource.py 的 14 个测试方法，与此前 21 个合计 35 个。包括有效组合、默认值、空标识、多种无效字段、规范化 DOI、唯一约束、绕过 save 的数据库保护、同标题/链接手动独立记录，以及空测试库迁移。测试内的 BibliographyProbeSerializer/JSONRenderer 只验证缺失作者/年份/DOI 的 JSON 空值契约，不创建公开接口或关联序列化器。
- backend/README.md 提供迁移、系统检查、迁移遗漏检查及 35 个测试的用户执行指引。2026-10-04，用户收到指引后回复“通过”，据此确认第 06 步本地验收；未提供逐项输出，不编造迁移日志、耗时或查询证据。GitHub CI 和 Linux 兼容性仍待验证。
- 已按约定先请求打开并更新 progress.md，再补充本文件的验收来源、文件职责与洞察，并同步 README 和 AGENTS。此次交接仅改文档，不运行测试、不修改代码或数据库；没有安装依赖、提交/推送 Git、线上 CI 或部署操作。第 07 步未开始。

## 16. 第 06 步验收后的架构洞察

- **书目身份与内容字段分开。** models.py 以整数 ID 定位共享资源，标准化 DOI 和 seed_key 提供可选的唯一导入身份；标题和 URL 不是身份键，手动同内容资料可以独立保存。后续关联应引用 Resource 主键，不能根据相同标题或链接隐式合并。
- **模型校验和数据库 schema 共同守住数据规则。** Resource.save 的 full_clean 提供字段错误及 DOI/标识规范化；0002_resource.py 固化唯一性、空值和检查约束。批量写入绕过模型校验，数据库 URL 检查也不等价于完整 URLValidator；后续导入服务仍需调用模型校验，并由数据库处理并发唯一冲突。
- **缺失书目与展示占位属于不同层。** Resource 保存作者空字符串及年份/DOI 的 NULL，test_resource.py 的测试探针验证 JSON 空值；未来公开序列化器必须遵循同一契约，前端再显示 Author not provided/Year not provided。当前探针只位于测试文件，不是公开 API 或关联输出。
- **共享书目与活动阅读语境仍保持边界。** Resource 不保存活动、推荐理由或顺序；第 07 步的 EventResource 将承担这些字段和组合唯一约束。选择已有资源、共享编辑提示与资源删除禁用属于后续 Admin/权限步骤，不能从本次模型验收推断已实现。
- **迁移和测试职责已有明确交接。** models.py 定义运行规则，0002_resource.py 提供可重建的表结构，test_resource.py 覆盖书目存取与真实 PostgreSQL 约束；既有三个测试文件继续回归基础环境与 Event。35 个方法的本地验收来源为用户确认，GitHub CI、Linux 和生产仍需独立证据。

## 17. 第 07 步实施与验收交接

- 已完整阅读全部六份 memory-bank 文档、AGENTS、既有模型/测试及后端 README，读取 Git 状态，保留现有修改，仅实施第 07 步。
- models.py 新增 EventResource：整数主键、必填 event/resource 外键、默认空字符串的可选 recommendation，以及默认 0 的必填有符号 IntegerField display_order。PostgreSQL 整数范围为 -2147483648 至 2147483647，允许负数优先展示；推荐理由不接受 NULL。
- Meta.ordering 按 display_order、id 升序；Event 和 Resource 均通过 event_resources 反向管理器读取关联。关联 ID 与 Resource ID 分属不同身份，未来详情排序必须基于关联，不依赖资源创建顺序。组合唯一约束 unique_event_resource 允许同一资源用于多个活动，并禁止同一活动重复引用该资源。
- 普通 save 调用 full_clean，含部分字段保存；重复正常保存产生 ValidationError，绕过模型校验的重复写入由数据库拒绝。当前不把重复错误转换为已有结果，也不实现并发导入服务；这些在第 22–23 步处理。批量写入仍跳过模型校验。
- event 外键采用 Django CASCADE，ORM 删除活动仅删除该活动的关联，保留共享及仅被该活动引用的 Resource。resource 外键采用 PROTECT，ORM 不得删除仍被引用的 Resource；这不是禁止所有未引用资源删除。原始 SQL 不走 Django 删除收集器。第 08 步仍须禁用全部 Resource Admin 删除入口，并提供活动删除确认与权限控制。
- 已使用安装的 Django 生成 0003_event_resource，仅新增关联表并依赖 0002_resource，不改现有书目或活动。生成操作成功不代表迁移应用或验收通过；助手未运行 migrate、系统检查、迁移遗漏检查或任何测试，没有改开发业务数据。
- test_event_resource.py 新增 13 个测试，覆盖完整/最小记录、共享资源不同理由与顺序、重复保存/批量插入/更新拒绝、负值排序、资源 ID 与关联 ID 不同的同值排序、编辑后稳定顺序、字段/外键约束、移除关联、单条及 QuerySet 删除活动保留资料、已关联资源保护与空测试库迁移。外键数据库测试显式检查 PostgreSQL 延迟约束，避免误把语句返回当作写入有效。
- 与此前 35 个方法合计 48 个测试，运行说明保存在 backend/README.md 的第 07 步。现有 CI 自动发现新测试，但未提交、推送或在线运行；Linux 兼容性仍未验证。没有安装依赖、注册 Admin、创建示例/管理员、接入 API/Crossref/前端或部署。
- 2026-10-04，用户收到完整 PowerShell 迁移、检查与测试指引后回复“通过”，据此记录第 07 步本地验收。范围为三项 events 迁移、系统检查、迁移遗漏检查与 48 个测试方法；无逐项输出，不编造数据库日志或耗时。本地模型验收不代表后台权限、确认页面、公开接口或并发保存服务已完成。
- 已先请求打开并更新 progress.md，再补充本文件的文件职责、验收来源和洞察，随后同步 README 与 AGENTS。此次交接仅更新文档，不运行测试、不修改代码/数据库，不安装依赖或提交/推送 Git。第 08 步未开始，等待新指令。

## 18. 第 07 步验收后的架构洞察

- **关联拥有自己的身份和内容。** models.py 用 EventResource 主键定位每条阅读关联，Resource 主键定位共享书目；推荐理由和顺序只保存在关联。未来详情序列化器须分别输出 association_id 和 resource_id，查询与预加载必须保持关联顺序。
- **排序是活动语境的一部分。** Meta.ordering 明确按 display_order、id 升序；负数可提前，同值不依赖 Resource ID 或未定义的数据库顺序。test_event_resource.py 用反向资源创建顺序覆盖此差别，后续 API 和种子导入不得另用资源 ID 排序。
- **去重约束与幂等服务承担不同职责。** unique_event_resource 为最终数据库边界，普通保存先通过 full_clean 给出校验错误。第 07 步的数据库测试覆盖绕过模型校验的重复插入/更新，但并发冲突回滚与返回已有结果仍待第 22–23 步，不能把唯一约束验收当成完整导入闭环。
- **外键删除策略不替代管理权限。** event 的 CASCADE 与 resource 的 PROTECT 约束 Django ORM 收集器行为；只移除关联或删除活动都保留书目，已关联书目不能被 ORM 删除。第 08 步仍需对未关联资源禁用全部后台删除入口，并验证确认、单条/批量及直接地址；原始 SQL 不执行 Django 删除收集器。
- **运行规则、schema 与验证按文件分工。** models.py 定义保存/排序/删除规则，0003_event_resource.py 固化关联表、外键与组合唯一约束，test_event_resource.py 验证真实 PostgreSQL 下的行为及延迟外键约束。48 个本地测试的验收来源为用户确认；CI、Linux、生产和后续界面仍需要各自证据。

## 19. 第 08 步实施与验收交接

- 完整阅读六份 memory-bank 文档、AGENTS、既有实现和本地锁定 Django Admin 源码，仅实施基础后台；保留此前全部修改。未执行检查、编译、测试、迁移、服务器或浏览器验收，不安装依赖、不创建开发管理员/数据，也不提交或推送 Git。
- admin.py 注册 Event、Resource、EventResource，沿用默认后台样式、认证、数据库会话和 CSRF。手动资料单独创建，再从关联表单选择已有活动/资源；不增加行内创建或 DOI 查询。资料来源和 DOI 只读、导入标识不在表单中，手动新增使用 manual；编辑保留原来源/DOI，同标题/URL 不合并。
- EventAdminForm 配合 LondonDateTimeField 和 LondonDateTimeWidget，在输入校验与展示拆分时显式使用 Europe/London，标签说明 GMT/BST。即便当前时区被临时切为 UTC，也按伦敦解释输入；不存在/歧义的 DST 时刻沿用 Django 字段错误，不猜测偏移。模型/schema 无变化，不需要新迁移。
- EventAdmin.view_on_site、只读 public_page 与成功消息提供 /events/{id}。当前只验证地址字符串，公开页面尚未实现，点击得到 404 属于已知步骤边界，不代表发布界面完成。
- 活动删除继续使用原生单条/批量确认、收集器与权限/CSRF；两份活动模板加入规定文案，保留原生警告、删除清单及确认/取消按钮。Event 和 EventResource 两种删除权限均必需，即便活动没有关联。确认后沿用已验收 ORM 规则，只删活动及关联、保留所有 Resource。
- ResourceAdmin 对全部记录返回无删除权限，禁用批量动作，并在 delete_model/delete_queryset 再拒绝；超级管理员、未关联资源、直接删除地址及伪造批量提交均在测试范围。该策略属于 Admin，不改变未关联 Resource 的普通 ORM 删除能力。
- EventResource 新增要求关联新增、活动修改及资源查看权限；保存后 event/resource 只读，编辑只影响当前推荐理由/顺序。单条移除继承原生确认并加入规定文案，批量关联动作禁用。第 27–28 步仍需复核操作入口与完整权限矩阵，不把基础实现当作完成 DOI/全 MVP 权限。
- test_admin.py 新增 21 个方法，连同此前 48 个共 69 个；测试内的管理员/staff 仅属于隔离测试库。覆盖后台页面、活动增改/地址、时区/DST、资料增改与来源保持、重复内容独立记录、字段错误、已有资源复用/重复拒绝、身份只读、匿名/非 staff/缺权限、删除确认/保留、全部资源禁删、关联移除及真实 CSRF。用户已确认本地验收，助手未代运行；说明位于 backend/README.md Step 08。
- 2026-10-04，用户收到完整 PowerShell 检查与测试说明后回复“通过”，据此记录第 08 步本地验收。范围为系统检查、迁移遗漏检查和 69 个测试方法；未提供逐项输出，不编造日志或耗时。可选浏览器验收及管理员创建没有独立证据，不推断已执行。
- 已先请求在编辑器打开并更新 progress.md，再补充本文件的验收、文件职责与洞察，随后同步 README/AGENTS。此次交接仅更新文档，不运行检查/测试、不改代码/数据库，不安装依赖或提交/推送 Git。第 09 步未开始，需后续明确指令；GitHub CI 与 Linux 仍待验证。

### 本步结构说明

- 时间字段及控件各自负责输入与显示，不靠服务器当前时区解释伦敦表单；UTC 持久化仍由原模型与 Django 完成。
- 删除模板只维护文案；后台权限/删除钩子和 ORM 收集器分别承担授权与数据保留，避免另写一套删除路径。全局后台禁删比 Resource 外键 PROTECT 覆盖范围更广。
- 基础后台关联通过记录身份复用资源；只读外键防止编辑语境时意外搬移关联，组合唯一仍是最终数据边界。后续 DOI 幂等/并发服务继续按第 22–23 步实施。
- 源码、schema 与验收证据分开记录。本步只有 Admin 与模板/测试新增，无迁移；69 个方法的本地验收来源是用户确认，CI、Linux 与部署仍无运行证据。

## 20. 第 08 步验收后的架构洞察

- **后台输入与模型存储分别负责时间。** admin.py 的 EventAdminForm、LondonDateTimeField、LondonDateTimeWidget 负责标签、伦敦输入校验及显示；models.py 负责有时区的时刻，数据库存取保持 UTC。冬夏及 DST 字段测试覆盖后台边界，未来公开页面仍需单独验证伦敦展示与活动分组。
- **模板维护文案，后台和 ORM 执行安全规则。** 三份确认模板只扩展原生确认界面，保留权限警告、删除清单、CSRF 与取消控件；EventAdmin 的双模型权限和 Django 删除收集器负责授权与关联级联。ResourceAdmin 的全局拒绝涵盖未关联资源，强于外键 PROTECT 对已关联记录的保护，普通 ORM 删除策略没有改变。
- **书目身份和活动语境在表单层继续分开。** ResourceAdmin 管理共享书目，保留 DOI/来源；EventResourceAdmin 新增时选择已有记录，编辑时锁定外键身份，仅改当前理由/顺序。手动同内容资料仍独立，后续 DOI 查询/并发保存不应依赖标题或 URL 合并。
- **公开地址先于公开页面。** EventAdmin 提供 /events/{id} 字符串、保存消息和 View on site；这只验证路径契约。活动 API、React 页面与刷新入口仍留到后续步骤，当前地址返回 404 不能写成页面发布成功。
- **后台测试不能代替整个权限闭环。** test_admin.py 使用隔离库中的测试用户、真实 Admin 请求和启用 CSRF 的客户端，覆盖当前基础操作；第 24–28 步仍须验证 DOI 预览/确认时权限重查、会话及完整矩阵。69 个方法按用户确认记录本地通过，不推断 GitHub CI、Linux、生产或可选手动浏览通过。
