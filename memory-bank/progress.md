# PsychTalk Hub — 实施进度

日期：2026-10-04｜最后完成步骤：08（用户确认本地验收通过；基础后端 GitHub CI 已通过）｜下一步骤：09（尚未开始，等待后续指令）

以下各步骤保留交接当时的事实，包括尚未提交和 CI 待验证的历史描述；最新 Git/CI 状态见文末补充记录。

## 第 01 步：核对必读文档并初始化架构记录

状态：用户验收通过。

### 已做事项

- 完整阅读 memory-bank 中六份文档，以及根目录 AGENTS.md；沿用现有设计，不创建带 @ 前缀文件或设计副本。
- 阅读当前文件清单与 Git 状态，确认仓库仍仅有文档及忽略规则，保留此前文档分支中的未提交修改。
- 初始化 [architecture.md](architecture.md)，说明当前仓库事实、每个现有文件的作用、计划目录职责及后续实现边界；明确区分已存在内容与尚未实现功能。
- 按用户指定顺序，在收到验收通过后才填写本进度记录，再补充架构文件的验收状态与新洞察。

### 验证来源与结果

- 验证由用户负责执行；用户在本次会话中回复“通过”，据此将第 01 步标记为已验收。
- 本步骤的验收范围为文档可读、初始架构事实准确、中英文规则一致、文档链接有效，以及无带 @ 前缀或额外设计副本。
- 用户未提供逐项测试输出或日志，不编造命令、日志或测量结果；助手未代用户运行测试。本结果不代表后端、前端、数据库、CI 或部署已验证。

### 改动位置与交接

本步骤仅初始化 memory-bank/architecture.md，并在验收后填写 memory-bank/progress.md、补充架构说明；其他现有文档修改属于此前的规范修订。本次没有创建应用目录、安装依赖、编写应用代码、提交或推送 Git。

第 01 步交接时，第 02 步尚未开始。其后收到用户指令执行目录骨架准备；最新状态见下方第 02 步记录。

## 第 02 步：建立仓库和目录骨架

状态：用户验收通过。

### 已做事项

- 复用已有 Git 仓库与功能分支 `docs/clarify-implementation-plan`，保留此前未提交的文档修改；没有重新初始化仓库或切换分支。
- 新增 `backend/.gitkeep`、`frontend/.gitkeep` 与 `.github/workflows/.gitkeep`，建立后端、前端和工作流基础目录。占位文件仅用于保留目录，不是应用代码或 CI 配置，仍为未跟踪文件，未暂存或提交。
- 沿用现有 `.gitignore`，排除环境文件、虚拟环境、依赖、缓存及构建产物，保留 `.env.example` 例外。
- 更新架构记录的当前目录状态与三个占位文件用途；验收通过后，按要求先更新本进度记录，再补充架构验收与洞察。

### 验证来源与结果

- 用户运行验证时遇到 Git 的 `dubious ownership` 提示：仓库归 Codex 沙箱账号所有，用户终端使用 Luxury 账号。已提供仅信任本项目路径的 `safe.directory` 处理说明；助手未修改用户全局 Git 配置。
- 用户随后回复“通过”，据此标记第 02 步验收通过。范围为 Git 状态可读取、目录和既有文档存在、忽略规则生效，以及环境变量示例未被忽略。
- 用户未提供修复后的逐项输出，不能据此确认其实际采用了哪种所有权处理方式；不编造日志或测试命令执行结果。助手仅读取仓库状态，未代用户运行验证测试。
- 本结果不代表 Django、React、数据库、依赖安装、CI 或部署通过。

### 改动位置与交接

本步骤新增三个目录占位文件，更新 `memory-bank/architecture.md`，验收后更新本文件。`.gitignore` 与其他现有文档未在本步骤修改；没有安装依赖、编写应用代码、提交或推送 Git。

第 02 步交接时，第 03 步尚未开始。随后收到用户指令建立最小 Django 项目；最新状态见下方第 03 步记录。

## 第 03 步：建立 Django 最小项目

状态：用户验收通过。

### 已做事项

- 完整阅读 memory-bank 六份文档、AGENTS.md 和此前进度，复用现有功能分支，保留所有先前修改。
- 从 Python 官方来源获取并核对安装包签名，将独立 CPython 3.13.16 安装到 `.tools/python313/`，在 `backend/.venv/` 建立隔离环境；未替换原有 Anaconda/Python，未修改 PATH、文件关联或启动器。
- 新增 `.python-version`、`backend/requirements.in` 与 `backend/requirements.txt`，首次安装前锁定直接及传递依赖。核心版本为 Django 5.2.17、DRF 3.16.1、Psycopg/Psycopg binary 3.3.6；Gunicorn 26.2.0 使用 Linux 平台标记，未在 Windows 安装或运行。安装包和解析报告留在被忽略的 `.tools/`。
- 使用 Django 脚手架创建 `backend/config/`、`backend/manage.py` 与唯一的 `backend/events/` 业务应用，注册 DRF 和 EventsConfig；删除后端目录占位文件，将空 tests.py 改为 tests 包。
- 移除默认 SQLite 配置，数据库配置留空；使用临时进程密钥供脚手架检查，保留英文及伦敦时区。没有新增业务模型、API、认证框架或实际测试用例。
- 新增后端 README，说明环境、锁定依赖、用户验证命令和预期结果；更新 `.gitignore`、AGENTS.md 及架构记录的实际状态。

### 验证来源与结果

- 验证由用户执行；用户在收到第 03 步验证说明后回复“通过”，据此将本步骤标记为已验收。
- 验收范围为独立解释器与环境隔离、版本符合选型、依赖一致性、Django 系统检查、唯一业务应用及可移植锁定文件。完整验证说明保留在 [后端 README](../backend/README.md)。
- 用户未提供逐项输出或日志，不编造具体测试输出。助手执行过安装与脚手架准备，未代用户执行 pip check、Django 系统检查或验收测试。
- Linux 实际安装和兼容性尚未验证，留到后续 CI；数据库、迁移、Admin 登录、业务功能、前端及部署不属于本次通过的范围。

### 改动位置与交接

本步骤新增最小后端代码、依赖清单、后端 README 与运行时版本文件，更新忽略规则、仓库指南和架构记录。用户确认后先打开并更新本进度，再补充架构洞察及同步验收状态。本次没有提交或推送 Git，也没有访问或改动 PostgreSQL。

第 03 步交接时，第 04 步尚未开始。随后按用户指令配置独立数据库、基础 CI 和健康检查；最新状态见下方第 04 步记录。第 03 步的 dummy backend 和临时密钥已经在该步骤替换。

## 第 04 步：配置独立数据库、基础 CI 与健康检查

状态：用户确认本地验收通过；GitHub CI 运行及 Linux 兼容性仍待验证。

### 已做事项

- 完整阅读 memory-bank 六份文件及 AGENTS.md，检查此前进度和 Git 状态，保留所有未提交修改与现有分支。
- 只读核对旧 PostgreSQL 11 服务及端口，保留 D:/Program Files/PostgreSQL/11 和 5432。下载官方 Windows 页面指向的 EDB PostgreSQL 17.11 ZIP，在被忽略的 .tools/postgres17 建立独立实例，仅监听 127.0.0.1:5433；未改 PATH 或注册新服务。
- 创建 psych_talk_dev 及本机应用角色，采用 SCRAM 与随机凭据；应用角色不是超级用户，允许在独立本机实例创建测试库。开发和测试私有配置被 Git 忽略，测试库名为 test_psychtalk，生产连接必须独立明确提供。
- 新增 config/environment.py，用 django-environ 区分开发、测试、生产；替换临时密钥与空数据库配置。生产不读取本机文件，要求强密钥、明确主机、关闭 DEBUG 及数据库 TLS；提供无真实凭据的 .env.example。
- 新增隔离测试运行器，禁止生产配置运行数据库测试；明确使用数据库会话、英文和伦敦时区。执行 18 项 Django 基础迁移，建立 Admin、认证、content types 和 sessions 表，没有业务迁移或 Django 管理员账号。
- 新增 /healthz/：数据库 SELECT 1 成功为 JSON 200，失败为安全 JSON 503，不访问 Crossref、不缓存；HEAD 无响应体，其他方法返回 405。
- 新增 12 个基础测试方法，覆盖 PostgreSQL 17 与测试库隔离、基础会话表、健康状态与失败模拟、方法限制、Admin 登录入口、配置错误/优先级及生产测试拒绝。
- 新增 .github/workflows/backend.yml，使用 PostgreSQL 17.11 与锁定 Python/依赖，执行依赖、系统、基础迁移、迁移遗漏检查及测试；移除工作流占位文件。
- 新增 Windows 本机数据库初始化/启停工具，更新后端 README、仓库指南和架构文件，说明每个新增文件的职责及用户验证路径。

### 验证来源与结果

- 用户在收到第 04 步测试命令和完整 README 验收说明后回复“通过”，据此记录本地验收通过。用户未提供逐项输出或日志，不编造测试耗时、命令输出或独立浏览器检查证据。
- 验证说明包括 Django 系统检查、迁移遗漏检查、12 个测试方法、旧服务保留、配置与凭据排除，以及 Admin 登录页和健康检查的浏览器路径；完整说明保留在 [后端 README](../backend/README.md)。
- 助手执行过安装、独立实例初始化及基础迁移，读取过新旧端口和 Git 忽略结果；没有代用户运行测试套件或浏览器验收。本地通过不代表业务模型、活动 API、React 或部署已验证。
- 工作流没有提交或推送，未提供 GitHub Actions 运行链接，因此 GitHub CI 与 Linux 依赖兼容性继续标为未验证。后续获明确 Git 提交/推送授权后再执行并记录真实结果，不用本地确认替代线上结果。

### 改动位置与交接

第 04 步增加环境加载器、隔离运行器、健康路由、测试、配置示例、CI 及本机数据库工具；更新 settings、urls、README、AGENTS 与 architecture。收到用户确认后，先打开并更新本 progress.md，再补充架构验收与洞察、同步 README 和 AGENTS 的状态。本次验收交接仅更新文档，没有运行测试、修改代码或数据库，也没有提交或推送 Git。

第 04 步交接时，第 05 步未开始。随后按用户明确指令建立 Event，实施及验收见下方第 05 步记录。本机 PostgreSQL 17 在机器重启后需手动启动；切回开发前检查 DJANGO_ENV，避免沿用测试模式。

## 第 05 步：建立活动模型

状态：用户确认本地验收通过；GitHub CI 运行及 Linux 兼容性仍待验证。

### 已做事项

- 完整阅读 memory-bank 六份文件、AGENTS 和此前进度，核对已有实现及 Git 状态，保留全部先前修改。
- 在 backend/events/models.py 建立唯一的 Event 模型：标题、可选简介/主题/讲者、有时区开始时间、默认 false 的 is_example，以及可空唯一 seed_key；没有新增结束时间、发布状态或审批流程。
- 普通保存先执行 full_clean，拒绝空白标题、缺失时间和无时区时间。seed_key 去掉两端空白，空值统一为 NULL，多个普通活动可以不填导入标识。数据库另有必填、非空白标题/标识检查及 seed_key 唯一约束，保护绕过模型校验的写入。
- 使用已安装的 Django 生成 backend/events/migrations/0001_initial.py，仅创建 Event 表；助手未应用本步迁移，也未运行系统检查或验收测试。
- 新增 backend/events/tests/test_event.py 的 9 个测试方法：完整及最小记录存取、默认值、必填拒绝、NULL 和唯一标识、数据库约束、冬夏伦敦时间的 UTC 存取，以及初始迁移在隔离测试库中的应用。
- 更新 backend/README.md、AGENTS.md 和 architecture.md 的文件职责与待验收状态，提供开发迁移和隔离测试指引；没有实现 Resource、EventResource、Admin 模型管理或活动 API。

### 验证来源与结果

- 2026-10-04，用户收到第 05 步测试指引后回复“通过”，据此记录本地验收通过。用户未提供逐项输出，不编造测试耗时、数据库查询结果或命令日志。
- 本步验收范围包括 Event 初始迁移、Django 系统检查、迁移遗漏检查，以及 21 个后端测试方法（此前 12 个基础测试和新增 9 个 Event 测试）。完整可复现说明保留在 [后端 README](../backend/README.md)。
- UTC 存取与 is_example 默认值属于本步模型验证；公开示例标签、伦敦时间页面展示和 Admin 表单仍留到后续步骤。本地确认不代表这些界面或部署已完成。
- 助手仅生成迁移并读取源码，没有代用户运行验收。GitHub 工作流未提交或推送，CI 线上执行和 Linux 兼容性继续标为未验证。

### 改动位置与交接

第 05 步修改模型，增加初始迁移与模型测试，同步后端 README、仓库指南和架构记录。收到确认后先打开并更新本 progress.md，再补充 architecture.md 的验收说明、文件职责和洞察，最后同步 README 与 AGENTS。此次验收交接仅改文档，不运行测试或改动代码/数据库，也不提交或推送 Git。

第 05 步交接时第 06 步未开始。随后按用户明确指令建立 Resource，实施及验收见下方第 06 步记录。Event.save 会校验完整实例，批量写入不调用 save/full_clean，后续种子路径须显式保持标识及时间规则。

## 第 06 步：建立共享资源模型

状态：用户确认本地验收通过；GitHub CI 运行及 Linux 兼容性仍待验证。

### 已做事项

- 完整阅读 memory-bank 六份文档、AGENTS 和此前进度，核对已有实现及 Git 状态，保留全部先前修改，仅实施 Resource。
- 在 backend/events/models.py 新增共享书目模型，保存标题、作者展示字符串、年份、HTTP(S) 原文链接、可选唯一 DOI、两种资料类型、两种来源及可空唯一 seed_key。作者缺失默认为空字符串，年份和 DOI 缺失为 NULL；年份限定为 1–9999。
- 普通保存执行 full_clean；纯 DOI 去掉两端空白、转小写并保留后缀标点。DOI 和 seed_key 空值转为 NULL，多个缺失值可共存；数据库约束保护唯一性、标题、年份、类型/来源及 DOI 格式。完整 URL 语法由模型校验，数据库仅保护 HTTP(S) 前缀与空白规则。
- 标题和原文 URL 没有唯一约束或自动合并逻辑，同标题或同链接的手动资料可独立创建。没有实现 EventResource、模型 Admin、公开接口或 DOI 查询；DOI 链接解析仍留到第 19 步。
- 使用已安装的 Django 生成 backend/events/migrations/0002_resource.py，依赖 0001_initial，仅创建 Resource；助手未应用迁移或代运行系统检查、测试。
- 新增 backend/events/tests/test_resource.py 的 14 个测试方法，覆盖字段存取、默认值、空标识、规范化、输入拒绝、数据库唯一性及约束、手动资料独立保存、普通书目编辑保留来源及空测试库迁移。测试内的 DRF 序列化探针验证缺失作者为空字符串、年份和 DOI 为 JSON null，不是公开 API。
- 同步 backend/README.md、AGENTS.md 和 architecture.md，提供用户迁移、检查和 35 个后端测试的验证指引，区分实现状态与验收结果。

### 验证来源与结果

- 2026-10-04，用户收到第 06 步验证指引后回复“通过”，据此记录本地验收通过；未提供逐项输出，不编造测试耗时、迁移日志或数据库查询结果。
- 验收范围为 Resource 迁移、Django 系统检查、迁移遗漏检查，以及 35 个后端测试方法（此前 21 个和新增 14 个）。完整可复现说明保留在 [后端 README](../backend/README.md)。
- 助手只生成迁移并读取源码，没有代用户运行验收。本地确认不代表活动关联、Admin 资源选择/删除权限、完整 API、Crossref 或部署已完成。
- GitHub 工作流未提交或推送，CI 线上执行和 Linux 兼容性继续标为未验证；测试内的书目序列化探针不能代替后续公开接口契约验收。

### 改动位置与交接

第 06 步修改 models.py，增加 0002_resource.py 与 test_resource.py，同步后端 README、仓库指南和架构记录。收到确认后先请求打开并更新本 progress.md，再补充 architecture.md 的验收说明、文件职责和洞察，最后同步 README 与 AGENTS。此次验收交接仅改文档，不运行测试或改动代码/数据库，也不提交或推送 Git。

第 06 步交接时第 07 步未开始。随后按用户明确指令建立 EventResource，实施及验收见下方第 07 步记录。保持 Resource 为共享书目，推荐理由与顺序属于各活动关联；批量写入仍须显式执行规范化与完整 URL 校验。

## 第 07 步：建立活动资源关联

状态：用户确认本地验收通过；GitHub CI 运行及 Linux 兼容性仍待验证。

### 已做事项

- 完整阅读六份 memory-bank 文档、AGENTS、已有模型/测试及后端 README，读取 Git 状态，保留此前所有修改，仅实施第 07 步。
- 在 backend/events/models.py 新增 EventResource，保存必填活动/资源外键、默认空字符串的可选推荐理由及默认 0 的有符号整数展示顺序；允许负数，默认按 display_order、关联 ID 升序。
- 使用 unique_event_resource 数据库组合唯一约束，允许同一共享资源用于多个活动，拒绝同一活动重复引用同一资源。普通 save 调用 full_clean；各活动的推荐理由与排序可以独立编辑，不修改共享书目。
- event 外键采用 Django CASCADE，ORM 删除活动清除其关联但保留全部资源；resource 外键采用 PROTECT，保护仍被引用的资源。后台全局资源删除禁用、活动删除确认及权限属于第 08 步，本步未实施。
- 使用已安装的 Django 生成 backend/events/migrations/0003_event_resource.py，仅新增关联表并依赖 0002_resource；助手未应用迁移、运行检查或验收测试。
- 新增 backend/events/tests/test_event_resource.py 的 13 个方法，覆盖存取/默认值、独立理由与顺序、模型及数据库去重、负数/同值确定排序、字段与外键约束、移除关联、活动删除保留资源、已关联资源保护及空 PostgreSQL 测试库迁移。加上此前 35 个，共 48 个测试方法。
- 同步 architecture.md、backend/README.md 和 AGENTS.md 的文件职责及验证指引；按用户追问提供完整 PowerShell 执行步骤，没有新增 Admin、API、示例数据、Crossref 或前端。

### 验证来源与结果

- 2026-10-04，用户收到迁移、检查与测试的完整执行指引后回复“通过”，据此记录第 07 步本地验收通过。用户未提供逐项输出，不编造日志、耗时或数据库查询证据。
- 验收范围包括三项 events 迁移、Django 系统检查、迁移遗漏检查，以及 48 个后端测试方法。完整可复现说明保留在 [后端 README](../backend/README.md) 的 Step 07。
- 助手只生成迁移并读取源码，未代用户执行验收。本地通过不代表 Admin 的删除确认、权限/CSRF、公开 API、并发保存服务或部署完成。
- GitHub 工作流仍未提交或推送，没有线上运行证据；GitHub CI 与 Linux 兼容性继续标为待验证。

### 改动位置与交接

本步修改 models.py，增加 0003_event_resource.py 与 test_event_resource.py，更新 README、AGENTS 和 architecture。收到确认后先请求在编辑器打开并更新本 progress.md，再补充 architecture.md 的验收、文件职责和洞察，最后同步 README 与 AGENTS。本次验收交接仅更新文档，不运行测试、不修改代码/数据库、不安装依赖、不提交或推送 Git。

第 07 步交接时第 08 步未开始。随后按用户明确指令实施基础 Django Admin，实施与验收见下方第 08 步记录。资源外键 PROTECT 只保护已关联记录，不能替代后台对未关联资源的删除禁用；并发冲突转换仍留到第 22–23 步。

## 第 08 步：配置基础 Admin 管理

状态：用户确认本地验收通过；GitHub CI 运行及 Linux 兼容性仍待验证。

### 已做事项

- 完整阅读全部六份 memory-bank 文档、AGENTS、已有实现及锁定版本的 Django Admin 源码，保留此前全部修改，仅实施基础后台。
- 在 backend/events/admin.py 注册 Event、Resource 和 EventResource，支持活动增改、手动资料创建，以及从关联表单选择已有活动和资源。手动资料保持 manual 来源，不按标题/URL 自动合并；DOI 与来源只读，导入标识不展示。已有关联的活动和资源身份只读，推荐理由与顺序独立编辑。
- 增加 EventAdminForm、LondonDateTimeField、LondonDateTimeWidget，明确 Europe/London 标签及 GMT/BST 说明；输入和显示均固定伦敦时区，歧义/不存在的夏令时时刻显示字段错误。保存消息、只读字段和 View on site 提供 /events/{id}；公开页面仍未实现，本步只验证地址。
- 活动单条及批量删除沿用原生确认、CSRF、权限和 ORM 删除收集器，要求 Event 与 EventResource 删除权限，保留全部 Resource。Resource 禁止全部后台删除，包含超级管理员、未关联资源、直接地址及批量提交；删除钩子也明确拒绝。
- 增加三份后台确认模板：活动单条/批量删除和阅读关联单条移除，使用设计规定文案并保留原生确认/取消和安全行为；禁用关联批量动作。
- 新增 backend/events/tests/test_admin.py 的 21 个测试方法，累计 69 个。覆盖后台页面、增改/字段错误、冬夏伦敦时间/DST、公开地址、手动空值与来源、已有资源复用/重复拒绝、关联身份、共享编辑来源保持、匿名/非 staff/模型权限、确认删除/保留、资源禁删和真实 CSRF。
- 更新 architecture.md、backend/README.md 和 AGENTS.md 的文件职责与待验收状态；按用户追问提供完整 PowerShell 验证操作。本步不修改模型/schema，无新迁移，不安装依赖、不创建开发管理员或业务数据、不实现演示数据/API/Crossref/React。

### 验证来源与结果

- 2026-10-04，用户收到第 08 步完整检查和测试操作说明后回复“通过”，据此记录本地验收通过。未提供逐项输出，不编造测试日志、耗时或独立浏览器验证证据。
- 验收范围为 Django 系统检查、迁移遗漏检查及 69 个后端测试方法（此前 48 个及新增 21 个）。可复现说明保留在 [后端 README](../backend/README.md) 的 Step 08；助手没有代运行检查、测试、服务器或浏览器验收。
- 本地通过包含基础 Admin 的权限/CSRF 与删除规则测试，不代表完整导入权限矩阵、DOI 预览、并发服务、公开页面或部署已完成。可选手动后台浏览及本地管理员创建未提供独立结果，不推断其已执行。
- GitHub 工作流仍未提交或推送，CI 线上运行与 Linux 兼容性继续标为未验证。

### 改动位置与交接

第 08 步修改 admin.py，新增三个确认模板与 test_admin.py，同步 README、AGENTS 和 architecture。收到确认后已先请求在编辑器打开并更新本 progress.md，再补充 architecture.md 的验收、文件职责与洞察，最后同步 README/AGENTS。本次验收交接仅修改文档，不运行测试、不改代码或数据库、不安装依赖、不提交或推送 Git。

第 09 步未开始，等待用户新指令。下一步先阅读全部 memory-bank 文档，再精选并核对真实论文/文章，为两场虚构讲座建立独立、可重复的演示导入；按稳定身份只补缺，保留人工编辑与既有日期，不加入启动/部署流程。资料及关联仍须显式遵守模型校验与数据库唯一约束；首次日期规则及重复导入验证以实施计划第 09 步为准。

## 第 04 步补充：阶段提交与 GitHub CI 验证

状态：2026-10-04，按用户“执行”授权完成阶段提交、推送及线上 CI 核对；第 09 步未开始。

### 已做事项与证据

- 检查 44 个候选文件、暂存清单、Git 忽略规则及差异格式。私有 `.env`、`.env.test`、虚拟环境及 `.tools/` 中数据库、管理员连接和下载文件未进入提交；内容扫描提示均为 CI 临时值、测试夹具、无真实值的示例或运行时生成变量。
- 将第 01–08 步现有文档和后端实现提交为 `66b41404f0d3e6aa91c0b6209faf768bb99f86ee`（`feat: establish backend models admin and CI`），推送到 `origin/docs/clarify-implementation-plan`，建立同名上游跟踪；未合并到默认分支、未创建 PR。
- 通过 GitHub Actions API 核对 [Backend checks #37208404049](https://github.com/1uxury/psych-talk-hub/actions/runs/37208404049)：对应上述提交，运行及 backend job 均为 `completed / success`。
- Linux runner 上的容器初始化、Python 设置、锁定依赖安装、依赖一致性、Django 系统检查、迁移、迁移遗漏检查及隔离 PostgreSQL 测试步骤全部为 `success`。仓库包含 69 个测试方法；本次读取的是运行和步骤结果，未读取逐项测试日志，不编造测试数量输出或耗时。
- CI 使用独立的 PostgreSQL 17.11 容器与测试数据库，不连接本机开发库或生产数据库，不访问真实 Crossref。助手未在本机重跑用户验收、启动服务或修改数据库，也未修改应用代码。

### 交接边界

先请求在编辑器打开并更新本文件，再同步 architecture.md、backend/README.md 和 AGENTS.md。此次补齐第 04 步基础 CI 的远程验证；后续前端 CI、第 34 步完整可复现性、生产启动/部署及 DOI 权限闭环仍需对应验收。第 09 步仍等待用户单独指令。
