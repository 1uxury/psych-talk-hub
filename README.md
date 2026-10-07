# PsychTalk Hub

English public talk pages with curated reading lists, title search and a private
Django Admin DOI import workflow. One Django application, two React pages and
PostgreSQL; no public write API.

- [GitHub](https://github.com/1uxury/psych-talk-hub)
- [Public Demo](https://psych-talk-hub.onrender.com)
- [Delivery status and demonstration checklist](DELIVERY.md)
- [Backend checks and Admin acceptance](backend/README.md)
- [Frontend checks and browser acceptance](frontend/README.md)
- [Deployment, free-plan limits and expiry](backend/DEPLOYMENT.md)
- [Private backup/isolated restore procedure](backend/BACKUP.md)
- [Product design](memory-bank/design-document.md) / [中文设计](memory-bank/design-document.zh-CN.md)
- [Technical/API contract](memory-bank/tech-stack.md), [architecture](memory-bank/architecture.md), [progress](memory-bank/progress.md)

## Local setup

Use the pinned Python **3.13.16**, Node **24.14.0**, npm **11.9.0**, and PostgreSQL
**17**. Windows commands below use PowerShell. Preserve existing installations;
this workspace's independent PostgreSQL 17 runs on **127.0.0.1:5433**. Never
operate an unrelated PostgreSQL 11 instance on 5432. Fresh clones must provide
their own development database and an application role allowed to create test
databases; ignored local tools and credentials are not shipped.

From the repository root, using the selected Python 3.13 executable:

```powershell
python -m venv backend/.venv
backend/.venv/Scripts/python.exe -m pip install -r backend/requirements.txt
Copy-Item backend/.env.example backend/.env
Copy-Item backend/.env.example backend/.env.test
```

Privately fill both files with a strong random SECRET_KEY of at least 50 characters and a PostgreSQL DATABASE_URL
for the **local development** database. Set TEST_DATABASE_NAME to a separate
`test_` name such as `test_psychtalk`. Do not use production credentials or
commit filled files. Development reads `.env`; test reads `.env.test`;
production reads process variables only and requires TLS and explicit hosts.

```powershell
Set-Location frontend
npm.cmd ci --no-audit --no-fund
npm.cmd run build
Set-Location ../backend
$env:DJANGO_ENV = 'development'
.venv/Scripts/python.exe manage.py migrate --noinput
.venv/Scripts/python.exe manage.py seed_demo
.venv/Scripts/python.exe manage.py createsuperuser
.venv/Scripts/python.exe manage.py runserver
```

`seed_demo` explicitly creates missing example records and links. Repeat runs
preserve edits and existing dates. It never runs at startup or deployment.
Keep administrator credentials private. Open `http://127.0.0.1:8000/admin/`.
For frontend development, run `npm.cmd run dev` in a second terminal inside
frontend and open `http://localhost:5173/`; Vite proxies `/api/` to Django.
For the built public pages and DEBUG=False static checks, follow the backend
guide's isolated development walkthrough.

## Reproduce checks

Build the frontend before backend tests: real-bundle checks reject missing
output. With the isolated local PostgreSQL 17 running:

```powershell
Set-Location frontend
npm.cmd run lint
npm.cmd test
npm.cmd run build
Set-Location ../backend
$env:DJANGO_ENV = 'test'
.venv/Scripts/python.exe -m pip check
.venv/Scripts/python.exe manage.py check --database default
.venv/Scripts/python.exe manage.py makemigrations --check --dry-run
.venv/Scripts/python.exe manage.py collectstatic --noinput
.venv/Scripts/python.exe manage.py test --noinput
```

Expected: **30 frontend tests**, **315 backend tests**, no missing migrations.
The test runner creates and destroys a separate database. CI uses PostgreSQL
17.11 and mocked Crossref, transfers the actual frontend build to the backend
job, and runs these checks on pushes and pull requests. A separate local real
Crossref/Admin/browser integration check is recorded in progress.md.

## Public contract and management

`GET /api/events/` lists talks; `GET /api/events/{id}/` includes shared bibliography
flattened with ordered association fields. Only GET/HEAD/OPTIONS are allowed.
Unknown API routes return JSON errors; public page routes are `/` and numeric
`/events/{id}`. `/healthz/` checks database connectivity without Crossref.
Dates display in Europe/London; a page snapshots one instant for Upcoming/Past.
Search filters the loaded talk's reading titles without additional requests.

In Admin, open an Event then **Import reading by DOI**. Fetching and checking
details do not publish a reading. A preview has a fixed 15-minute lifetime,
independent per-tab identity and explicit confirmation. Existing DOI metadata
is read-only and reused; repeat confirmation preserves the original association.
New resources and links save atomically with PostgreSQL concurrency protection.
Manual records remain independent. Shared resource edits affect every linked
talk; recommendations/order belong to each link. Removing a link or deleting a
talk preserves resources. Resource deletion is blocked, including superusers.
All management uses model permissions and CSRF.

## Deployment and delivery limits

The existing Frankfurt Free Render Web Service and PostgreSQL 17 are the only
production resources. Manual deployment requires successful CI for the exact
commit; migrations finish before one Gunicorn worker starts. No auto-seeding
or account creation occurs. Preserve the build PATH repair in DEPLOYMENT.md.
Free service cold starts and database expiry are documented there. Original
publisher links may require subscriptions. A stage delivery does not claim
full MVP acceptance while online checks or the management video remain pending.
