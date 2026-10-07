# PsychTalk Hub — 架构记录

日期：2026-10-07｜最后明确用户确认步骤：31｜第 30 步本地验证通过、当前版本远程 CI 待办｜第 31 步用户验收通过｜生产 SHA 仍为 d8bdd29｜第 32 步未开始

最新状态以第 73–74 节为准：收到明确实施第 31 步的新指令后核对公开状态并完成 13 组只读夹具浏览器验证，用户随后回复“通过”，确认第 31 步本地验收。已先记录 progress.md；验收指引在 frontend/README.md。没有补写用户“通过30”或远程 CI 结果；下列待验收/未开始的描述为历史交接。第 32 步等待新的明确实施指令。

本文记录当前事实与后续边界，不代表完整 MVP 已完成。用户已确认第 01–29 步；第 6–45 节保留历史交接及真实 CI/部署/生产初始化来源。生产 d8bdd29 含两场示例、六条资源/关联和私有管理员，最终命令重部署已 Live；非空重部署保留、备份/恢复及完整验收仍待办。第 18–21 步见第 46–53 节，第 22 步见第 54–55 节，第 23 步见第 56–57 节，第 24 步见第 58–59 节。第 25 步 Admin 确认保存及同事务结果见第 60–61 节，第 26 步共享编辑与排序见第 62–63 节，第 27 步关联移除及恢复验证见第 64–66 节，第 28 步权限矩阵/真实 CSRF 见第 67–68 节，第 29 步真实 Crossref 集成见第 69–70 节。第 30 步第二个里程碑本地 lint/30 前端/311 后端及 12 组浏览器路径通过，当前服务/会话/权限/测试边界与未完成远程 CI 见第 71 节；已先记录 progress.md。本步待用户验收，最后用户确认保持 29，第 18–30 步未提交/推送/部署，第 31 步未开始。

2026-10-07（Europe/London）按用户要求再次复查本地验收，lint/30 前端/build/311 后端及 **20 组浏览器路径（12 核心 + 8 真实 DOI）**通过，最新证据与保留原运行数据库的清理结果见第 72 节；第 71 节保留首次验证来源。没有开始后续实现或扩大为当前线上验收。

第 15 步助手独立实测的 28 项测试及 19 组浏览器证据保留在第 37 节。第 16 步首次验收来源是用户确认；随后第 17 步实测当前 lint、30 项前端测试、构建、135 项后端回归及 20 组浏览器流程，均通过。历史记录中的未执行描述属于当时事实，不替代当前版本证据。

## 1. 当前仓库状态

仓库复用功能分支 `docs/clarify-implementation-plan`，跟踪 `origin/docs/clarify-implementation-plan`。第 01–08 步现有文档及实现已提交并推送为 `66b4140`，未合并默认分支，未创建 PR。

当前第 09–17 步实现提交 a174723 与文档提交 d8bdd29 均已推送并通过前后端 CI，实际 Render 发布使用 d8bdd2923304475f05281d5d56a71018eb43cf4f。下列逐步描述保留当时未提交/未执行事实，当前发布状态以本段和第 43 节为准；未合并默认分支或创建 PR。

第 03 步已在 backend 建立 Django config 项目和唯一的 events 业务应用，并移除 backend/.gitkeep。第 04 步已加入环境配置、独立 PostgreSQL 17、健康检查、基础测试与 backend CI 工作流，移除工作流占位文件；当时 frontend 仅为占位。第 05–07 步分别加入 Event、Resource、EventResource 及三份迁移、9/14/13 个模型测试，用户已确认本地验收；助手在实施时只生成业务迁移，未代运行本地验收。第 08 步增加基础 Admin、三份确认模板和 21 个测试，用户已确认本地验收，累计 69 个方法。上述文件已随阶段提交推送，基础后端 CI 在线成功。后续演示内容、公开接口和 React 脚手架见下段，DOI 导入未实现。

第 09 步已加入本地演示清单、独立导入服务、seed_demo 管理命令和 13 个测试，累计 82 个方法，用户已确认本地验收。助手未执行导入、检查或测试；可选开发库导入没有独立证据，不推断开发库已存在演示内容。此步不修改模型/schema，无新迁移或依赖，新增改动未提交/推送；前述 CI 成功不覆盖这些新增改动。

第 10 步新增只读活动列表 /api/events/、序列化器与路由，聚合关联数量并按活动 ID 升序返回固定字段，明确 UTC Z 输出。新增 8 个接口测试，累计 90 个方法，用户已确认本地验收，无逐项输出；助手未执行验收命令。没有新迁移、依赖或开发数据操作。

第 11 步新增 /api/events/{id}/，继承已有活动输出并增加扁平关联资料，聚合计数、预加载共享资源，按 display_order、关联 ID 排序。增加 API 专用 JSON 404 回退和安全 500 中间件，支持调试开启/关闭，不改变 Admin 或非 API 页面错误。新增 14 个测试方法，累计 104 个，用户已确认本地验收，无逐项输出；助手未代运行验证。没有新迁移、依赖或开发数据操作。

第 12 步复用两个视图已有的 GET/HEAD/OPTIONS 限制，新增 test_public_api_methods.py 的 12 个测试方法，累计 116 个，用户已确认本地验收，无逐项输出；助手未代运行验证。匿名和真实已登录管理员使用相同公开能力；测试覆盖 JSON 405、Allow/OPTIONS、无正文 HEAD、逐字段数据保留及方法覆盖提示。该步没有应用代码、模型/schema、迁移、依赖或数据库操作。

第 13 步按用户明确指令建立 JavaScript Vite React、声明式路由占位、普通 CSS、JSDoc 契约类型、本地 API 代理和独立 frontend CI job，移除 frontend/.gitkeep。复用现有 Node 24.14.0/npm 11.9.0，不改全局安装或 PATH；精确锁定直接与传递依赖。用户明确回复“13步通过”，据此记录本地验收，不把安装操作本身当作通过证据。页面仅含临时真实后端连接检查与详情路由占位，不是正式首页/详情。远程 CI 尚未验证，第 14 步未开始。

随后按用户明确指令仅实施第 14 步：共用只读 API 模块、请求生命周期 Hook、英文状态组件与页面路由。首页自动加载未分组链接，详情自动显示真实标题/计数，未知页面提供返回；正式分组/阅读卡片仍待第 15–16 步。新增 18 个 Node 内置测试，CI 加入 npm test，没有新增依赖、锁文件或后端变化。用户授权助手检查，lint、测试、构建及 14 组浏览器检查全部通过，随后回复“通过”确认本地验收。第 15 步未开始。

第 15 步已写入首页分组、活动卡片和伦敦时间显示：新增 TalkCard.jsx、utils/talks.js、tests/talks.test.js，扩展列表响应的卡片字段检查、HomePage 与 CSS；新增十个测试，总计 28 个前端测试。用户截图随后显示冬季 GMT+0，已补时区名称兼容修正与模拟测试，用户在重新验证指引之后回复“通过”确认本地验收。首次实施时助手仅阅读和编辑文件；随后用户要求检查，助手 lint、28 项测试、构建和 19 组浏览器场景全部通过，无需修改应用。实际证据见第 37 节，保留既有请求/路由及 API 顺序。后端 116 个测试未重跑，依赖、schema 与生产集成均未变化，第 16 步未开始。

独立 CPython 3.13.16 安装于项目内被忽略的 .tools/python313，项目虚拟环境位于 backend/.venv，不读取系统 site-packages。安装未修改 PATH、文件关联或启动器，未替换 Anaconda 3.11.5 或既有 Python 3.10。后端直接与传递依赖已按精确版本锁定并安装到该虚拟环境；Gunicorn 限定 Linux 安装，未在 Windows 安装或运行。环境准备日志不等同于用户验收通过。

第 16 步新增 ResourceCard.jsx，扩展 TalkPage、共享时间规则、详情响应防御检查、CSS 和两个现有测试文件：展示完整活动元数据、状态、有序资源、原文入口、缺失与示例状态。当前前端定义 20 个请求测试与十个时间测试，共 30 项，用户确认本地验收；助手未代运行，无逐项日志。后端 116 个方法保持不变，未重跑。没有依赖/锁文件、后端、schema、迁移、数据库操作或生产集成变化。第 17 步需新的明确指令，不自动推进。

随后收到用户明确指令实施第 17 步，已接入生产入口/静态服务及受控启动流程，新增 19 个后端方法（135 个），前端仍 30 个。实施交接后用户授权助手测试，当前检查/构建、135 项后端、30 项前端及 20 组浏览器流程通过；具体隔离和清理见第 41 节。没有安装依赖、改 schema/锁文件、提交/推送或部署。当前工具没有 Render 账号连接，也没有已提供的授权免费服务/数据库标识，远程部署仍为外部阻塞；这不推断用户本人没有账号。第 18 步保持未开始。

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
| `memory-bank/implementation-plan.md` | 40 个依赖有序的实施步骤；第 01–29 步用户确认，第 30 步本地验证通过、待验收及当前远程 CI，第 31 步未开始；本次未修改计划 |
| `memory-bank/architecture.md` | 本文件，记录初始事实、计划职责及验收后洞察，后续随实际功能更新，不把设计目标写成已有代码 |
| `memory-bank/progress.md` | 保存实施、助手检查与用户确认的独立来源；最后用户确认步骤 29，第 30 步验证与 CI 待办单独记录，旧待验收描述保留为历史事实 |
| `.node-version` | 准确 Node 24.14.0，复用既有本机运行时并供 CI 读取；不自动切换或安装本机环境 |
| `frontend/package.json` | 精确直接依赖、npm 11.9.0/Node 24.14.0 和 dev/lint/test/build/preview 脚本；test 使用 Node 内置运行器，不是 Node 业务后端 |
| `frontend/package-lock.json` | npm 生成的 v3 锁，固定传递依赖、公开下载地址及完整性哈希；干净安装由用户确认本地验收，Linux CI 尚未验证 |
| `frontend/.npmrc` | 保存精确版本并严格检查 Node/npm engines；不包含认证或私有 registry |
| `frontend/index.html` | 唯一英文 HTML 源入口、viewport、root 与本地模块；Vite 生成 dist/index.html，Django 将生成目录注册为模板目录，不维护第二份 HTML |
| `frontend/src/main.jsx` | StrictMode、createRoot 和 BrowserRouter 挂载；使用 Router 声明式模式，无服务端框架 |
| `frontend/src/App.jsx` | 首页与详情路由、数字 ID 检查、按 ID 隔离详情组件，以及未知页面回退；第 14 步浏览器实测通过，用户确认本地验收 |
| `frontend/src/api/client.js` | 相对 GET、JSON/HTTP 状态、共用活动展示字段及详情身份检查；第 16 步检查详情简介、阅读身份/标题/作者/年份/类型/理由及 HTTP(S) 原文地址，错误走既有 error/Retry；不改空值或排序，取消并屏蔽晚到结果，不展示内部异常 |
| `frontend/src/hooks/useApiRequest.js` | 两页共用 useEffect 生命周期与清理、加载/结果/重试；结果按 loader/argument/attempt 匹配，旧内容立即隐藏 |
| `frontend/src/components/RequestState.jsx` | 英文加载、未找到和失败/Retry 文案，稳定状态区域及 status/alert 语义 |
| `frontend/src/pages/HomePage.jsx` | 自动加载列表；成功子组件用懒初始化 state 固定一个当前时刻，传给分组函数；保持 Upcoming/Past 两区及单组/全空文案，加载/失败不渲染成功内容；第 15 步用户确认本地验收 |
| `frontend/src/components/TalkCard.jsx` | 语义化 article/h3、示例标记、可选主题/讲者、time 的原始 UTC 属性及伦敦展示、零/单/多资料数量和带活动标题的 Explore resources 可访问名称；不增加独立请求 |
| `frontend/src/utils/talks.js` | groupTalks 接收明确当前时刻，新数组排序且同时间数字 ID 升序；第 16 步 getTalkStatus 共用于首页/详情的 UTC 边界；formatTalkTime 用 en-GB、Europe/London、24 小时及 GMT/BST |
| `frontend/src/pages/TalkPage.jsx` | 自动读取详情；成功子组件固定时间并展示活动/示例/阅读。第 18 步加入该挂载独立的 query、当前标题筛选、数量 status、无结果/清空及焦点返回；保留 API 关联顺序，无资料隐藏搜索；已用户确认本地验收 |
| `frontend/src/components/ResourceCard.jsx` | 第 16 步新增纯展示组件，以 association_id 定位 article/h3，映射类型，处理缺失作者/年份、非空理由及换行，提供带标题/新标签提示的 HTTP(S) 原文入口及 noopener/noreferrer；不另发请求 |
| `frontend/src/pages/NotFoundPage.jsx` | 未知前端地址或非数字详情地址的未找到文案与返回，不发活动 API 请求 |
| `frontend/tests/api-client.test.js` | 第 16 步定义 20 个 Node 请求测试：保留原 19 项、扩展多关联顺序/空值并新增坏详情字段与危险 URL 安全失败；用户确认本地验收，无逐项输出，助手未代运行；无 React DOM、数据库或外网 |
| `frontend/tests/talks.test.js` | 定义十个 Node 测试；在原九项固定时刻、排序、空组、伦敦时间/DST/名称回退之外新增首页/详情共用边界；当前 30 项完整套件验收来源为用户确认，助手未代运行 |
| `frontend/src/api/types.js` | 引用既有 Public API contract 的 JSDoc：活动、扁平关联资料、详情及安全错误；包含 nullable 年份/DOI，不是运行时校验或新规范 |
| `frontend/src/index.css` | 暖白/深绿、系统字体、换行/焦点和活动响应式网格；资源始终单列。第 18 步追加有标签的全宽搜索输入，至少 44 px 高、min-width:0；当前 375/768/1280 px 搜索布局已检查，完整对比度验收留第 33 步 |
| `frontend/vite.config.js` | 开发 base /、localhost:5173/strictPort、原样 API 代理；第 17 步构建 base /static/frontend/，React BrowserRouter 与 API 地址仍在根路径；无生产代理 |
| `frontend/eslint.config.js` | 保留官方 create-vite 8.2.0 ESLint recommended/hooks/refresh 规则，tests/*.js 额外使用 Node globals；不禁用规则或改用 Oxlint |
| `frontend/README.md` | 当前第 30 步验证/待验收状态，指向后端里程碑清单；保留第 18 步标题筛选、数量/顺序、清空焦点、活动隔离、零资料与宽度验收，以及既有启动和历史证据 |
| `.python-version` | 记录独立 CPython 的准确版本 3.13.16，供后续开发、CI 与部署统一运行时；不会自动切换系统解释器 |
| `backend/requirements.in` | 直接依赖约束与平台条件的维护来源；更新时需要重新解析，不能当作锁定安装文件 |
| `backend/requirements.txt` | 可移植的精确版本锁，覆盖直接与传递依赖；Gunicorn 仅在 Linux 安装，无本机路径或凭据 |
| `backend/README.md` | 当前环境、独立数据库启停/初始化、环境配置、用户验证指令及未验证边界；不是完整应用部署指南 |
| `backend/manage.py` | Django 管理入口，加载 config.settings；第 04 步已在新开发库执行基础迁移 |
| `backend/config/__init__.py` | Django 项目配置包标识 |
| `backend/config/settings.py` | 既有环境/会话/时区/安全设置；第 17 步注册 WhiteNoise、dist 模板目录、静态输出及 assets 命名空间，压缩但不二次改名；配置与真实生产仍待验收 |
| `backend/config/urls.py` | 既有 API/JSON 回退、Admin 和健康路径保持优先；第 17 步只新增 / 与数字 /events/{id} 入口，不做宽泛回退，不吞 API/Admin，不新增详情末尾斜杠别名 |
| `backend/config/public_pages.py` | 第 17 步仅 GET/HEAD 返回构建后的入口、禁止缓存；模板缺失返回安全 503，不泄露路径或调试信息；活动是否存在由 API/React 判断，不查询数据库 |
| `frontend/dist/index.html`、`frontend/dist/assets/` | 被忽略的 Vite 生成模板与哈希资产，须构建后才可用；第 17 步授权实测已重新构建，真实产物经后端与浏览器验证 |
| `backend/staticfiles/` | 被忽略的 collectstatic 输出，合并 frontend/assets 与原生 Admin 资产；生成入口不作为静态文件提供；此轮未收集或运行验证 |
| `backend/scripts/deploy.py` | 第 17 步标准库 Linux 发布入口；明确 production 与精确运行时，锁安装/构建/检查/收集；启动检查产物、配置与迁移，成功后 exec 单 worker Gunicorn；不导入示例或初始化管理员 |
| `backend/DEPLOYMENT.md` | 免费 Render 配置、构建 PATH 修复、实际资源/发布/到期证据与独立初始化/备份待办；区分真实发布和完整业务验收 |
| `backend/events/tests/test_public_pages.py` | 第 17 步六个无数据库页面/静态边界方法，以及一个隔离 PostgreSQL Admin 手动新增+关联→匿名 API 重读测试；静态夹具与真实构建检查分开，尚未执行 |
| `backend/events/tests/test_production_build.py` | 第 17 步两个实际 Vite 构建测试：DEBUG=False 入口与直接详情、临时收集后的真实前端/Admin 资产正文和类型；没有 dist 或前缀错误必须失败，不跳过，也不证明浏览器交互 |
| `backend/events/tests/test_deployment.py` | 第 17 步十个标准库入口测试，mock 所有子进程、Linux 和 exec：固定依赖/顺序、迁移失败不启动、运行时/端口/产物拒绝、安全异常；不执行真实 Linux 发布或生产迁移 |
| `backend/config/api_errors.py` | 第 11 步 API 前缀判断、未知地址安全 JSON 404 与中间件；视图/序列化/渲染异常转安全 500，其他 API 500 响应也脱敏；自定义日志仅异常类别，不改非 API 错误；用户确认本地验收 |
| `backend/config/wsgi.py` | WSGI application 入口；第 17 步真实 Render Linux 上已由 Gunicorn 26.2.0 单 worker 启动 |
| `backend/config/asgi.py` | Django 默认生成的 ASGI 入口，保留但未配置对应服务器；生产设计仍使用 WSGI |
| `backend/events/__init__.py` | 唯一业务应用的 Python 包标识 |
| `backend/events/apps.py` | EventsConfig 应用注册与默认主键类型 |
| `backend/events/models.py` | 用户确认本地验收的 Event、Resource 和 EventResource；普通保存前 full_clean，书目标识规范化及字段约束；关联保存活动语境，定义组合唯一、确定排序与外键删除策略 |
| `backend/events/services/__init__.py` | 第 19 步新增轻量服务包；不执行请求、导入或数据库操作 |
| `backend/events/services/doi.py` | normalize_doi 负责纯标识/严格 HTTPS doi.org 链接、一次路径解码、注册者/后缀校验及英文 ValidationError；无网络/ORM |
| `backend/events/services/crossref.py` | request_doi 保留固定目标的原始响应；fetch_metadata 检查成功单 work JSON、调用纯转换并关闭响应；第 21 步将预期状态/JSON/传输故障转为安全 CrossrefLookupError，保留输入/恢复标记，无 ORM/保存；Admin 接入仍待后续步骤 |
| `backend/events/services/resource_save.py` | 第 22 步 save_doi_to_event 与 DoiSaveResult：短事务匹配/创建书目及关联、不覆盖当前数据；第 23 步在回滚后只恢复验证过的 DOI/关联身份唯一冲突，每种最多一次、重读赢家；无 HTTP/会话/路由 |
| `backend/events/tests/test_resource_save.py` | 第 22 步 14 个 PG17 方法：顺序复用/去重、预览后新增/修改模拟、全字段保留、校验及真实数据库失败回滚、调用方事务组合/目标删除、保存无 HTTP；不是并发竞争测试 |
| `backend/events/tests/test_resource_save_concurrency.py` | 第 23 步 14 个 PG17 方法：7 个 TransactionTestCase 独立连接/协调竞争及 7 个错误边界 TestCase；真实 SQL/模型唯一冲突、赢家字段保留、同连接恢复、外层回滚/两阶段恢复和有限尝试；禁止 HTTP |
| `backend/events/services/crossref_metadata.py` | 第 20 步 convert_work 与不可变 CrossrefMetadata：标题/作者/年份/URL/类型/来源白名单，必需补充字段及可选缺失 review 标记；无网络/ORM/持久化 |
| `backend/events/tests/test_doi.py` | 第 19 步 16 个禁止数据库访问的测试，HTTP 边界模拟；规范化、请求前拒绝、真实 Requests 编码/重定向准备、单次传输及不转换响应，助手专项及完整回归均通过 |
| `backend/events/tests/test_crossref_metadata.py` | 第 20 步 18 个测试：13 项纯转换、3 项模拟成功获取和关闭响应、2 项 PG17 完整字段保留/零查询及模型拒绝无效保存；本轮包含于通过的 183 项回归，历史第 20 步为 169 项 |
| `backend/events/tests/test_crossref_errors.py` | 第 21 步 14 个测试：12 项无数据库的状态/JSON/传输、安全文案/输入/恢复与单次请求验证；2 项 PG17 失败零查询及三模型完整快照不变，外部 HTTP 全部模拟 |
| `backend/events/admin.py` | 第 08 步注册三个模型，定义伦敦时间输入/控件、活动公开地址/保存消息、手动书目、已有资料关联与不可更改的关联身份；活动确认及双模型删除权限、全部资源删除拒绝；用户确认本地验收 |
| `backend/events/templates/admin/events/event/delete_confirmation.html` | 单条活动删除确认文案；继承原生模板，保留权限、受保护对象、删除清单、CSRF 与确认/取消控件 |
| `backend/events/templates/admin/events/event/delete_selected_confirmation.html` | 批量活动删除确认文案；继承原生模板，保留选择记录、原生权限/确认和 CSRF，不重写删除收集器 |
| `backend/events/templates/admin/events/eventresource/delete_confirmation.html` | 单条阅读关联移除确认文案，保留原生确认路径；不删除共享书目 |
| `backend/events/templates/admin/events/eventresource/submit_line.html` | 第 27 步继承原生按钮块，按模型自动选择；将当前关联删除操作命名为 Remove from this talk，保留权限与筛选参数，专项及浏览器已验证 |
| `backend/events/tests/test_admin_reading_removal.py` | 第 27 步 10 项 PG17 Admin 移除专项，包含取消/确认、匿名计数、全字段保留、移除权限/CSRF及旧 DOI 结果不重建；与旧 Admin 合跑 39 项通过 |
| `backend/events/tests/test_admin_permissions.py` | 第 28 步 28 项 PG17 跨入口矩阵：逐权限/失效身份/撤权/最小正向权限、真实 CSRF 和 Origin、GET 不写、单条/批量确认保留及资源全部禁删；业务/日志/预览快照；专项及 311 项完整回归通过 |
| `backend/events/templates/admin/events/resource/change_form.html` | 第 26 步继承原生 change_form，在可编辑的已有 Resource 字段前显示共享影响提示，新增页不显示，错误重显保留 |
| `backend/events/tests/test_admin_reading_edits.py` | 第 26 步 8 项 PG17 Admin→匿名 API 验证：共享编辑/提示、单场理由与数字排序隔离、默认/负数/同值确定顺序、无效输入不部分保存及身份来源保留 |
| `backend/events/tests/test_admin.py` | 第 08 步 21 个真实 Admin 请求测试：增改、字段错误、伦敦时间/DST、公开地址、手动来源/空值、关联复用/身份、权限、确认/删除保留、资源全局禁删及真实 CSRF；用户确认本地验收，无逐项输出，助手未代运行；测试账号仅在隔离库创建 |
| `backend/events/views.py` | EventListView 聚合计数及 ID 排序；第 11 步 EventDetailView 聚合计数、Prefetch 有序关联并 select_related Resource，公开只读 JSON，无认证/过滤；两个接口均由用户确认本地验收 |
| `backend/events/serializers.py` | EventListSerializer 八个活动字段及 UTC Z；第 11 步 EventResourceSerializer 白名单扁平书目与当前关联语境，EventDetailSerializer 继承活动字段并读取预加载 reading_links；用户确认本地验收 |
| `backend/events/urls.py` | events 命名空间的 event-list 与 event-detail，分别定位 /api/events/ 和 /api/events/{id}/；列表与详情均由用户确认本地验收 |
| `backend/events/tests/test_event_detail_api.py` | 第 11 步 14 个 APITestCase 方法：字段/类型/空值/白名单、关联身份/排序、共享与当前语境、计数变化、UTC、固定两次查询、无网络/写入、缺失/未知 JSON 404、安全故障及非 API 边界；累计 104 个方法，用户确认本地验收，无逐项输出，助手未代运行 |
| `backend/events/tests/test_public_api_methods.py` | 第 12 步 12 个 APITestCase 方法：真实数据库会话管理员与匿名 GET/HEAD/OPTIONS、写入及其他方法 JSON 405、Allow、无正文 HEAD/404、OPTIONS 无写能力、全字段数据快照、缺失对象/无效正文拒绝及方法覆盖提示；累计 116 个方法，用户确认本地验收，无逐项输出，助手未代运行 |
| `backend/events/tests/test_event_list_api.py` | 第 10 步 8 个 DRF APITestCase 方法：匿名/空列表、精确字段类型、默认值、ID 排序、计数变化、UTC 时区、常量查询次数及无外部调用/业务写入；累计 90 个方法，用户确认本地验收，无逐项日志，助手未代运行 |
| `backend/events/data/demo_reading.json` | 第 09 步的两场虚构讲座、六条真实书目及六条示意阅读关联；保留来源核对日期/链接、稳定身份和明确声明；无网络或数据库行为 |
| `backend/events/demo_seed.py` | 读取本地清单，以同一有时区时刻设置首次日期；按 DOI/稳定标识及关联唯一组合只补缺，用普通模型校验和整批事务，不更新已有记录；用户确认本地验收 |
| `backend/events/management/__init__.py` | 标识 Django 管理命令包，不自动执行导入 |
| `backend/events/management/commands/__init__.py` | 标识命令发现目录，不自动执行导入 |
| `backend/events/management/commands/seed_demo.py` | 独立的显式命令入口，提示迁移状态、调用导入、报告新增数量和安全错误；不创建管理员或提供 HTTP 入口；用户确认本地验收 |
| `backend/events/tests/test_demo_seed.py` | 第 09 步 13 个隔离库测试：首次日期/声明/书目、重复及编辑保留、DOI 复用、手动资料身份、缺项恢复、无效时间、回滚、命令与无网络；用户确认本地验收，无逐项日志，助手未代运行 |
| `backend/events/migrations/__init__.py` | 迁移包标识 |
| `backend/events/migrations/0001_initial.py` | Django 生成的初始 Event 表迁移，含默认值、非空字段、可空唯一 seed_key 和检查约束；用户确认本步迁移验收，助手只生成，未代应用 |
| `backend/events/tests/test_event.py` | 第 05 步 9 个模型测试，覆盖存取、默认值、输入拒绝、NULL/唯一约束、绕过模型校验的数据库保护、UTC 时间及空测试库迁移；用户确认本地验收，无逐项输出 |
| `backend/events/migrations/0002_resource.py` | Django 生成的 Resource 表迁移，依赖 0001_initial；包括唯一 DOI/seed_key、必填字段、年份/类型/来源及标准化 DOI 检查；用户确认迁移验收，助手只生成、未代应用 |
| `backend/events/tests/test_resource.py` | 14 个测试，覆盖书目存取、校验、规范化、数据库保护、手动资料独立保存及迁移；用户确认本地验收，无逐项日志；包含仅供测试的 DRF 书目序列化探针，不是公开 API |
| `backend/events/migrations/0003_event_resource.py` | Django 生成的关联表迁移，依赖 0002_resource；整数主键、必填外键、推荐理由/顺序默认值、活动/资源组合唯一和默认排序；用户确认本地迁移验收，助手只生成、未代应用 |
| `backend/events/tests/test_event_resource.py` | 13 个测试：关联存取、独立活动语境、唯一性、负数及同值排序、字段/外键约束、移除与删除保留规则，以及空 PostgreSQL 测试库迁移；用户确认本地验收，无逐项输出；Admin 权限测试位于 test_admin.py，列表/详情及公开方法验证分别位于对应 API 测试文件 |
| `backend/events/tests/__init__.py` | 后端测试包标识 |
| `.tools/`、`backend/.venv/` | 被忽略的本机解释器、下载/解析中间产物和隔离依赖；不随 Git 克隆分发，另一台机器需独立重建 |
| `.github/workflows/backend.yml` | 前端锁安装/lint/30 项测试/build 后上传 dist；后端下载同次构建并在 PG17 隔离库检查/收集/自动发现测试；当前本地 311 项通过；历史 a174723/d8bdd29 两 job 成功（135 项），未推送第 18–28 步无远程结果 |
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

backend/config 已有环境配置与健康检查，backend/events 的三个业务模型与基础 Admin 已由用户确认本地验收，第 01–08 步基础后端 CI 已在线通过。第 09 步显式离线导入、第 10 步公开列表、第 11 步详情与 API 错误处理、第 12 步方法测试、第 13 步 frontend/src 脚手架均已有用户确认的本地验收。第 09–13 步未提交/推送或线上验证，DOI 服务尚不存在。下表描述完整产品的未来职责，不表示全部功能已运行或验证。

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
- **数据库会话现在有基础持久化，但 DOI 预览仍未实现。** 标准 sessions 迁移及 当时 SESSION_ENGINE 为后续预览提供存储基础；多标签页合并、会话行锁、15 分钟期限和幂等确认须在第 24–25 步实现及验证，不能用基础迁移替代这些业务要求。
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

## 21. 基础后端 CI 线上验证与架构洞察

- **工作流已有独立远程证据。** 2026-10-04，阶段提交 `66b41404f0d3e6aa91c0b6209faf768bb99f86ee` 触发 [Backend checks #37208404049](https://github.com/1uxury/psych-talk-hub/actions/runs/37208404049)，运行、backend job 和所有检查步骤均成功。证据来自 GitHub API 的运行及步骤状态，不是本地用户确认，也不是逐项日志。
- **版本锁在干净 Linux 环境中可安装。** .python-version、requirements.txt 与 backend.yml 分别定义解释器、精确依赖及执行环境；此次 Python 设置、Linux 依赖安装和一致性检查成功，包含 Linux 条件依赖。尚未验证 Gunicorn 生产启动、静态集成或部署。
- **CI 数据库是可丢弃的独立实例。** backend.yml 提供 PostgreSQL 17.11 容器；environment.py 和 test_runner.py 继续约束测试配置及独立测试库。迁移与后端测试步骤成功，没有访问本机开发库或生产库。
- **Git 发布边界与产品发布边界不同。** 当前实现已推送到功能分支，私有配置、解释器和数据库仍被忽略；未合并默认分支、未创建 PR、未部署。第 13 步将扩展前端检查，第 34 步仍需完整可复现性和失败检测验收；第 09 步未开始。

补充：记录文档提交 `f203069` 对应 [Backend checks #37208663494](https://github.com/1uxury/psych-talk-hub/actions/runs/37208663494) 也成功；第 09 步开始前重新通过 GitHub API 核对。该运行不包含第 09 步尚未提交的新增代码。

## 22. 第 09 步实施与验收交接

- 完整阅读六份 memory-bank 文档及 AGENTS，核对此前进度和实现；先更新最新 CI 证据，没有失败需修复。仅编写第 09 步，不开始第 10 步，不提交/推送新增代码。
- 从 Crossref 读取四篇真实论文的公共书目，从 NIH/WHO 原网站核对两篇文章；核对日期与 URL 留在 JSON 清单和后端 README。论文使用 Crossref 第一标题、作者顺序、年份及 URL；文章为人工精选，机构名称作展示署名，无虚构个人作者或 DOI。实时来源核对不是 Django 导入集成，第 19–29 步仍未实施。
- 两场讲座、讲者及资料搭配均明确虚构/示意。首次 is_example 为 true，标题、描述和推荐文案含示例声明；描述保留规定的独立项目与虚构阅读说明。公开 badge/footer 尚无页面可验收，按第 15–16 步实现，不临时新增公开页面或 API。
- demo_seed.py 在显式调用时读取本地清单，规范化资源后匹配 DOI，无 DOI 用 seed_key；活动用 seed_key，关联用活动/资源组合。仅在缺失时通过普通 ORM 保存，已有记录不执行 save/update，包括空值、编辑后的书目、日期、理由及顺序。导入身份必须稳定，不能通过清除 DOI/seed_key 后期望仍匹配原记录。
- 一个导入时刻为新活动计算 +30/-7 天；已存在活动不移动。被删除后重建的活动属于新记录，按新的导入时刻设置日期；另一场活动及所有已有资源保持不变。所有新增记录在一个事务中保存，任一步失败整体回滚，不将静态文件或网络读取作为长期事务工作。
- seed_demo.py 只提供受控命令入口，不创建账号、不访问网络、不加入启动、迁移、AppConfig、CI 或部署。此命令不替代第 22–23 步交互式 DOI 保存与并发冲突转换服务，也不宣称这些验收已完成。
- 新增 13 个测试方法，累计 82 个；用户执行指引在 backend/README.md Step 09。助手未执行 seed_demo、系统检查、迁移检查、测试或浏览器验收，没有访问/修改项目数据库。
- 2026-10-04，用户收到完整验证说明后回复“通过”，据此确认第 09 步本地验收。范围为系统检查、迁移遗漏检查和 82 个后端测试；没有逐项输出，不编造日志或耗时。可选开发库导入、后台浏览及开发数据状态没有独立证据；公开展示仍需第 15–16 步验证。
- 已先请求打开并更新 progress.md，再补充本文件的验收、文件职责与洞察，随后同步 README 和 AGENTS。此次交接仅改文档，不运行检查或测试、不改代码/数据库，不安装依赖、不提交/推送 Git。第 09 步新增代码线上 CI 未验证，第 10 步未开始，需后续明确指令。

## 23. 第 09 步验收后的架构洞察

- **资料清单、导入规则与命令入口各自承担职责。** demo_reading.json 保存经核对的书目、来源和示意搭配；demo_seed.py 执行身份匹配、首次日期和事务规则；management 包只提供 Django 命令发现，seed_demo.py 负责显式调用、计数和安全错误。文件存在或导入模块都不会自动创建数据。
- **稳定身份决定是否补缺，展示内容可以编辑。** DOI、seed_key 和活动/资源组合分别识别共享书目、预置活动/无 DOI 资料及阅读关联。已有记录不执行 save/update，刻意清空的字段也被保留；标题和 URL 不作为合并键。清除身份后无法继续识别原记录，需保持标识稳定。
- **日期只属于新建记录的默认内容。** 同一个有时区导入时刻产生 +30/-7 天，重复导入不会刷新旧活动；删除后重建的活动获得新的首次日期。未来活动随时间变成历史属于正常行为，后续 Demo 验收需重新检查分组，不能靠导入覆盖人工日期。
- **整批回滚与交互式并发导入分属不同验收。** demo_seed.py 的整批事务避免失败后留下部分演示记录；test_demo_seed.py 覆盖末条关联失败及重试。第 22–23 步仍需独立验证交互式 DOI 保存、并发唯一冲突与已有结果转换，本地种子测试通过不能代替这些能力。
- **真实来源核对、隔离库测试及页面展示分别留证。** 来源 URL/日期可供人工复核，自动化测试不访问外部服务；82 个方法的本地验收来源为用户确认。数据库中准备的示例声明不等于已渲染公开页面，已有 CI 结果也不覆盖第 09 步未推送的新文件；后续分别验证页面和线上版本。

## 24. 第 10 步实施与验收交接

- 完整阅读六份 memory-bank 文档、AGENTS 和既有实现，保留此前改动，仅实施活动列表；第 11 步未开始。字段依据仍为 tech-stack.md 的 Public API contract，不另建契约副本。
- EventListSerializer 显式列出八个字段，不含 seed_key、资源书目、会话、预览或管理员信息；DateTimeField 固定 UTC 与 ISO 8601，不依赖当前显示时区。缺失可选活动文字沿用模型空字符串，零关联输出整数 0。
- EventListView 使用 DRF ListAPIView、AllowAny 和 JSONRenderer，无会话认证、分页或过滤；只提供 GET/HEAD/OPTIONS 处理器，不增加 CRUD。get_queryset 用 Count 聚合 event_resources，再按 Event ID 升序；不按时间分组、不逐活动读取关联、不访问 Crossref。两个端点的完整方法验证仍在第 12 步。
- events/urls.py 维护列表路由，config/urls.py 在 /api/ 下挂载；详情及未知 API 的 JSON 404、安全 500 留到第 11 步，未提前实施。前端页面路径 /events/{id} 仍无 React 入口。
- 新增 8 个 APITestCase 方法，累计 90 个；空/单/21 个有资源活动的匿名列表均只有一次数据库查询属于测试断言。本地验收来源为用户确认，无逐项日志或独立查询测量记录，不编造输出或耗时。
- backend/README.md Step 10 提供用户执行的 PostgreSQL 状态、Django 系统检查、迁移遗漏检查和全套测试操作。助手仅写入/阅读源文件，没有运行检查、编译、测试、服务、浏览器或数据库操作，没有安装依赖、生成迁移、提交或推送。
- 2026-10-04，用户收到完整验证说明后回复“通过”，据此确认第 10 步本地验收：系统检查、迁移遗漏检查及 90 个后端测试方法。助手未代运行验收；该确认不涵盖详情与 API 故障处理、两个端点完整方法矩阵、React 或部署。
- 已先请求在编辑器打开并更新 progress.md，再补充本文件的验收来源、文件职责与洞察，随后同步 README 和 AGENTS。此次交接仅更新文档，不运行检查/测试、不改代码或数据库、不安装依赖、不提交或推送。第 09–10 步未提交改动不在既有远程 CI 范围内；第 11 步未开始，等待后续明确指令。

## 25. 第 10 步验收后的架构洞察

- **输出契约由序列化器守住。** serializers.py 的字段白名单控制公开信息边界，内部 seed_key 即使存在于 ORM 实例也不输出；resource_count 来自视图的聚合，序列化器不逐活动读关联。后续详情应复用活动字段和时间规则，按既有契约单独增加关联资料输出。
- **交换时间与界面时间各自明确。** EventListSerializer 显式转换为 UTC Z，后台仍按 Europe/London 输入/显示，未来 React 再负责伦敦文案。冬夏及临时活动时区测试保护接口不随服务器显示时区变化；该验收不代表前端时间展示已实现。
- **计数在查询层完成，分组在前端完成。** views.py 的 Count 与 ID 排序让列表一次返回零关联、普通及示例活动；查询次数不随活动数增长的断言覆盖空/单/21 个活动。Upcoming/Past 时间分组不属于此接口，后续不能把前端排序要求误改为后端列表排序。
- **路由和运行权限具有独立职责。** config/urls.py 挂载 API 前缀，events/urls.py 定位业务入口；ListAPIView 仅提供读处理器，公开读取不需要会话认证或调用 Crossref。第 11 步仍须补齐详情/JSON 错误，第 12 步仍须完成匿名及管理员方法矩阵，不能从列表验收推断这些已通过。
- **本地确认、远程 CI 和产品页面分别留证。** test_event_list_api.py 通过隔离数据库与 DRF 客户端验证列表，不修改开发内容；90 个方法的验收来源是用户回复“通过”，没有逐项日志。第 09–10 步未推送代码仍没有线上 CI 证据，API 可读也不等于 React 页面或公开 Demo 已交付。

## 26. 第 11 步实施与验收交接

- 完整阅读六份 memory-bank 文档、AGENTS、既有代码及锁定版本的 Django/DRF 请求、异常与渲染源码，保留第 09–10 步全部未提交工作，仅实施第 11 步。
- 输出依据引用 [tech-stack.md 的 Public API contract](tech-stack.md#public-api-contract)，不建立新的契约。EventDetailSerializer 继承 EventListSerializer 的八字段及 UTC Z；EventResourceSerializer 通过只读 source 字段将共享书目扁平输出，关联身份、推荐理由和顺序来自当前 EventResource。不返回 seed_key、会话、预览或管理员信息。
- EventDetailView 用 Count 聚合资源数量；Prefetch 按 display_order、id 读取当前活动关联，关联查询用 select_related 一并获取 Resource，保存为 reading_links 列表。活动查询一次、关联与共享资料查询一次，不在序列化中逐项查询。零关联仍保留活动并返回空数组。固定两次查询由新增测试断言覆盖，本地验收来源是用户确认；无逐项日志或独立查询测量记录。
- events/urls.py 增加标准末尾斜杠详情路径；config/urls.py 将已知业务路径放在 API 404 回退之前。回退包括 API 根、无效 ID 及未知深层路径；缺少契约要求的末尾斜杠同样返回 JSON 404，不自动重定向。no_append_slash 防止 CommonMiddleware 将未知路径改为重定向，回退无业务写入。
- config/api_errors.py 仅作用于 /api 或 /api/ 子路径。Django 异常中间件覆盖 DRF 未处理的视图、序列化及延迟渲染故障，返回不带内部信息的 JSON 500；响应阶段将其他 API 500 正文也统一脱敏。缺失活动仍由 DRF 产生 JSON 404，未知路径由显式回退处理，DEBUG 开关不使这些响应转为 HTML。自定义故障日志只记录异常类别，不写异常正文、SQL、凭据或 traceback；非 API、Admin、健康检查沿用既有处理。
- 新增 test_event_detail_api.py 的 14 个方法，覆盖契约、空值、零资料、负数/同值排序、共享编辑与当前活动理由/移除、UTC、零/单/21 条资源的两次查询断言、无外部请求/写入，以及缺失/未知 JSON 404、数据库/序列化/渲染故障与非 API 边界。先前 90 个与本次 14 个合计 104 个方法；README Step 11 提供用户验证说明。
- 本次仅读取/编写文件，未运行系统检查、编译、迁移、测试、服务器、浏览器或 seed_demo，未访问/修改开发或生产数据库；无新模型/schema、依赖、迁移、Git 提交/推送或部署。既有远程 CI 不覆盖第 09–11 步新增文件。
- 2026-10-04，用户收到第 11 步验证说明后回复“通过”，据此记录本地验收：Django 系统检查、迁移遗漏检查与 104 个后端测试方法。未提供逐项输出，不编造日志、耗时或独立查询测量。本地确认不代表第 12 步方法矩阵、React、DOI 导入或线上部署完成。
- 已先请求在编辑器打开 progress.md（返回 queued），先更新进度，再补充本文件的验收、文件职责与洞察，随后同步 README、AGENTS。本次交接仅改文档，不运行检查/测试、不改代码或数据库，不安装依赖、不提交/推送 Git。第 09–11 步远程 CI 待验证；第 12 步未开始，等待后续明确指令。

### 本步设计依据与职责边界

- 活动字段继承避免列表与详情产生不同时间或空值规则；关联序列化器把书目共享字段与活动语境汇合成契约要求的扁平对象，不修改模型结构。
- reading_links 是明确的预加载结果，排序基于关联身份，不由资源 ID 或书目查询排序替代。查询次数验证由测试断言承担；用户确认本地验收，无独立性能测量或压测结果。
- JSON 404 的路由边界与安全 500 的异常边界分别实现，避免未来 React 入口吞掉 API 地址。异常处理不依赖 DRF renderer，因此 JSON 渲染本身故障仍可返回安全正文；后台 HTML 行为单独保留。
- 只读处理器沿用第 10 步方式；第 12 步仍需独立验证两个端点的匿名及已登录管理员写方法拒绝、HEAD 无正文与 OPTIONS 能力，不能从本步源码推出这些已通过。

## 27. 第 11 步验收后的架构洞察

- **共享书目与活动语境在输出处汇合。** models.py 仍分别保存 Resource 与 EventResource；serializers.py 的 EventResourceSerializer 明确区分 association_id、resource_id，并将共享标题/作者与当前活动理由/顺序组合成扁平资料。共享修改在下一次读取时反映到所有引用活动，关联语境只影响当前活动。
- **预加载由视图准备，序列化器消费。** views.py 在 EventDetailView 中负责 Count、排序与两次查询的数据准备；EventDetailSerializer 读取 reading_links，不自行发起数据库查询。继承列表字段让两个接口保持相同 UTC 和空文字规则；零资料、单条及 21 条资料的查询断言由 test_event_detail_api.py 保护。
- **未知地址与服务故障分别处理。** config/urls.py 负责有效 API 和未知地址回退的优先级，events/urls.py 只定位业务端点；config/api_errors.py 负责 JSON 404 和安全 500。该异常边界不依赖 DRF JSONRenderer，延迟渲染故障也有安全响应；Admin 与非 API 页面仍保留各自 HTML 行为。
- **错误响应和日志各有信息边界。** 客户端只收到非空 detail，未处理故障不会返回异常正文或 SQL；自定义日志只记录异常类别。当前故障模拟测试验证这些边界，不代表生产日志与真实数据库故障已验收，第 36 步仍需完整检查。
- **本地验收、方法矩阵与线上证据分别交接。** test_event_detail_api.py 新增 14 个方法，累计 104 个，本地通过依据为用户确认，无逐项输出或独立性能数据。第 12 步完整方法矩阵未开始，第 09–11 步仍未提交/推送，既有远程 CI 不覆盖它们；公开 API 已有本地验收也不等于 React 页面或 Demo 已交付。

## 28. 第 12 步实施与验收交接：公开接口方法限制

- 完整阅读六份 memory-bank 文档、AGENTS、已有视图/序列化器/路由/模型/测试及锁定 Django/DRF 方法分派、OPTIONS 元数据与测试客户端源码；保留此前全部未提交改动，仅实施第 12 步。
- EventListView 与 EventDetailView 已使用 ListAPIView/RetrieveAPIView 和显式 http_method_names，仅提供 GET/HEAD/OPTIONS。无需改写运行代码或新增 CRUD/路由/权限系统；本步通过新的回归测试守住现有方法边界。
- 新增 backend/events/tests/test_public_api_methods.py，共 12 个 APITestCase 方法，与先前 104 个合计 116 个。测试身份包括匿名访客与真实数据库会话登录的超级管理员；APIClient 启用 CSRF 检查，先验证管理员会话能够访问 Admin，不使用 force_authenticate 冒充登录。
- GET 对两端点与两身份返回 JSON 200；HEAD 比较 GET 状态、Content-Type、Content-Length、Allow 并断言正文为空，缺失活动 HEAD 保持无正文 404。OPTIONS 的 Allow 精确为 GET/HEAD/OPTIONS，JSON 元数据不含写入 actions，不查询活动或访问外部服务。
- POST/PUT/PATCH/DELETE/TRACE/CONNECT/PURGE 对两端点与两身份返回含非空 detail 的 JSON 405，精确 Allow 保持只读；逐次比较三个业务模型的所有数据库字段，验证内容、私有身份及共享关联未变。拒绝请求不调用活动 queryset 或外部服务。
- 有效详情路由即使对象不存在，写方法仍在对象读取前返回 405；GET/HEAD 保持 404。无效 JSON、未支持的正文格式和方法覆盖提示不能打开写入能力或把 POST 改成 GET。未知 API 地址继续沿用第 11 步的 JSON 404，不重新定义路径与方法的优先级。
- OPTIONS 的 parses 描述请求正文解析器支持的格式，不代表允许写入；实际能力由 Allow 和处理器控制。公开 API 不使用会话认证，管理员的 Django 登录不会扩大公开能力，后台编辑继续走独立权限/CSRF 路径。
- 实施阶段同步本文件、backend/README.md 与 AGENTS.md 的待验收状态及文件职责，未提前标记通过。实施只读写文件，未执行系统检查、编译、测试、迁移、服务器、浏览器或 seed_demo，没有访问/修改数据库、安装依赖、提交/推送或部署。
- 2026-10-04，用户收到完整验证说明后回复“通过”，据此记录本地验收：Django 系统检查、迁移遗漏检查及 116 个后端测试方法。无逐项输出，不编造日志、耗时或数据库测量；助手未代运行验证。该确认不代表 React、DOI 管理闭环、生产或第 09–12 步线上 CI 已完成。
- 已先请求在编辑器打开 progress.md（返回 queued），先更新进度，再补充本文件验收、文件职责与洞察，随后同步 README 与 AGENTS。验收交接只改文档，不运行检查/测试、不改应用代码或数据库、不安装依赖、不提交/推送。第 13 步未开始，需后续明确指令。

## 29. 第 12 步验收后的架构洞察

- **公开方法与管理员授权属于不同边界。** views.py 的只读视图和显式 http_method_names 决定公开 API 能力，登录 Admin 不会扩大它。admin.py 继续负责经过模型权限及 CSRF 保护的管理操作；公开 405 测试通过不代表未来 DOI 自定义入口的完整授权已验收。
- **方法限制、能力声明和响应语义应一起保护。** test_public_api_methods.py 同时检查写方法 405、精确 Allow、OPTIONS 无写入 actions，以及 HEAD 的状态/响应头和空正文。DRF 元数据中的 parses 仅说明解析格式，不能当作 CRUD 能力；未来改通用视图或路由时应保留这一组回归测试。
- **已登录身份需要真实会话证据。** 测试创建隔离库账号，通过 Django 数据库会话登录并确认 Admin 可访问，再请求公开端点；不依赖 force_authenticate 或伪造请求头。这验证实际会话与公开方法边界，不意味着开发/生产账号已初始化。
- **数据保留应比较内容，而不止数量。** 新测试 snapshot 比较三个业务模型所有字段，覆盖共享书目、私有身份和各活动关联语境，防止数量不变却被覆盖。缺失对象的写方法在读取前拒绝，错误正文或方法覆盖提示也不能触发业务写入；未知地址仍由独立 JSON 404 回退处理。
- **文件分工与验收来源继续明确。** views.py 维护运行时只读处理器，urls.py 定位路由，serializers.py 维护输出，test_public_api_methods.py 保护方法边界。新增 12 个、累计 116 个方法的本地验收来源是用户确认，无逐项日志；第 09–12 步未提交/推送，既有 CI 仅覆盖第 01–08 步，第 13 步与前端 CI 尚未开始。

## 30. 第 13 步实施与验收交接：前端脚手架

- 已完整阅读六份 memory-bank 文档、AGENTS、此前进度、已有接口序列化器/根路由/环境加载器/CI 和忽略规则；保留之前全部未提交修改，仅实施第 13 步。
- 核对 [React 官方版本](https://react.dev/versions)、[Vite 安装说明](https://vite.dev/guide/)、[Router 声明式安装](https://reactrouter.com/start/declarative/installation) 和官方 npm 包元数据。选择 React/React DOM 19.3.0、Vite 8.3.2、React 插件 6.1.1，Router 采用计划中 7.x 的稳定补丁 7.18.4；没有为了 latest 的 Router 8.x 改变既定系列。
- 复用本机已有 Node 24.14.0/npm 11.9.0，准确记录在 .node-version、manifest 与 CI。没有改全局安装、系统 PATH、Python、Anaconda 或旧数据库；.npmrc 严格检查运行时，另一台机器需自行准备相同版本。
- 新版 create-vite 9.2.1 的 React 模板已改用 Oxlint。为保持本项目 ESLint 选型，读取官方 create-vite 8.2.0 的 React ESLint 模板，保留 recommended/hooks/refresh 规则并锁定兼容的 ESLint 10.12.0 等工具；不引入另一套 lint、React Compiler 或 TypeScript 工具链。下载模板留在被忽略的 .tools/frontend-scaffold。
- 首次 npm 安装即生成 package-lock.json，直接版本精确固定，传递版本、公开 registry 地址及完整性哈希由 npm 生成，含 Windows/Linux 可选原生绑定。安装使用项目内 .tools/npm-cache，未执行依赖生命周期脚本；安装成功只表示准备操作完成，不代替 npm ci/lint/build 或 Linux 验收。
- main.jsx 挂载 StrictMode/BrowserRouter，App.jsx 仅提供两条公开页面路由占位。临时按钮通过相对地址读取真实列表及首场活动详情，显示作者/年份缺失占位；无硬编码活动身份、假数据或写入能力。首页分组、完整详情、搜索尚未实现。共用请求模块、取消旧请求、完整加载/404/失败和未知页面状态属于第 14 步，不能将本步单次连接检查当作完成这些能力。
- api/types.js 引用既有技术契约，记录整数身份、UTC Z、空字符串、年份/DOI null、扁平关联和排序；不改变后端输出，也不把 JSDoc 当作运行时字段校验。页面不直接访问 Crossref。
- vite.config.js 仅提供开发代理，/api 原路径转发至 127.0.0.1:8000，无 CORS 包；固定 localhost:5173/strictPort，避免悄悄换端口。Django 仍直接提供 Admin，未修改后端运行代码/schema/数据库。生产资产前缀、入口模板和 WhiteNoise 仍留第 17 步，Vite preview 不提供该开发代理。
- 同一 backend.yml 增加独立 frontend job：读取 .node-version、固定 npm、从锁 npm ci，再 lint/build；后端 PostgreSQL job 保持原流程。工作流名称为 Project checks；未提交/推送，无新远程执行证据，不能引用旧 Backend checks 成功冒充前后端 CI 通过。
- frontend/README.md 给出干净安装、lint/构建、真实代理/空值、路由刷新、未知 API JSON 404、116 个后端回归及对应提交 CI 的用户验证指引；同步 AGENTS、后端 README 与本文件实际职责。用户确认后已先请求打开 progress.md（返回 queued），先更新进度，再补充本文件验收与洞察，最后同步相关指南。
- 2026-10-04，用户明确回复“13步通过”，据此记录本地验收。截图直接确认 Django 启动/系统检查与真实后端空列表连接，另有路由项确认；干净安装、lint/构建、后端回归、其余代理/空值/错误/键盘场景按总体确认记录，没有完整逐项日志。不编造耗时、具体导入命令或开发账号状态。
- npm ci 验证期间出现过删除 Rolldown 原生绑定的 EPERM；已指导先停止 Vite再重装，README 补充该顺序。截图只证明当次失败，文件占用是当时判断；最终验收没有附恢复日志，不声称助手诊断了具体锁定进程或修改了权限。
- 助手仅阅读/编辑文件、核对官方公共版本及安装依赖，没有代运行 npm ci 验收、lint、build、Django 检查/迁移/测试、服务、浏览器或演示导入，也没有访问/修改数据库、创建部署、提交或推送。本次通过后的交接只改文档。**第 13 步本地验收来源为用户确认，第 09–13 步线上 CI 待验证，第 14 步未开始。**

本步的新增文件职责见第 2 节。运行时/版本锁负责可复现基础，JSDoc 负责契约说明，App 的临时读取负责代理验证，CI 配置负责未来远程检查；四者均不能单独证明产品页面或完整验收已完成。

## 31. 第 13 步验收后的架构洞察

- **运行时、依赖锁和工具配置分别交接。** .node-version 固定 Node，package.json 固定直接依赖/npm 与脚本，package-lock.json 固定传递依赖，.npmrc 强制版本策略。eslint.config.js 沿用官方推荐规则，vite.config.js 负责转换与开发代理；本地验收不能代替未执行的 Linux CI。
- **入口和临时读取不等于正式页面。** index.html 提供 root，main.jsx 挂载 StrictMode/BrowserRouter，App.jsx 负责两条路由及手动连接检查，index.css 负责基础视觉。第 14 步应将共用请求、取消旧响应和完整错误状态拆出，第 15–16 步再实现正式浏览，不能继续依赖一次性按钮承担全部请求生命周期。
- **契约描述、空值与界面显示各有职责。** api/types.js 的 JSDoc 引用唯一技术契约，不提供运行时校验；后端序列化器维护 JSON 空字符串/null，页面选择作者/年份的占位文案。连接成功且列表为空证明代理可读，不能由该截图单独证明有资料或空值渲染；这部分验收依据为用户整步确认。
- **代理与生产入口是两套环境职责。** 开发 Vite 将 /api 原样转发至 Django，Admin 直接使用后端端口；Django 的未知 API JSON 404 保持独立。第 17 步仍须新增生产模板/静态前缀/WhiteNoise，不使用 Vite dev 或 preview 代替生产服务。
- **重装依赖需要先释放开发进程。** Windows 原生绑定可被运行中的前端占用，README 明确先停止 Vite再 npm ci，不删除锁文件或要求修改全局权限。frontend/README.md 保存复现路径，progress.md 保存确认来源，backend.yml 保存未来双 job 检查；目前只有第 01–08 步有远程 CI 证据。

## 32. 第 14 步实施交接：共用请求状态与页面路由（待用户验证）

本节保留最初只编写实现、尚未执行检查时的状态。随后用户授权助手检查，最新实测结果与洞察见第 33 节。

- 实施前完整阅读 memory-bank 六份文件、根 AGENTS、progress 及现有前端/API/工作流，保留全部先前改动。只实施第 14 步，用户确认前不开始第 15 步；没有重跑第 13 步验收。
- client.js 将请求限制为相对 GET，发送 JSON Accept 与 AbortSignal。先检查 HTTP 状态，再检查成功响应类型并解码；列表需要数组及基本身份/标题，详情需要匹配当前 ID 的对象与 resources 数组。只做防止明显错误渲染的基本结构检查，不复制完整契约或修改空字符串/null/资料顺序。404 转 not_found，其他 HTTP、网络、JSON 或基本结构错误转 error；不展示响应错误正文、异常详情或凭据。
- startReadRequest 拥有一个 AbortController 与独立 active 标记；cancel 同时中止请求并取消更新资格，即使 fetch 或 JSON 解码忽略取消，旧成功或失败也不能提交结果。settled Promise 仅方便等待单次请求生命周期，未引入轮询、缓存、自动重试或外部请求库。
- useApiRequest.js 用稳定的导入 loader、活动参数与重试次数识别结果；不同身份的已有数据在 render 时立即隐藏为 loading，不在 Effect 内同步更新加载状态。Effect 只启动异步读取并返回取消清理；重试是用户操作并生成新生命周期。App 中详情按 id 使用 key，切换活动重建独立状态。React StrictMode 额外 setup/cleanup 使用同一路径；实际浏览器效果待验证。
- RequestState.jsx 维护 Loading talks… / Loading resources…、规定的活动未找到及失败/Retry 文案，使用 status/alert 与稳定区域。HomePage 成功显示未分组真实链接，空数组为成功；TalkPage 成功仅显示当前标题/计数及示例声明，不误把无资料活动视为不存在。NotFoundPage 处理未知地址/非数字活动参数，提供 Back to talks；API 未知地址仍由 Django 返回 JSON，不使用 React 回退。
- 页面内容为第 14 步验证所需的最小展示；Upcoming/Past 分组、时间、正式卡片仍留第 15 步，完整详情与阅读留第 16 步，搜索第 18 步。首页不再显示临时检查按钮，详情不再是“Talk page”占位。没有更改产品/API 契约、两份设计、技术栈、实施计划、后端运行代码或数据库。
- tests/api-client.test.js 新增 18 个 Node 内置测试，使用 mock fetch 和手动控制的 Promise；覆盖安全 GET、原样空值/顺序、404/500、错误 JSON/HTML/结构/身份、空列表与零资料成功、失败再尝试、延迟、取消、晚到 body、B 先于 A 返回、取消拒绝及立即 setup/cleanup/setup。测试只覆盖请求模块/生命周期，不宣称已覆盖 React DOM 或浏览器返回。
- package.json 增加 npm test，无新依赖或 lockfile 修改；ESLint 仅对 tests 目录补充 Node globals，保留既定推荐规则。backend.yml 的前端 job 在 lint/build 之间加入请求测试，后端 PostgreSQL job 保持原流程；新增 job 与第 09–14 步仍未提交/推送或远程运行。
- frontend/README.md 提供完整用户验证：lint、18 测试、build；真实自动读取/刷新/Back/Forward；Network 延迟、Offline 后恢复 Retry；已确认不存在的数字 ID、非数字 ID、未知页面与未知 API；两场活动快速切换、取消及旧结果保护。没有数据时需记录浏览器场景未验证，开发导入仅由用户显式执行，不推断当前开发库或管理员状态。
- **实际验证状态：代码已写入，待用户验证。** 助手仅读取/编辑文件及核对官方文档，未运行测试、lint、build、系统检查、服务器、浏览器、迁移/导入或数据库操作；没有安装依赖、提交、推送或部署。116 个后端测试不变，第 14 步尚未验收。progress.md 本轮保持最后已验收步骤 13；确认通过后先请求打开并更新 progress，再补充本文件的实际验收来源及新洞察。第 15 步未开始。

## 33. 第 14 步助手实测与用户确认

2026-10-04，用户明确要求“你帮我检查”，授权助手执行第 14 步验证。lint 退出码 0；Node 请求测试 18/18 通过、0 失败/跳过/取消；Vite 构建退出码 0。复用现有开发服务与只读数据，不重装依赖、不重跑未变的后端测试，不修改应用代码或数据库。已先请求打开 progress.md（queued）并记录实测，再补充本文件与相关指南。用户随后回复“通过”，确认第 14 步本地验收；确认交接仍先请求打开并更新进度，再补充本文件。第 15 步未开始，远程 CI 仍待验证。

- **请求逻辑和 React 生命周期有独立证据。** api/client.js 的 18 个测试使用 Node mock fetch，验证 HTTP/JSON、空值和取消/晚到结果。Headless Edge 154 另外完成 14 组真实 DOM/网络/导航检查，包括两页自动读取、刷新、Back/Forward、缺失/未知路由、延迟与断网 Retry、快速 A→首页→B、键盘 Tab/Enter 和 3 px 可见焦点；无未捕获应用异常。两类检查不能互相替代，也不构成生产部署或完整浏览器矩阵验收。
- **取消必须同时阻止晚到结果提交。** 实际切换观察到请求取消，等待原延迟后 B 的标题仍保持正确。Node 测试额外控制 B 先返回、A 后返回且忽略 abort 的顺序，保护 active 标记；useApiRequest 的身份匹配与 App 的详情 key 保护加载时不显示旧活动。离页取消未产生失败提示，错误后 Retry 成功恢复真实数据。
- **空数据、HTTP 故障与不存在分属三个状态。** 真实不存在的活动为 JSON 404，显示未找到而非零资料；浏览器内临时覆盖分别验证 200 空列表、200 零资料详情和 500 空数组。前两者成功、后者失败且可重试；这些受控覆盖不修改数据库，不当作开发库实际空数据的证据。页面状态和 API 错误边界继续独立，未知 API 仍为真实代理 JSON 404。
- **临时浏览器检查与仓库测试分工明确。** 浏览器工具初始化失败，受限环境启动的 Edge 退出；同样隔离参数的授权重试成功，没有审批拒绝。独立浏览器只访问本地公开页面，不登录 Admin、不操作用户日常浏览器。临时 CDP 脚本、profile、截图与结果保存在被忽略的 .tools/step14-browser；已清除响应覆盖/恢复网络并关闭本次浏览器，用户既有前后端服务保留。没有加入正式框架或依赖；CI 仍只新增 Node 请求测试。
- **实际读取、前端构建与远程发布分别交接。** 当时真实列表包含 ID 1/2、资源计数 4/3，详情与列表一致；这只记录本次观察，不推断此前如何导入或创建账号。结果文件时间 2026-10-04T19:32:02.388Z；截图确认基本界面、加载和失败状态。构建只是生成本地资产，生产入口仍留第 17 步。第 09–14 步未提交/推送，旧 CI 不能覆盖这些改动；第 15 步活动分组与第 16 步完整阅读未实施。

## 34. 第 14 步验收后的文件职责与洞察

- **后续页面复用已有请求能力。** client.js 负责 HTTP/JSON 与取消后结果有效性，useApiRequest.js 负责 React 生命周期/重试身份，RequestState.jsx 负责英文状态文案。HomePage 与 TalkPage 只消费结果；第 15–16 步增加内容展示时不要另写 fetch 或把错误当作空数据。
- **路由身份与资料身份分开。** App.jsx 的详情 key 隔离不同活动状态，NotFoundPage.jsx 处理前端未知地址；backend/config/urls.py 继续保护 API JSON 回退。页面分组不能改变 API 路由、字段、活动 ID 或关联资料顺序。
- **测试、指南与进度各自保存不同证据。** tests/api-client.test.js 是可复现的 18 个请求测试，frontend/README.md 保存运行与浏览器检查方法，progress.md 保存实际执行和用户确认，本文件解释分工；.tools 中临时浏览器记录不随 Git 分发，也不代替 CI。
- **第 14 步确认没有扩展已验证范围。** 用户“通过”确认已报告的本地结果；确认交接仅更新文档，没有重跑测试、修改代码/数据库或提交推送。后端 116 个测试未在本步重跑，远程 CI/生产仍须独立证据。第 15 步需新的明确指令，首页分组与完整阅读尚未实现。

## 35. 第 15 步实施交接：首页分组与活动卡片（历史待验证状态）

本节保留实现及截图修正当时的待验证状态；后续用户确认与最新交接见第 36 节。

- 实施前完整阅读六份 memory-bank 文件、AGENTS、progress 和既有前端/测试/工作流，保留所有先前改动。仅实施第 15 步，不修改产品/API 契约或第 16 步详情展示。
- HomePage 继续使用 readTalks/useApiRequest/RequestState。只在 success 时挂载 TalkGroups，用懒初始化 state 捕获一次 Date.now，两个分组共用同一快照；刷新、离开再进入或重试后成功挂载会重新取时刻。页面停留期间没有定时器或实时移组，这与 MVP 不增加实时更新一致，也避免不纯的 render 时钟调用。
- utils/talks.js 负责纯分组及时间展示：starts_at 的 UTC 时刻晚于快照为 Upcoming，恰好等于或早于快照为 Past；分别时间升序/降序，最终按数值 ID 升序。只排序新分组数组，不修改 API 数组、记录或后端 ID 排序。Intl.DateTimeFormat 明确 en-GB、Europe/London、24 小时及 short 时区名称，展示 GMT/BST；比较时不使用格式化字符串。
- TalkCard.jsx 只负责展示标题、非空主题/讲者、伦敦时间、真实资源数量及 Explore resources；语义化 time 的 dateTime 保留原始 UTC 值。示例标记只依赖 is_example；普通活动没有示例标签。0 条资料仍有活动详情入口；单数/复数区分。卡片链接的可访问名称含活动标题，正文保持规定的英文文案。
- 成功时 Upcoming/Past 标题始终保留，分别展示规定空组提示；全空另在介绍下方展示规定总提示。加载、失败及未找到仍由原状态组件负责，此时不展示成功空组/卡片。CSS 使用标准颜色与 16/24/32 间距、白卡片、最小 44 px 链接和原焦点样式；小于 768 px 单列，达到 768 px 双列，允许长文字换行。
- api/client.js 列表只增加卡片实际需要的防御检查：日期字符串可解析，计数非负整数，主题/讲者字符串、示例布尔值。不填造假的日期/数量或尝试纠正契约；坏数据进入现有 error/Retry，避免日期格式化时渲染崩溃。详情读取及请求取消/身份行为保持不变。
- tests/talks.test.js 新增九个 Node 测试，使用固定 now 检查 ±1 毫秒和精确相等、两组方向/数字 ID 同值排序、冻结数组/记录保持不变、单组及全空、冬夏/跨日及春秋 DST，并模拟浏览器时区名称回退。api-client.test.js 新增一个多种坏卡片字段的错误状态测试。总计 19 个请求测试加九个分组/时间测试，现有 npm test/CI 自动发现，无新依赖或配置变化。
- frontend/README.md 给出用户 lint/test/build、真实数据卡片和导航、375/768/1280 px、键盘及请求状态回归；单组和全空通过仅本地标签页 fetch 响应覆盖验证，不删除或更新数据库。该临时夹具只匹配同源活动列表 GET，刷新可清除，虚构 ID 不能当作真实活动；本轮没有执行该夹具。
- 同步本架构文件、AGENTS 和前后端 README 的实际状态；progress.md 保留最后用户验收步骤 14。确认后先请求打开并更新 progress，再补充本文件的新洞察和验证来源。**当前仅完成实现，尚未运行 lint、28 个测试、构建、浏览器或后端回归，不标记第 15 步通过。**
- 本轮没有安装依赖、改锁文件、修改后端应用/schema/迁移、启动服务、访问或写入数据库、导入示例、提交/推送或部署。第 09–15 步远程 CI 未验证，历史成功只覆盖第 01–08 步。完整详情与资源卡片留第 16 步；在用户验证前不得开始，验收通过也仍需后续明确指令。

### 本步结构洞察

- 请求状态属于加载层，分组与时区显示属于展示层，TalkCard 不另发请求；API 仍返回完整未分页列表和聚合计数。HomePage 的时间快照与 utils 的显式参数分别支持 React 稳定渲染及固定时刻测试。
- groupTalks 比较 UTC 时刻；formatTalkTime 将同一个时刻转为伦敦标签。秋季重复的本地 01:30 可因 GMT/BST 区分，排序不会因此颠倒。后续详情可复用格式化函数，但本步没有接入详情。
- 逻辑测试不证明 JSX、响应式布局或浏览器导航通过；README 的浏览器场景必须另行验收。现有 18 个请求测试的历史成功也不能替代这次扩展后的 28 项执行结果。
- 用户提交的首页截图直接显示两组真实活动卡片、资源计数 4/3、讲者、示例标签和阅读入口，说明该次页面已有数据；不能据此判断测试套件、全部空状态或整步验收通过。截图冬季时间为 GMT+0，夏季为 BST；formatTalkTime 改用 formatToParts，仅将时区部分 GMT+0/GMT+00:00 映射 GMT、GMT+1/GMT+01:00 映射 BST，原日期时间和 London 计算保持不变，避免按月份猜夏令时。已补回归测试并同步测试数量，助手未执行检查，等待用户重新验证。

## 36. 第 15 步验收后的文件职责与洞察

2026-10-04，用户在 GMT/BST 修正和重新运行 lint、28 项测试、构建及刷新确认的说明后回复“通过”，据此确认第 15 步本地验收。没有逐项输出或修正后截图，不编造助手独立执行、命令日志或测量数据。已先请求打开 progress.md（queued）并更新进度，再补充本文件及指南；此确认交接只改文档。第 16 步未开始，第 09–15 步远程 CI 未验证。

- **HomePage 管成功列表，utils 管规则，TalkCard 管展示。** HomePage.jsx 继续消费原请求 Hook，通过成功子组件的一次时刻快照保证两组边界一致；utils/talks.js 接收显式时刻，创建新分组数组，不更改 API 数据。TalkCard.jsx 渲染单场活动的元数据和路由链接，不重复查询后端。index.css 负责卡片/网格/焦点；详情仍沿用原简版，不据首页验收推断阅读卡片完成。
- **时间比较与名称兼容分别处理。** groupTalks 比较 UTC 时刻，formatTalkTime 使用 Europe/London 确定日期与时差，再只规范化 Intl 时区部分的 GMT+0/GMT+1 回退。不同浏览器名称差异不能靠硬编码月份解决；原始 UTC time 属性仍可供核对。未来第 16 步可复用格式化函数，第 32 步仍需完整首页/详情一致性验证。
- **传输检查、逻辑测试与浏览器证据分开。** client.js 保护卡片必要字段，不制造替代值；api-client.test.js 共 19 项，talks.test.js 共九项，合计 28 项。固定时刻和模拟 formatToParts 可复现边界及名称差异，不能单独证明 JSX 或布局。修正前截图证明两组卡片当时显示及原标签差异，最终整步验收依据为用户确认。
- **文档各自保留对应证据。** frontend/README.md 保存验证方法和临时浏览器夹具，progress.md 保存实施/修正/确认来源，本文件保存职责与洞察，AGENTS.md 保存推进规则。夹具只覆盖当前标签页列表 GET，刷新清除，不代表写入数据库或正式演示数据。
- **确认不扩大发布范围。** 助手未运行第 15 步检查，没有重跑 116 个后端测试或改变应用/schema/依赖。第 01–08 步历史 CI 不覆盖当前未推送工作；线上、完整两页可访问性与生产集成仍留后续验收。下一步需用户新指令，先读全部 memory-bank，再实现第 16 步完整详情。

## 37. 第 15 步授权后实测：桌面网格与完整当前验收

2026-10-04，用户要求助手检查，关注“电脑版也是单列，可能没有第二列内容”。实际 lint/构建退出码 0，Node 28 项通过、0 失败/取消/跳过；独立 Headless Edge 154 的 19 组场景通过，结果时间 2026-10-04T20:39:58.180Z。第 36 节未代运行的说明保留为首次确认时的历史事实，本节补充之后的独立证据。已先请求打开并记录 progress.md，再更新本文件。

- **网格列数与内容数量分开。** index.css 对每个 talk-grid 独立定义断点：1280 px 实测两列各 504 px，24 px 间距；真实 Upcoming/Past 各一张，均在左列，右列空白。HomePage 先渲染 Upcoming 区、再渲染 Past 区，不让两个不同分组共享同一网格。同组临时多卡片实测 1280/768 px 并排，767/375 px 纵排；第一、第二张的坐标和轨道已记录，无横向溢出。
- **卡片实测与状态实测覆盖不同路径。** 真实服务核对 ID 1/2、计数 4/3、字段、示例/GMT/BST、44 px 阅读链接、详情刷新与返回/前进、两页延迟/实际断网/Retry；键盘遍历链接有 3 px 焦点，Enter 可导航。浏览器覆盖数据验证同时间数字 ID 排序、精确开始边界、单组/全空、可选内容/零单多计数、长文字、500 和坏时间安全失败。设备时区改为洛杉矶后日期仍按伦敦显示；未捕获应用异常为零。
- **临时验证不属于应用数据或正式框架。** CUA 初始化因路径错误失败，独立隐藏 Edge 启动获自动审查允许，没有拒绝，不使用日常浏览器/Admin。CDP 工具、profile、结果和截图仅在忽略的 .tools/step15-browser，未安装新依赖。固定时间及响应覆盖只在该浏览器使用，未写数据库；全部恢复并关闭该浏览器，保留用户服务。
- **当前无需调整卡片布局。** 桌面右侧留白符合每组只有一条记录的现有内容与双列 CSS；增加同组记录后自然使用右列。不能因只有一张卡片就推断媒体查询失败，也无需修改示例数据以适配截图。应用源码、样式、schema、锁文件未修改。
- **验证边界仍明确。** 本次增加第 15 步实际前端证据，没有重跑 116 个后端测试、推送/远程 CI、生产部署或实现第 16 步。完整两页对比度与生产路径仍按后续步骤验收。progress.md 记录执行来源，frontend/README.md 保留复现方法，AGENTS.md 指明最新交接。

## 38. 第 16 步实施交接：详情页基本阅读（待用户验证）

本节保留首次实施时的待验证状态；随后用户确认通过，最新验收来源与文件职责洞察见第 39 节。

- 实施前完整阅读 memory-bank 六份文件、AGENTS、此前进度与现有前端/API/测试/工作流，复用现有分支并保留全部此前改动。用户只授权本步，验收仍由用户执行，第 17 步未开始；没有提前实施第 18 步搜索。
- TalkPage.jsx 继续使用 readTalk、useApiRequest 和 RequestState。成功时挂载 TalkDetails，以懒初始化 state 固定一次当前时刻，展示 Upcoming/Past、标题、伦敦时间、非空主题/讲者/简介和 Related reading。重试/重入/刷新在下次成功挂载重取时刻，没有定时器；失败/加载时成功内容不渲染，不保留旧活动或误显示零资料。
- utils/talks.js 新增 getTalkStatus，详情与 groupTalks 共用 starts_at > now 为 Upcoming、其余为 Past 的 UTC 边界，继续复用既有 Intl London/GMT/BST 格式化。首页原分组、排序、新数组及其快照行为不变；不使用本地显示字符串判断状态。
- ResourceCard.jsx 只渲染一条已经读取的扁平活动关联。article/h3 与 React key 使用 association_id，不以共享 resource_id 代替活动语境；TalkDetails 直接 map resources，不按标题、书目 ID 或年份重排。类型映射为两条规定英文文案，作者空字符串为 Author not provided，year null 为 Year not provided，年份 1 正常显示。
- 非空 recommendation 展示 Why this reading? 和原文字，空值连标题区域一起省略；简介/主题/讲者为空同样省略。React 按纯文本渲染，CSS pre-wrap 保留简介/推荐理由换行，不生成结论或解释为 HTML。原文入口使用 original_url、target=_blank、rel=noopener noreferrer；可访问名称包含标题和 opens in a new tab，沿用 44 px 操作和清晰焦点。
- 零资料仍显示活动元数据、适用示例声明、Related reading、0 reading resources 与 Reading resources will be added here soon.；没有资源卡片或原文操作，不增加搜索框。is_example 决定 Example event 与 Reading selections are illustrative; these talks are fictional.，普通活动不添加两者；App 原独立项目页脚保留，无 Admin 入口或账号。
- client.js 将已有活动卡片所需检查抽为共用 hasTalkFields，并拒绝空白标题；详情另检查 description 字符串及用于渲染的资料身份、标题、作者字符串、nullable 合法年份、两类类型、理由字符串与绝对 HTTP(S) 原文地址。无效输入进入原 error/Retry，不创建占位原文或可点击的 javascript/data/ftp 地址。该防御层不替代后端模型/契约，不改 DOI、来源、顺序或元数据；取消、HTTP 分类及旧结果保护保持原路径。
- index.css 复用白卡片/间距基础并区分两个网格：只有 talk-grid 在 768 px 以上成为双列，resource-list 始终单列。追加详情标识、作者/年份/类型、推荐区及正文换行样式，长文字允许换行。当前 JSX、键盘、新标签和响应式表现仍待真实浏览器验收，不能从 CSS 声明推断已通过。
- api-client.test.js 当前定义 20 个测试：扩展旧空值/顺序测试为三条不同资源 ID、负值及同值关联、两种类型与多行理由；新增坏详情字段和非 HTTP(S) 链接进入安全错误、data 为 null 的场景。talks.test.js 当前定义十个测试：新增未来 1 毫秒、恰好开始、此前 1 毫秒下首页与详情边界一致。合计 30 项由现有 npm test/CI 自动发现，无新依赖、脚本或工作流变化；这些是测试定义，不是执行结果，也不覆盖 React DOM。
- frontend/README.md 提供完整用户验收清单和重启已有服务的路径：lint/30 项测试/build、真实详情与接口顺序、新标签/访问提示、375/768/1280 px 单列与键盘、空值/零资料/普通活动和加载/失败/快速导航回归。可选夹具仅覆盖当前标签页某个真实活动的详情 GET，并保留实际书目和原文；刷新清除，不写业务数据，不冒充真实存储或生产证据。
- 同步本文件、AGENTS 与前后端 README 的实际实现/待验证状态；两份设计、技术栈和实施计划未修改。progress.md 保留最后已验收步骤 15，本轮不填写完成/通过；收到用户确认后先请求打开并更新 progress，再追加本文件的验收来源和新洞察。
- **验证状态：第 16 步仅写入实现，待用户验证。** 助手没有运行 lint、30 项测试、构建、浏览器、后端回归、服务器、迁移或导入；没有访问或修改数据库、安装依赖、改锁文件、提交/推送或部署。后端 116 个测试方法与 schema 均不变。第 15 步的 28 项及 19 组历史成功不证明本版本通过，第 01–08 步远程 CI 不覆盖第 09–16 步；第 17 步保持未开始。

### 本步结构洞察

- **成功内容和请求状态按层分工。** TalkPage 决定成功/状态分支，TalkDetails 负责一次当前时刻和活动阅读组合，ResourceCard 只负责书目展示；client/Hook 继续负责传输、取消和重试，不让卡片重复请求或直接访问 Crossref。
- **原文地址先校验，再作为链接渲染。** client 拒绝不能用于安全阅读的字段，ResourceCard 保留已校验的原文并说明新标签；字段失败走普通请求错误，不以缺失可选内容占位掩盖契约错误。作者/year 占位属于展示，不修改接口空字符串/null。
- **关联身份和顺序来自 API。** React 使用 association_id 作为 key，直接遍历收到的数组，保留同值排序、共享书目与各活动不同理由。前端既不重新排序，也不写入或修复关联。
- **验证范围必须随新版本更新。** 30 项是待执行测试定义，历史 28 项仅属于第 15 步。Node 测试不能代替 JSX、原文新标签和零资料 DOM 验收；文档保存用户可复现步骤，progress 在用户确认后才记录通过。

## 39. 第 16 步验收后的文件职责与洞察

2026-10-04，用户收到第 16 步实现报告及完整验证指引后回复“通过”，据此确认本地验收。范围包括 lint、30 项前端测试、构建和 README 规定的详情阅读/空值/原文/导航/状态检查；没有逐项日志、截图或测量结果，不编造助手独立执行证据。已先请求打开 progress.md（queued）并更新进度，再补充本文件，随后同步指南；确认交接只修改文档。第 17 步未开始，第 09–16 步远程 CI 仍未验证。

- **页面组合和资源展示分别维护。** TalkPage.jsx 复用 client/Hook/RequestState 处理请求，成功子组件组织活动元数据、时间快照、示例说明及 Related reading；ResourceCard.jsx 仅展示一条扁平关联的类型、书目、当前理由和原文入口。后续搜索应在当前活动已加载数组上筛选，不增加卡片请求或直接调用 Crossref。
- **时间规则共用，快照属于页面。** utils/talks.js 的 getTalkStatus 让首页分组与详情标签采用同一 UTC 边界，formatTalkTime 始终显示 London/GMT/BST；两页各自成功挂载取一次快照。活动恰好开始时归入 Past，离开/刷新/重试后重新判断，停留不实时更新；第 32 步仍需完整时间/导航复核。
- **展示身份和排序来自关联。** TalkDetails 按 API resources 数组渲染，以 association_id 为 key；ResourceCard 使用同一身份关联标题。共享 resource_id 定位书目，不能代替当前活动理由或服务端确定顺序。index.css 让资源列表始终单列，首页双列断点保持独立。
- **接口空值、渲染占位和错误不混用。** client.js 拒绝坏日期、非法字段及非 HTTP(S) 原文地址，但不改写书目、DOI、来源或空值。ResourceCard 将作者空字符串/year null 映射为指定文案，空推荐连标题一起省略；TalkPage 省略其他空可选信息。零资料仍是成功活动，传输失败仍是错误，404 仍是未找到。
- **新标签提示与纯文本表达属于展示职责。** ResourceCard 提供原文 URL、noopener/noreferrer、标题和新标签可访问提示；CSS 保留正文换行，React 转义文字。产品只链接原文，不托管全文、推断研究结论或保证出版方免费访问。
- **测试、指引、确认和发布分别留证。** api-client.test.js 20 项与 talks.test.js 十项提供可复现的请求/时间验证；frontend/README.md 保存浏览器清单和仅标签页夹具；progress.md 记录用户确认，本文件解释职责。用户总体确认不证明实际采用了哪种夹具、产生哪些日志或完成线上验收，不能编造独立 DOM/性能结果。
- **本次确认没有推进后续步骤。** 后端 116 个方法不变且未重跑，没有代码、依赖、数据库、提交/推送或部署操作。完整对比度、最小生产入口、免费服务连接与上线仍按后续编号执行；只有新的明确指令才开始第 17 步。

## 40. 第 17 步实施交接：首个里程碑与部署可行性（待用户验证）

本节保留首次实施交接时未执行验收的事实；之后用户授权测试，实际通过来源见第 41 节。

2026-10-04，用户明确要求阅读全部 memory-bank 并继续第 17 步，验证前不得开始第 18 步。已完整阅读六份文档、AGENTS、进度与相关实现，保留所有先前工作。此次只写入实现和验收指引，progress.md 仍保留最后已验收步骤 16；确认后先请求打开并更新进度，再记录本步验收来源及新洞察。

### 已写入的文件分工

- **前端构建和 Django 入口共用一个生成文件。** vite.config.js 用命令模式区分开发 base / 与构建 /static/frontend/；frontend/index.html 仍是唯一源入口。settings.py 将 frontend/dist 注册为模板目录，public_pages.py 只为已定义 Home/数字详情 GET/HEAD 渲染 dist/index.html，入口 no-store。没有复制另一份入口或动态猜哈希文件名，也没有在模板中加入开发服务器地址。
- **模板与静态资产独立提供。** dist/assets 通过 frontend/assets 命名空间收集到 backend/staticfiles，Admin 资产由原生 finder 一起收集。WhiteNoise 紧跟 SecurityMiddleware，使用已锁定 6.12.0 的压缩存储，保留 Vite 已生成的文件名；不二次哈希，不新增 Brotli、CDN、CORS 或业务 Node 服务。当前项目没有 public 目录资产，将来增加时须显式接入。
- **路由与数据状态保持原边界。** config/urls.py 的 API 端点及 JSON 回退、Admin、healthz 保持各自处理；仅新增 / 与 /events/{整数}，未知服务器页面保持 Django 404，Admin 未授权路径保持登录重定向，没有宽泛 React 回退。详情入口本身不查 Event：缺失 ID 的 HTML shell 为 200，API 为 JSON 404，React 再显示未找到；不将客户端文案误作服务端页面 HTTP 404。缺少生成模板时安全 503，不暴露异常或文件路径。
- **构建与启动生命周期分开。** scripts/deploy.py 为标准库入口，main 要求明确 production 与 Python 3.13.16。build 核对 Node 24.14.0/npm 11.9.0，锁定 pip/npm 安装、构建、引用资产检查、Django 配置检查和 collectstatic；不迁移。start 限 Linux，校验 PORT、生成/已收集前端及 Admin 资产，配置检查和迁移成功后 exec 单 worker Gunicorn WSGI；任一前置失败不启动应用。此入口从不 seed_demo/创建管理员，私有初始化仍是独立受控生产连接操作。
- **实际构建进入后端 CI 验证。** backend.yml 的前端 job 构建并上传短期 dist 产物；backend job 等其成功，下载同次产物后保留 PostgreSQL 17.11、系统/迁移/隔离测试，增加静态收集。没有用固定旧 bundle、缺失时跳过或临时 JS 夹具代替实际构建；工作流尚未推送，旧成功仅属于第 01–08 步。
- **测试分层并保留执行边界。** test_public_pages.py 的六个 SimpleTestCase 方法检查入口、GET/HEAD/405、未知 API JSON、未知页面/Admin、缺失模板及夹具静态；同文件一个 TestCase 用隔离账号真实 Admin 新增手动 Resource/关联，验证匿名 API 下一次读取得到理由/顺序/计数。test_production_build.py 两个方法读取当前 dist，在临时目录实际收集并验证 DEBUG=False 页面和真实 JS/CSS/Admin 文件正文与类型；测试前必须先构建。test_deployment.py 十个方法 mock 所有子进程/exec，检查失败停止、顺序、固定版本、端口/产物及安全错误。新增 19 个后端方法、累计 135，前端仍 30；方法定义不等于运行结果，真实浏览器仍须另验收。
- **文档保存可复现路径和外部条件。** backend/README.md 的 Step 17 给出前端 lint/30 项测试/build、pip/Django/迁移遗漏/135 项回归，然后用现有 development 数据库、DEBUG=False、独立 8001 端口及 --nostatic/--noreload 验证不依赖 Vite。提供既有 Admin 添加临时示例活动/已有阅读关联→匿名刷新→可选确认删除活动的路径，不创建多余共享书目。backend/DEPLOYMENT.md 保存免费平台核对、实际配置表和未知远程状态，frontend README 与 AGENTS 同步当前实现及测试前构建要求。

### 平台核对与阻塞

已只读核对 [Render Python](https://render.com/docs/python-version)、[Node](https://render.com/docs/node-version)、[原生运行时](https://render.com/docs/native-runtimes)、[Postgres 创建/连接](https://render.com/docs/postgresql-creating-connecting)、[发布阶段](https://render.com/docs/deploys#pre-deploy-command)、[免费方案](https://render.com/docs/free)，并核对 [WhiteNoise 6.12 配置](https://whitenoise.readthedocs.io/en/stable/django.html) 与 [Vite base](https://vite.dev/guide/build.html#public-base-path)。官方说明支持显式 Python/Node 与 PostgreSQL 17；免费服务不依赖付费发布前命令、后台 Shell 或一次性任务。平台默认版本不代替本仓库准确 pin；Python 服务实际 Node/npm 工具可用性、安装和远程运行须由第一次受控构建确认。

免费限制记录在部署文档：Web 15 分钟空闲休眠/冷启动，每工作区免费小时和构建/流量预算；同工作区一个免费数据库、1 GB、创建后 30 天到期、无托管备份。真实创建/到期日期、账户额度、区域、URL、发布 SHA 和备份恢复均未知，不填写推算的“已部署”记录；额度支出仍须按零付费约束检查。

**当前远程部署为外部阻塞，未验证。** 本会话工具列表无可调用 Render 账号连接，用户没有提供已有授权免费服务/数据库标识或生产配置；未检查其个人账户登录态，也不推断本人没有账号。第 09–17 步尚未提交/推送，当前版本 CI 也是发布前置。没有实际部署尝试请求、购买资源、开通服务或初始化生产；文件中的构建/启动命令只是待受控执行的配置，不代表已经发布。没有自动审批拒绝。

### 实际验证状态与后续交接

本轮只读源码、规范、Git 状态和官方说明，并编辑实现/测试/指引；没有运行 lint、30 项前端测试、build、pip check、Django check、迁移、135 项后端测试、collectstatic、服务器、浏览器或数据库操作。不安装依赖、不改锁文件或模型/schema，不创建账号/导入数据、不暂存/提交/推送。135/30 为静态定义数量，历史第 15 步和旧 CI 不能替代本版本验收。用户将负责验证；本步本地尚未通过，远程明确阻塞，两者分开记录。

新增的架构洞察是：生成入口作为模板可避免复制与哈希同步；WhiteNoise 提供资产而不承担 SPA 回退；前端真实产物应先于后端集成测试；迁移的失败状态必须阻断进程替换；本地 DEBUG=False 的开发库验收不能证明生产 TLS/账号/线上数据。第 35–38 步将在同一集成上补齐正式上线与日志/安全验收，不另建部署路径。第 18 步搜索未开始，在用户验证之前不推进。

## 41. 第 17 步授权实测后的文件职责与洞察

2026-10-04，用户要求“你帮我测试”。当前 lint、30 项 Node 测试、Vite 构建、依赖/系统/迁移遗漏检查、135 项 Django 回归及 collectstatic 均通过；隔离浏览器 15 组公开/静态检查和 5 组 Admin 发布流程通过，应用异常为零。已先请求打开并记录 progress.md，再更新本文件。第 17 步仍待用户确认；远程 CI/部署未验证，第 18 步未开始。

- **构建源、模板和资产各有职责。** vite.config.js 决定生成引用前缀；dist/index.html 是 settings.py 配置的模板；public_pages.py 只提供已定义页面的无缓存入口；WhiteNoise 提供实际收集的哈希 JS/CSS 与原生 Admin 资产。DEBUG=False/--nostatic 实测不依赖 Vite，入口刷新和静态加载均成功。不能把页面入口 200 当作活动存在：API 404 驱动 React 未找到状态，未知服务器路径仍 404。
- **真实产物测试与启动顺序测试证明不同事项。** test_production_build.py 实际收集当前构建并检查正文/类型；test_public_pages.py 检查路由和 Admin→匿名数据可见性；test_deployment.py 使用 mock 验证 build/start 顺序和失败阻断。CI 下载同次前端产物的配置仍待上传运行，Windows 本地通过不证明 Linux Gunicorn 或生产数据库迁移启动成功。
- **数据库事务之外还需浏览器发布证据。** 临时 admin_live_test.py 使用 Django LiveServerTestCase、专用 test_psychtalk_step17_browser 与测试账号；admin-verify.mjs 通过真实 Admin 表单登录、验证 CSRF 403，再保存关联并清除会话进行匿名读取/刷新。额外 ORM 断言关联唯一和理由/顺序，测试结束销毁数据库；不借用个人 Admin 凭据或更改开发内容。
- **验收工具不增加产品架构。** 忽略的 .tools/step17-browser/cdp.mjs 负责专用 Edge 的协议连接；verify.mjs 检查真实公开页面/静态/导航/布局/失败；admin-verify.mjs 检查临时库中的发布流程；results.json、admin-results.json 和 PNG 保存实测证据。它们没有进入应用、依赖或 CI，永久测试仍由 backend/events/tests 与 frontend/tests 负责。检查器曾遇到跳转时 body 暂空，修正等待后通过，并确保真正导航结束再判刷新成功，没有修改产品实现。
- **运行环境的准备和清理须对称。** 开始时独立 PostgreSQL 17 停止，连接失败不是应用回归；只启动既有项目实例。结束关闭专用 8001 服务器、隔离浏览器和项目数据库，恢复先前停止状态，未触碰旧 PostgreSQL 11、用户日常浏览器及原有服务。生成 dist/staticfiles 保留为忽略的产物，两个测试库已销毁。
- **状态文档区分证据与接受。** progress.md 保存执行结果和待确认状态，本文件解释职责；AGENTS、两份 README 与 DEPLOYMENT.md 同步当前通过来源和远程边界。此次授权不是“通过”的替代，也不是下一步、提交或部署授权；第 18 步搜索保持未开始。

## 42. 第 17 步远程 CI 后的文件职责与洞察

2026-10-05（Europe/London），用户明确授权执行提交、推送和 GitHub CI 验证。a174723 的 [Project checks 37242589180](https://github.com/1uxury/psych-talk-hub/actions/runs/37242589180) 及 frontend/backend 两个任务均 success，无需修复。已先记录 progress.md，再同步本文件和指南。第 17 步仍待用户确认，第 18 步未开始。

- **工作流验证产物交接，而非只验证两个独立源码目录。** backend.yml 的 frontend job 在固定 Node/npm 下安装、lint、测试、构建并上传 dist；backend job 等其成功、下载同次产物，再在 Ubuntu/PostgreSQL 17.11 执行检查、迁移、收集与测试。真实产物测试不会依赖本地忽略目录，当前交接链已在线通过。
- **平台通过和生产运行仍有边界。** CI 成功证明锁定 Linux 依赖安装及测试流程正常；test_deployment.py 的 mock 仍只验证启动顺序和失败阻断，不能证明 Gunicorn 真实绑定端口、Render 运行时、生产 TLS 或线上数据初始化。DEPLOYMENT.md 继续记录独立远程阻塞。
- **提交号、任务号和接受状态各自保存。** progress.md 记录实现 SHA、任务 URL、结果与授权来源；本文件解释结构影响；README/AGENTS 指向当前通过证据。文档交接使用后续独立提交，引用已验证实现 SHA，不假定新文档提交自动通过，也不将 CI 成功写成用户确认或默认分支合并。
- **忽略目录是证据缓存，不是交付来源。** .tools/step17-browser/github-ci-a174723.json 保存公开 API 的任务/步骤状态，未进入 Git。提交前检查 52 个文件的路径和潜在凭据，没有包含私有 .env、数据库、node_modules、dist/staticfiles 或测试浏览器 profile；无应用代码修复、生产数据或资源操作。

## 43. 第 17 步真实免费部署后的文件职责与洞察

2026-10-05（Europe/London），用户另行授权部署并回复“允许”创建两项 Free 资源。Frankfurt 的单实例 Python Web Service 与 PostgreSQL 17 已建立；首次成功部署 dep-db1ed66gekts73dehfsg 使用已通过 CI 的 d8bdd29，实际 Live、迁移成功后 Gunicorn 启动、11 组 HTTP 与 6 组浏览器检查均有证据。最终命令的重部署 dep-db1egmdg1s2s739qisag 于 UTC 2026-10-05T00:04:05.947081Z（伦敦 01:04:05 BST）Live，No migrations to apply 后实际启动 Gunicorn/worker，两组线上检查再次全部通过。已先记录 progress.md；生产示例资料及私有账号未初始化，第 17 步待用户确认，第 18 步未开始。

- **平台命令和子进程寻址需要一致。** Render shell 可调用指定 Node/npm，但 Python 子进程原先使用 /usr/bin 默认版本。部署构建命令把实际 Node 目录及 npm 前缀的 bin 显式加入进程 PATH，之后仍由 scripts/deploy.py 精确核验。该修复属于服务配置；不放宽版本、不修改本机全局安装或应用代码。首次构建包含 Python 源码编译，不能将其探测输出误判为应用错误。
- **build、start、readiness 的实际证据分别交接。** deploy.py build 已安装锁、构建及收集真实资产；start 在生产执行 events 三项与 Django 基础迁移后 exec Gunicorn 26.2.0 并启动 worker；health.py SELECT 1 的线上 JSON 200 证明应用能读生产库。CI 的测试数据库没有连接这项生产资源，生产测试保护层未绕过。
- **入口、内容和协商状态分别验证。** public_pages.py 对 /events/1 返回构建入口 200，生产尚无活动时 API 按 application/json 返回 404，React 显示未找到。DRF 对有效端点不支持的 text/html 返回 JSON 406；未知 API 回退即使 Accept HTML 仍为 JSON 404。检查器应按实际请求契约区分这些状态，不为测试改变应用行为。Gunicorn 对 HEAD 丢弃正文，线上 HEAD 实际零正文。
- **上线配置不包含数据初始化。** Django 迁移只建立结构；seed_demo、私有管理员须另行通过受控 TLS 数据库连接执行。当前 [] 和匿名空首页是真实生产状态，有内容详情、登录后发布/CSRF、非空内容重部署保留及备份恢复仍待验收。没有新增初始化 HTTP 入口、自动 seed 或付费 Shell。
- **服务状态、版本与数据库生命周期分别保存。** DEPLOYMENT.md 记录准确构建命令、真实公开 URL、资源 ID、同区 Free/auto-deploy off、release/deploy/CI，以及数据库实际 2026-11-03 23:33:20 GMT 到期时间。progress.md 记录授权、失败排查和测试来源；本文件解释职责。指南引用实际发布，不把旧阻塞或历史未提交状态当成当前事实，也不把首次 Live 当作完整 MVP。
- **私有配置与验证缓存都不属于仓库源码。** 忽略的 .tools/render.env 提供用户私存 API key；render-database.private.json 保存连接信息；render-production-env.private.json 保存随机生产配置；仅按需读取，不输出凭据。render-state.json 和 render-deployment-plan.json 跟踪资源/部署及零付费约束。render-resources-public.json、render-deployment-evidence.json 保存公开元数据与脱敏日志。
- **临时检查器保留可追溯作用。** .tools/render-http-check.mjs 验证实际健康、资产、Cookie、API/方法/错误；render-http-results.json 只保存安全结果和资产路径。render-browser/cdp.mjs、check.mjs 仅连接本次专用 9238 隐藏 Edge，results.json 和 PNG 保存真实桌面/手机/Admin 证据。检查未使用个人会话、登录管理员或写业务记录，不新增依赖或正式框架；核对 profile/PID 后已关闭本次浏览器，9238 无监听。六份交接文档的本地改动未另行提交/推送；部署 SHA 仍为 CI 验证的 d8bdd29。

## 44. 第 17 步生产初始化后的文件职责与洞察

2026-10-05，用户授权初始化并明确允许查询公网 IP。生产新增两场虚构讲座、六条真实资料、六个阅读关联及私有管理员；TLS/数据库身份/迁移状态、重复导入、真实 Admin 保存与匿名刷新已验证。已先记录 progress.md，再更新本文件；第 17 步仍待用户确认，第 18 步未开始。

- **结构发布与内容初始化各有入口。** scripts/deploy.py 仍只构建、收集、迁移和启动；events/demo_seed.py 仍负责显式事务及稳定标识补缺。忽略的 .tools/production-initialize.py 仅是本次本地操作工具，读取私有外部连接，在独立子进程核对 psych_talk_prod/PostgreSQL 17.11/TLS/零待迁移，然后把 seed 与管理员创建置于事务中。没有应用内初始化路由、启动 seed 或账号默认密码；既有模型/约束均未修改。
- **外部运维连接与线上内部连接分离。** 操作前记录外部规则 []，临时添加当前公网 IPv4 /32，结束恢复并再次读取确认 []。Web 的内部连接保持正常。本次访问恢复结果在 production-db-access-results.json；原始规则仅在 render-db-access-original.private.json。自动审批曾拒绝未经授权的第三方 IP 查询，直到用户明确允许才执行，不绕过拒绝、不把公网 IP 或凭据写入公开文档。
- **幂等导入和用户会话验证证明不同事项。** production-initialization-results.json 保存 2/6/6 新增、再次导入 0/0/0、三模型字段快照相同及实际日期；这不证明部署后的数据保留。production-admin-check.py 通过真实 HTTPS 表单/CSRF 登录与保存，再用独立匿名请求确认发布，且用原关联基线恢复临时推荐理由并退出会话。测试运行器的生产保护保持原样，没有调用生产测试套件。
- **临时编辑必须有可核对的恢复基线。** production-association-baseline.private.json 保存关联 ID、资源 ID、活动 ID、理由与排序；检查器仅在当前值匹配原值或本次临时值时保存，避免覆盖他人修改。publish/restore-results.json 保存脱敏结果；恢复后独立匿名浏览器核对原值、身份及顺序，临时文案已清除。管理员身份与随机密码只保存于 production-admin.private.json，退出检查会话不删除持久管理员账号。
- **公开浏览器证据不能替代出版商访问承诺。** render-browser/initialized-check.mjs 验证两场非空页面、三条排序资料、原文属性/新标签页、1280/375 px、后台保存可见性及真实生产请求；restored-check.mjs 验证恢复后的公开页面。对应结果和 PNG 都在忽略目录，应用异常为零，专用浏览器已关闭。production-original-link-results.json 记录 DOI 解析到预期出版商，Nature/PLOS/WHO 为 200，Physiology/SAGE/NIH 的自动读取为 403；没有绕过限制或保证全文开放。首次检查器引号/用户手势及请求超时的修正仅涉及临时工具。
- **日期、验收与交付状态独立交接。** 首次导入时刻决定 +30/-7 天，当前未来示例为 11 月 4 日，数据库仍在 11 月 3 日到期，不能因演示日期改变生命周期。progress.md 记录授权、实测、限制和待办；DEPLOYMENT.md 记录公开地址、初始化状态及运营期限；AGENTS/README 指向当前证据。非空重部署保留、备份恢复及完整 MVP 验收仍待执行，文档交接未提交/推送，发布 SHA 仍为 d8bdd29。
- **会话安全属性需要实际响应证据。** 另行真实登录核对 sessionid 的 Secure、HttpOnly、SameSite=Lax，立即退出，production-session-results.json 仅保留布尔结果。数据库初始化成功或登录页 CSRF Cookie 正常不能替代已认证会话 Cookie 的核验；不在文档或证据中保存 Cookie 值。

## 45. 第 17 步用户确认与 Git 交接

2026-10-05，用户回复“通过 推送git”。第 17 步现已用户确认；先记录 progress.md，再同步本文件及指南。第 18 步未开始，后续实施需新的明确指令。

- progress.md 保存确认来源、既有验证依据、此次仅文档提交范围与待办；本文件解释实际部署/初始化与文件职责，保留此前未确认的历史记录。AGENTS 和两份 README 的当前状态指向第 17 步已接受，DEPLOYMENT.md 指向实际非空生产状态及固定部署配置。
- Git 文档提交不修改已发布应用或数据库；Render auto-deploy 保持关闭，生产仍运行 d8bdd29。本次常规推送沿用既有功能分支，不等同默认分支合并、PR 或部署。私有初始化工具/凭据及运行证据缓存保持 .tools 忽略规则，不成为公共交付源码。
- 用户确认不代替尚未执行的非空重部署保留、备份恢复及完整 MVP 后续验收；当前结构及功能没有新增变更，因此只验证文档格式/链接、待提交范围与凭据排除，不重复应用套件。

## 46. 第 18 步：当前活动标题搜索的职责与验证边界

2026-10-05，用户明确授权仅实施第 18 步。写代码前完整读完全部 memory-bank；已先记录 progress.md，再更新本文件。第 18 步已实现且助手检查通过，等待用户验收；第 19 步保持未开始。

- TalkDetails 在成功挂载内持有 query 与搜索 input ref；从当前 talk.resources 派生过滤结果，query.trim().toLowerCase() 与标题小写做字面子串匹配。不匹配作者/理由/其他活动，不重排或修改数组，不引入额外 API/Crossref/缓存/依赖。
- 页面身份仍由 App 的 keyed TalkPage 隔离，请求状态仍由原 client/Hook 负责。活动切换、完整刷新或重试后的新成功挂载重置查询；输入期间既有 now 快照不变。每张过滤卡片仍以 association_id 标识，ResourceCard 的书目/推荐/原文安全行为保持既有职责。
- 非空资源显示 Search resources/Search by title，数量在 reading-count 的 status 中通告（未筛选为总数，筛选为匹配数 of 总数）。无匹配提供规定文案/Clear search，恢复顺序与数量并回焦点；真正零资料仍是原成功空状态，无搜索框。index.css 沿用颜色、字体和焦点，新增至少 44 px、可缩至移动宽度的输入。
- npm lint、现有 30 项请求/时间测试、build 实际通过；Node 测试没有新增搜索/React DOM 覆盖。当前构建另经独立隐藏 Edge 11 组实际 DOM/输入/导航检查，验证大小写/空白/标题范围/顺序/清空/活动隔离/零资料/无额外请求及 1280/768/375 px；无未捕获 JS 异常，截图已查看。
- 本次浏览器使用临时只读 API 夹具（来自本地演示清单）和当前 dist，不连接数据库，不能替代真实开发数据或线上验收。忽略的 .tools/step18-browser 仅保存检查器/结果/截图/profile，不增加产品架构、正式测试框架或长期服务；8002/9239 及本次进程已关闭。初始化/沙箱与检查器的排查来源见 progress.md。
- 后端、模型/schema、迁移、依赖锁、设计/API 规范不变，未重跑后端回归。生产仍运行 d8bdd29，当前搜索尚未提交/推送/部署；历史 CI/线上检查不覆盖本步。frontend/README.md 保存用户真实本地验收清单，用户确认才决定步骤接受。

## 47. 第 18 步用户验收后的文件职责与交接

2026-10-05，用户收到完整验收说明后回复“通过”，确认第 18 步本地验收；未附逐项输出或截图，不编造夹具使用、测量或命令日志。已先更新 progress.md，再同步本文件和指南。本次仅文档交接，没有重跑测试或修改代码/数据库；第 19 步未开始，需新的明确指令。

- 搜索属于 TalkDetails 的成功内容状态，从当前 resources 派生结果；client/Hook 继续负责请求、取消与重试，App 的活动 key 隔离查询生命周期。现有 ResourceCard 只负责展示，保留关联身份/顺序、当前理由和原文安全属性。
- index.css 负责搜索输入的尺寸、收缩与焦点；frontend/README.md 保存可复现验收方法；progress.md 区分助手临时数据检查和用户接受。本次确认不将 Node 请求/时间测试写成新增搜索 DOM 单元覆盖，也不将浏览器夹具写成真实数据库证据。
- 生产 d8bdd29、既有 CI 与本地第 18 步接受是独立状态。搜索未提交/推送/部署，后端 135 项未在本步重跑；非空重部署保留、备份恢复和后续 MVP 验收仍待办。第 19 步只在新指令后建立 DOI 规范化，不因本次“通过”自动推进。

## 48. 第 19 步：DOI 规范化与固定目标请求的职责和验证

2026-10-05，按用户新指令完整阅读六份 memory-bank 后只实施第 19 步。已先记录 progress.md，最后用户确认步骤仍是 18，第 19 步助手检查通过、待用户验收；第 20 步未开始。

- **输入身份与持久化分开。** doi.py 提供 normalize_doi，纯 DOI 去两端空白/转小写且不解码；HTTPS doi.org 的 path 去首个斜杠并严格 UTF-8 解码一次，再验证 10.、4–9 位 ASCII 注册者和非空无空白后缀。保留标点与未再次解码的百分号。既有 Resource 继续只保存纯 DOI，不改模型、schema、迁移或演示导入，也不自动让 Admin 输入链接。
- **解析器不等于校验器。** 在 urlsplit 前拒绝链接内部空白/C0 控制字符，防止其自动删除字符；netloc 忽略域名大小写后必须精确 doi.org，这同时拒绝凭据、显式端口、子域/尾点/编码主机。原链接中的 ?/# 分隔符即使为空也拒绝；解码得到的后缀标点则保留为 DOI 文本。非法值统一为 ValidationError/code invalid_doi，不回显异常详情。依据：[Python 3.13 URL parsing](https://docs.python.org/3.13/library/urllib.parse.html#url-parsing-security)。
- **输入不能改变外部目标。** crossref.py 的 request_doi 始终先调用规范化，再把整个 DOI quote(safe="") 拼接到固定 https://api.crossref.org/works/；不请求用户传入的 URL。allow_redirects=False 禁止全部自动重定向，满足一次获取最多一次外部请求，保持 TLS 校验与 (3, 7) 等待限制。依据：[Requests redirects](https://requests.readthedocs.io/en/latest/user/quickstart/#redirection-and-history)、[Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/)。
- **传输先建立，转换和流程仍待实现。** request_doi 返回原始 Response，调用方负责关闭；本步不解析 JSON、抽取书目、映射错误、查询已有 DOI、创建预览或保存关联。固定超时是新传输的必要边界，不表示第 20 步转换已实施。服务没有 Admin/公开路由入口，也不导入模型/事务；第 20–29 步逐步接入转换、幂等保存、会话、权限及真实集成。
- **测试验证真正的请求准备行为。** test_doi.py 有十个规范化和六个 HTTP 边界方法，SimpleTestCase 拒绝 ORM 使用；除 requests.get 参数测试外，mock 最底层 HTTPAdapter.send，让锁定 Requests 实际准备编码地址和处理 301/302/303/307/308，20 种 Location 组合全部仅一次传输。特殊标点不能进入 query/fragment 或另一个主机；无效输入在 HTTP 前被拒绝。404/429/5xx/连接异常只断言单次传输/原样返回或抛出，不实现第 21 步提示转换。
- **验收与回归证据分别保存。** 专项 16 项实际通过（0.057 秒，不初始化数据库）；当前前端重新构建后，Django check、迁移遗漏检查及 PG17 隔离库完整 151 项通过（12.161 秒），测试库销毁。此次前端源码不变，未重跑 lint/30 项/浏览器；生产/真实 Crossref/远程 CI未验证。初次沙箱状态查询失败，授权 pg_ctl 确认 PG17 原已运行，未启停或初始化，检查后保持运行，PG11 未操作。
- **交接保持可复现且不推进步骤。** backend/README.md 保存专项与全套验收命令；progress.md 保存实际输出与等待用户确认；AGENTS/前端 README 指向当前边界。没有依赖/锁、产品规范或发布改动，不提交/推送/部署，第 18 步未提交工作完整保留。用户验收之后先更新进度再记录确认，不自动开始第 20 步。

## 49. 第 19 步用户确认后的职责与交接

2026-10-05，用户收到验收命令与完整回归说明后回复“通过”，确认第 19 步本地验收；未提供逐项输出，不推断其实际执行命令或新增真实外部集成证据。已先更新 progress.md，再补充本文件并同步指南，第 48 节等待验收描述保留为首次实施时事实。

- doi.py 只负责 DOI 身份规范化与输入拒绝；crossref.py 只负责固定目标的一次 HTTP 请求，返回未转换响应。Resource 的纯 DOI 存储规则、Admin 表单、演示导入和公开 API 均保持既有职责，第 20 步转换尚未实施。
- test_doi.py 保存可复现的 16 项输入/传输验证；backend/README.md 保存专项和 151 项全套指引；progress.md 区分助手实测与用户接受。本次确认没有增加测试执行、数据库、线上或真实 Crossref 证据。
- 本次交接只修改文档，没有代码/schema/依赖、测试重跑、进程启停、提交/推送或部署。生产仍为 d8bdd29，第 18–19 步改动尚未发布；当前版本远程 CI、真实 DOI 集成及既有待办仍需独立验证。第 20 步必须等新的明确实施指令。

## 50. 第 20 步：成功书目转换的职责与验证边界

2026-10-05，收到新的第 20 步实施指令后完整阅读六份 memory-bank 和已有实现；保留所有先前工作。已先记录 progress.md，再更新本文件。最后用户确认仍为 19，第 20 步助手检查通过、待用户验收，第 21 步未开始。

- **传输、转换与持久化分别维护。** crossref.py 的 request_doi 仍返回 raw Response；fetch_metadata 用响应上下文检查 HTTP 200/status=ok/message-type=work/message 对象并解码，调用 crossref_metadata.py 的 convert_work，结束关闭响应。后者只构造不可变 CrossrefMetadata，无 HTTP/ORM/事务/会话。底层 HTTP/JSON/结构异常未映射为用户提示，错误转换留第 21 步；已有 DOI 数据库匹配、预览页面和保存仍留后续步骤。
- **输入身份与书目白名单固定。** 结果 DOI 来自请求输入的 normalize_doi，不能由上游 DOI 替换；仅 title/authors/year/original_url/doi/resource_type/metadata_source 七字段，来源固定 crossref。dataclasses.asdict 可得到后续会话/表单需要的普通值，但本步不保存会话或业务记录，不导入 abstract、summary、其他外部字段或生成结论。
- **优先级与空值属于纯转换规则。** 标题取首个非空字符串，去两端空白、不合并后续标题；作者保留来源顺序/重复署名，given/family 用空格组合，个人名缺失才用 name 组织名，非空条目以 `; ` 组合，无作者为 ""。年份只检查 published-print → published-online → issued 的首个 date-parts 起始年份，type 为 int 且 1–9999 才接受，排除 bool/string/float，无则 None；两种 paper 类型精确匹配，其余 article。
- **不完整结果不能等同可保存书目。** 仅采用返回的 URL 并按 Django HTTP(S) URLValidator、2048 字/控制字符规则校验；无效时为空，不使用 DOI resolver/link/resource 字段补造。missing_required_fields 指出缺失或超过 500 字的首选标题及空链接，needs_review 同时识别可选作者/年份缺失；前者要求管理员补充/修正，后者不能把可选字段变必填。真正模型/表单校验仍是保存边界，Admin 文案与页面留第 24 步。
- **测试覆盖转换与数据保留的不同层。** test_crossref_metadata.py 16 个 SimpleTestCase 方法拒绝数据库访问，验证多标题/署名/组织/部分姓名、年份冲突/回退/范围/类型、空值/链接安全/白名单/输入不变和真实 Requests 准备（仅 mock 最底层传输）；另两项 TestCase 使用编辑过的隔离记录，获取零查询、比较三模型全部字段，并验证实际 Resource.save 拒绝缺失/无效/超长必填字段。第 19 步重定向与固定目标回归保持通过。
- **当前证据与历史发布分别交接。** 32 项无数据库专项通过（0.140 秒），重新构建当前前端后 check/迁移遗漏检查通过，PG17 完整 169 项通过（12.113 秒），test_psychtalk 销毁。沙箱误报数据库停止，授权状态确认原已运行 PID 2220，没有启停/初始化；保持运行、PG11 未操作。没有真实 Crossref/生产访问、开发业务写入、依赖/schema/Admin/公开 API 变化或提交/推送/部署；没有前端 lint/30 项/浏览器重跑，当前远程 CI 未验证。
- **规范核对与产品变更分开。** 使用既有双语设计/技术栈规则，不修改产品规范；参考当前 [Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/)、[Requests JSON](https://requests.readthedocs.io/en/latest/user/quickstart/#json-response-content) 与 [timeouts](https://requests.readthedocs.io/en/latest/user/quickstart/#timeouts)，URL 校验另阅读本地锁定 Django 5.2.17 源码。Crossref 旧 GitHub 文档标注 deprecated，不作为当前接口变化的依据；Swagger 仅可读取页面，真实 DOI 集成留第 29 步。
- **验收入口与推进限制明确。** backend/README.md 提供当前 32 项专项和 169 项完整回归；progress.md 保存助手输出，用户确认后先更新进度再补充架构接受状态。服务尚无 Admin 获取入口，本步不能通过浏览器按钮验收。第 21 步保持未开始，等待用户验收和新的明确实施指令。

## 51. 第 20 步用户确认后的职责与交接

2026-10-06（Europe/London），用户收到具体验收命令和预期结果后回复“通过”，确认第 20 步本地验收。已先更新 progress.md，再同步本文件及指南；第 50 节等待验收描述保留为首次实施时的历史状态。用户未附逐项输出，不推断实际命令、数据库状态或新增外部集成证据。

- crossref.py 负责固定目标传输、成功响应解码及关闭；crossref_metadata.py 负责纯书目转换和补充/审阅标记。两者不保存 Resource/EventResource 或会话；模型继续守住真实保存校验，错误提示映射、已有资源匹配、Admin 预览/确认仍按后续编号实施。
- test_crossref_metadata.py 的 18 项验证分别覆盖转换/获取和 PostgreSQL 数据保留/拒绝无效保存，test_doi.py 保留输入/固定目标回归；backend/README.md 保存 32 项专项与 169 项全套复现方法，progress.md 区分助手实测与用户确认。本次确认不把模拟响应写成真实 DOI 集成，也不将本地验收写成远程 CI 或生产发布。
- 此次交接仅改文档，没有测试重跑、代码/schema/依赖改动、数据库访问、进程启停、提交/推送或部署。生产仍为 d8bdd29，第 18–20 步尚未发布；备份恢复及其他既有待办保持原状态。第 21 步未开始，需用户新的明确实施指令。

## 52. 第 21 步：安全错误与恢复选择的服务边界

2026-10-06，按新指令完整阅读六份 memory-bank 和既有服务后仅实施第 21 步。已先更新 progress.md，再补充本文件。第 21 步助手检查通过、待用户验收；最后用户确认仍为 20，第 22 步未开始。

- **原始传输与业务错误边界分别维护。** request_doi 不变，仍返回 raw Response，固定目标/TLS/(3, 7)/禁止重定向。fetch_metadata 对 404 → not_found、429 → rate_limited、5xx → upstream_error，其余非 200 或无效 JSON/单 work 结构 → invalid_response；Timeout → timeout，ConnectionError → connection_failed，其他 RequestException → provider_unavailable。ConnectTimeout 同时继承连接与超时，先判断超时；JSON ValueError/过深 RecursionError 只在解码边界转换，未预期编程故障不被一概吞掉。
- **公开提示与内部类别分开。** CrossrefLookupError 仅以设计的固定英文文案构造 Exception：404 为 No publication was found for this DOI.，其余为 We couldn't fetch publication details. Please try again or add the resource manually.。code 用于未来流程判断；不拼入 DOI、响应正文或连接异常详情。JSON/传输故障用 from None 抑制底层异常链，测试检查 str/repr/格式化异常文本中无模拟私密信息。本步不增加日志平台/故障日志，日志完善仍留第 36 步。
- **输入保留不是会话持久化。** input_value 保存传入的原始值，can_add_manually 为 true；can_retry 对临时失败为 true，对 404 为 false（先修正 DOI 或手动添加）。无效 DOI 保持既有 ValidationError 并在网络前拒绝。未来 Admin 应保留绑定输入并消费这些安全提示/恢复标记，本步尚无表单或操作按钮，不能称浏览器入口已验收。
- **失败、元数据不完整与保存继续分开。** 合法单 work 中缺书目仍是第 20 步 CrossrefMetadata 的补充/审阅结果；失败不伪装为空成功。一轮 fetch 最多一次传输，429 不等待 Retry-After、不自动重试；人工重新调用才有新请求，成功/失败 Response 均关闭。第 22 步短事务保存/已有 DOI 复用、第 24 步预览、第 25 步确认不请求 Crossref 尚未开始。
- **行为与数据库保留有独立验证。** test_crossref_errors.py 新增 12 个 SimpleTestCase 和 2 个 TestCase；前者用真实 Requests 请求准备与模拟最底层适配器，覆盖状态、JSON/结构、TLS/代理/连接/超时/解码、安全提示/精确输入/恢复标记、再次调用成功及编程错误；后者对新/已保存 DOI 逐失败断言零查询、三模型完整字段/数量不变，覆盖共享和未关联记录及已编辑/清空值。所有外部 HTTP 模拟，未创建确认流程或实际 Admin 浏览器入口。
- **实际证据与后续验收分别交接。** 专项 44 项 OK（0.194 秒），当前 Vite 构建成功，check/迁移遗漏检查通过，完整隔离 PG17 回归 183 项 OK（12.211 秒），test_psychtalk 销毁。首次重定向失败属于缺少 request/url 的测试夹具，修正后通过；Requests 预备未跟随重定向会先 close，再由服务上下文关闭，夹具按实际行为核对，而不是放宽单次请求。受限状态误报后授权只读确认 PG17 原已运行 PID 6588，结束保持同 PID，无启停/初始化，PG11 未操作。
- **来源、文件职责和发布范围保持明确。** 参考 [Requests errors](https://requests.readthedocs.io/en/latest/user/quickstart/#errors-and-exceptions)、[JSON](https://requests.readthedocs.io/en/latest/user/quickstart/#json-response-content) 和 [Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/)，另核对本地锁定 Requests 2.34.2 异常继承；没有真实 DOI 查询。backend/README.md 保存 44 项专项/183 项完整验收，progress.md 保存实际结果与待确认状态。无 schema/依赖/Admin/公开 API 变化、开发业务写入、生产访问或提交/推送/部署；前端源码不变，未重跑其 lint/Node/浏览器。用户验证前不开始第 22 步，验收之后也须新的明确指令。

### 第 21 步按用户要求重新验证

2026-10-06，用户要求“你直接帮我验证”。在当前实现上重跑 README 检查：44 项无数据库专项 OK（0.211 秒），当前前端构建成功（261 毫秒），Django/迁移遗漏检查通过，完整隔离 PostgreSQL 后端 183 项 OK（12.824 秒），测试库销毁。使用 verbosity 2；两项失败数据保留及既有成功/模型校验边界均包含于全套通过结果，无需应用修复。

前后只读状态确认项目 PG17 同为 PID 6588，保持原运行状态，无启停/初始化或 PG11 操作；全部 Crossref 模拟，无真实服务/生产访问、开发业务写入、代码/schema/依赖变化、提交/推送/部署。已先更新 progress.md，再记录本节与后端指南。本次执行授权不等于用户接受，最后确认仍为 20，第 21 步待确认，第 22 步未开始。

## 53. 第 21 步用户确认后的职责与交接

2026-10-06，用户收到助手重新验证结果后回复“通过”，确认第 21 步本地验收。已先更新 progress.md，再同步本文件和指南；第 52 节待验收描述保留为历史状态。用户未提供新的独立输出，本次确认不扩展至真实 DOI、Admin 导入页面、远程 CI 或生产发布。

- crossref.py 继续分开原始固定目标传输与安全获取错误；crossref_metadata.py 继续负责纯成功书目转换。输入/恢复标记不等于会话预览，服务无 ORM/保存；第 22 步原子保存与复用、第 24–25 步 Admin 预览/确认仍待新的对应指令。
- test_crossref_errors.py 的 14 项验证、既有 DOI/转换回归及完整 183 项检查提供当前本地证据；backend/README.md 保存复现操作，progress.md 区分助手实际执行和用户确认。模拟外部失败与隔离数据快照不当作真实 Crossref 或浏览器管理流程验收。
- 本次交接仅修改文档，没有测试重跑、代码/schema/依赖、数据库或进程操作、提交/推送/部署。生产仍为 d8bdd29，第 18–21 步尚未发布，既有待办不变。第 22 步未开始，需新的明确实施指令。

## 54. 第 22 步：原子保存、当前书目复用与后续流程的边界

2026-10-06，按新的明确指令完整阅读六份 memory-bank 和相关实现后仅实施第 22 步。已先记录 progress.md，再补充本文件。助手专项 14 项/完整 197 项及构建/检查通过，最后用户确认仍为 21，第 22 步待用户验收，第 23 步未开始。

- **查询与保存是独立服务。** crossref.py/crossref_metadata.py 继续只查询/转换；新增 resource_save.py 不导入或调用它们，不持有外部请求。save_doi_to_event 接收可信 event_id/doi、已审阅 bibliography 映射和关联字段；DOI 沿用 normalize_doi，短 atomic 内重新读取 Event、Resource 和 EventResource，再只创建缺失记录。返回 DoiSaveResult 的对象和 resource_created/association_created 标记，未来入口可区别新增和已存在。
- **当前数据库记录优先于预览。** DOI 命中后不采用 bibliography，不执行共享保存；标题、原文、作者空字符串、年份 None、类型、来源和稳定身份保持现值。已有关联返回当前原记录，忽略新理由/顺序，包括无效替换值；另一活动只新建自己的关联。预览后资源已被创建或编辑的模拟用例验证相同规则，不持久化或信任预览身份。
- **新书目有明确初始化白名单。** bibliography 只允许五个书目字段初始化 Resource；独立 DOI 固定身份，来源 crossref，seed_key 默认为 None，其他字段不导入。可消费 dataclasses.asdict 的转换结果，但实际保存仍走 Resource.save/EventResource.save 完整模型校验。映射不被修改，缺标题/非法 URL/年份/类型拒绝，缺作者/年份仍可保存。
- **事务支持后续状态的组合，尚无状态流程。** 关联失败退出 atomic 回滚新书目；实际 PG NOT NULL 故障测试确认退出后连接可继续查询/再调用，原故障不被吞掉。调用方外层 atomic 失败也可回滚服务内成功写入，这为第 25 步同事务结果持久化提供能力，不等于会话保存已实现。依据：[Django 5.2 transactions](https://docs.djangoproject.com/en/5.2/topics/db/transactions/#controlling-transactions-explicitly)。并发唯一冲突回滚/转换和独立连接协调属于第 23 步，本步没有捕获竞争冲突、加锁或并发测试。
- **数据库测试分别证明数据保留与失败回滚。** test_resource_save.py 的 14 个 TestCase 方法用隔离 PostgreSQL，比较三模型完整快照，覆盖新建/跨活动/重复调用/已编辑原记录、顺序模拟预览后变化、输入白名单/不变、可选默认、无效 DOI 零查询、校验与数据库失败/再调用、外层回滚、目标删除。每例禁止 Requests Session.request；没有 HTTP 确认视图或 Admin 浏览器操作，权限和服务器预览验证仍由第 24–28 步接入。
- **本轮实际环境变化有独立记录。** 文件工具异常留下空字节/缺文件，首次专项导入失败；只重写两个新增文件后核对正常文本。PG17 初次状态为已运行 PID 6588，之后连接超时且确认停止（原因未知）；只启动既有实例，不初始化或操作 PG11。专项 14 项 OK（0.783 秒），当前 Vite 构建成功（342 毫秒），check/迁移检查通过，完整 197 项 OK（13.510 秒），test_psychtalk 销毁。结束 PG17 PID 28764、5433 就绪并保持运行，恢复最初运行状态，不能宣称未启停或保留原 PID。
- **交接不扩展接受或发布。** backend/README.md 保存 14 项 PG 专项/197 项全套复现及服务契约，progress.md 保存实际结果与排查，AGENTS/前端指南指向当前边界。模型/schema、依赖、Admin、公开 API 与前端源码无变化；无开发业务写入、真实 Crossref/生产访问、提交/推送/部署。双语产品规则保持一致无需改动；第 22 步等待用户验收，第 23 步须用户确认后新的明确指令，当前生产仍 d8bdd29。
## 55. 第 22 步用户确认后的职责与交接

2026-10-06（Europe/London），用户收到具体验收操作及预期 14 项专项/197 项回归结果后回复“通过”，交接中断后再次明确回复“通过22”，确认第 22 步本地验收。已先更新 progress.md，再补充本文件及指南；第 54 节待验收描述保留为首次实施事实。用户未提供逐项输出，不推断实际执行命令、当前数据库状态或新增真实 Crossref/Admin/并发竞争证据。

- resource_save.py 负责短事务内 DOI 匹配/创建和关联保存，复用当前数据库书目，已有关联保留当前理由与顺序；crossref.py/crossref_metadata.py 仍只负责查询/转换，不在保存事务中发 HTTP。当前服务没有预览会话或 Admin 确认入口，第 24–25 步继续按计划接入权限、可信状态与结果记录。
- test_resource_save.py 的 14 项 PostgreSQL 验证及完整 197 项回归保存助手实际证据；backend/README.md 保存复现命令，progress.md 区分实施、助手检查和用户确认。顺序模拟预览后变更不等于独立连接并发验收；第 23 步唯一冲突恢复和真实竞争仍未开始。
- 本次确认交接只改文档，不重跑测试、不修改应用/schema/依赖，不访问数据库或操作进程，不提交/推送/部署。生产仍 d8bdd29，第 18–22 步尚未发布，既有待办不变。第 23 步未开始，必须等新的明确实施指令。

## 56. 第 23 步：并发唯一冲突、回滚恢复与独立连接验证

2026-10-06，按新的明确指令完整阅读六份 memory-bank 和既有代码后，仅实施并验证第 23 步。先记录 progress.md，再补充本文件。28 项保存专项/211 项完整回归、当前构建及检查通过；最后用户确认仍为 22，第 23 步待验收，第 24 步未开始。

- **数据库身份约束与恢复服务共同去重。** 原模型/schema 不变，Resource.doi 的 PG 唯一名称 events_resource_doi_key、关联 unique_event_resource 是最终边界。resource_save.py 只在相应新增模型保存阶段识别 SQLSTATE 23505 加精确表/约束；不吞其他唯一约束、检查、NOT NULL、连接故障或普通字段校验。full_clean 可能先看到赢家，因此也严格识别单独 DOI unique 或对应组合 unique_together 的模型/字段参数，不解析英文错误文本。
- **回滚必须先于恢复读取。** 整个尝试的 atomic 退出后才分类/查询已存在身份；还要确认赢家存在。每种身份只恢复一次、最多三次尝试，复读 Event/书目/关联而不返回失败尝试的对象。支持一个请求先后输掉 DOI、关联两轮竞争；重复同种冲突或无赢家仍抛原错误。书目和已有关联从当前数据库取，复用时不采用输家的标题、理由或排序。调用方事务失败仍回滚本请求写入。依据：[Django transactions](https://docs.djangoproject.com/en/5.2/topics/db/transactions/#controlling-transactions-explicitly)、[Psycopg diagnostics](https://www.psycopg.org/psycopg3/docs/api/errors.html)。沿用当前默认 READ COMMITTED，不增加更高隔离级别重试策略。
- **真实竞争与顺序回归分别留证。** 原 test_resource_save.py 的 14 项保持原职责；新 test_resource_save_concurrency.py 增加 7 个 TransactionTestCase 和 7 个边界方法。工作线程独立 Django 连接、不同 pg_backend_pid、同一 test_ 库；INSERT 前 Barrier 让两者都通过真实校验，再由 PG 裁定赢家，三组核心场景各三轮。另协调提交后 full_clean，验证模型唯一竞争；三个连接实际制造同一请求的两阶段冲突。唯一异常未模拟；OperationalError 边界为模拟，其他错误边界实际触发 PG 约束。依据：[Django TransactionTestCase](https://docs.djangoproject.com/en/5.2/topics/testing/tools/#transactiontestcase)。
- **解释结果和连接恢复也是验收内容。** DoiSaveResult 标记最终尝试的新增/复用，返回赢家资源与关联；同活动最终 1/1，跨活动 1/2，已存资源完整字段不变。恢复入口 SELECT 1 证明 atomic/savepoint 已回滚；每个请求返回后在同一工作连接读取，确认 needs_rollback=false、autocommit 恢复，再 finally 关闭连接。调用方结果失败回滚测试保留另一连接已提交赢家，未实现实际会话结果。
- **运行与发布证据继续独立。** 最终专项 28 项 OK（5.199 秒），Vite build 成功（255 毫秒），Django/迁移遗漏检查通过，完整 211 项 OK（15.777 秒），测试库销毁。PG17 初始确认停止，仅启动既有实例测试，结束 stop 后 pg_ctl/pg_isready 确认停止；PG11 未操作。没有开发业务写入/迁移、真实 Crossref/生产访问、依赖/schema/Admin/API/前端源码变化、提交/推送/部署，也未重跑前端 lint/Node/浏览器；旧 CI 不覆盖本步。
- **后续流程仍有明确边界。** 服务不处理权限、预览、会话或路由；Admin 调用方须在第 24–25 步接入可信状态/权限及结果保存。backend/README.md 保存 28/211 项验收指引，progress.md 区分助手检查与用户接受，AGENTS/前端指南指向当前边界。双语产品规则无需变更；第 24 步在用户验收后仍须新的明确实施指令，生产仍 d8bdd29。

## 57. 第 23 步用户确认后的职责与交接

2026-10-06（Europe/London），用户收到助手第 23 步实现与验证报告后回复“通过”，确认本地验收。已先更新 progress.md，再补充本文件及指南；第 56 节待验收说明保留为首次实施的历史事实。用户未提供新的独立输出，不推断实际命令或当前数据库状态，也不扩大至真实 Crossref、Admin/会话、远程 CI 或生产验收。

- resource_save.py 在短 atomic 尝试退出后仅识别并恢复验证过的 DOI/关联唯一冲突，检查赢家存在、重新读取当前书目与关联，每种身份最多一次；其他错误继续传播。已有书目、理由/顺序和调用方事务组合保持第 22 步规则，查询服务仍不参与保存事务。
- test_resource_save.py 的 14 项顺序回归与 test_resource_save_concurrency.py 的 14 项真实竞争/错误边界分别维护，28 项专项和 211 项完整回归是助手已有执行证据；progress.md 保存用户接受来源，backend/README.md 保存复现操作。独立连接验证不等于已实现 Admin 预览、可信会话、权限或确认结果持久化，这些仍在第 24–25 步接入。
- 本次确认交接只更新文档，不重跑测试、不改代码/schema/依赖，不访问数据库或操作进程，不提交/推送/部署。第 01–23 步已接受，第 24 步未开始，需新的明确实施指令；生产仍 d8bdd29，第 18–23 步尚未发布，既有待办不变。

## 58. 第 24 步：Admin 两步预览、数据库会话合并与确认边界

2026-10-06，仅按第 24 步新指令实施。写代码前完整阅读全部 memory-bank，先记录 progress.md；第 01–23 步已用户接受，第 24 步助手检查通过、待用户验收，第 25 步未开始。已有模型/schema、公开 API、React 两页与依赖未变，生产仍 d8bdd29。

| 文件 | 当前职责 |
| --- | --- |
| backend/events/admin.py | 在保存过的 Event 编辑页提供 DOI 入口；get_urls 把 Admin 包装的获取/独立预览路由置于通用对象路由之前；已有维护/删除规则保留 |
| backend/events/doi_admin.py | GET 只读页面、CSRF POST 获取/检查/取消；模型权限、当前目标、输入保留及安全提示；已有 DOI 重读当前书目，不调用保存服务 |
| backend/events/doi_forms.py | 规范化前验证 DOI；校验五个书目字段及推荐理由/有符号顺序；已有书目字段服务端 disabled、原字符串不 trim，忽略提交替换值 |
| backend/events/services/doi_preview.py | 先按 DOI 查 Resource，未命中才调用已有 fetch_metadata；服务端独立随机预览、管理员/会话/目标/DOI 绑定、固定 900 秒、状态读取与单个取消；业务模型零写入 |
| backend/config/session_backend.py、settings.py | 继承 db SessionStore，仍用原 django_session 表/签名/JSON/Cookie/SessionMiddleware；普通 save/asave 锁行保留最新预览命名空间，禁止默认旧快照回写覆盖；新会话清空预览、已删除行 UpdateError |
| backend/events/templates/admin/events/event/doi_preview.html | 原生 Admin forms/按钮、始终可见目标、完整只读数据库书目、缺失提示、字段错误、检查/取消和返回入口；不显示 Save to event |
| backend/events/static/events/doi_preview.js | 原生 submit 事件保留操作值并禁用重复按钮，显示待处理文字；pageshow 恢复浏览器 Back 的控件；不调用 API/Crossref、不包含可信身份 |
| backend/events/tests/test_doi_preview.py | 23 个 PG TestCase：Admin 请求/业务快照、模型权限/真实 CSRF、字段/转义/身份不泄漏、绑定/期限/取消/登录失效/目标删除、旧会话回写/兼容/写失败及没有保存入口 |
| backend/events/tests/test_doi_preview_concurrency.py | 3 个真实 PG TransactionTestCase：同 Cookie/独立 PID，在 SELECT FOR UPDATE 前同步并发获取（三轮）、取消与获取、取消与旧普通 save；其他预览及业务快照不变 |

- **会话命名空间有独立写入边界。** 预览服务只在短 atomic 内锁 django_session 行、解码最新状态并合并一个 ID；外部 HTTP 已结束。普通 SessionStore.save 锁同一行并从数据库保留 doi_previews，不允许 request.session 缓存中的旧内容覆盖；服务不依赖标记整个 request.session.modified 来持久化。asave 使用同一路径，原 db 签名兼容，轮换后的旧预览不能使用。原生注销删除仍有效，旧请求不能重建删除行。依据：[Django sessions](https://docs.djangoproject.com/en/5.2/topics/http/sessions/)、[select_for_update](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#select-for-update)，另完整读取本地锁定源码；当前单 default 数据库/WSGI 架构未改。
- **身份和期限来自服务器。** token_hex(24) 每次生成独立预览，绑定 user/session/Event，DOI 来自规范化输入；客户端提交的 DOI/target/resource/source 不参与身份。成功加载时开始 900 秒，行锁等待及编辑/检查均不刷新；当前认证 hash、绑定、active 和严格到期判断共同守住读取/检查/取消。取消只改变自己的状态，不删除共享书目或其他预览。
- **当前数据库书目仍优先。** 首次命中不访问提供方；预览后同 DOI 被新增/修改时，页面和表单重新读取当前记录并转为只读。readonly 文本完整显示长标题/链接并转义 HTML；理由/顺序仍属于活动表单。新 DOI 可补充五个书目字段，缺作者/年份允许，必填标题/HTTP(S) URL 校验后才显示检查成功。
- **Admin 页面与业务提交分开。** get_urls 使用 admin_site.admin_view 的身份/CSRF/cache 包装（[官方说明](https://docs.djangoproject.com/en/5.2/ref/contrib/admin/#django.contrib.admin.ModelAdmin.get_urls)）；显式 view 三模型权限，POST 要求 Event change/EventResource add，新 DOI 获取/检查还需 Resource add。Check details 只验证输入且不写预览编辑或业务数据；不存在 save 动作与成功结果状态。第 25 步再连接 save_doi_to_event、重新校验权限/目标/期限，并组合结果事务/幂等重复确认，当前并发会话测试不替代该验收。
- **证据来源分层保留。** 最终 26 项专项 OK（5.032 秒）、237 项全套 OK（20.527 秒）、Django/迁移检查与 Vite build（253 毫秒）通过。临时销毁式 StaticLiveServerTestCase + 独立隐藏 Edge 8 组实际页面检查通过，最终结果 UTC 2026-10-06T17:17:08.622Z，零 JS 异常；只用模拟 Crossref，完整业务快照不变，桌面/手机截图已查看。两个正式测试库每次销毁；旧 CUA/sky 初始化故障、HTML 断言/禁用字段 trim/短暂状态观察的修正记于 progress.md，不把失败尝试记为通过。
- **验证工具和运行环境对称清理。** .tools/step24-browser 中 live_test.py、CDP 检查器、结果/截图/profile 仅为忽略的验证材料，无正式依赖。结束关闭专用 Edge 和临时 LiveServer，9237 无监听（TIME_WAIT），PG17 仅启动既有 5433 后恢复最初停止状态，PG11 未操作。没有开发业务写入/迁移、真实外部/生产访问、Git 发布或部署；前端源码/30 项 Node 测试未改，未重跑前端 lint/Node/公开页浏览器。当前后端 237 项未获新的远程 CI 证据。
- **交接等待用户接受。** backend/README.md 保存当前 26/237 项与 Admin 入口验收，progress.md 区分助手检查与用户确认；两份设计/技术栈规则一致无变更。最后已接受步骤仍为 23，第 24 步待用户验收，第 25 步必须等接受及新的明确实施指令，生产/真实 DOI/备份恢复待办不扩大。


## 59. 第 24 步用户确认后的职责与交接

2026-10-06（Europe/London），用户在收到第 24 步完成报告与验收指引后回复“通过”，确认本地验收。已先更新 progress.md；第 58 节待验收描述保留为实施交接时的历史事实。用户未附逐项输出，不推断新增测试、真实 Crossref/生产验证或当前数据库状态。

- Admin DOI 获取/独立预览、当前书目只读、补充校验、取消和固定 900 秒期限已接受；doi_preview.py 与 session_backend.py 共同保护数据库会话中的绑定状态及并发合并，业务数据只读。
- 26 项专项、237 项后端回归和 8 组浏览器检查为助手既有执行证据；用户接受来源保存在 progress.md，复现与手动检查保存在 backend/README.md。Check details 没有业务保存能力，第 25 步仍须接入保存服务、权限/状态重查及成功结果事务。
- 本次交接只改文档，不重跑测试、不修改应用代码/schema/依赖，不访问数据库或操作进程，不提交、推送或部署。第 01–24 步已接受，第 25 步未开始，需后续明确实施指令；生产仍 d8bdd29，第 18–24 步未发布，既有待办不变。

## 60. 第 25 步：确认事务、可信结果与重复入口

2026-10-06，仅按新的第 25 步指令实施。写代码前完整阅读六份 memory-bank；先更新 progress.md，再记录本节。最后用户确认仍为 24，第 25 步助手检查通过、待用户验收，第 26 步未开始。

| 文件 | 当前职责 |
| --- | --- |
| backend/events/doi_permissions.py | 共用 view/write 权限及 active/staff 规则；供页面和最终确认重查，不引入所有权策略 |
| backend/events/services/doi_confirmation.py | confirm_preview 重读用户/权限、锁会话与目标、校验可信预览及当前书目/字段，组合原保存服务和会话结果事务；saved_result 验证原关联身份，拒绝已移除结果 |
| backend/events/services/doi_preview.py | 获取/取消继续只写会话；读取支持原期限内 saved 状态并校验状态字段，原取消只允许 active；不会延期或清除成功业务记录 |
| backend/events/doi_admin.py | 新增 save 分派、安全失败保留输入、成功 POST→结果 GET、现存结果与公开地址；保留获取/Check/取消和 Admin/CSRF 边界 |
| backend/events/templates/admin/events/event/doi_preview.html | Save to event / Saving…、新关联/重复关联文案、阅读关联与公开活动链接；目标始终可见 |
| backend/events/tests/test_doi_confirmation.py | 24 个真实 PG TestCase：确认/匿名发布、字段/绑定/期限/撤权/CSRF/目标删除、旧结果不重建、会话/业务失败回滚及重试 |
| backend/events/tests/test_doi_confirmation_concurrency.py | 4 个真实 PG TransactionTestCase：同预览重复、同会话跨活动、跨会话实际 SQL 唯一竞争、确认与取消；独立连接/最终状态/连接恢复 |

- **结果与业务的原子边界现在接通。** 确认服务在 default 数据库 atomic 内锁定最新 django_session，读取服务器绑定，锁目标 Event 并复核固定期限，再校验当前字段、调用 save_doi_to_event，最后在同一事务存储原 Resource/EventResource ID 和 created 标记。结果写失败会回滚本次新增业务；成功前只修改会话的预览路径继续独立。外部获取始终在最终事务外，确认/重复确认零 Crossref。
- **权限和书目必须在最终入口重读。** 页面权限只控制访问；confirm_preview 读取新的用户对象，复核模型权限和会话认证 hash，按最新 DOI 资源决定 Resource add 能力及只读字段。客户端 DOI/目标/资源/source/seed 值不能改变服务器身份；新书目只由已校验白名单初始化，已有书目和原关联字段仍由第 22–23 步服务保留。
- **固定期限包含等待和失败重试。** row lock 前的页面检查不替代锁后验证；目标锁等待后和业务写入后再检查，900 秒边界仍严格拒绝并回滚。loaded_at/expires_at 从不更新，结果页刷新和重复确认也不续期。首次确认必须校验字段，成功状态重复提交只返回原记录，忽略新的字段/理由/顺序。
- **幂等结果由原关联主键定位。** 成功后的 GET 和 POST 检查原 association_id/resource_id/Event/DOI 一致性，POST 再经过确认事务和权限。删除原关联后，即使同组合另建新记录，旧结果也失效，不能让浏览器 Back 或 POST 重放重新添加。成功 POST 统一重定向到同地址结果 GET，公开地址仍 /events/{id}；没有新增公开写接口。
- **普通会话回写不能覆盖成功状态。** session_backend.py 不需再改，仍锁同一行并保留数据库最新 DOI namespace。旧请求、SAVE_EVERY_REQUEST、另一个预览及取消与确认竞争不会把 saved 状态改回 active；同 Cookie 两次确认由同一会话行顺序处理。跨会话竞争仍交给原数据库身份约束/回滚恢复服务，实际 23505 有请求级测试证据。
- **证据按层保存。** 新 28 项 + 原预览 26 项 = 54 项专项 OK（14.117 秒）；完整 265 项 OK（30.218 秒），当前 Vite build（268 毫秒）和 Django/迁移检查通过。8 组隔离浏览器检查 OK，UTC 2026-10-06T18:28:37.649Z，零 JS 异常，Live test 10.183 秒；当前生成前端通过真实 WhiteNoise 提供，匿名阅读/刷新展示实际测试库保存内容，截图已检查。模拟提供方、真实 PG/浏览器与用户接受仍分别记录。
- **测试工具不成为产品依赖。** .tools/step25-browser 临时 LiveServer、CDP、profile、截图/结果及静态收集只用于销毁式测试库。初始化工具故障、错误包含退出按钮的 pending 断言、临时静态服务器资产 404 及其 WhiteNoise 修正记于 progress.md；没有修改应用以配合这些临时断言。测试库销毁，专用 browser/server 已关闭，9237 无监听，PG17 恢复初始停止，PG11 未操作。
- **本步交接停在确认。** backend/README.md 保存 28/54/265 项及本地真实保存验收；AGENTS/前端指南同步现状。无 schema/依赖/公开 API/React 源码变化，没有开发业务写入、真实 Crossref/生产访问、Git 发布或部署；前端 lint/30 Node 未重跑。共享编辑与排序的第 26 步、权限全面复核第 28 步、真实 DOI 第 29 步及生产待办未自动推进，生产仍 d8bdd29。

## 61. 第 25 步用户确认后的职责与交接

2026-10-06（Europe/London），用户在第 25 步完成报告及验收指引后回复“通过”；已先在 progress.md 记录，再同步本架构与相关指南。第 01–25 步现已用户验收通过。用户未另提供逐项输出，54 项专项、265 项回归及 8 组浏览器证据仍归属助手执行，不增加真实 Crossref、生产或远程 CI 结论。

确认保存职责仍由第 60 节的权限、可信会话、短事务、原结果身份与回滚边界承担。本次交接仅修改文档，不重跑测试、不修改应用/schema/依赖、不访问数据库或操作服务、不提交、推送或部署。第 26 步共享编辑与排序仍未开始，须用户新的明确实施指令；生产仍 d8bdd29，第 18–25 步未发布，既有待办保持不变。

## 62. 第 26 步：共享编辑提示与活动关联维护

2026-10-06，收到新指令后完整阅读六份 memory-bank，保留已有工作并只实施第 26 步。先更新 progress.md，再记录本节；最后用户确认仍为 25，本步助手检查通过、待用户验收，第 27 步未开始。

- **提示由资源表单模板承担。** ResourceAdmin.change_form_template 指向新的 resource/change_form.html，继承原生 Admin form_top。change 且 has_change_permission 时，在字段前显示规定的 Changes to this resource will appear in every talk that uses it.，包括未被引用的已有资源；新增表单不显示，校验错误后仍显示。原生布局、CSRF、按钮/校验/保存与资源禁删保持原职责，无额外确认阶段或自定义写入路由。
- **共享书目与当前活动语境沿用原边界。** ResourceAdmin 的五项可编辑书目影响所有引用活动；DOI/来源只读，稳定身份不在表单中，编辑不会把 Crossref 来源改为 manual。EventResourceAdmin 只改理由/有符号整数顺序，已有关联身份只读；其他活动理由/顺序和所有书目保持原值。模型默认 0、ordering 与详情 Prefetch 的 display_order/id 升序一致，同值由关联 ID 决定，无拖拽/批量新路径、模型/迁移/API/React/依赖变更。
- **写入和公开读取通过集成验证。** 新 test_admin_reading_edits.py 的 8 项真实 PG17 TestCase，用 Admin 表单保存后独立匿名 API 重读，覆盖两种来源/空作者年份/身份保护、只改 A 理由或顺序/清空、默认/负数/自定义同值及反向资源 ID、无效书目/整数错误后完整业务快照不变。旧 Admin 21 项继续保护当前权限/CSRF/删除基础行为；本步不宣称第 28 步完整权限矩阵已完成。
- **证据分别保存。** 8 新项 + 21 Admin = 29 项 OK（4.479 秒），完整 273 项 OK（29.932 秒），Django/迁移检查与当前 Vite build（280 毫秒）通过。6 组临时隔离库浏览器检查 OK（UTC 2026-10-06T19:35:57.550Z、零 JS 异常，Live test 6.150 秒），包括桌面/375 px 提示、实际共享/单场保存、默认同值排序及退出后真实 React 两场/刷新；截图已查看。前端 lint/30 Node 未重跑，HTTP 全部阻止，无真实 DOI/生产/远程 CI 结论。
- **临时验证和生产架构分开。** CUA/sky 初始化失败后使用预装专用隐藏 Edge/CDP；.tools/step26-browser 的 LiveServer、专用静态收集、profile、结果/截图均忽略。test_psychtalk 与 test_psychtalk_step26_browser 销毁，测试浏览器/服务器关闭，9237 无监听；PG17 初始停止，仅启动既有 5433 实例测试后停止恢复，PG11 未操作。没有开发业务写入/迁移、账号初始化、提交/推送/部署。
- **验收与后续仍由用户指令控制。** backend/README.md 保存 8/29/273 项命令及两场活动共享编辑/单场维护清单；progress.md 保存实际输出和待确认状态，AGENTS/前端指南同步边界。产品双语规则已相同，无需变更规范。第 27 步移除流程需验收后新指令；生产仍 d8bdd29，第 18–26 步未发布，真实 DOI/备份恢复等待办不变。

## 63. 第 26 步用户确认后的职责与交接

2026-10-06（Europe/London），用户在第 26 步完成报告及验收指引后回复“通过”，确认本地验收。已先更新 progress.md，再同步本文件及相关指南；第 62 节待确认描述保留为首次实施事实。第 01–26 步现已用户验收通过，用户未提供逐项输出，29 项 Admin、273 项回归及 6 组浏览器证据仍归属助手执行，不追加真实 Crossref、生产或远程 CI 结论。

共享提示由 Resource 原生编辑模板承担；共享书目和活动关联语境继续分别由 ResourceAdmin 与 EventResourceAdmin 维护，排序沿用 display_order/id。此次确认交接仅修改文档，不重跑测试、不修改应用/schema/依赖，不访问数据库或操作服务，不提交、推送或部署。第 27 步未开始，须新的明确实施指令；生产仍 d8bdd29，第 18–26 步未发布，既有待办不变。

## 64. 第 27 步：关联移除入口与首次审批阻塞（历史）

2026-10-06，完整阅读六份 memory-bank 后仅处理新的第 27 步指令；先记录 progress.md，再补本节。最后用户确认仍为 26，第 27 步已写入但未验证，不能标记完成，第 28 步未开始。

- **按钮命名与实际删除分开。** 新 eventresource/submit_line.html 由 Django InclusionAdminNode 按模型自动选择，继承原生 submit-row，临时隐藏父块的 Delete 链接后显示 Remove from this talk。沿用 show_delete_link/原 URL/add_preserved_filters，不复制保存按钮或自建删除路由。确认模板增加自动转义的完整活动和阅读标题，保留规定提示及原生确认/取消控件。
- **原生 Admin 继续承担删除边界。** 模型删除权限和 CSRF、确认 POST 中的权限复查、事务/删除收集器/审计日志由锁定 Django 执行；只删除 EventResource URL 指向的关联。Resource 和其他关联保留，包括最后引用被移除的资料；原共享禁删、公开 API 只读及 DOI 原结果身份规则保持不变，无 schema/依赖/API/React 改动。
- **新测试定义不能当作通过证据。** test_admin_reading_removal.py 定义 10 项 PG17 TestCase，覆盖入口及筛选、取消/确认、目标转义、匿名计数、全字段保留、最后引用/空活动、伪造目标、移除授权/撤权、真实 CSRF、重复确认及实际 Admin 移除后旧 DOI 结果拒绝。39 项与旧 Admin 合跑、预计 283 项全套均尚未执行；不宣称第 28 步完整权限矩阵已补齐。静态核对修正测试用户名称，git diff --check 通过。
- **自动审批故障明确阻断运行验证。** 初始 PG17 为停止；start 工具返回 0/无输出，但随后只读 pg_ctl 仍 no server running，不声称启动成功。39 项测试请求因审批服务用量限额而无法完成审查，进程未启动；返回明确这是审查失败而非安全性判定，未绕过。测试库、浏览器或开发服务器未创建，本轮没有测试/Django/迁移检查、构建、真实 Crossref/生产访问、开发业务写入/迁移、Git 发布或部署。最后确认 PG17 仍停止，PG11 未操作。
- **下一项仍是完成本步验证。** backend/README.md 提供 10/39 项专项、预期 283 项回归及本地取消/确认验收；恢复用量后继续运行并修复，或由用户按指南执行并反馈。历史 273 项/6 组浏览器属于第 26 步，不能代替新版本验证。第 27 步待验证及用户接受，第 28 步未开始，生产仍 d8bdd29，既有待办不变。

## 65. 第 27 步：审批恢复后的验证与交接

2026-10-06，用户询问重置用量后先前错误的含义。当前用量与命令重试均正常，继续原已授权验证；此前失败属于审批请求当时的限额故障，未能确定重置与请求状态不一致的原因。第 64 节保留首次交接事实，当前结论以本节及 progress.md 为准。

- **界面职责保持很小。** 仅模型专用 submit_line 命名现有动作、confirmation 提供完整目标；实际权限、CSRF、事务删除及日志仍属原生 Admin。39 项专项 OK（5.932 秒）验证 10 新项和既有基础/编辑回归；283 项完整 OK（34.865 秒），当前 Vite build（237 毫秒）及 Django/迁移检查通过。未改 schema/依赖/公开接口/React。
- **取消需要验证实际导航。** 临时销毁式 LiveServer/隐藏 Edge 的 5 组检查通过（UTC 2026-10-06T20:32:01.178Z、零 JS 异常，Live test 7.720 秒），实际点击 Cancel/history 回到关联表单且两场匿名数据不变。真实 CSRF 确认只移除 A 关联，Resource 禁删/完整元数据及 B 推荐/顺序保留，375 px 确认无溢出、退出后真实 React A 刷新及 B 阅读正常；资产 200、截图已查看，ORM 完整快照核对，Requests 外部 HTTP 全部阻止。忽略的 .tools/step27-browser 不成为应用/依赖/CI 架构。
- **当前环境已恢复。** 恢复阶段授权 pg_ctl 确认既有 PG17 运行 PID 28576，不再次 start；此前沙箱状态与 start 结果不一致，不推断原因。所有测试库销毁，专用 Edge/PID 与 9237 已关闭、临时服务器退出，项目 stop 后最终授权 pg_ctl no server running，恢复本步初始停止状态；PG11 未操作。最终首次 status 路径遗漏 pgsql，经核实后正确复查，无重复启停。没有开发业务写入/迁移、真实 Crossref/生产访问、Git 发布或部署。
- **下一项是用户验收。** README 的 10/39/283 命令与手动清单仍供复核，progress.md 先更新后同步本节及指南。第 01–26 步已接受，第 27 步助手验证通过、待用户验收，第 28 步未开始；全面权限矩阵仍留后续明确指令。生产 d8bdd29 和真实 DOI/非空重部署/备份恢复等待办不变。

## 66. 第 27 步用户确认与职责交接

2026-10-06（Europe/London），用户在恢复验证报告和验收指南后回复“通过”，据此确认第 27 步本地验收。已先更新 progress.md，再同步本文件和相关指南；第 64–65 节保留首次阻塞与恢复验证的历史来源。第 01–27 步现已用户验收通过；用户未附逐项输出，39 项 Admin 专项、283 项回归及 5 组浏览器结果仍为助手执行证据，不增加真实 Crossref、远程 CI 或生产验证结论。

关联移除入口及完整目标由模型专用模板承担，实际确认/取消、权限、CSRF、事务删除与日志沿用原生 Admin。确认只删除 URL 指向的 EventResource，保留共享资料、活动与其他关联，公开页面下次读取反映当前计数。此次确认交接只修改文档，不重跑测试、不修改应用/schema/依赖，不访问数据库或启停服务，不提交、推送或部署。第 28 步未开始，须新的明确实施指令；生产仍 d8bdd29，第 18–27 步未发布，真实 DOI、非空重部署、备份恢复等既有待办不变。


## 67. 第 28 步：统一后台权限矩阵与真实 CSRF 证据

2026-10-06，完整阅读全部 memory-bank 后只实施新的第 28 步指令，先记录 progress.md。第 01–27 步已接受，本步助手验证通过、待用户验收，第 29 步未开始。生产仍 d8bdd29，当前实现未发布。

- **授权分别由原生 Admin 与 DOI 确认承担。** 没有新的权限系统、所有权或路由。Event/Resource 创建各自检查 add，原生选择关联检查 add_eventresource/change_event/view_resource；共享修改、理由/排序、移除分别检查 change_resource/change_eventresource/delete_eventresource。Django 原生确认 POST 再查权限，活动单条/批量删除必需 delete_event 与 delete_eventresource，Resource 全局禁删。
- **自定义 DOI 入口保持 Admin 包装和明确矩阵。** 查看须三个 view；提交须三个 view 加 change_event/add_eventresource，新 Resource 的获取/校验/保存另需 add_resource，已有书目复用不需 Resource add/change。取消可在没有 Resource add 时失效自己的预览。最终 confirm_preview 使用新的用户对象检查授权，即便页面已有允许权限缓存，撤销 Resource add 仍被拒绝；原有 add_eventresource 事务撤权测试继续通过。
- **新测试守住现有运行边界，无需增加运行代码。** test_admin_permissions.py 的 28 项 PostgreSQL TestCase 用真实 Admin 请求/数据库会话与受控提供方，逐项去权限、身份失效、预览后撤权、成功重复结果撤权，以及最小允许权限。拒绝时比较全部三模型、Admin 审计日志和预览命名空间，不能只以数量或隐藏按钮作为授权证明。临时权限/账号只存在于销毁式测试库，Requests 外部 HTTP 阻止。
- **CSRF 中间件执行和模型授权独立验证。** enforce_csrf_checks=True 的客户端对所有写路径验证缺失/格式有效的假令牌与合法令牌配不可信 Origin 均 403，无数据/会话预览/日志变化。另真实合法令牌依次完成创建、共享及关联编辑、获取/检查/确认/取消、移除、单条及批量活动删除，避免只有拒绝测试而保存路径不可用。没有额外前端令牌方案。
- **确认与数据保留沿用原生收集器。** 单条 GET/空 POST、批量初次 POST 不删除；确认仅清除指定 Event 和其关联，所有 Resource（含独占/未关联）及未选 B 保留。缺双删除权限时批量动作被移除，伪造提交返回列表 200 但不执行；单条返回 403。对 staff 显式 delete_resource 和 superuser，资源按钮/批量/直接地址与删除钩子均拒绝。GET 写参数不会执行自定义动作或删除，原生列表把无效筛选重定向 ?e=1。
- **验证来源不扩展为 UI 或真实集成。** 专项 28 项 OK（5.748 秒），当前 Vite build（252 毫秒）、Django/迁移遗漏检查通过，完整 311 项 OK（41.612 秒、退出码 0），测试库销毁。首轮 26 项两项断言误期待 GET 列表只 200/403，核对原生重定向后修正测试并增加两项，未调整产品适配测试。本步不改 UI，无新浏览器/前端 lint/30 Node 执行；真实请求测试不称浏览器证据，模拟 Crossref 不称第 29 步真实 DOI 通过。
- **环境和后续边界明确。** PG17 初始停止，启动现有 5433 后测试，结束 stop 及授权 pg_ctl 确认停止，PG11 未操作；无 init/reset、开发业务写入/迁移、生产访问、schema/依赖/API/运行代码变化、Git 暂存/提交/推送或部署。README 保存矩阵、28 项专项与 311 项全套操作；本步等待用户确认，第 29 步须接受后新的明确实施指令，既有非空重部署/备份恢复待办保持原状态。

## 68. 第 28 步用户确认与交接

2026-10-06（Europe/London），用户收到第 28 步完成报告及验收说明后回复“通过”，确认本地验收。已先更新 progress.md，再同步本文件及相关指南；第 67 节待验收描述保留为实施交接时的历史事实。第 01–28 步现已用户验收通过；用户未提供逐项输出，28 项权限/真实 CSRF 专项、311 项完整回归和构建/检查仍为助手执行证据，不追加真实 Crossref、浏览器、远程 CI 或生产验证结论。

后台授权继续由原生 ModelAdmin、自定义 admin_view 和确认服务承担，新增权限测试保护跨入口矩阵、撤权、CSRF/Origin、删除确认及资源保留，不增加运行权限层。本次确认交接只修改文档，不重跑测试、不修改应用/schema/依赖，不访问数据库或启停服务，不提交、推送或部署。第 29 步真实 DOI 集成未开始，须新的明确实施指令；生产仍 d8bdd29，第 18–28 步未发布，非空重部署、备份恢复等既有待办不变。

## 69. 第 29 步：真实外部书目与本地管理/公开阅读集成

2026-10-06，完整阅读全部 memory-bank 后只执行新的第 29 步指令；已先记录 progress.md。最后用户确认仍为 28，第 29 步助手验证通过、待用户验收，第 30 步未开始。

- **真实 HTTP 通过原服务，不新增外部路径。** development 配置下对 `10.1038/nrn2762` 的独立 probe 和实际 Admin 获取均使用原 crossref.py 的固定编码 works 地址、TLS、(3, 7) 超时和无重定向/重试。浏览器链路只发一次真实 Crossref 请求，取数时不在 atomic 内；后续确认、重复确认、已有 DOI 和跨活动复用均未再次请求。
- **来源、转换、预览和持久化逐层核对。** 当次真实 work 的标题 `The memory function of sleep`、作者 `Susanne Diekelmann; Jan Born`、published-print 年 2010 和 URL `https://doi.org/10.1038/nrn2762` 与预览、Resource 及匿名 API 相同；DOI 标准化、research_paper/crossref 及 NULL seed 保持原规则。输入为大写/两端空白的 HTTPS 链接；预览后业务计数零，真实 CSRF 确认后发布，重复导入保留原 ID/理由/-3 顺序，另一活动只新建关联，最终一资源两关联。
- **公开阅读不依赖提供方在线。** 验证工具在下一次新查询受控抛出 ConnectionError，页面按原服务显示安全错误、保留输入/Retry/Add manually。该故障是模拟，真实成功查询是未模拟的 Requests。故障期间已保存两场匿名 API/React/完整刷新继续可读，无额外外部调用。Read original 新标签最终到达 Nature 对应文章，标题一致；不保证全文免费访问。
- **验证工具与正式测试边界不变。** 忽略的 `.tools/step29-browser/probe.py` 单独查询；live_test.py 用 development 配置及销毁式 `test_psychtalk_step29_browser` 创建临时账号/两场示例，原 Requests 真实获取后只记录书目白名单/安全参数；check.mjs 及已有 CDP 连接器验证实际表单、匿名页面和新标签。不会自动进入管理命令、CI、部署或生产。业务快照/ORM 断言只涉及临时库，既有 psych_talk_dev 未写入。
- **实际证据区分成功、故障模拟和接受。** 8 组浏览器通过、零 JS 异常（UTC 2026-10-06T21:54:10.059Z），live test OK 11.431 秒，1280/375 px 截图已查看、真实资产 200。当前构建 251 毫秒，check/迁移检查通过，311 项常规 PG17 回归 OK 57.826 秒。普通测试继续模拟 Crossref，未新增正式测试或依赖，前端源码不变，未重跑 lint/30 Node；本地证据不当作新远程 CI 或线上 DOI 验收。
- **环境恢复与实施边界可追溯。** CUA/sky 初始化失败后使用预装专用隐藏 Edge；首个探测命令 shell 引号错误未发请求，文件脚本修正后成功。两个测试库均销毁，临时服务与 profile/PID 核对后的 Edge 已关闭，9237/2821 无监听；PG17 从停止启动既有 5433 后恢复停止，授权 pg_ctl 确认，PG11 未操作。无应用运行代码/UI/schema/迁移/API/依赖改动、开发业务写入、生产访问或 Git 发布/部署。
- **交接保持用户验收边界。** backend/README.md 保存真实来源及人工重现步骤，两端 README/AGENTS 指向本步待验收；两份设计与技术栈已经规定同一行为，无需产品规范修改。生产仍 d8bdd29，第 18–29 步未发布。第 30 步须用户验收后新的明确实施指令；非空重部署、备份恢复、线上全流程和视频等既有待办不变。

## 70. 第 29 步用户确认与交接

2026-10-06（Europe/London），用户收到第 29 步完成报告后回复“通过”，确认本地真实 DOI 集成验收。已先更新 progress.md，再同步本文件及相关指南；第 69 节的待验收描述保留为实施交接时的历史事实。第 01–29 步现已用户验收通过，最后用户确认步骤为 29。

用户未提供逐项输出；真实 Crossref 查询及 8 组浏览器、311 项回归、构建/检查保持助手执行来源，提供方不可用保持受控模拟故障来源。预览不写业务、确认保存后公开读取和已有 DOI 复用不依赖 Crossref 的架构保持不变。本次仅修改文档，不重跑测试、不修改应用/schema/依赖，不访问数据库或启停服务，不提交、推送或部署。第 30 步未开始，须新的明确实施指令；生产仍 d8bdd29，第 18–29 步未发布，非空重部署、备份恢复及完整 MVP 验收等既有待办保留。

## 71. 第 30 步：第二个里程碑的当前边界与验证

2026-10-06，完整阅读六份 memory-bank 后按新的第 30 步指令验证既有实现；已先记录 progress.md。第 01–29 步用户接受，第 30 步本地检查通过、待用户验收及当前版本远程 CI，第 31 步未开始。无需应用代码、schema、依赖或产品规范变更。

### 服务、接口与状态职责

| 边界 | 当前实现与约束 |
| --- | --- |
| 公开 API / React | 两页沿用 [tech-stack.md → Public API contract](tech-stack.md#public-api-contract)。仅 GET/HEAD/OPTIONS；详情通过预加载 event_resources/resource 扁平输出，display_order/id 排序。标题搜索仅过滤当前已读数据，无额外请求/写入；以 association_id 定位卡片。Admin 登录不增加公开 API 写能力。 |
| 标准化/外部书目 | doi.py 无网络/ORM；crossref.py 一次固定编码 works 请求、TLS、(3,7) 超时、无自动重试/重定向；crossref_metadata.py 转换书目，crossref.py 映射安全错误。已有 DOI 用数据库当前书目且不调用 Crossref；外部查询不进入业务保存事务。 |
| Admin 预览 | doi_admin.py/doi_forms.py/doi_permissions.py 承担页面、输入与入口授权；doi_preview.py 将独立随机 ID 绑定管理员/会话/Event。加载后固定 900 秒，Check details/编辑不延期；取消仅移除本预览。Row lock 合并预览命名空间，session_backend.py 保护普通 save/asave 不覆盖最新状态或复活取消预览。获取/校验/取消可写会话，不写业务模型。 |
| 确认/原子保存 | doi_confirmation.py 锁定会话、重新检查用户/模型权限、目标、状态、期限与字段；恰好到期及之后拒绝。resource_save.py 在短事务内匹配/创建 Resource 与关联，确认成功结果同事务保存，失败全部回滚。复用当前 DOI 书目，同活动重复导入/确认返回原关联并保留理由/顺序；旧结果不重建已移除关联。 |
| 并发身份 | 仅恢复已核对的 DOI/活动资源对唯一冲突，回滚后检查保存赢家，每种身份最多恢复一次；其他数据库错误传播。预览后并发产生 DOI 也复用获胜的当前书目。正式 PostgreSQL 独立连接测试覆盖实际竞争。 |
| 共享编辑/删除 | 原生 Resource 表单附影响所有引用活动的警告，保留 DOI/source/seed；EventResource 只改当前理由/整数顺序，身份只读。移除需确认，只删指定关联。活动单条/批量确认仅删活动和关联，保留全部 Resource；Resource 包括未关联记录及超级管理员均禁删。手动书目不按标题/URL 合并。 |

权限使用 Django 模型授权和原生 CSRF，无活动所有权或新权限体系。原生创建/共享编辑/关联编辑/移除分别检查相应 add/change/delete；关联创建额外要求 change_event/view_resource；活动删除要求 delete_event 和 delete_eventresource。DOI 查看要求三个 view，提交另需 change_event/add_eventresource，新资源获取/检查/保存要求 add_resource；已有 DOI 复用不需 Resource add/change。最终确认重新读取授权，预览后撤权仍拒绝。拒绝、GET 和失效状态的业务/日志/预览不变由权限套件核对。

### 当前测试与浏览器证据

- 当前前端 lint、**30 项 Node 请求/生命周期/链接/时间测试**（332.9551 毫秒）、build（248 毫秒）通过，固定 Node24.14.0/npm11.9.0/Python3.13.16。pip/Django/迁移遗漏检查和静态收集通过；**311 项后端 OK（41.926 秒）**，实际 bundle 测试不跳过缺少输出。无依赖重装/新正式测试，干净安装与 CI 故意失败检查仍留第 34 步。
- 正式套件覆盖模型/API、演示重复导入、公开只读/静态页面、DOI 输入/书目/错误、短事务保存和真实 PG 并发、会话锁/多标签合并、期限前/到期/之后、取消/身份/权限撤销、幂等结果/会话失败回滚、共享编辑/排序/移除和全部删除/CSRF矩阵。该测试范围不等于后续完整线上、可访问性及交付验收。
- 忽略的 step30-browser/live_test.py 用 test 配置及销毁式 test_psychtalk_step30_browser，真实 Admin/CSRF/数据库会话/API 和 DEBUG=False/WhiteNoise 的当前 React。12 组检查完成新 DOI 未确认不发布/确认/重复、已有跨活动复用、独立手动资料、标题搜索/清空焦点/无额外请求、两个预览/取消、共享编辑、单关联理由/排序、移除及活动删除的取消/确认、退出后匿名刷新和移动端。**全部通过、零 JS 异常、前端资产全部 200**；live test OK 23.236 秒，UTC 2026-10-06T22:13:05.329Z，五张截图已查看。
- 本轮外部 HTTP 被阻止，三次模拟取数来源是演示清单；恰好 900 秒过期由测试时钟触发，未实际等待或改系统/原状态时间。数据库最终三资源/一关联、A 删除/B 完整保留、手动同内容独立、取消/过期 DOI 未保存。第 29 步真实 Crossref HTTP 证据仍独立保留，不用本轮 mock 冒充真实服务可用。

### CI 与未完成事项

只读核对最新已有 [Project checks 37320118006](https://github.com/1uxury/psych-talk-hub/actions/runs/37320118006)：SHA 01e1dd094277cb8b89ba5d2bb791d62b0f24f972，前后端 jobs 和所有 steps success。该已提交版本只有第 17 步实现及后续文档，**第 18–30 步未提交本地改动尚无远程 CI 结果**。本地执行了现有检查/回归/静态收集，不声称等于 Linux 干净安装和当前远程通过；CI 待发布后验证，本步不自动提交/推送/触发。

初始 PG17 停止，仅启动已有5433实例，两个测试库销毁后恢复停止，最终 pg_ctl no server running（退出码3），5433/9237无监听，PG11未操作。CUA/sky失败后用预装隐藏专用Edge；首轮忽略的浏览器脚本重复声明造成失败，仅修正其作用域后重跑成功；专用profile/PID核对后关闭进程树。首次清理断言误期待status1，按实际3只读复查成功，详细排查在progress.md。不写既有开发业务/生产，不新增持久账号，无Git发布/部署。

backend/README.md 保存可重复命令和手动清单，两端指南/AGENTS 同步本地结果与验收边界。已对照两份设计：固定 15 分钟、重复保留原记录、活动删除保留资料/资源禁删、阶段交付与完整 MVP 要求相同；无行为调整，双语设计和技术栈不变。只读结构检查通过 9 份文档/67 个本地文件链接、闭合代码块、对应 10 个设计章节/关键英文提示及当前验收门槛；git diff --check 通过，验证工具/证据确认忽略。**第 30 步待用户验收及当前版本远程 CI，最后用户确认 29，第 31 步未开始。** 生产仍 d8bdd29；非空重部署/备份恢复、线上全流程、干净复现、可访问性与视频等按原计划待办。

## 72. 第 30 步用户要求助手复查：核心路径与真实 DOI

2026-10-07（Europe/London），用户要求“你帮我检查”本地核心验收，已先记录 progress.md。该指令不是用户接受第 30 步或启动第 31 步，最后确认仍为 29；原服务、接口、模型/会话/权限职责保持第 71 节规则，无应用代码修复。

- **当前完整检查再次通过。** 固定运行时的 lint、30 Node（290.874 毫秒，无跳过）、build（249 毫秒）及原资产哈希保持；pip/Django/迁移检查通过，静态收集 2 copied / 164 unmodified / 156 post-processed；完整 PG17 后端 **311 OK（44.641 秒）**。test_psychtalk 销毁，故障日志仍为受控测试来源。
- **20 组浏览器证据分开归因。** step30-browser 在 test 配置/销毁库中运行 12 组核心路径，mock 外部书目、恰好 900 秒由测试时钟触发，live test OK 23.780 秒，UTC 2026-10-06T23:00:49.930Z。step29-browser 在 development 配置/另一销毁库中运行 8 组真实 Crossref→Admin→匿名 React/重复/跨活动复用，真实一次 HTTP 200，live test OK 9.309 秒，UTC 2026-10-06T23:01:25.172Z；提供方失败为受控模拟。两组均零 JS 异常/实际资产 200，资料/关联最终 ORM 断言和来源比对通过，新标签最终 Nature URL/标题匹配，五张核心及三张真实链路截图已查看。
- **测试工具保持本机专用。** 复用既有 LiveServer/原 Admin 表单/CSRF/session/current bundle 与 CDP，不依赖假公开 API。首次证据先复制到忽略的 evidence-before-recheck 目录，最新结果/截图继续忽略。不存在的 step30/cdp 只读探测不代表连接失败，实际复用 step26 连接器；没有新增正式测试/依赖/CI集成。
- **清理以本轮初始状态为准。** 初始 PG17 PID 29760 已运行，保持运行而不再次 start/stop；三个测试库销毁。只关闭核对后的专用 Edge/recheck-profile/PID 33136 及临时 LiveServer，9237 无监听；最终授权 pg_ctl 保持相同 PID。PG11/现有开发服务不操作，现有开发业务和生产无写入/访问。
- **完成与待办不混淆。** 已有 GitHub 37320118006/01e1dd0 的前后端 jobs/全部 steps 再次核对 success，仍不覆盖未提交的第 18–30 步。没有 Git 发布/部署/工作流触发；结构检查9文档/67本地链接及 git diff --check 通过。第 30 步本地核心验证通过、待用户接受和当前远程 CI，第 31 步未开始；生产 d8bdd29、线上全流程/非空重部署/备份恢复/干净复现/可访问性/视频等待办不变。

## 73. 第 31 步：公开状态职责与当前浏览器证据

2026-10-07，用户明确授权继续第 31 步；完整读取全部 memory-bank 并先更新 progress.md。本步检查已有实现，不重复创建页面状态或增加请求路径。最后明确的“通过”步骤仍为 29，新指令授权本步推进；当前远程 CI 待办不因本地通过消失。第 31 步待用户验收，第 32 步未开始。

| 边界 | 当前职责与验证 |
| --- | --- |
| client.js / useApiRequest.js | HTTP 状态优先于解码，坏 JSON 与网络故障为 error，404 为 not_found，200 空数组为 success；离页 abort 与 active 标记屏蔽晚到结果，重试生成新请求身份。现有 30 项 Node 测试继续覆盖忽略 abort 的晚到响应；浏览器实际观察离页取消和晚到失败不污染首页。 |
| RequestState.jsx | 英文 Loading talks… / Loading resources…、活动未找到及固定安全失败文案，失败提供 Retry；loading 的 status 与 error 的 alert 语义已核对。 |
| HomePage.jsx | 只在 success 挂载 TalkGroups；成功全空提供总提示并保留两组标题，单组为空只显示该组提示，加载/失败不误展示空组。 |
| TalkPage.jsx / TalkDetails | 加载/404/失败保留 Back to talks；零资料保留活动信息、隐藏搜索；已加载资源的搜索无结果提供 Clear search，恢复 API 顺序、计数及焦点且无额外请求。 |
| frontend/README.md | 第 31 步可复现状态矩阵、已有空夹具链接、延迟/断网/500/坏 JSON/重试/取消方法；只在本地浏览器临时覆盖读取，不改业务数据。 |

当前 lint、30 项 Node（288.267 毫秒）、build（250 毫秒）通过，哈希资产保持；**13 组浏览器全部通过、零 JS 异常、实际资产全部 200**（UTC 2026-10-06T23:13:02.711Z）。检查两页加载、全空/单空组、零资料/无匹配/清空、404/Back、两页 500 空正文数组和坏 JSON、两页真正浏览器 Offline/恢复/Retry，以及延迟错误期间离页。重试进入 loading 后错误消失，成功也无旧错误；观察 4 条取消请求，最终场景明确断言取消事件和等待延迟后首页无错误。五张状态截图已查看。无需运行代码/样式/schema/依赖/API/双语产品规则变更；311 项后端最近证据保留第 72 节，本步未重跑。

`.tools/step31-browser/serve.py` / check.mjs 是忽略的临时工具，复用 step26 CDP，独立隐藏预装 Edge；只服务当前 dist 和演示清单派生的固定夹具，不连接数据库或外网。临时控制端点、延迟及网络模拟不属于 Django/公开 API，不进入 CI 或部署。computer-use/CUA 因 sandbox setup refresh 无法初始化后采用既有方式；结束恢复网络/夹具，核对 PID34200/profile 后关闭仅测试浏览器及8002服务，用户开发服务/PG17/PG11未操作。没有创建数据库或账号，无发布/生产访问。本地夹具验证不替代真实数据库、当前远程 CI 或线上完整验收；后续时间/导航专项仍是第 32 步，待用户验收后新指令。

最终文档检查通过9份文档/69本地文件链接、闭合代码块/对应双语章节与当前交接门槛；README临时控制台夹具直接执行验证了正常/500/坏JSON/取消与同源GET限定，不覆盖Admin/外网/POST。git diff --check及忽略规则核对通过，8002/9237无监听；这些证据不扩大为新的正式测试或生产验收。

## 74. 第 31 步用户确认与职责交接

2026-10-07（Europe/London），用户收到第 31 步完成报告和验收清单后回复“通过”，确认本地验收；已先更新 progress.md，最后明确用户确认步骤为 31。用户未提供新的逐项输出，前述30项Node/13组只读夹具浏览器/build仍为助手执行证据，不增加真实数据库、远程CI或生产验证结论。

请求状态继续由client/Hook/RequestState承担，成功空组由HomePage承担，零资料/搜索无结果及清空由TalkDetails承担；本次只更新交接文档，没有运行代码、数据库、依赖、测试重跑、服务或发布操作。第32步未开始，须新的明确实施指令。生产仍d8bdd29，当前远程CI/线上完整验收及其他待办保持不变。

## 75. 截止前阶段交付：时间/布局/干净检查/安全日志

已先记录 progress.md。用户最新授权必要收尾，后续步骤不再逐步等待；最后明确用户接受仍为31。第32–35步沿用现有日期、路由、样式、构建/静态架构，无新产品行为、schema或依赖。时间由页面单次快照及 Europe/London 显式格式化；请求 Hook 隔离过时响应。当前九组专项浏览器、30 Node、干净依赖/迁移/静态检查和 **315 PG17测试（43.307秒）**通过，临时故意失败只在忽略副本且全部恢复；当前远程CI/线上版本另待发布核对。

安全日志边界：config.safe_logging.SafeRequestFilter 作用于控制台 handler，将 django.request/security 的路径、参数、异常/堆栈替换为固定失败信息和整数状态；config.health 只记数据库异常类型，不查询 Crossref；events.doi_admin 只记固定 lookup 分类及保存异常类型，不记录输入/DOI/预览标识/外部响应。Gunicorn access format 为 `%(m)s %(s)s %(M)sms`，不带 URI、query、用户或 IP；错误流保持控制台。新增四项测试覆盖 request/security/health/lookup/save 敏感哨兵及无业务写入；14日志/部署检查和315全套均通过。

README.md/DELIVERY.md 为当前独立环境、安装/启动/测试/API/管理流程与阶段缺项入口；历史章节仍是当时证据，以最新收尾段为准。第37–40进行中，生产仍旧d8bdd29；视频未录制/完整MVP未验收。Render只读确认Free/Frankfurt/no autoDeploy/PG17/外部规则[]/2026-11-03到期。初始PG17运行PID29760保持，专用测试服务将结束后清理，不操作PG11。
