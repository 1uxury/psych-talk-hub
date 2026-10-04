# PsychTalk Hub backend

## Current handoff: step 17 local checks passed, awaiting user confirmation

Last user-accepted step is 16. Step 17 adds the built React template, declared
page routes, WhiteNoise/static collection and a fail-closed Linux deployment
entry. At the user's request the assistant passed frontend lint, all 30 frontend
tests and build; pip/Django/migration checks; all 135 backend tests; collectstatic;
and 20 browser scenarios. Five browser checks use a disposable database for real
Admin login, rejected missing-CSRF submission, save and anonymous publication.
Test databases were destroyed; development data was read-only. Test-only browser
and server processes were closed, and project PostgreSQL 17 restored to its prior
stopped state. Those checks made no schema/dependency changes or installations.
On 5 October 2026 (London), the user authorised commit/push/CI verification:
implementation commit a174723 was pushed and both Linux CI jobs passed.
No remote deployment occurred. Step 17 awaits user confirmation; step 18 has not started.
Older sections retain their historical counts/evidence; current results are in
[progress.md](../memory-bank/progress.md).

Remote deployment is blocked: this session has no callable Render account
connection or supplied authorised existing free service/database. Current
implementation a174723 has successful frontend/backend CI in
[Project checks 37242589180](https://github.com/1uxury/psych-talk-hub/actions/runs/37242589180).
All workflow steps passed, including frontend tests/build/artifact transfer and
backend checks/migrations/static collection/tests. Actual Gunicorn/Render startup
remains unverified. See [deployment handoff](DEPLOYMENT.md).

### Historical step handoffs

Steps 01–08 have **user-confirmed local acceptance**. Basic backend GitHub CI passed
on 4 October 2026 for commit 66b4140; see the CI section for remote evidence.
Step 05 adds Event, an initial migration and nine tests, accepted locally by the user.
Step 06 adds Resource, migration 0002_resource and 14 tests, accepted locally by the user.
Step 07 adds EventResource, migration 0003_event_resource and 13 tests, accepted locally by the user.
Step 08 adds basic Admin management and 21 tests (69 total), accepted locally by the user.
Step 09 adds an explicit, offline demo importer and 13 tests (82 total), accepted
locally by the user. Step 10 implements the anonymous JSON event list and adds
eight tests (90 total), accepted locally by the user. Step 11 adds the detail API,
flat reading output and safe API JSON errors, with 14 new tests (104 total),
**accepted locally by the user**. Step 12 adds 12 public-method tests (116 total),
**accepted locally by the user**, reusing the existing read-only views.
Step 13 prepares the JavaScript React scaffold, local proxy, JSDoc API types and
frontend CI; **accepted locally by the user** on 4 October 2026. Full visitor pages
were then pending; DOI import and deployment remain unimplemented. See
[frontend validation](../frontend/README.md) for the current page status.
Step 14 implements shared frontend request states, cancellation/retry and routing.
At the user's request the assistant ran lint, all 18 Node request tests, build and
14 isolated browser scenarios: **all passed locally; the user then confirmed acceptance**
on 4 October 2026.
Backend runtime/schema/migrations/dependencies are unchanged; the 116 backend
tests were not rerun. Step 15 implements Home groups/cards, London dates and
ten additional frontend tests (28 total); the user confirmed local acceptance
after the GMT/BST fix/recheck instructions on 4 October 2026. No backend
changes or checks were made for this step; at that handoff step 16 had not started.
The user subsequently authorised assistant checks: frontend lint, all 28 tests,
build and 19 isolated browser scenarios passed. Desktop columns work with
multiple cards per group; the real groups currently have one card each.
No backend regression, business write or remote deployment was performed.
The user subsequently requested step 16. It now implements full event information,
ordered single-column reading cards, missing metadata and empty-reading states,
and accessible new-tab original links. The frontend defines 30 tests; the assistant
has not run this version's lint/tests/build/browser checks. **The user confirmed
step 16 local acceptance on 4 October 2026; step 17 has not started.** No individual
outputs were supplied. Backend runtime/schema/dependencies and the 116 backend
test methods are unchanged and were not rerun. Progress records last accepted
step 16; the confirmation handoff only updates documentation.
The stage implementation was committed and pushed to docs/clarify-implementation-plan.
The numbered handoff sections retain their historical validation status; the CI
section below records the later remote verification.
That successful CI covers the pushed steps 01–08 version, not the uncommitted
steps 09–16 changes. Follow frontend/README.md for the current step 16 checklist.
Historical step sections retain their original status.

## Runtime and dependencies

Use CPython **3.13.16**, recorded in the root .python-version. The independent
interpreter is in .tools/python313/ and the isolated environment in backend/.venv/.
Existing Anaconda/Python, PATH and launcher settings were preserved. Ignored local
tools are not distributed through Git.

On another workstation, independently install Python 3.13 and create the virtual
environment. Install requirements.txt with its interpreter; requirements.in is
the update source. Direct and transitive versions are locked. Gunicorn installs
only on Linux; Windows uses runserver. tzdata supports London time on both.
Locked Linux dependency installation passed in CI. Production server startup and
deployment remain unverified.

## Independent PostgreSQL

The existing **PostgreSQL 11 service on port 5432** was preserved. Independent
**PostgreSQL 17.11** binaries/data are in .tools/postgres17/, listening only on
**127.0.0.1:5433**. It is not a Windows service and does not automatically restart
after a reboot. Local logs and administrator connection information stay inside
that ignored directory; never share them.

The application role psychtalk_dev is not a superuser and cannot create roles.
It can create test databases on this isolated instance. The development database
is psych_talk_dev; Django creates/destroys test_psychtalk during tests. Production
uses a separately supplied remote database and role.

From backend/, control only this project-local instance:

~~~powershell
.\.venv\Scripts\python.exe scripts/local_database.py status
.\.venv\Scripts\python.exe scripts/local_database.py start
.\.venv\Scripts\python.exe scripts/local_database.py stop
~~~

Run start only when stopped. If another Windows account started the process, that
account may be needed to stop it. Do not stop the existing PostgreSQL 11 service.

For a fresh Windows clone, download the 17.x Windows x64 archive through the
[official PostgreSQL Windows page](https://www.postgresql.org/download/windows/)
and [EDB binaries](https://www.enterprisedb.com/download-postgresql-binaries).
Extract so .tools/postgres17/pgsql/bin/initdb.exe exists, then run
scripts/local_database.py init once with the virtual-environment interpreter.
It refuses existing data/environment files, checks port 5433 before initialising,
uses SCRAM, generates random credentials and creates the development database
and private environment files. It does not change PATH or register a service.
If initialisation fails halfway, retain the files/logs for recovery instead of
repeatedly initialising or deleting the directory.

On Linux, independently provision PostgreSQL 17 with a local development
role/database and test-database creation permission, then fill the environment
files below. The helper is Windows-only, not a production deployment tool.

## Configuration

config/environment.py uses django-environ. Process variables override local files.
Choose DJANGO_ENV in the **process environment**, not inside an environment file.

| Mode | File read | Behaviour |
| --- | --- | --- |
| development (default) | backend/.env | Local PostgreSQL, persistent explicit secret; DEBUG defaults to true |
| test | backend/.env.test | Local connection, separate test DB; DEBUG always false |
| production | None | Explicit secret, DB URL, hosts and TLS required; DEBUG must be false |

.env.example deliberately leaves required credentials blank. This workstation
already has ignored .env and .env.test files with random persistent keys and the
local database URL. Never print or commit them. The test connection initially
points to the development database so Django can create TEST_DATABASE_NAME;
test cases then run against the separate test database. Its name must begin with
test_ and differ from the development database. Local modes reject remote hosts;
the test runner refuses production mode before database setup. There is no
SQLite or generated-secret fallback.

Production requires a strong SECRET_KEY of at least 50 characters, an explicit
PostgreSQL DATABASE_URL with sslmode=require, verify-ca or verify-full, and
specific ALLOWED_HOSTS without wildcards. DEBUG=True is rejected. Secure
session/CSRF cookies and HTTPS redirection are enabled. The forwarded-protocol
header is trusted for the planned Render proxy; /healthz/ allows its HTTP probe.
Step 17 now implements static integration, awaiting user checks below; actual
production HTTPS, Cookie behaviour and remote deployment remain unverified.

## Implemented infrastructure

The 18 built-in migrations for Admin/auth/content types/database sessions were
applied to psych_talk_dev. Step 05 adds events/migrations/0001_initial.py;
the assistant generated it but did not apply it or run acceptance tests.
The user subsequently confirmed step 05 acceptance without individual command logs.
Step 06 adds events/migrations/0002_resource.py; the assistant only generated it,
without applying it or running acceptance tests. The user subsequently confirmed
step 06 acceptance without individual outputs. Step 07 adds 0003_event_resource;
the assistant generated it but did not apply it or run acceptance checks/tests.
The user subsequently confirmed step 07 acceptance without individual outputs.
No Django administrator account was created.

GET /healthz/ queries PostgreSQL with SELECT 1 and returns JSON 200 with
{"status":"ok"}, or safe JSON 503 with {"detail":"Service unavailable."}.
It never calls Crossref, prevents caching and supports HEAD without a body.
Other methods return JSON 405. Database connection establishment times out after
three seconds. The user confirmed step 04 acceptance; no individual test outputs
or separate browser-check logs were supplied. This does not establish successful
administrator authentication or online deployment.

The root .github/workflows/backend.yml configures PostgreSQL 17.11 and the pinned
Python on Linux. Push/PR checks install the lock, check dependencies and Django,
apply migrations, check missing migrations and run isolated database tests.
Credentials there are disposable CI-only values. On 4 October 2026, commit
66b41404f0d3e6aa91c0b6209faf768bb99f86ee was pushed to the feature branch.
[Backend checks #37208404049](https://github.com/1uxury/psych-talk-hub/actions/runs/37208404049)
completed successfully. GitHub API results confirm successful Linux dependency
installation, dependency consistency, Django checks, migrations, missing-migration
checks and isolated PostgreSQL tests. The repository defines 69 test methods;
individual test logs were not read. This is separate from user-confirmed local
acceptance and does not establish production deployment or full MVP acceptance.

## Step 04 validation — run by the user

The user replied “通过” after receiving these instructions. They are retained for
reproduction; no individual results or logs were supplied. Use PowerShell in
G:\STUDY\psych-talk-hub\backend. The assistant installed and
initialised PostgreSQL and applied base migrations, but **did not run this suite
or browser acceptance checks**. Step 05 was subsequently implemented on your
instruction; its separate acceptance is recorded below.

Check the preserved old service, new runtime and dependencies:

~~~powershell
Get-Service postgresql-x64-11
..\.tools\postgres17\pgsql\bin\postgres.exe --version
.\.venv\Scripts\python.exe scripts/local_database.py status
.\.venv\Scripts\python.exe -m pip check
~~~

Expected: the old service still runs, PostgreSQL reports 17.11, the local server
runs from .tools/postgres17/data and no dependency conflicts exist.

Run checks with test configuration and restore your previous mode:

~~~powershell
$previousDjangoEnvironment = $env:DJANGO_ENV
try {
    $env:DJANGO_ENV = 'test'
    .\.venv\Scripts\python.exe manage.py check --database default
    .\.venv\Scripts\python.exe manage.py showmigrations
    .\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
    .\.venv\Scripts\python.exe manage.py test --noinput --verbosity 2
} finally {
    if ($null -eq $previousDjangoEnvironment) {
        Remove-Item Env:DJANGO_ENV -ErrorAction SilentlyContinue
    } else {
        $env:DJANGO_ENV = $previousDjangoEnvironment
    }
}
~~~

Inspect **each** result: PowerShell does not stop automatically on a native
program's nonzero exit. Expected: no system-check errors, all built-in migrations
marked [X], no missing migrations, and all **12 test methods** pass. Django creates
and destroys test_psychtalk; development data is untouched. A stale test database
causes --noinput to recreate only the explicitly named test database.

Tests cover real PostgreSQL 17 connectivity/isolation, session migrations,
safe simulated database failures, health methods/no external requests, the Admin
login/redirect/CSRF fields, invalid/production configuration, local-file precedence
and production-test refusal. Failure simulation does not stop either server.

For browser checks:

~~~powershell
$env:DJANGO_ENV = 'development'
.\.venv\Scripts\python.exe manage.py runserver
~~~

Open http://127.0.0.1:8000/admin/login/ (English form and usable styling),
http://127.0.0.1:8000/admin/ (redirect to login), and
http://127.0.0.1:8000/healthz/ (JSON status: ok). No administrator credentials are
needed to check the login page. Stop runserver with Ctrl+C afterward.

Inspect Git status from the repository root: filled environment files, database
data/logs, downloads and .venv must be absent. .env.example and the workflow must
be eligible for tracking. Review changed files for accidental real credentials.
The later authorised stage push and successful CI run are recorded above.

## Step 05: Event model — user-confirmed local acceptance

On 4 October 2026, the user replied “通过” after receiving the migration/check/test
instructions. This records local step acceptance without individual outputs;
the assistant did not run the acceptance suite. GitHub CI and Linux compatibility
remain unverified. The instructions below are retained for reproduction.

Step 05 introduced Event in events/models.py. Title (up to 255 characters) and an
aware starts_at are required. Description defaults to an empty string; topic
(100 characters) and speaker (255 characters) also default to empty strings.
is_example defaults to false. seed_key is an optional unique string of at most
100 characters; surrounding whitespace is removed and empty values become NULL.
Multiple ordinary events can therefore omit it.

Event.save calls full_clean before persistence, including when using
Event.objects.create. Empty/whitespace-only titles and naive datetimes fail with
field validation errors. Database NOT NULL, title/seed text checks and seed
uniqueness also protect writes that bypass model validation. Bulk writes do not
call save/full_clean: future import code must validate aware times and normalise
seed identifiers explicitly. PostgreSQL stores the instant; retrieved times use
UTC. London presentation remains later UI/Admin work. No end time, publishing
state or Admin model registration was added.

Run from G:\STUDY\psych-talk-hub\backend. Check local_database.py status first;
use start only if the project-local PostgreSQL 17 instance is stopped. Preserve
the old PostgreSQL 11 service. Apply the new migration to the development database,
then run checks and tests with the isolated test configuration:

~~~powershell
$previousDjangoEnvironment = $env:DJANGO_ENV
try {
    $env:DJANGO_ENV = 'development'
    .\.venv\Scripts\python.exe manage.py migrate --noinput
    if ($LASTEXITCODE -ne 0) { throw 'Development migration failed.' }
    .\.venv\Scripts\python.exe manage.py showmigrations events
    if ($LASTEXITCODE -ne 0) { throw 'Migration listing failed.' }

    $env:DJANGO_ENV = 'test'
    .\.venv\Scripts\python.exe manage.py check --database default
    if ($LASTEXITCODE -ne 0) { throw 'Django checks failed.' }
    .\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
    if ($LASTEXITCODE -ne 0) { throw 'A migration is missing.' }
    .\.venv\Scripts\python.exe manage.py test --noinput --verbosity 2
    if ($LASTEXITCODE -ne 0) { throw 'Backend tests failed.' }
} finally {
    if ($null -eq $previousDjangoEnvironment) {
        Remove-Item Env:DJANGO_ENV -ErrorAction SilentlyContinue
    } else {
        $env:DJANGO_ENV = $previousDjangoEnvironment
    }
}
~~~

Expected: events.0001_initial applies successfully and is marked [X], no system
errors or missing migrations, and all **21 test methods** pass (12 infrastructure
plus 9 Event tests). Without --keepdb, Django creates a fresh test_psychtalk and
applies all migrations before tests, verifying the initial migration on an empty
database. --noinput recreates a stale explicitly named test database; it does not
wipe development data. The development command above only adds the Event schema.

Event tests cover complete/minimal records, missing text/defaults, blank titles,
missing/naive start times, multiple empty seed identifiers, duplicate non-empty
identifiers at validation and database levels, database rejection of invalid
updates, and winter/summer London instants returning in UTC. Example labelling
on public pages will be verified once those pages exist; this step verifies the
default flag only. No external services are needed.

The assistant has not run these acceptance commands. Following the user's
confirmation, progress.md was opened and updated first, followed by architecture
insights and acceptance status. That handoff changed documentation only; step 06
was subsequently requested and its local acceptance is documented below.
No commit or push was made.

## Step 06: Resource model — user-confirmed local acceptance

On 4 October 2026, the user replied “通过” after receiving the migration/check/test
instructions. This records local acceptance without individual command outputs;
the assistant did not run the acceptance suite. GitHub CI and Linux compatibility
remain unverified. The instructions below are retained for reproduction.

Resource stores shared bibliography independently of talks. Title (up to 500
characters) and a valid HTTP(S) original_url (up to 2048 characters) are required.
Authors default to an empty display string; year defaults to NULL and accepts
integers 1–9999. Types are research_paper / article; sources are crossref / manual.
Ordinary manual entry defaults to article and manual; either type can be selected.

doi is optional and unique (up to 2048 characters). Normal saves trim and lowercase
bare identifiers, preserving suffix punctuation, and reject invalid DOI structure.
Empty DOI/seed_key values become NULL; non-empty seed_key (up to 100 characters)
is trimmed and unique. A DOI link must be parsed before model saving; the importer
that accepts doi.org links remains step 19. This model makes no external requests.
Manual records with identical titles or URLs remain separate. Existing records
can be selected by their integer ID in later Admin/association steps.

Resource.save calls full_clean, including for partial-field saves. PostgreSQL
constraints protect nonblank titles, year bounds, type/source choices, canonical
DOI, seed text and unique identifiers. URL field validation checks full HTTP(S)
syntax; its database check guards only the HTTP(S) prefix and whitespace.
Bulk_create/QuerySet.update bypass model validation and normalisation, so callers
must validate full URLs and normalise identifiers before using them.

The 14 new tests cover both types/sources, defaults, empty identifiers,
normalisation, invalid DOI/title/URL/year/choices, database uniqueness and checks,
independent manual records, editing bibliography without changing its source,
and migration application in the fresh isolated PostgreSQL database. A test-only
DRF serializer and JSON renderer verify empty authors and null year/DOI; the
public API serializer and event-specific fields are not implemented yet.
Existing 21 tests remain regression coverage, for **35 test methods** in total.

Run from G:\STUDY\psych-talk-hub\backend. Check local_database.py status first
and start the project-local instance only if stopped. Preserve PostgreSQL 11.
The assistant generated 0002_resource but has **not applied it or run tests**:

~~~powershell
$previousDjangoEnvironment = $env:DJANGO_ENV
try {
    $env:DJANGO_ENV = 'development'
    .\.venv\Scripts\python.exe manage.py migrate --noinput
    if ($LASTEXITCODE -ne 0) { throw 'Development migration failed.' }
    .\.venv\Scripts\python.exe manage.py showmigrations events
    if ($LASTEXITCODE -ne 0) { throw 'Migration listing failed.' }

    $env:DJANGO_ENV = 'test'
    .\.venv\Scripts\python.exe manage.py check --database default
    if ($LASTEXITCODE -ne 0) { throw 'Django checks failed.' }
    .\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
    if ($LASTEXITCODE -ne 0) { throw 'A migration is missing.' }
    .\.venv\Scripts\python.exe manage.py test --noinput --verbosity 2
    if ($LASTEXITCODE -ne 0) { throw 'Backend tests failed.' }
} finally {
    if ($null -eq $previousDjangoEnvironment) {
        Remove-Item Env:DJANGO_ENV -ErrorAction SilentlyContinue
    } else {
        $env:DJANGO_ENV = $previousDjangoEnvironment
    }
}
~~~

Expected: both events migrations marked [X], no system errors or missing migrations,
and **35 tests pass**. Django creates/destroys test_psychtalk and migrates it from
scratch; --noinput recreates a stale explicitly named test database. Development
migration adds the Resource table without resetting existing Event data.
No Crossref connection, administrator account or frontend is required.

Following user confirmation, progress.md was requested in the editor and updated
first, then architecture insights and acceptance status were recorded. This
handoff changed documentation only. Step 07 was subsequently requested;
its user-confirmed local acceptance is described below.
GitHub CI remains unverified; no commit or push was made.

## Step 07: EventResource model — user-confirmed local acceptance

On 4 October 2026, the user replied “通过” after receiving the complete
migration/check/test instructions. This records local acceptance without
individual outputs; the assistant did not run acceptance tests. GitHub CI and
Linux compatibility remain unverified. Instructions below remain for reproduction.

EventResource links a saved Event and Resource by integer foreign keys. Its own
integer ID identifies the association, independently of the resource ID.
recommendation is optional text, defaults to an empty string and rejects NULL.
display_order is a required signed IntegerField (PostgreSQL 32-bit integer),
defaults to zero and allows negative values. Default queries sort ascending by
display_order then association ID, including through each model's event_resources
reverse manager. Keep association queries for reading order; sorting Resource
records by their IDs would lose this per-event order.

Normal saves call full_clean, including partial-field saves. Database foreign
keys/NOT NULL and unique_event_resource protect bypassed validation too. The
same Resource can belong to multiple events; changing one link's recommendation
or order does not edit shared bibliography or another event's link. Duplicate
normal saves raise ValidationError; bypassed duplicate writes raise IntegrityError.
Converting duplicates into an existing-result response remains steps 22–23.

The Event foreign key uses CASCADE: Django ORM event deletion removes that event's
links while preserving all Resource records. The Resource foreign key uses
PROTECT to reject ORM deletion of a linked resource. This is not a blanket
deletion ban for unlinked resources. Admin deletion permissions, confirmation
screens and direct/bulk deletion denial remain step 08; no Admin changes were made.
Raw SQL deletion does not use Django's cascade/protection collector.

The 13 new tests cover round trips/defaults, independent recommendations/orders,
validation and database duplicate rejection, negative ordering, ties using link
IDs rather than resource IDs, edits, required fields/foreign keys, removing links,
single/queryset event deletion preserving resources, linked-resource protection,
and fresh PostgreSQL migration application. Earlier 35 tests remain regression
coverage, for **48 test methods** in total. These tests have not been run by the
assistant. No Crossref, administrator account or frontend is needed.

Run in PowerShell from G:\STUDY\psych-talk-hub\backend. Check the project-local
database status first; run start only if it is stopped. Preserve PostgreSQL 11.
The following applies the new schema to development, then validates in test mode:

~~~powershell
.\.venv\Scripts\python.exe scripts/local_database.py status
# If stopped, run: .\.venv\Scripts\python.exe scripts/local_database.py start

$previousDjangoEnvironment = $env:DJANGO_ENV
try {
    $env:DJANGO_ENV = 'development'
    .\.venv\Scripts\python.exe manage.py migrate --noinput
    if ($LASTEXITCODE -ne 0) { throw 'Development migration failed.' }
    .\.venv\Scripts\python.exe manage.py showmigrations events
    if ($LASTEXITCODE -ne 0) { throw 'Migration listing failed.' }

    $env:DJANGO_ENV = 'test'
    .\.venv\Scripts\python.exe manage.py check --database default
    if ($LASTEXITCODE -ne 0) { throw 'Django checks failed.' }
    .\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
    if ($LASTEXITCODE -ne 0) { throw 'A migration is missing.' }
    .\.venv\Scripts\python.exe manage.py test --noinput --verbosity 2
    if ($LASTEXITCODE -ne 0) { throw 'Backend tests failed.' }
} finally {
    if ($null -eq $previousDjangoEnvironment) {
        Remove-Item Env:DJANGO_ENV -ErrorAction SilentlyContinue
    } else {
        $env:DJANGO_ENV = $previousDjangoEnvironment
    }
}
~~~

Expected: events.0001_initial, 0002_resource and 0003_event_resource all marked [X],
no system-check errors, no missing migrations, and **48 tests pass**. Django
creates/destroys test_psychtalk and applies migrations from scratch; --noinput
recreates a stale explicitly named test database. The development migration only
adds the association table; it does not reset existing Event or Resource data.

Following user confirmation, progress.md was requested in the editor and updated
first, then architecture insights and acceptance status were recorded, followed
by README and AGENTS synchronisation. This handoff changes documentation only;
no tests, code or database operations were performed. Step 08 was subsequently
requested; its implementation and acceptance are recorded below. GitHub CI/Linux remain unverified, and no
commit or push was made.

## Step 08: Basic Admin management — user-confirmed local acceptance

On 4 October 2026, the user replied “通过” after receiving the full check/test
instructions. This records local acceptance of system checks, the missing-migration
check and 69 backend test methods, without individual outputs. The assistant did
not run acceptance tests. GitHub CI/Linux remain unverified; optional manual
browser checks and administrator creation have no separate evidence. Instructions
below remain for reproduction.

Event, Resource and EventResource are registered in Django Admin. Create/edit talks
through Events, add a manual resource through Resources, then choose the existing
talk/resource in Event resources. There is no inline editor or DOI import yet.
Manual creation requires a title and HTTP(S) original URL; authors/year are optional,
and either resource type is allowed. DOI/source are read-only; the source defaults
to manual. Seed identifiers are excluded. Bibliographic edits preserve source/DOI.
No title/URL merge is performed. Link edits change recommendation/order; event and
resource identity are read-only after creation.

The date/time field is labelled Europe/London and explicitly parses/displays that
zone even when another current timezone is active. Winter GMT and summer BST map
to the corresponding UTC instant; ambiguous/nonexistent daylight-saving times
produce field errors. Saved talks show `/events/{id}` in a message, an edit-page
link and View on site. Only the address is available now: the public page is still
unimplemented, so opening it currently returns 404.

Single/bulk event deletion uses Django's native confirmation, CSRF, permission
checks and cascade collector, with the design's exact confirmation copy. Both Event
and EventResource delete permissions are required even for a talk with no links.
Confirmed deletion retains all resources and other talks' links. Resource delete
buttons/actions are absent; direct GET/POST delete addresses return 403 even for
superusers and unlinked resources. Forged bulk actions have no effect, and direct
delete_model/delete_queryset hooks deny deletion. This Admin policy does not change
the ORM policy for unlinked resources outside Admin. Single link removal has the
specified confirmation; bulk link actions are disabled.

The 21 new test methods use real Admin requests and PostgreSQL, covering registration,
create/edit, messages/addresses, winter/summer UTC storage, timezone-independent
input/display, DST errors, manual metadata, independent duplicate-content records,
invalid fields, reuse/duplicate links, immutable link identities, shared edit source
preservation, anonymous/nonstaff/staff access, single/bulk confirmation and retention,
global Resource deletion denial, link removal and real CSRF enforcement. Fixture
users exist only in the isolated test database. The assistant has not run these
tests or any checks, changed development data, or created an administrator account.
No dependency or model/schema changes are needed for step 08.

Run this complete block in PowerShell. Check status first and start the local
PostgreSQL 17 instance only if stopped, using the earlier database instructions.

~~~powershell
Set-Location G:\STUDY\psych-talk-hub\backend
.\.venv\Scripts\python.exe scripts/local_database.py status
# If stopped, run: .\.venv\Scripts\python.exe scripts/local_database.py start

$previousDjangoEnvironment = $env:DJANGO_ENV
try {
    $env:DJANGO_ENV = 'test'
    .\.venv\Scripts\python.exe manage.py check --database default
    if ($LASTEXITCODE -ne 0) { throw 'Django checks failed.' }
    .\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
    if ($LASTEXITCODE -ne 0) { throw 'A migration is missing.' }
    .\.venv\Scripts\python.exe manage.py test --noinput --verbosity 2
    if ($LASTEXITCODE -ne 0) { throw 'Backend tests failed.' }
} finally {
    if ($null -eq $previousDjangoEnvironment) {
        Remove-Item Env:DJANGO_ENV -ErrorAction SilentlyContinue
    } else {
        $env:DJANGO_ENV = $previousDjangoEnvironment
    }
}
~~~

Expected: no system-check errors, no missing migrations, **69 tests pass** and `OK`.
The test runner creates/destroys test_psychtalk and applies migrations from scratch;
--noinput recreates a stale explicitly named test database. No new migration should
be generated. Development migrations remain the three already accepted in step 07.

Optional visual validation uses a private local administrator. If you have none,
create one interactively in development mode; do not share or commit the password:

~~~powershell
$env:DJANGO_ENV = 'development'
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver
~~~

Skip createsuperuser if you already have an account. Visit http://localhost:8000/admin/,
create a test talk/manual resource, associate the resource and inspect the public
address. Check London time labels and delete-confirmation copy; cancelling keeps
the talk. Resource edit pages must have no delete button. Stop runserver with Ctrl+C
and restore your previous DJANGO_ENV when finished. These records are your own
development test data, not step 09 demo seeding.

Following user confirmation, progress.md was requested in the editor and updated
first, then architecture file responsibilities, acceptance and insights were recorded,
followed by README/AGENTS synchronisation. This handoff changes documentation only;
no checks, tests, code or database operations were performed. Step 09 has not started
and requires a new instruction. At this handoff, GitHub CI/Linux were unverified
and no commit or push had been made. The later stage push and successful Linux
backend CI are recorded in the CI section above.

## Step 09: Repeatable demo data — user-confirmed local acceptance

On 4 October 2026, the user replied “通过” after receiving the complete validation
instructions. This records local acceptance of Django checks, the missing-migration
check and 82 backend test methods, without individual outputs or timings. The
assistant did not run acceptance tests or seed the development database. Optional
development seeding and Admin browsing have no separate confirmation. Step 09
changes are still uncommitted and have not run in GitHub CI; step 10 has not started.

events/data/demo_reading.json contains two fictional talks and six real reading
records: four papers and two institutional articles, three links per talk.
events/demo_seed.py loads this local manifest; the independent management command
is seed_demo. Neither application startup nor CI/deployment invokes the command.
The command creates no administrator account and performs no external requests.

One timezone-aware import instant sets newly created talks to +30 days and -7 days.
Resources with DOIs match the trimmed, lowercased DOI; other demo resources and
talks match stable seed_key values. Links match their event/resource pair.
Existing records are never saved or updated, including deliberately cleared text,
edited dates, recommendations and ordering. Repeating only fills missing records
or links. Changing/deleting a stable identity is not a supported rename procedure:
the importer cannot recognise a record whose identity has been removed. Recreating
a missing talk assigns its date relative to that new import instant; surviving
talk dates remain unchanged. An expired future date is not automatically moved.

The entire import uses one transaction and normal model validation; a failure
rolls back newly created records. Created counts are reported after success.
This controlled CLI entry is not the future interactive DOI save service and
does not claim its concurrency acceptance from steps 22–23.

### Reading provenance

Bibliography was checked on **4 October 2026**. Verification URLs and date remain
in the local manifest for reviewers; they are not public API fields. Four paper
records use Crossref's first title, ordered author names, publication-year priority
and original URL, with crossref provenance:

| Reading | Verification source |
| --- | --- |
| About Sleep's Role in Memory (2013) | [Crossref record](https://api.crossref.org/works/10.1152%2Fphysrev.00032.2012) |
| The memory function of sleep (2010) | [Crossref record](https://api.crossref.org/works/10.1038%2Fnrn2762), [publisher](https://www.nature.com/articles/nrn2762) |
| Social Relationships and Mortality Risk: A Meta-analytic Review (2010) | [Crossref record](https://api.crossref.org/works/10.1371%2Fjournal.pmed.1000316), [publisher](https://journals.plos.org/plosmedicine/article?id=10.1371/journal.pmed.1000316) |
| Social Interactions and Well-Being (2014) | [Crossref record](https://api.crossref.org/works/10.1177%2F0146167214529799), [PubMed](https://pubmed.ncbi.nlm.nih.gov/24769739/) |
| Sleep On It (2013) | [NIH article](https://newsinhealth.nih.gov/2013/04/sleep-it), [April 2013 issue](https://newsinhealth.nih.gov/2013/04) |
| WHO social-connection news release (2025) | [WHO article dated 30 June 2025](https://www.who.int/news/item/30-06-2025-social-connection-linked-to-improved-heath-and-reduced-risk-of-early-death) |

Crossref's first title for the weak-ties paper omits its subtitle; the stored
title follows that verified metadata rather than constructing a different title.
NIH and WHO have institutional display credits, not invented individual bylines.
Those articles were manually curated and use manual provenance and no DOI.
Paper links use verified Crossref DOI URLs; publisher full-text access may vary.
Importing uses the curated snapshot and never fetches these sources during tests.

Each initial talk has is_example=true, an Example event title, explicitly fictional
speaker names and the prescribed fictional-reading/independent-project disclosure
in its description. Recommendations identify their selection as illustrative.
Public badge/footer rendering cannot be verified yet: React and public APIs do
not exist. Their display remains steps 15–16; this step verifies the prepared
data and disclosure copy without creating a temporary public page or API.

### Validation — run by the user

No new migration or dependency is needed. The assistant has not run seed_demo,
checks or tests, and has not changed the development database. Run in PowerShell:

~~~powershell
Set-Location G:\STUDY\psych-talk-hub\backend
.\.venv\Scripts\python.exe scripts/local_database.py status
~~~

If the project-local PostgreSQL 17 instance is stopped, start it using the same
tool's start action. Preserve the old PostgreSQL 11 service. Then run the complete
acceptance suite, restoring your previous environment afterwards:

~~~powershell
$previousDjangoEnvironment = $env:DJANGO_ENV
try {
    $env:DJANGO_ENV = 'test'
    .\.venv\Scripts\python.exe manage.py check --database default
    if ($LASTEXITCODE -ne 0) { throw 'Django checks failed.' }
    .\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
    if ($LASTEXITCODE -ne 0) { throw 'A migration is missing.' }
    .\.venv\Scripts\python.exe manage.py test --noinput --verbosity 2
    if ($LASTEXITCODE -ne 0) { throw 'Backend tests failed.' }
} finally {
    if ($null -eq $previousDjangoEnvironment) {
        Remove-Item Env:DJANGO_ENV -ErrorAction SilentlyContinue
    } else {
        $env:DJANGO_ENV = $previousDjangoEnvironment
    }
}
~~~

Expected: no system errors, No changes detected and **82 test methods / OK**
(69 previous methods and 13 demo tests). The new tests fix the import instant,
check bibliography/disclosures, later repeat imports, manual edits including
empty values, DOI reuse, manual identity separation, missing link/talk/article
replacement, invalid times, full rollback and command output/error/network rules.
They run solely in the isolated test database; they do not seed development data
and do not perform live source verification.

Optional: after tests, explicitly add demo data to your development database.
All three existing events migrations must already be applied. Run the command
twice to inspect its output and the records in your private Admin session:

~~~powershell
$previousDjangoEnvironment = $env:DJANGO_ENV
try {
    $env:DJANGO_ENV = 'development'
    .\.venv\Scripts\python.exe manage.py seed_demo
    if ($LASTEXITCODE -ne 0) { throw 'Demo import failed.' }
    .\.venv\Scripts\python.exe manage.py seed_demo
    if ($LASTEXITCODE -ne 0) { throw 'Repeated demo import failed.' }
} finally {
    if ($null -eq $previousDjangoEnvironment) {
        Remove-Item Env:DJANGO_ENV -ErrorAction SilentlyContinue
    } else {
        $env:DJANGO_ENV = $previousDjangoEnvironment
    }
}
~~~

For a fresh development dataset, expect 2 talks / 6 resources / 6 links created
on the first run and 0 / 0 / 0 on the second. If matching records already exist,
the first counts may be lower. Unrelated development records are preserved.
Check initial dates, three readings per talk, fictional labels and source links
in Admin. Existing public-address links still return 404 at this stage.
Production seeding remains a later explicitly selected, controlled operation;
do not use production configuration for validation tests.

After user confirmation, progress.md was requested in the editor and updated
first, then architecture responsibilities, acceptance and insights were recorded,
followed by README/AGENTS synchronisation. This handoff changes documentation only;
no checks, tests, code or database operations were performed. Step 10 has not
started and requires a new instruction. Step 09 changes have not been committed,
pushed or verified in GitHub CI. Public disclosure rendering remains steps 15–16.

## Step 10: Public event list — user-confirmed local acceptance

On 4 October 2026, the user replied “通过” after receiving the complete validation
instructions. This records local acceptance of Django checks, the missing-migration
check and 90 backend test methods, without individual outputs, timings or separate
query measurements. The assistant did not run acceptance commands. Steps 09–10
remain uncommitted and have not run in GitHub CI; step 11 has not started.

GET /api/events/ returns an unpaginated JSON array, ordered by event ID ascending.
Each object exposes only id, title, description, topic, starts_at, speaker,
is_example and resource_count, as defined in the
[authoritative API contract](../memory-bank/tech-stack.md#public-api-contract).
Optional text stays an empty string. starts_at is explicitly UTC ISO 8601 with
a Z suffix, regardless of Django's active display time zone. The client remains
responsible for upcoming/past grouping and London display.

events/serializers.py defines the read-only output. events/views.py counts reading
links using one aggregate query and exposes a JSON-only ListAPIView with public
access, no session authentication, pagination or filtering. events/urls.py mounts
the list under the root /api/ prefix. No seed identifier, bibliography, session,
preview or administrator information is returned; reading never calls Crossref.

Only this list route is added. Detail, missing/unknown API and safe server-error
handling remain step 11; the full two-endpoint method matrix remains step 12.
The list already provides only GET/HEAD/OPTIONS handlers, with no write actions.
There is no new dependency, model change or migration. Development data was not
seeded or changed by the assistant, and no acceptance commands were run.

### Validation — run by the user

In PowerShell, check that the project-local PostgreSQL 17 instance is running:

~~~powershell
Set-Location G:\STUDY\psych-talk-hub\backend
.\.venv\Scripts\python.exe scripts/local_database.py status
~~~

If stopped, run the same tool with start. Preserve PostgreSQL 11 on port 5432.
Run the checks and complete isolated database test suite:

~~~powershell
$previousDjangoEnvironment = $env:DJANGO_ENV
try {
    $env:DJANGO_ENV = 'test'
    .\.venv\Scripts\python.exe manage.py check --database default
    if ($LASTEXITCODE -ne 0) { throw 'Django checks failed.' }
    .\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
    if ($LASTEXITCODE -ne 0) { throw 'A migration is missing.' }
    .\.venv\Scripts\python.exe manage.py test --noinput --verbosity 2
    if ($LASTEXITCODE -ne 0) { throw 'Backend tests failed.' }
} finally {
    if ($null -eq $previousDjangoEnvironment) {
        Remove-Item Env:DJANGO_ENV -ErrorAction SilentlyContinue
    } else {
        $env:DJANGO_ENV = $previousDjangoEnvironment
    }
}
~~~

Expected: no system errors, No changes detected and **90 test methods / OK**.
The eight new APITestCase methods cover anonymous empty JSON, exact fields/types
and private-field exclusion, optional defaults, ID order without pagination,
shared/unlinked resource counts and link changes, winter/summer UTC output under
multiple active time zones, one query for empty/one/21 populated events, and no
external requests or business-record changes. Fixtures live only in the isolated
test database; an empty development list is valid and does not trigger seeding.

No commit or push has been made for steps 09–10; earlier CI success does not cover
them. After user confirmation, progress.md was requested in the editor and updated
first, then architecture acceptance, file responsibilities and insights were
recorded, followed by README/AGENTS synchronisation. This handoff changes documents
only; no checks, tests, code or database operations were performed. Step 11 has not
started and requires a subsequent instruction.

## Step 11: Public event detail and API errors — user-confirmed local acceptance

On 4 October 2026, the user replied “通过” after receiving the validation
instructions. This records local acceptance of Django checks, the missing-migration
check and 104 backend test methods, without individual outputs, timings or separate
query measurements. The assistant did not run acceptance commands. Steps 09–11
remain uncommitted and have not run in GitHub CI; step 12 has not started.

GET /api/events/{id}/ returns the same eight activity fields as the list, plus
resources. The authoritative field/type source remains
[Technology stack — Public API contract](../memory-bank/tech-stack.md#public-api-contract).
EventDetailSerializer inherits the list fields and UTC conversion; each flat
reading object distinguishes association_id from resource_id and includes only
the contract's shared bibliography and current-event recommendation/display_order.
Missing authors/recommendation remain empty strings; missing year/doi remain null.
Zero readings return resources as an empty array and resource_count as integer zero.

EventDetailView aggregates the count and preloads ordered EventResource rows with
their Resource in a joined query. Ordering uses display_order then association ID,
including negative values. The tests assert two queries for zero, one and 21
readings; local acceptance is user-confirmed, with no independent query measurements.
There are no per-reading lookups, external requests or public write actions.

events/urls.py registers the canonical trailing-slash detail route.
config/urls.py keeps valid API routes ahead of explicit JSON 404 fallbacks, including
unknown subpaths, invalid IDs and bare /api. A URL missing the required trailing
slash is unknown and returns JSON 404 rather than redirecting to HTML.
config/api_errors.py handles API view/serialization/rendering exceptions in both
DEBUG modes and masks other API 500 responses. Errors have a non-empty detail
string; unexpected failures return `Internal server error.` without exception text,
SQL or credentials. The custom fault log records only the exception class.
Admin, health and non-API page handling retain their existing behaviour. Unknown
API addresses cannot reach a future React fallback. There are no schema,
migration, dependency or development-database changes.

### Validation — run by the user

In PowerShell, select this project's backend and inspect its PostgreSQL 17 status:

~~~powershell
Set-Location G:\STUDY\psych-talk-hub\backend
.\.venv\Scripts\python.exe scripts/local_database.py status
~~~

If stopped, start the same project-local instance:

~~~powershell
.\.venv\Scripts\python.exe scripts/local_database.py start
~~~

Preserve the old PostgreSQL 11 service on 5432. Run checks and the complete suite
against the isolated test database, restoring your previous environment afterward:

~~~powershell
$previousDjangoEnvironment = $env:DJANGO_ENV
try {
    $env:DJANGO_ENV = 'test'
    .\.venv\Scripts\python.exe manage.py check --database default
    if ($LASTEXITCODE -ne 0) { throw 'Django checks failed.' }
    .\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
    if ($LASTEXITCODE -ne 0) { throw 'A migration is missing.' }
    .\.venv\Scripts\python.exe manage.py test --noinput --verbosity 2
    if ($LASTEXITCODE -ne 0) { throw 'Backend tests failed.' }
} finally {
    if ($null -eq $previousDjangoEnvironment) {
        Remove-Item Env:DJANGO_ENV -ErrorAction SilentlyContinue
    } else {
        $env:DJANGO_ENV = $previousDjangoEnvironment
    }
}
~~~

Expected: no system errors, No changes detected, and **104 tests / OK**.
The 14 new methods cover exact event/flat reading fields and types, private-field
exclusion, null/default values, zero readings, negative/tied association order,
shared edits and event-specific reasons/unlinking/counts, winter/summer UTC,
constant queries, no external calls/business writes, missing/deleted events,
unknown paths even with HTML Accept, database/serializer/renderer failures,
safe custom logs and non-API boundary preservation. DEBUG false and true are
both exercised for missing routes and query failures. Existing list and Admin
tests run as regressions. Fixtures exist only in the test database; no seeding
or development administrator is required.

The assistant has not run these checks, tests, compilation, migrations, services
or browser validation. Step 11 local acceptance comes from the user's confirmation;
there is no step 11 remote CI result. After confirmation, progress.md was requested
in the editor (queued) and updated first, then architecture acceptance, file roles
and insights were recorded, followed by README/AGENTS synchronisation. This handoff
changes documentation only; no checks, tests, code or database operations were
performed. Step 12's complete anonymous and administrator method matrix has not
started and requires a subsequent instruction. No commit, push or deployment
was performed; existing remote CI verifies only the earlier steps 01–08 version.

## Step 12: Restrict public API methods — user-confirmed local acceptance

On 4 October 2026, the user replied “通过” after receiving the validation
instructions. This records local acceptance of Django checks, the missing-migration
check and 116 backend test methods, without individual logs, timings or separate
database measurements. The assistant did not run acceptance commands. Steps 09–12
remain uncommitted and have not run in GitHub CI; step 13 has not started.

The existing ListAPIView and RetrieveAPIView already explicitly allow only
GET/HEAD/OPTIONS. Step 12 preserves those handlers, serializers and routes without
adding CRUD, dependencies, migrations or application configuration changes.
Public reading deliberately has no session authentication: an authenticated
administrator uses the same public capabilities as an anonymous visitor. Admin
editing remains a separate, authorised interface.

events/tests/test_public_api_methods.py adds 12 test methods (116 total). It uses
APIClient with CSRF checks enabled and a real database-backed superuser session;
it first verifies the logged-in session can access Admin. It never creates a
development administrator. Every stored Event, Resource and EventResource field
is compared before/after the tested public requests, including private seed
identities, shared bibliography and each event's recommendation/order.

- GET returns JSON 200 for both endpoints and both identities.
- HEAD matches GET status, Content-Type, Content-Length and Allow but has no body;
  a missing event similarly returns body-free 404 with the corresponding headers.
- OPTIONS returns JSON 200 and Allow containing exactly GET, HEAD and OPTIONS,
  without write actions or event queryset/external-service calls. The default DRF
  `parses` metadata lists request formats; it does not advertise a writable method.
- POST, PUT, PATCH, DELETE, TRACE, CONNECT and an unknown PURGE method return JSON
  405 with a non-empty detail string and the same exact Allow header. Rejection
  does not call the event querysets or external services. An Admin session does
  not grant public writes or turn these responses into CSRF/permission errors.
- Write methods on a valid detail route with a missing event return 405 before
  object lookup; GET/HEAD retain 404. Unknown API routes retain step 11's JSON 404.
- Invalid JSON and unsupported request-body media types still produce 405 for
  rejected methods. `_method` and X-HTTP-Method-Override hints cannot enable a
  write on GET or turn POST into a permitted GET.

### Validation — run by the user

In PowerShell, inspect this project's isolated PostgreSQL 17 instance:

~~~powershell
Set-Location G:\STUDY\psych-talk-hub\backend
.\.venv\Scripts\python.exe scripts/local_database.py status
~~~

If stopped, start the same project-local instance; preserve PostgreSQL 11 on 5432:

~~~powershell
.\.venv\Scripts\python.exe scripts/local_database.py start
~~~

Run checks and the complete suite against the isolated test database:

~~~powershell
$previousDjangoEnvironment = $env:DJANGO_ENV
try {
    $env:DJANGO_ENV = 'test'
    .\.venv\Scripts\python.exe manage.py check --database default
    if ($LASTEXITCODE -ne 0) { throw 'Django checks failed.' }
    .\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
    if ($LASTEXITCODE -ne 0) { throw 'A migration is missing.' }
    .\.venv\Scripts\python.exe manage.py test --noinput --verbosity 2
    if ($LASTEXITCODE -ne 0) { throw 'Backend tests failed.' }
} finally {
    if ($null -eq $previousDjangoEnvironment) {
        Remove-Item Env:DJANGO_ENV -ErrorAction SilentlyContinue
    } else {
        $env:DJANGO_ENV = $previousDjangoEnvironment
    }
}
~~~

Expected: no system-check errors, No changes detected, and **116 tests / OK**.
Subtests cover the method/endpoint/identity combinations inside the 12 new methods;
they do not increase the reported test-method count. Fixtures and login sessions
exist only in the test database; no seed_demo or development account is needed.

The assistant has only read and edited files, without executing checks, tests,
compilation, migrations, services, browser acceptance or database operations.
Step 12's local acceptance is based on the user's confirmation. After confirmation,
progress.md was requested in the editor (queued) and updated first, then architecture
acceptance, file roles and new insights were recorded, followed by README/AGENTS
synchronisation. This handoff changes documentation only, without checks, tests,
application code or database operations. Steps 09–12 have not been committed/pushed
or verified by remote CI. Step 13 has not started and requires a subsequent instruction.

## Step 17 validation — run by the user

The assistant subsequently passed these local checks with user authorisation:
30 frontend tests, 135 backend tests and 20 browser scenarios. User confirmation
is pending; remote deployment and actual Linux startup remain unverified. The
instructions below remain available to reproduce the checks. Build the current frontend
**before backend tests**: two new tests inspect actual Vite output and collect it
with Admin assets into a temporary directory. A missing/stale build must fail,
not be silently skipped. No new dependency installation or migration is needed
for this step. Keep private environment files and existing database data.

### 1. Frontend checks and production build

Stop Vite in its terminal with Ctrl+C, then:

~~~powershell
Set-Location G:\STUDY\psych-talk-hub\frontend
npm.cmd run lint
if ($LASTEXITCODE -ne 0) { throw 'Frontend lint failed.' }
npm.cmd test
if ($LASTEXITCODE -ne 0) { throw 'Frontend tests failed.' }
npm.cmd run build
if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed.' }
~~~

Expected: no lint issues, **30 tests passed**, successful build. Generated
frontend/dist/index.html must reference /static/frontend/assets/ JS and CSS,
without /src/main.jsx or /@vite/client. Source/lock files remain unchanged.

### 2. Database status, backend checks and complete regression

~~~powershell
Set-Location G:\STUDY\psych-talk-hub\backend
.\.venv\Scripts\python.exe scripts/local_database.py status
~~~

If stopped, start only this isolated instance:

~~~powershell
.\.venv\Scripts\python.exe scripts/local_database.py start
~~~

Then run the full suite using the test configuration:

~~~powershell
$step17PreviousMode = $env:DJANGO_ENV
try {
    $env:DJANGO_ENV = 'test'
    .\.venv\Scripts\python.exe -m pip check
    if ($LASTEXITCODE -ne 0) { throw 'Dependency consistency failed.' }
    .\.venv\Scripts\python.exe manage.py check --database default
    if ($LASTEXITCODE -ne 0) { throw 'Django checks failed.' }
    .\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
    if ($LASTEXITCODE -ne 0) { throw 'A migration is missing.' }
    .\.venv\Scripts\python.exe manage.py test --noinput --verbosity 2
    if ($LASTEXITCODE -ne 0) { throw 'Backend tests failed.' }
} finally {
    if ($null -eq $step17PreviousMode) {
        Remove-Item Env:DJANGO_ENV -ErrorAction SilentlyContinue
    } else {
        $env:DJANGO_ENV = $step17PreviousMode
    }
}
~~~

Expected: dependencies consistent, no system errors, No changes detected,
**135 tests / OK**. Added methods: six page/static boundary tests, one real
Admin-to-anonymous-API publication test, two actual-build/static tests and ten
deployment-order/guard tests. The deployment tests mock subprocesses, platform
and process replacement; they do not connect to production, install anything,
execute Gunicorn or run actual migration-failure experiments against data.

### 3. DEBUG=False browser verification without Vite

Use a dedicated PowerShell window and keep it running. This uses the existing
**development database**, with DEBUG=False; it tests production-style asset
handling locally, not production credentials, TLS or secure Cookie deployment.
Do not set production mode or copy production credentials into this window.
Port 8001 separates this check from any existing server on 8000. If occupied,
choose an unused port and adjust the URLs; do not kill an unrelated process.

~~~powershell
Set-Location G:\STUDY\psych-talk-hub\backend
$step17SavedMode = $env:DJANGO_ENV
$step17SavedDebug = $env:DEBUG
try {
    $env:DJANGO_ENV = 'development'
    $env:DEBUG = 'False'
    .\.venv\Scripts\python.exe manage.py collectstatic --noinput
    if ($LASTEXITCODE -ne 0) { throw 'Static collection failed.' }
    .\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8001 --nostatic --noreload
} finally {
    if ($null -eq $step17SavedMode) {
        Remove-Item Env:DJANGO_ENV -ErrorAction SilentlyContinue
    } else {
        $env:DJANGO_ENV = $step17SavedMode
    }
    if ($null -eq $step17SavedDebug) {
        Remove-Item Env:DEBUG -ErrorAction SilentlyContinue
    } else {
        $env:DEBUG = $step17SavedDebug
    }
}
~~~

Keep Vite stopped throughout this check. After rebuilding or recollecting assets,
restart this no-reload server so WhiteNoise reloads its file list.

Check these paths in order:

1. Open http://127.0.0.1:8001/ anonymously. Real groups/cards load normally.
   In Network, built JS/CSS return 200 with the appropriate content types from
   /static/frontend/assets/; there are no Vite/HMR requests or asset 404s.
2. Click an actual Explore resources link. Copy its /events/{id} URL, open it
   directly in another tab and refresh. Event/readings/original new-tab links,
   Back to talks and browser Back/Forward work. Use actual IDs, not a presumed 1.
3. Open http://127.0.0.1:8001/admin/login/. It has styled forms; Admin CSS/JS
   requests return 200. http://127.0.0.1:8001/static/admin/css/base.css returns CSS.
   Keep your administrator credentials private.
4. Open http://127.0.0.1:8001/api/unknown/. It is JSON 404 with detail, never the
   React entry. An actually missing numeric event returns JSON 404 from its API
   and the existing not-found UI from its page. The HTML shell itself is 200;
   that is distinct from the event's API status.
5. Open http://127.0.0.1:8001/healthz/. It returns 200 and {"status":"ok"}.
   An unknown server page such as /unknown/ remains Django 404, not a SPA fallback.

### 4. Admin save → public refresh

Use the existing private administrator in the 8001 service. Do not initialize a
second database or account. If no usable local account/resources exist, report
that browser subcheck as pending; the isolated automated test remains separate.

1. Add a temporary talk titled `Example event: Milestone verification`, mark it
   as an example, and choose a valid future London start (for example 1 December
   2026 at 18:00). Save and open its provided public URL anonymously; verify zero
   reading resources and the defined empty-reading message.
2. In Event resources → Add, choose that talk and an existing verified resource.
   Set recommendation `Milestone verification reading.` and order -1, then save.
   Reusing an existing Resource avoids leaving an unnecessary new bibliography.
3. Reload its public page: count is now 1, title/original URL/recommendation match
   the selected resource, with no draft or approval stage. Its API reflects the
   same association. This verifies adding reading through Admin; manual Resource
   creation is also covered by the new isolated database test.
4. Optionally delete this temporary talk through the existing confirmation.
   Its reading link disappears while the shared resource and other talks remain.
   Do not attempt to delete a Resource or change the seeded talks for cleanup.

### 5. Remote status and handoff

Read [DEPLOYMENT.md](DEPLOYMENT.md) for the checked platform facts and exact
settings. No connected/authorised free resources are available to this session,
and current steps have no pushed CI result. Remote service runtime, database
capacity/dates, deployment, HTTPS/Cookies and online acceptance therefore remain
**externally blocked / unverified**. Local acceptance cannot be reported as online
success. No paid feature, Shell, pre-deploy command, seeding or admin initialization
was used or added to the deployment lifecycle.

Stop the temporary server with Ctrl+C after checking; the finally block restores
its process environment. You can then resume the ordinary Django/Vite development
servers described in frontend/README.md. Collected and built files stay ignored.
Send results or failure output without credentials. After confirmation, progress
is updated first, then architecture; step 18 still needs a subsequent instruction.

## References and boundaries

events/models.py implements Event, Resource and EventResource; admin.py implements
basic management with three app-level confirmation templates. serializers.py,
views.py and urls.py provide the accepted step 10 event list and step 11 detail;
config/api_errors.py defines the API error boundary, accepted locally by the user.
events/tests/ contains infrastructure, model, Admin, demo, list/detail and public
method API tests; step 12's method acceptance is user-confirmed locally.
Steps 01–12 have user-confirmed local acceptance, without individual outputs.
DOI import, shared-edit warning/refinements and the full permissions matrix remain
later steps; do not treat these basic Admin tests as complete MVP acceptance.
The standard ASGI entry remains; production is planned around WSGI.

[Architecture](../memory-bank/architecture.md), [design](../memory-bank/design-document.md),
[technology stack](../memory-bank/tech-stack.md) and
[implementation plan](../memory-bank/implementation-plan.md).
