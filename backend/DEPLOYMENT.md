# Free Render deployment — step 17 handoff

Latest image/demo extension: **b85902b45df9a8b6b84dbdc9614b4fc6148aa710** passed
[CI 37602418895](https://github.com/1uxury/psych-talk-hub/actions/runs/37602418895);
**dep-db318n7lk1mc73936ohg** Live **2026-10-07T09:45:23.224798Z** on the same Free
service. Logs confirm image migration 0004 OK before Gunicorn. Static SVGs survive
redeployment as tracked assets; no uploaded files/persistent disk were introduced.
Explicit separate TLS demo enrichment gives 8 talks/11 resources/24 links, only fills
two old empty covers, preserves original dates/readings/admin data and repeats without
changes. Temporary external database access was restored to []. Production poster/API/
Admin/CSRF and 12 browser groups passed. Existing build PATH, plan, branch, autoDeploy=no
and database expiry below are unchanged; old releases are historical evidence.

Current stage delivery (7 October 2026): application release **06f98e2** passed [current frontend/backend CI](https://github.com/1uxury/psych-talk-hub/actions/runs/37552097967) and is **Live** on the existing Free Render service. Clean local lint/30 frontend/build/checks and **315 PostgreSQL backend tests (43.307 s)** passed, as did nine time/layout/keyboard groups, eleven production HTTP/Admin checks and seven fresh anonymous browser groups. Nonempty redeployment preserved every public field; explicitly authorized private backup/isolated restore matched all business/admin/migration fields. See [README](../README.md), [delivery](../DELIVERY.md) and [backup procedure](../backend/BACKUP.md). Management video and the full production management matrix remain pending; this is a stage delivery, not full MVP acceptance. Last explicit user acceptance is step 31; latest instruction authorizes finishing work. Earlier statuses below are historical.

Checked: 5 October 2026 (Europe/London). **The first Free Render deployment is
Live; migrations, real Gunicorn startup and online HTTP/browser checks passed.
Step 17 was user-confirmed on 5 October 2026.** The user separately authorised creating
both Free resources in Frankfurt. Deployment uses d8bdd2923304475f05281d5d56a71018eb43cf4f,
verified by [Project checks 37242897644](https://github.com/1uxury/psych-talk-hub/actions/runs/37242897644).
The final build command below removes temporary diagnostic output; its second
deployment is also Live and the online checks passed again. Separate authorised
TLS initialization created two example talks, six resources/links and a private
administrator. Nonempty browser and actual Admin publication/restoration checks
passed; nonempty redeploy preservation, backup/restore and full MVP acceptance
remain pending. Step 18 has not started. Any later release SHA needs its own successful CI.

User-authorised local checks passed frontend lint/30 tests/build, all 135 backend
tests, dependency/system/migration checks, collectstatic and 20 browser scenarios.
DEBUG=False checks used a local development database; Admin publication used a
disposable test database. Test-only services were closed afterwards. This does
not alone verify production. Separate Render logs now show migrations preceding
Gunicorn 26.2.0/worker startup; 11 online HTTP and six isolated browser checks
passed against the public URL without business writes. See
[progress.md](../memory-bank/progress.md) for evidence and pending work.

## Implemented asset and startup path

- `frontend/vite.config.js` uses `/` for development and `/static/frontend/` for
  builds. React routing and relative `/api/` requests remain rooted at `/`.
- `frontend/dist/index.html` is the generated Django template, using a configured
  template directory rather than copying or maintaining a second HTML source.
  Only `dist/assets/` is collected under `frontend/assets/`; the entry is not a
  static file. Future public-directory assets need explicit integration.
- Django serves the entry on `/` and numeric `/events/{id}`, with GET/HEAD and
  no-store caching. A missing entry returns a safe 503. Event existence remains
  an API/React responsibility: the page shell may return 200 for a missing ID,
  while `/api/events/{id}/` returns JSON 404. Unknown server page routes return
  normal Django 404; there is no general SPA fallback or trailing-slash alias.
- WhiteNoise follows SecurityMiddleware and serves collected React/Admin assets
  from `backend/staticfiles/`, including with DEBUG=False. Its compressed storage
  preserves Vite's hashed filenames; no second manifest hash, Brotli dependency,
  CDN or Node application server is added.
- `backend/scripts/deploy.py build` validates Python/Node/npm pins, installs locked
  dependencies, builds, checks the entry's asset references, checks Django and
  collects static files. It performs no migrations or data/account initialization.
- `backend/scripts/deploy.py start` requires explicit production mode and Linux,
  checks build/collected assets and configuration, runs migrations, then replaces
  itself with one Gunicorn WSGI worker bound to PORT. A failed prerequisite or
  migration prevents Gunicorn startup. No seeding or administrator creation occurs.

## Checked platform feasibility

| Requirement | Official documentation checked | Actual evidence |
| --- | --- | --- |
| Python 3.13.16 | [Explicit Python versions](https://render.com/docs/python-version) | Exact version compiled and accepted by deployment checks |
| Node 24.14.0 / npm 11.9.0 | [Node pins](https://render.com/docs/node-version), [native runtimes](https://render.com/docs/native-runtimes) | Python subprocess versions verified after the PATH repair below; Vite build passed |
| PostgreSQL 17 | [Creating Postgres](https://render.com/docs/postgresql-creating-connecting) | API reports Free/17/available; migrations and live database health passed |
| Free startup migration | [Deploy stages](https://render.com/docs/deploys#pre-deploy-command): pre-deploy commands require paid services | Actual migration logs before Gunicorn/worker startup |
| Free limitations | [Free plans](https://render.com/docs/free) | Both resources confirmed Free; actual creation/expiry recorded below; usage still requires ongoing review |

Documentation establishes platform constraints; actual API/logs/checks establish
this deployment's state. Do not copy the official Django tutorial's paid Shell, four workers,
alternative database driver, ASGI server or build-time migrations into this MVP.

## Settings for the authorised free service

Use authorised Free resources in the same region. On 5 October the user explicitly
approved creating these two resources, replacing the earlier existing-resource
blocker. Future resource creation needs its own authorised scope. If Free is
unavailable, keep the blocker; do not create paid resources, change database
major/platform or add a payment method automatically.
Repository root directory must be blank so both backend and frontend are present.

| Render setting | Required value |
| --- | --- |
| Runtime | Python 3 |
| Repository / branch | `1uxury/psych-talk-hub` / `docs/clarify-implementation-plan`; release SHA recorded below |
| Instance / scale | Free; one instance |
| Auto-deploy | Off; manually deploy the precise commit after its CI passes |
| Build command | Copy the Bash command below into Render only |
| Start command | `python backend/scripts/deploy.py start` |
| Pre-deploy command | Empty |
| Health check | `/healthz/` |
| PYTHON_VERSION / NODE_VERSION | `3.13.16` / `24.14.0` |
| DJANGO_ENV / DEBUG | `production` / `False` |
| SECRET_KEY | Private strong random value, at least 50 characters |
| DATABASE_URL | Private same-region database connection, requiring TLS with `sslmode=require` or stronger |
| ALLOWED_HOSTS | Exact actual service hostname, no wildcard or URL scheme |

Render **Build Command** (repository root; not a local PowerShell command):

```bash
npm install --global npm@11.9.0 && export PATH="$(dirname "$(node -p process.execPath | tail -n 1)"):$(npm config get prefix | tail -n 1)/bin:$PATH" && python backend/scripts/deploy.py build
```

The initial shorter command failed strict runtime checks: Render's shell used
the requested versions, while Python subprocesses found system Node 24.21.0/npm
11.19.0 in `/usr/bin`. Prepending the real Node directory and npm prefix fixes
subprocess discovery. Verified subprocesses then used Node 24.14.0/npm 11.9.0
under `/opt/render/project/nodes/node-24.14.0/bin`. Keep the exact checks; do not
accept default versions or hard-code that platform directory into application code.

The npm version installation is confined to Render's disposable build runtime;
do not execute that command to change the user's global local npm. Existing
`django-environ`, Psycopg, Gunicorn and WhiteNoise locks remain unchanged.
Render supplies PORT; the script defaults to 10000 and validates its range.
Production reads process variables only. HTTPS proxy handling, secure session/CSRF
cookies and the HTTP health-probe exemption reuse the step 04 configuration.

## Initialization completed; remaining release checks

On 5 October 2026, the user authorised separate production initialization and
explicitly permitted querying the local public IP. A temporary IPv4 /32 rule
enabled the controlled external TLS connection; database identity, PostgreSQL
17.11, TLS and zero pending migrations were verified. The existing seed function
and private administrator creation ran in a transaction: two fictional talks,
six resources and six links. Repeated import created zero records and preserved
all existing fields. External rules were restored to [] and independently checked;
the service continues to use its internal database connection. No production test
runner, startup seeding, public initialization endpoint or paid Shell was used.

Private administrator credentials are in the ignored local file
`.tools/production-admin.private.json` at the repository root; open it locally to
obtain the generated password for [Admin](https://psych-talk-hub.onrender.com/admin/).
Do not publish that file, copy secrets to documentation or show them in a video.
Future controlled operations must protect external connection credentials and
preserve separate development configuration; never test with production settings.

Before initialization, verified: real empty Home, direct missing-event shell/refresh/Back, Admin
login form/static files/secure CSRF cookie, HTTPS database health, JS/CSS types,
JSON 404/406, rejected POST, HEAD/OPTIONS, unknown page 404 and migration-before-
Gunicorn order. Screenshots confirm 1280/375 px and Admin styling; no uncaught JS
exceptions or Vite requests. The production list is genuinely empty, not mocked.
Those empty-state checks describe the earlier release, not current content.
The API client requests JSON: a valid API endpoint with unsupported text/html
Accept returns 406 before object lookup, while unknown API routes remain JSON 404.

After initialization, ten actual browser checks passed: nonempty Home grouping,
desktop/mobile layout, both direct details and fresh reloads, ordered readings,
safe original links/new tab, Back navigation, actual production assets and zero
uncaught app JavaScript exceptions. Real HTTPS Admin login rejected a missing-CSRF
save with 403, accepted a valid save and exposed the result to anonymous API and
browser refresh. The original recommendation was restored, identities/orders
verified unchanged and check login sessions logged out. The actual administrator
session cookie's Secure, HttpOnly and SameSite=Lax flags were also verified, and
that check session logged out. The isolated browser was
closed; no application code or deployment changed.

All six original-link targets match the seeded bibliography. DOI URLs resolve to
the expected publishers; automated HTTP reads returned 200 for Nature/PLOS/WHO
and 403 for Physiology/SAGE/NIH. NIH new-tab navigation was verified; that does
not establish full-text access. Do not bypass publisher restrictions or treat
an automated 403 as an application failure.

Still verify: nonempty business data preservation on redeploy, backup/restore and
remaining full MVP acceptance. Earlier empty-database redeployment checks do not
prove nonempty business-data preservation. Step 17 is user-confirmed.
Only additive migrations compatible with the still-running previous release belong
in initial deployments; reverting code does not mean reversing data migrations.

## Free limits and historical step 17 operational record

As checked on 4 October: web services sleep after 15 idle minutes, with cold starts;
each workspace has 750 free instance hours per month and limited build/bandwidth
allowances. One free Postgres database per workspace has 1 GB storage, expires
30 days after creation and provides no managed backups. After expiration it is
inaccessible; the paid-upgrade grace period is not a free extension.
Review account usage/spending settings before any deployment and retain the
zero-paid-services constraint. Do not assume Free prevents every usage charge.

| Deployment record | Current value |
| --- | --- |
| Web Service / region / URL | psych-talk-hub / srv-db1e5ak9v7es73f565d0 / Free / Frankfurt / [public URL](https://psych-talk-hub.onrender.com) |
| PostgreSQL instance / major / region | psych-talk-hub-db / dpg-db1e4g7avr4c73bfs90g-a / Free / 17 / Frankfurt / available |
| Database created / expires | UTC 2026-10-04 23:33:20 (London 5 October 00:33:20 BST) / UTC and London 2026-11-03 23:33:20 GMT |
| Release SHA / CI | d8bdd2923304475f05281d5d56a71018eb43cf4f / frontend and backend success (run 37242897644); code implementation a174723 also passed run 37242589180 |
| First Live deployment | dep-db1ed66gekts73dehfsg / UTC 2026-10-04 23:56:43 / London 5 October 00:56:43 BST |
| Final-command revalidation | dep-db1egmdg1s2s739qisag / Live / UTC 2026-10-05 00:04:05 / London 01:04:05 BST; same SHA, no migrations remaining, Gunicorn started, 11 HTTP + six browser checks passed again |
| Initialization / remote acceptance | Completed UTC 2026-10-05 11:51:55 / London 12:51:55 BST; two example talks, six resources/links, private admin; repeat import preserved fields; ten nonempty browser checks + real Admin CSRF/save/anonymous refresh/restoration passed; full MVP acceptance pending |
| Backup / restore | Pending; manually export before expiry, store outside Git, verify restore in an isolated disposable local PostgreSQL 17 database |

Never invent creation/expiry dates. An expired database requires controlled
recovery; do not silently upgrade it. The three-day reviewable milestone and full
MVP/online acceptance remain separate. Later steps 35–38 refine and verify this
same integration; step 18 search has not started.

[Local step 17 validation](README.md#step-17-validation--run-by-the-user) ·
[Architecture](../memory-bank/architecture.md) ·
[Technology stack](../memory-bank/tech-stack.md)

## Current release — 7 October 2026

| Item | Verified current value |
| --- | --- |
| Application commit / exact CI | 06f98e21e0d8ac3eb269d0bacc016c1c657ee0d7 / [37552097967](https://github.com/1uxury/psych-talk-hub/actions/runs/37552097967), both jobs/all steps success |
| Live deploy | dep-db2p5kk9v7es739oncig / UTC 2026-10-07 00:32:40 / London 01:32:40 BST |
| Service/database | Existing Free Frankfurt Web + PG17; autoDeploy=no, external IP rules=[]; no new resources |
| Startup | Actual app logs: migrations finished before one Gunicorn worker; access format method/status/duration |
| Data preservation | All fields/IDs/dates/recommendations/orders of 2 events and 6 links unchanged across redeploy |
| Backup/restore | Private custom dump outside Git; disposable local PG17 restore matched all business/admin/migration fields; test database destroyed; [procedure](BACKUP.md) |
| Current online checks | 11 HTTP/Admin groups and 7 fresh anonymous browser groups; real Crossref new preview cancelled, repeat existing link preserved; all public fields unchanged, admin session logged out |
| Remaining | Full online management matrix and management video; do not claim full MVP |

[Render Free limits](https://render.com/docs/free) were checked on 7 October;
the actual existing resources and expiry were separately confirmed by API.
Database expires **3 November 2026 at 23:33 GMT**. No fresh cold-start timing was
measured in this release; earlier cold-start/platform limits remain documented.
The existing build PATH repair above is unchanged. Later documentation commits
record evidence; production application remains the exact verified release above.
