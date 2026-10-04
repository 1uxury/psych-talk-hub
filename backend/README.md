# PsychTalk Hub backend

Steps 01–08 have **user-confirmed local acceptance**. Basic backend GitHub CI passed
on 4 October 2026 for commit 66b4140; see the CI section for remote evidence.
Step 05 adds Event, an initial migration and nine tests, accepted locally by the user.
Step 06 adds Resource, migration 0002_resource and 14 tests, accepted locally by the user.
Step 07 adds EventResource, migration 0003_event_resource and 13 tests, accepted locally by the user.
Step 08 adds basic Admin management and 21 tests (69 total), accepted locally by the user.
Event API, React and deployment remain unimplemented. Step 09 has not started.
The stage implementation was committed and pushed to docs/clarify-implementation-plan.
The numbered handoff sections retain their historical validation status; the CI
section below records the later remote verification.

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
Static integration and actual deployment remain for later steps.

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

## References and boundaries

events/models.py implements Event, Resource and EventResource; admin.py implements
basic management with three app-level confirmation templates. views.py remains a
placeholder. events/tests/ contains infrastructure, model and Admin tests.
Steps 01–08 have user-confirmed local acceptance, without individual outputs.
DOI import, shared-edit warning/refinements and the full permissions matrix remain
later steps; do not treat these basic Admin tests as complete MVP acceptance.
The standard ASGI entry remains; production is planned around WSGI.

[Architecture](../memory-bank/architecture.md), [design](../memory-bank/design-document.md),
[technology stack](../memory-bank/tech-stack.md) and
[implementation plan](../memory-bank/implementation-plan.md).
