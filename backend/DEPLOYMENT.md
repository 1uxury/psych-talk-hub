# Free Render deployment — step 17 handoff

Checked: 4 October 2026. **Local checks passed; user confirmation is pending. Remote
deployment is externally blocked and unverified.** This session has no callable
Render account connector, supplied existing service/database identifiers or
production configuration. No account login was inspected, and no claim is made
about whether the user personally has a Render account. No service was created,
modified or deployed. Steps 09–17 were committed/pushed as a174723 on 5 October
2026 (London); both frontend/backend jobs passed in
[Project checks 37242589180](https://github.com/1uxury/psych-talk-hub/actions/runs/37242589180).
This implementation SHA is now CI-verified; any later release SHA requires its
own successful checks before deployment.

User-authorised local checks passed frontend lint/30 tests/build, all 135 backend
tests, dependency/system/migration checks, collectstatic and 20 browser scenarios.
DEBUG=False checks used a local development database; Admin publication used a
disposable test database. Test-only services were closed afterwards. This does
not verify Render, production TLS or actual Linux Gunicorn startup;
startup sequencing is covered by mocked tests. See
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

| Requirement | Official documentation checked | Remaining evidence |
| --- | --- | --- |
| Python 3.13.16 | [Explicit Python versions](https://render.com/docs/python-version) | Actual service build and interpreter version |
| Node 24.14.0 / npm 11.9.0 | [Node pins](https://render.com/docs/node-version), [native runtimes](https://render.com/docs/native-runtimes) | Node/npm availability in this Python service; build refuses a mismatch |
| PostgreSQL 17 | [Creating Postgres](https://render.com/docs/postgresql-creating-connecting) lists new-instance majors 13–18 | Existing free workspace capacity, actual major and connection |
| Free startup migration | [Deploy stages](https://render.com/docs/deploys#pre-deploy-command): pre-deploy commands require paid services | Linux startup and real migration logs |
| Free limitations | [Free plans](https://render.com/docs/free) | Account-specific usage, dates and capacity |

The docs support the proposed path; they do not prove account access or a working
deployment. Do not copy the official Django tutorial's paid Shell, four workers,
alternative database driver, ASGI server or build-time migrations into this MVP.

## Settings for an existing authorised free service

Use only an existing, authorised free Web Service and a free PostgreSQL 17
database in the same region. If unavailable, keep the blocker; do not create paid
resources, change database major/platform or add a payment method automatically.
Repository root directory must be blank so both backend and frontend are present.

| Render setting | Required value |
| --- | --- |
| Runtime | Python 3 |
| Repository / branch | This repository and the explicitly verified release branch/commit |
| Instance / scale | Free; one instance |
| Auto-deploy | Off; manually deploy the precise commit after its CI passes |
| Build command | `npm install --global npm@11.9.0 && python backend/scripts/deploy.py build` |
| Start command | `python backend/scripts/deploy.py start` |
| Pre-deploy command | Empty |
| Health check | `/healthz/` |
| PYTHON_VERSION / NODE_VERSION | `3.13.16` / `24.14.0` |
| DJANGO_ENV / DEBUG | `production` / `False` |
| SECRET_KEY | Private strong random value, at least 50 characters |
| DATABASE_URL | Private same-region database connection, requiring TLS with `sslmode=require` or stronger |
| ALLOWED_HOSTS | Exact actual service hostname, no wildcard or URL scheme |

The npm version installation is confined to Render's disposable build runtime;
do not execute that command to change the user's global local npm. Existing
`django-environ`, Psycopg, Gunicorn and WhiteNoise locks remain unchanged.
Render supplies PORT; the script defaults to 10000 and validates its range.
Production reads process variables only. HTTPS proxy handling, secure session/CSRF
cookies and the HTTP health-probe exemption reuse the step 04 configuration.

## Initialization and release checks still pending

After an authorised deployment, separately use a controlled local TLS connection
to the production database to initialize example data and a private administrator.
Use the external database connection for local access, protect credentials from
terminal history/output, then restore development configuration. Never invoke the
test suite with production settings. There is no public initialization endpoint,
automatic seed, automatic admin account, paid Shell or one-off job dependency.
This handoff does not execute or claim that initialization.

Verify anonymous Home/detail/direct refresh/original links, Admin login/static
files/CSRF, `/healthz/`, JSON API errors, startup migration order and data preservation
on redeploy. Record the actual URL, release SHA and logs only after verification.
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
| Web Service / region / URL | Not connected or verified |
| PostgreSQL instance / major / region | Not connected or verified |
| Database created / expires | Unknown until actual existing database is inspected |
| Implementation SHA / CI / Render build | a174723 / frontend and backend success (run 37242589180) / Render build not performed |
| Initialization / remote acceptance | Not performed |
| Backup / restore | Pending; manually export before expiry, store outside Git, verify restore into a separately provisioned free database |

Never invent creation/expiry dates. An expired database requires controlled
recovery; do not silently upgrade it. The three-day reviewable milestone and full
MVP/online acceptance remain separate. Later steps 35–38 refine and verify this
same integration; step 18 search has not started.

[Local step 17 validation](README.md#step-17-validation--run-by-the-user) ·
[Architecture](../memory-bank/architecture.md) ·
[Technology stack](../memory-bank/tech-stack.md)
