# Free Render deployment — step 17 handoff

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

## Free limits and operational record

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
| Backup / restore | Pending; manually export before expiry, store outside Git, verify restore into a separately provisioned free database |

Never invent creation/expiry dates. An expired database requires controlled
recovery; do not silently upgrade it. The three-day reviewable milestone and full
MVP/online acceptance remain separate. Later steps 35–38 refine and verify this
same integration; step 18 search has not started.

[Local step 17 validation](README.md#step-17-validation--run-by-the-user) ·
[Architecture](../memory-bank/architecture.md) ·
[Technology stack](../memory-bank/tech-stack.md)
