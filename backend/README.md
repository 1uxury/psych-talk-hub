# PsychTalk Hub backend

Current stage delivery (7 October 2026): application release **06f98e2** passed [current frontend/backend CI](https://github.com/1uxury/psych-talk-hub/actions/runs/37552097967) and is **Live** on the existing Free Render service. Clean local lint/30 frontend/build/checks and **315 PostgreSQL backend tests (43.307 s)** passed, as did nine time/layout/keyboard groups, eleven production HTTP/Admin checks and seven fresh anonymous browser groups. Nonempty redeployment preserved every public field; explicitly authorized private backup/isolated restore matched all business/admin/migration fields. See [README](../README.md), [delivery](../DELIVERY.md) and [backup procedure](../backend/BACKUP.md). Management video and the full production management matrix remain pending; this is a stage delivery, not full MVP acceptance. Last explicit user acceptance is step 31; latest instruction authorizes finishing work. Earlier statuses below are historical.

Current work: **step 31 public page states are user-accepted on 7 October 2026,
after assistant verification; step 32 has not started.** The explicit step 31 instruction
authorises this work without inventing a separate step 30 acceptance reply.
Lint/30 Node tests/build and 13 read-only fixture browser groups passed on
7 October 2026; zero JS exceptions, assets 200, screenshots reviewed. Existing
runtime state handling needed no changes. No backend tests/database operations
were required this step; the last complete 311-test evidence remains below.
See [step 31 manual validation](../frontend/README.md#step-31-validation--public-page-states).
Current uncommitted changes still need remote CI and production delivery.

Historical step 30 handoff: **steps 01–29 are user-accepted**. Step 30 second milestone passed
local assistant verification, rechecked on 7 October 2026; **user acceptance and remote CI
for the current uncommitted version remain pending. Step 31 has not started.**
Current frontend lint/30 tests/build, dependency/Django/migration checks,
collectstatic and **311 backend tests / OK (44.641 s)** passed. Twenty browser
paths passed actual Admin/CSRF/session/API and the current React bundle: 12 core
paths with mocked lookup/test clock, plus 8 real Crossref integration paths.
No application code, schema, dependencies or product behavior changed.

Three disposable test databases were destroyed; the dedicated browser/servers
closed and existing PG17 kept in its initially running state. PG11 and existing
development services were untouched.
No existing development business writes, production access, Git publication or
deployment occurred. Production remains d8bdd29; steps 18–30 are unpublished.
The accepted step 29 real Crossref evidence is separate below. Earlier sections
retain historical evidence, rather than current acceptance or CI claims.

## Step 30 validation — second milestone

### Latest recheck — 7 October 2026

At the user's request, lint/30 frontend tests (290.874 ms)/build (249 ms),
pip/Django/migration checks, collectstatic (2 copied, 164 unmodified, 156
post-processed), and **311 backend tests / OK (44.641 s)** passed again.
The 12 core browser checks passed again (live test 23.780 s), followed by 8 real
DOI integration checks (9.309 s). Both used disposable data, actual Admin/CSRF/
session/API/current React; zero JS exceptions, assets 200, screenshots reviewed.

The real chain fetched `10.1038/nrn2762` once through the original service:
Crossref HTTP 200 outside the transaction, bibliography matching the preview,
saved Resource and public API; confirmation/repeat/reuse made no lookup.
Provider unavailability was simulated. The original-link tab finally reached
Nature's matching article. Core expiry still used a test clock at exactly 900
seconds, rather than a real wait. Three test databases were destroyed. PG17 was
already running at this recheck and was **kept running**; only the dedicated
browser/test servers closed, with no changes to existing development data/services.

Existing CI run 37320118006/01e1dd0 and both jobs/all steps were rechecked success;
current uncommitted remote CI remains pending. This recheck is not user acceptance
or step 31 implementation. Earlier results below retain the initial evidence.

### Initial assistant results — 6 October 2026

| Current check | Result |
| --- | --- |
| Pinned runtimes | Node 24.14.0, npm 11.9.0, Python 3.13.16; existing installations |
| Frontend lint / Node tests / build | Passed / 30 passed, none skipped (332.9551 ms) / passed (248 ms) |
| pip / Django / missing migrations | No broken requirements / no issues / No changes detected |
| Static collection | 3 copied, 163 unmodified, 156 post-processed |
| Complete PostgreSQL regression | 311 tests / OK (41.926 s); test database destroyed |
| Actual browser workflow | 12 groups passed; live test OK (23.236 s), zero JS exceptions, assets 200 |
| Existing remote CI | Run 37320118006: frontend/backend and all steps success, SHA 01e1dd0 |
| Current uncommitted remote CI | Pending; the existing successful run covers published step 17 code/documents |

Browser verification used `DJANGO_ENV=test`, disposable
`test_psychtalk_step30_browser`, temporary example talks/accounts, real Admin
forms/CSRF/database sessions and the actual built React/WhiteNoise/public API.
Lookup returned bibliography from the checked-in demo manifest, with all real
external HTTP blocked. Expiry used a test clock at the original load time plus
900 seconds; it was **not a real 15-minute wait**, and neither system time nor
stored preview timestamps were changed. The regular 311-test suite also covers
before/at/after expiry, edit without extension, permissions/CSRF, real PostgreSQL
concurrency, session merging, idempotence and rollback.

The 12 browser groups covered login/empty baseline; new DOI preview/check/save
and repeated confirmation; saved readonly bibliography/reuse; two independent
manual records with identical title/URL; title-only search/trim/case/no-match/
clear/focus/event scope/no extra request; independent previews/cancel replay;
exact expiry; shared edit; per-talk reason/order; association removal with cancel;
event deletion with cancel and retained resources; logout/anonymous refresh/mobile.
Final ORM assertions found three retained Resources, one B association, A deleted,
unchanged B reason/order and no canceled/expired DOI saved. Five screenshots were
reviewed. Ignored `.tools/step30-browser` helpers/results are local evidence;
they are not application code, formal CI tests or clean-checkout tooling.

The existing successful [Project checks 37320118006](https://github.com/1uxury/psych-talk-hub/actions/runs/37320118006)
was verified read-only for SHA `01e1dd094277cb8b89ba5d2bb791d62b0f24f972`.
It does **not** validate uncommitted steps 18–30. Current remote CI awaits
publication and verification; no commit/push/workflow trigger or deployment was
performed. Clean dependency installation and deliberate CI failure checks remain
step 34 work. Local validation is not full MVP or online acceptance.

### Repeat automated checks

Run frontend lint/tests before the [complete regression commands](#2-complete-regression-isolated-local-postgresql),
which build current assets, select test settings and run all 311 backend tests
against isolated local PG17. Start only the existing project instance if stopped
and restore its prior state afterwards; never select production configuration.

~~~powershell
Set-Location G:\STUDY\psych-talk-hub\frontend
$env:PATH = 'G:\Program Files\nodejs;' + $env:PATH
& 'G:\Program Files\nodejs\npm.cmd' run lint
if ($LASTEXITCODE -ne 0) { throw 'Frontend lint failed.' }
& 'G:\Program Files\nodejs\npm.cmd' test
if ($LASTEXITCODE -ne 0) { throw 'Frontend tests failed.' }
Set-Location G:\STUDY\psych-talk-hub\backend
.\.venv\Scripts\python.exe -m pip check
if ($LASTEXITCODE -ne 0) { throw 'Dependency check failed.' }
~~~

### Repeat the browser milestone locally

Use the local development Admin/Vite startup commands in
[step 29](#repeat-the-real-workflow-locally), a private local administrator and two
temporary example talks A/B. These manual saves edit local development data; the
assistant's own verification used disposable test data. Use sample records you
can edit/delete, and retain shared resources under the application's rules.

1. Import a verified DOI absent from Resources into A. **Fetch metadata** and
   **Check details** must leave anonymous `/api/events/A/` unchanged. Only
   **Save to event** publishes the reviewed bibliography/reason/order. Record
   resource/association IDs and repeat confirmation before its deadline:
   count/IDs/reason/order remain unchanged.
2. Import that DOI again into A with a different reason/order: readonly saved
   bibliography and **This resource is already linked to this talk.**; original
   values remain. Import into B: same resource ID, distinct association and its
   own reason/order. An existing DOI requires no Crossref lookup.
3. Use Resources **Add** twice for the same valid manual title/URL; expect two
   resource IDs, no DOI and Manual source. Associate one with A using Event
   resources **Add**. Manual records never merge by title/URL.
4. On anonymous A at `http://localhost:5173/events/ID`, search a title substring
   with mixed case/spaces. Only A titles match; an author-only query must not
   match. **Clear search** restores count/order and focuses input. Network shows
   no extra API requests while typing. Open B: query starts empty.
5. Open two DOI previews in separate tabs. Cancel one; its saved URL/old form
   must reject saving with the invalid-preview message, while the other remains
   valid. Anonymous count stays unchanged until confirmation. For a manual expiry
   check, fetch a fresh preview, leave it unconfirmed for **at least 15 minutes
   from loading**, then Save: invalid-preview message, no business writes.
   Editing/Check details must not extend the deadline. Automated tests cover the
   exact boundary without a real wait.
6. Edit the shared Resource after seeing **Changes to this resource will appear
   in every talk that uses it.** Refresh A/B: both show the edit; DOI/source stay
   unchanged. Edit only A's association reason/order, including a negative
   integer: A reorders by order then association ID, B stays unchanged.
7. Open A's shared association and **Remove from this talk**. Confirm the exact
   talk/reading and warning. Cancel first: no change. Repeat and confirm: only
   A's link disappears; B/resource persist.
8. Open A's Event deletion: **Delete this talk and its reading links? Shared
   resources will be kept.** Cancel first: no change. Confirm afterwards:
   A returns public 404/not found, B remains readable, all Resources including
   A-only manual records remain. Resources have no deletion control, including
   for a superuser; direct deletion URLs are rejected by the regression suite.
9. Log out, directly load/refresh B anonymously and check at 375 px. Stop only
   the development services you started and restore PG17's prior state.

The product rules in both designs already agree on fixed expiry, repeat behavior,
deletion and staged/full delivery; no translation change is needed. See
[architecture section 71](../memory-bank/architecture.md#71-第-30-步第二个里程碑的当前边界与验证)
and [progress](../memory-bank/progress.md) for evidence and pending work.
The step 30 handoff originally awaited acceptance/current remote CI. A subsequent
explicit instruction authorised step 31; its state checks passed locally and
the user subsequently accepted it. **Step 32 remains unstarted.** Current remote CI is pending.

## Step 29 validation — real DOI integration

### Verified source and actual results

The assistant queried this real DOI through the application service, then again
through a new Admin import in a disposable development-configured database.
The browser workflow made exactly one real Crossref request; confirmation,
repeat confirmation, subsequent import and reuse in another talk made none.

| Field | Actual Crossref / preview / saved / public value |
| --- | --- |
| DOI | `10.1038/nrn2762` |
| Title | The memory function of sleep |
| Authors, in source order | Susanne Diekelmann; Jan Born |
| Year, from published-print | 2010 |
| Original URL | `https://doi.org/10.1038/nrn2762` |
| Type / source | `research_paper` / `crossref` |

Source: [Crossref work](https://api.crossref.org/works/10.1038%2Fnrn2762).
The actual original-link click opened a new tab, eventually reaching
[Nature's article](https://www.nature.com/articles/nrn2762) with the matching
article title. This verifies the target, without guaranteeing free full text.

Eight browser checks covered login/empty baseline; new real lookup/preview;
CSRF confirmation/publication; repeat confirmation and a second import;
another talk sharing the Resource; safe provider-failure input/Retry/manual
controls; logged-out React reading/refresh during failure; and the original
link. Final ORM checks found one Resource and two associations, matching the
real source and preserving the first reason/order/IDs. Screenshots at 1280 and
375 px were reviewed; public bundle responses were 200.

Provider unavailability was a **controlled ConnectionError in the verification
tool**, rather than an actual Crossref outage. The successful lookup was a real
Requests HTTP call, with normal TLS, fixed encoded target, no redirects and
(3, 7) timeouts outside the save transaction. Existing public data stayed readable
without additional Crossref calls. Windows UI tools failed initialization, so
the check used a dedicated installed Edge instance and the repository's existing
temporary browser-check approach. No new browser dependency or CI integration
was added. Local evidence is in ignored `.tools/step29-browser`; it is not part
of a clean checkout or a production release.

### Repeat the real workflow locally

Use the private **local development** administrator and an existing saved talk.
Check/start only the existing PG17 instance; do not initialize/reset it or operate
PG11. Use two terminals if the development server is not already running:

~~~powershell
Set-Location G:\STUDY\psych-talk-hub\backend
.\.venv\Scripts\python.exe scripts/local_database.py status
# Only if stopped:
# .\.venv\Scripts\python.exe scripts/local_database.py start
$env:DJANGO_ENV = 'development'
.\.venv\Scripts\python.exe manage.py check --database default
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000 --noreload
~~~

In the frontend terminal:

~~~powershell
Set-Location G:\STUDY\psych-talk-hub\frontend
$env:PATH = 'G:\Program Files\nodejs;' + $env:PATH
& 'G:\Program Files\nodejs\npm.cmd' run dev
~~~

1. Open `http://127.0.0.1:8000/admin/`, log in privately, select a saved talk,
   and choose **Import reading by DOI**. Inspect Resources first: a DOI already
   present must show saved readonly bibliography and must not call Crossref.
   The demo seed already contains `10.1038/nrn2762`; if present in your database,
   use another independently verified real DOI absent from Resources for the
   **new lookup** check. Do not delete existing resources to force a query.
2. Enter the new DOI or its HTTPS doi.org link and choose **Fetch metadata**.
   Match title, authors, year and original URL against that DOI's Crossref work.
   Confirm the target talk; before saving, reload the talk at
   `http://localhost:5173/events/ID`: count and readings must remain unchanged.
   If fetching fails, record real integration as unverified for that attempt;
   preserve the input and use Retry/manual entry as shown.
3. Review required fields, add a reason/order, then **Save to event**. Expect
   **Resource added to this talk.** Refresh the anonymous public talk: one new
   reading, matching source, reason and order. **Read original** opens its URL
   in another tab and leaves the talk available. These manual saves change
   local development data; the assistant's own check used disposable records.
4. Fetch the same DOI again for the same talk. Bibliography must be readonly.
   Save with a different reason/order: expect **This resource is already linked
   to this talk.** Count, resource/association IDs and original reason/order stay
   unchanged. Import into a second talk: reuse the Resource and create only its
   association. Inspect IDs through `/api/events/ID/` on the backend.
5. For an unavailable-provider observation, use the displayed failure state for
   a new lookup, then read/refresh already saved talks while the local server and
   database remain available. Browser Offline blocks the local API too and does
   not isolate Crossref availability. The assistant separately tested this with
   the controlled server-side failure described above.
6. Log out and stop only services you started. Restore the terminal's previous
   DJANGO_ENV and stop PG17 only if it was initially stopped. Existing shared
   resources remain retained under the application's deletion rules.

For reproducible offline regression, use the [complete regression commands](#2-complete-regression-isolated-local-postgresql):
current frontend build, Django/migration checks and **311 tests / OK**. These
mocked checks supplement the real workflow and do not substitute for it.
**Step 29 was user-accepted on 6 October 2026.** Its acceptance handoff updated
documents only; subsequent step 30 verification is recorded above.

## Step 28 validation — Admin permissions and CSRF

### Automated acceptance (isolated PostgreSQL 17)

Check the current project instance; start it only if stopped, never run init.
Preserve PG11 on 5432. These tests create disposable accounts and business records
in the test database, and do not edit development data or call real Crossref.

~~~powershell
Set-Location G:\STUDY\psych-talk-hub\backend
.\.venv\Scripts\python.exe scripts/local_database.py status
# Only if stopped:
# .\.venv\Scripts\python.exe scripts/local_database.py start
$step28PreviousMode = $env:DJANGO_ENV
try {
    $env:DJANGO_ENV = 'test'
    .\.venv\Scripts\python.exe manage.py test events.tests.test_admin_permissions --noinput --verbosity 2
    if ($LASTEXITCODE -ne 0) { throw 'Step 28 permission/CSRF tests failed.' }
} finally {
    if ($null -eq $step28PreviousMode) {
        Remove-Item Env:DJANGO_ENV -ErrorAction SilentlyContinue
    } else {
        $env:DJANGO_ENV = $step28PreviousMode
    }
}
~~~

Expected: **28 tests / OK**, no system issues, and `test_psychtalk` destroyed.
For full regression, [follow the commands below](#2-complete-regression-isolated-local-postgresql):
current frontend build, Django/migration checks, then **311 tests / OK**. Stop
PG17 afterwards only if you started it; otherwise preserve its initial state.

All names below are Django `events` model permissions. Each missing permission
is tested separately; positive cases also check the minimum permitted combination.

| Operation | Required permissions |
| --- | --- |
| Create / edit a talk | `add_event` / `change_event` respectively |
| Add a manual resource | `add_resource` |
| Select existing resource for a talk | `add_eventresource`, `change_event`, `view_resource` |
| View DOI lookup/preview | `view_event`, `view_resource`, `view_eventresource` |
| Fetch, check, save or cancel DOI preview | All three view permissions, `change_event`, `add_eventresource` |
| Fetch/check/save a new DOI resource | Above import permissions plus `add_resource`; existing resources need no Resource add/change permission |
| Edit shared bibliography | `change_resource` |
| Edit per-talk recommendation/order | `change_eventresource` |
| Remove reading association | `delete_eventresource` |
| Delete talk, including an empty talk | `delete_event` and `delete_eventresource`; bulk list access additionally needs Event view/change |
| Delete any Resource | Disabled for every account, including superusers and staff with `delete_resource` |

Acceptance covers anonymous, non-staff, inactive and unprivileged staff; each
missing permission; permission removal after preview/confirmation; and fresh
permission lookup inside the final save transaction despite an earlier cached
allowance. View-only accounts may inspect their own preview, but cannot submit.
Cancel does not require Resource creation permission. Saved-result replay still
requires current import permissions.

The real CSRF middleware rejects missing/forged tokens and valid tokens from an
untrusted Origin on every write route, including fetch/check/cancel. Valid tokens
actually complete permitted operations. GET with write action parameters leaves
business data and previews unchanged. Native changelists may redirect invalid
GET filters to `?e=1`; this is not a write.

Single and bulk event deletion must first display the prescribed confirmation.
Revoking either delete permission before confirmation prevents deletion. Successful
confirmation retains every Resource and unselected talks/links. Resource single,
bulk, direct URL and Admin deletion hooks remain blocked. Native Admin filters
unavailable bulk actions: a forged bulk POST can return the list with 200 while
performing no deletion; direct forbidden delete URLs return 403. Tests compare
full business fields, Admin logs and preview state rather than status alone.

The assistant's first run found two incorrect test expectations for the native
GET redirect; only those assertions were repaired, then two additional boundary
cases were added. All final targeted and regression checks passed. **Step 28 is
user-accepted on 6 October 2026.** That confirmation only updated documentation.
Step 29's subsequent real integration evidence and current handoff are above.

## Step 27 validation — remove reading from one talk

### Automated acceptance (isolated PostgreSQL 17)

The assistant ran the combined suite and full regression successfully. To repeat,
check the existing project instance and start it only if stopped; do not run init.
Preserve PG11 on 5432.

~~~powershell
Set-Location G:\STUDY\psych-talk-hub\backend
.\.venv\Scripts\python.exe scripts/local_database.py status
# Only if stopped:
# .\.venv\Scripts\python.exe scripts/local_database.py start
$step27PreviousMode = $env:DJANGO_ENV
try {
    $env:DJANGO_ENV = 'test'
    .\.venv\Scripts\python.exe manage.py test events.tests.test_admin_reading_removal events.tests.test_admin events.tests.test_admin_reading_edits --noinput --verbosity 2
    if ($LASTEXITCODE -ne 0) { throw 'Step 27 Admin tests failed.' }
} finally {
    if ($null -eq $step27PreviousMode) {
        Remove-Item Env:DJANGO_ENV -ErrorAction SilentlyContinue
    } else {
        $env:DJANGO_ENV = $step27PreviousMode
    }
}
~~~

Expected after successful execution: **39 tests / OK**, no system issues and
`test_psychtalk` destroyed. To run only the ten new cases, omit the last two test
modules. For complete regression, [follow the full commands below](#2-complete-regression-isolated-local-postgresql):
build the current frontend, run Django/migration checks and the expected **311
tests / OK**. Fix failures before acceptance. Stop PG17 only if you started it.

| Acceptance case | Expected |
| --- | --- |
| Existing association form | Remove from this talk, native save controls and retained event filter; no remove action on the add form |
| Open confirmation / cancel | Exact warning, full escaped target titles; no business changes |
| Confirm removing A's shared reading | Only A's link removed; A list/detail count decreases; all B fields and shared bibliography retained |
| Remove a last reference / leave a talk empty | Resource and Event still exist; zero resources is a valid public talk |
| Posted replacement identities / repeated confirmation | Only the original URL's association removed; no other link deleted |
| Anonymous, non-staff, missing or revoked removal permission | No deletion; login redirect or 403 as appropriate; EventResource delete permission required |
| Missing/forged CSRF token | 403 and unchanged business records; valid confirmation succeeds |
| Old saved DOI confirmation after native removal | Preview invalid; removed association is not recreated |
| Public delete attempts | Existing read-only API methods/unknown-route handling remain unchanged |

### Local browser acceptance

Manual confirmation **removes an association from your development database**.
Use local test talks and your existing private administrator; the automated suite
above writes disposable test databases only. Use step 26's build/collectstatic/
runserver commands below to serve Admin and the current React bundle on 8000.

1. Choose two local Events A and B referencing the **same Resource ID**. Record
   each public count, B's recommendation/order and the shared resource ID/title.
2. In **Event resources**, filter by A and open that reading association. Click
   **Remove from this talk**. Confirm the target talk/reading and exact text:
   `Remove this reading from this talk? Other talks will keep it.`
3. Click **No, take me back**. The association remains; refresh both public pages
   and `/api/events/`: counts, reasons, order and bibliography remain unchanged.
4. Open removal again and click **Yes, I'm sure** (the native button uses a curly
   apostrophe). Refresh `/events/{A-id}` and `/events/{B-id}` in a private window:
   A has one fewer reading, B retains that resource and its reason/order. Verify
   **Resources → original resource ID** still exists with unchanged fields.
5. At 375 px and desktop widths, check the operation and full target text are
   visible, with no horizontal overflow. An account lacking EventResource delete
   permission must not have the action; its direct confirmation POST must fail.

Stop your server with Ctrl+C and restore the prior PG17 running state. Re-link
test data only if you intentionally want to restore it; removing a link does not
restore it automatically. The assistant passed five disposable-database browser
scenarios; the user then confirmed step 27. Step 28 was subsequently
implemented; see the current permission/CSRF validation above.

## Step 26 validation — shared bibliography and reading order

### Automated acceptance (isolated PostgreSQL 17)

Check the existing project instance and start it only if stopped. Do not run init.

~~~powershell
Set-Location G:\STUDY\psych-talk-hub\backend
.\.venv\Scripts\python.exe scripts/local_database.py status
# Only if stopped:
# .\.venv\Scripts\python.exe scripts/local_database.py start
$step26PreviousMode = $env:DJANGO_ENV
try {
    $env:DJANGO_ENV = 'test'
    .\.venv\Scripts\python.exe manage.py test events.tests.test_admin_reading_edits events.tests.test_admin --noinput --verbosity 2
    if ($LASTEXITCODE -ne 0) { throw 'Step 26 Admin tests failed.' }
} finally {
    if ($null -eq $step26PreviousMode) {
        Remove-Item Env:DJANGO_ENV -ErrorAction SilentlyContinue
    } else {
        $env:DJANGO_ENV = $step26PreviousMode
    }
}
~~~

Expected: **29 tests / OK**, no system issues and `test_psychtalk` destroyed.
To run only the 8 new cases, omit `events.tests.test_admin`. The new cases block
external HTTP and use real Admin form submissions followed by fresh anonymous
API reads. For full regression, [follow the complete commands below](#2-complete-regression-isolated-local-postgresql):
build the current frontend, run Django/migration checks and the expected **311 tests / OK**.
Stop PG17 only if you started it; preserve a previously running instance.

| Acceptance case | Expected |
| --- | --- |
| Existing Resource edit GET | Shared-impact warning before fields; no business write |
| Resource add form | No existing-resource warning |
| Save shared title/authors/year/URL/type | Both referencing talks show the new bibliography on next read; original DOI/source/seed and link fields retained |
| Change only A recommendation, including clearing it | Only that association changes; B and shared bibliography remain unchanged |
| Change only A numeric display order | A reading moves; its reason, B and shared bibliography remain unchanged |
| Default 0, negative/custom numbers, equal values | Order ascending, then association ID ascending; repeat reads and reverse edit order stay deterministic |
| Invalid/blank/fractional/out-of-range integer or invalid shared bibliography | Field errors and entered values retained; no partial business edit; shared warning still shown |

### Local Admin acceptance

The automated suite writes disposable test databases only. Manual saves below
**change your development database**. Use suitable local test talks and your
existing private administrator. Keep original values if you intend to restore them.

Build and collect the current assets first, then start Django so the same server
can serve Admin and the React public pages:

~~~powershell
Set-Location G:\STUDY\psych-talk-hub\frontend
& 'G:\Program Files\nodejs\npm.cmd' run build
if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed.' }
Set-Location G:\STUDY\psych-talk-hub\backend
$env:DJANGO_ENV = 'development'
.\.venv\Scripts\python.exe manage.py collectstatic --noinput
if ($LASTEXITCODE -ne 0) { throw 'Static collection failed.' }
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000 --nostatic
~~~

1. In `http://127.0.0.1:8000/admin/`, choose two local Events A and B referencing
   the **same Resource ID**. If needed, use **Event resources → Add** to select that
   existing resource for the missing talk. Include a second reading in A to observe order.
2. Open **Resources → that shared resource**. Before its fields, confirm:
   `Changes to this resource will appear in every talk that uses it.`
   Change its title and Save. Open `/events/{A-id}` and `/events/{B-id}` in a private
   visitor window and refresh: both must show the new title. DOI/source remain readonly.
3. In **Event resources**, filter by A, open its association and change only
   **Recommendation**. Save and refresh both public pages: only A's reason changes.
   The Event and Resource identities are readonly; B's reason/order stay unchanged.
4. Change only A's **Display order** to `-1`, then to a value greater than A's
   second reading. Save/refresh each time: the card moves earlier/later, retaining
   its reason. B's order remains unchanged. Set both A orders to `0`: ties follow
   association ID ascending. The add form's default is `0`.
5. Submit a fractional value such as `1.5`: a field error must appear and the
   previous public data remain unchanged. Check the Resource edit warning at
   desktop and 375 px widths; it wraps visibly above the fields.

Stop the server with Ctrl+C and restore the prior database state. Do not remove
associations as part of step 26 acceptance. Step 26 is user-accepted;
step 27 requires a new explicit implementation instruction.

Browser evidence: ignored `.tools/step26-browser` holds a disposable LiveServer,
CDP checker, results and inspected screenshots. Six real scenarios passed at
2026-10-06T19:35:57.550Z, including CSRF login/native saves, shared updates, A-only
context edits, default tie order, mobile warning and logged-out React reads/refresh.
All external HTTP was blocked. This adds no browser dependency or CI framework.

## Step 25 validation — Admin confirmation

### Automated acceptance (isolated PostgreSQL 17)

From PowerShell, check the existing project instance. If stopped, start that
instance only; do not run `init`. Preserve a previously running instance.

~~~powershell
Set-Location G:\STUDY\psych-talk-hub\backend
.\.venv\Scripts\python.exe scripts/local_database.py status
# Only if stopped:
# .\.venv\Scripts\python.exe scripts/local_database.py start
$step25PreviousMode = $env:DJANGO_ENV
try {
    $env:DJANGO_ENV = 'test'
    .\.venv\Scripts\python.exe manage.py test events.tests.test_doi_confirmation events.tests.test_doi_confirmation_concurrency --noinput --verbosity 2
    if ($LASTEXITCODE -ne 0) { throw 'Step 25 confirmation tests failed.' }
} finally {
    if ($null -eq $step25PreviousMode) {
        Remove-Item Env:DJANGO_ENV -ErrorAction SilentlyContinue
    } else {
        $env:DJANGO_ENV = $step25PreviousMode
    }
}
~~~

Expected: **28 tests / OK**, no system issues, `test_psychtalk` destroyed.
The 24 TestCase and 4 TransactionTestCase methods block external HTTP and mock
Crossref. For combined preview regression, add `events.tests.test_doi_preview
events.tests.test_doi_preview_concurrency` to that test command: **54 tests / OK**.
For full regression, follow the [complete commands below](#2-complete-regression-isolated-local-postgresql):
build the current frontend, run Django/migration checks and the expected **311 tests / OK**.
Stop PG17 after checks only if you started it; never run tests in production.

| Acceptance case | Expected |
| --- | --- |
| Fetch / GET / Check details | No Resource or EventResource writes |
| Confirm new DOI | Reviewed bibliography, crossref source, target link and session result committed together; anonymous API sees reading |
| Saved DOI / created or edited since preview | Current DB bibliography readonly and preserved; only missing target link created |
| Duplicate link / repeated confirmation | Original link ID, reason/order retained; result GET and existing-record/public links |
| Removed original success link, even if pair recreated | Old preview rejected; no replacement link created |
| 899 / 900 / 901 seconds, including waits | Before deadline valid; at/after invalid and writes rolled back; no renewal |
| Cancel, wrong session/admin/target, logout, password change, missing state | No save, safe invalid state or authentication response |
| Deleted event / revoked permission / invalid CSRF | No save; target missing or forbidden; final transaction rechecks cached view permissions |
| Missing title/HTTP(S) URL / invalid year/type/order | Field errors, input retained; optional authors/year allowed |
| Link database error / session result write error | New records and success state rolled back; input/buttons preserved, unexpired preview can retry |
| Real concurrent confirmations and cancellation | One DOI identity and one link per target; successful results merge; original connections remain usable |

### Local Admin acceptance

The automated commands only write disposable test databases. The following
manual Save to event **does write your development database**. Use your existing
private local Admin and a suitable saved Event; do not use production credentials.

~~~powershell
Set-Location G:\STUDY\psych-talk-hub\backend
$env:DJANGO_ENV = 'development'
.\.venv\Scripts\python.exe manage.py runserver
~~~

1. Open `http://127.0.0.1:8000/admin/`, choose an Event, then **Import reading by DOI**.
   The target talk title must stay visible. Fetch an existing saved DOI; shared
   bibliography is readonly. Fetch and **Check details** must leave reading unchanged.
2. Enter recommendation and display order, then **Save to event**. During submit
   the current form controls disable and show **Saving…**. A new link displays
   `Resource added to this talk.`; an already linked resource displays
   `This resource is already linked to this talk.` with its original fields.
3. Follow **View public talk page** and refresh anonymously. The saved reading,
   recommendation and order must appear. Refresh the result page or submit the
   original form again within its original deadline: no duplicate or overwrite.
4. Open two independent preview addresses. Cancel one; reopening/saving that
   address must show `This preview is no longer valid. Fetch metadata again.`
   The other remains usable. The automated suite covers exact expiry, removed
   result rejection, real concurrency, revoked permissions and forced rollback.
5. For a new DOI, title and HTTP(S) URL are required; authors/year may be empty.
   Actual development fetch may call real Crossref; the assistant's checks used
   simulated metadata and do not claim real integration. Real integration remains
   step 29. If unavailable, use the automated acceptance rather than production.

Stop your runserver with Ctrl+C and restore PG17 only if you started it.
Step 25 is user-accepted. Step 26 is user-accepted; see the guide above.

Browser evidence: `.tools/step25-browser` is ignored, temporary verification
material. A disposable LiveServer test collected the current bundle into its own
static directory and served it through WhiteNoise. Eight real scenarios passed,
including a simulated result-write failure, successful retry and logged-out React
reading/refresh; screenshots were inspected. This is separate from the 28
permanent PostgreSQL confirmation tests and introduces no dependency/CI framework.

## Step 24 validation — Admin DOI previews

Step 24 is user-accepted. Its original 26 tests remain the preview regression;
step 25 above now supplies Save to event and saved-result handling. Historical
step 24 evidence was preview-only; follow step 25 for current confirmation acceptance.

### Automated acceptance (isolated PostgreSQL 17)

From PowerShell, check the existing project instance first:

~~~powershell
Set-Location G:\STUDY\psych-talk-hub\backend
.\.venv\Scripts\python.exe scripts/local_database.py status
~~~

If stopped, run `.\.venv\Scripts\python.exe scripts/local_database.py start`.
Do not run `init`. Leave a previously running instance running. Then:

~~~powershell
$step24PreviousMode = $env:DJANGO_ENV
try {
    $env:DJANGO_ENV = 'test'
    .\.venv\Scripts\python.exe manage.py test events.tests.test_doi_preview events.tests.test_doi_preview_concurrency --noinput --verbosity 2
    if ($LASTEXITCODE -ne 0) { throw 'Step 24 preview tests failed.' }
} finally {
    if ($null -eq $step24PreviousMode) {
        Remove-Item Env:DJANGO_ENV -ErrorAction SilentlyContinue
    } else {
        $env:DJANGO_ENV = $step24PreviousMode
    }
}
~~~

Expected: **26 tests / OK**, no system issues, `test_psychtalk` destroyed.
There are 23 request/state TestCase methods and 3 TransactionTestCase methods.
External HTTP is blocked and Crossref is simulated. No install or new migration
is required. Stop the project instance after all checks only if you started it;
never run tests in production.

| Acceptance case | Expected |
| --- | --- |
| Fetch new / existing DOI | New preview only; saved DOI makes no provider request; three business models unchanged |
| Provider failure / invalid DOI | Safe message, raw input retained, retry/manual option; other previews unchanged |
| Existing bibliography / later shared edit | Complete escaped text, readonly server fields, current DB values; only reason/order editable |
| Incomplete new bibliography | Title and HTTP(S) URL required; authors/year optional; invalid check keeps entered values |
| Two previews / cancellation | Independent random IDs; cancelling one leaves the other intact |
| Same-session concurrent fetch / cancel / ordinary session save | Real independent PG connections retain latest merged previews; no resurrection or broken transaction |
| Session, user, target, DOI or source substitution | Server binding wins; another session or changed target rejected; public API exposes no preview IDs |
| 899 / 900 / 901 seconds | Valid before deadline, invalid at/after; checks/retries do not renew original preview |
| Permissions / real CSRF / logout / deleted event | Forbidden or invalid state; no business writes; existing unrelated data preserved |
| Check details / unknown action | Check only validates; unknown action rejected; Save to event is covered by step 25 above |

Concurrent fetches run three coordinated rounds with distinct PostgreSQL backend
PIDs in the same test database, synchronizing immediately before actual session
row locks. Additional races cover cancellation versus fetching and a stale ordinary
session save. Sequential checks cover SAVE_EVERY_REQUEST, original db-session
compatibility, deleted-session UpdateError, state-write rollback, and safe long
bibliography display. These tests do not prove step 25 result/save transactions.

For full regression, follow the [complete commands below](#2-complete-regression-isolated-local-postgresql):
build the current frontend first, set `DJANGO_ENV=test`, run Django/migration
checks and the full suite. Expected now: **311 tests / OK**, `No changes detected`
and destroyed test database. Frontend source is unchanged in step 24.

### Local Admin acceptance

Use your existing development account/data. With project PG17 running, start
Django in a separate PowerShell terminal:

~~~powershell
Set-Location G:\STUDY\psych-talk-hub\backend
$env:DJANGO_ENV = 'development'
.\.venv\Scripts\python.exe manage.py runserver
~~~

1. Open `http://127.0.0.1:8000/admin/`, sign in with your existing private local
   administrator, open a saved Event, then **Import reading by DOI**. The target
   title must remain visible throughout the flow.
2. Choose a DOI already shown on an existing Resource. Fetch it; all shared
   bibliography appears as readonly text. Only recommendation/display order can
   be entered. **Check details** shows `Details checked. No resource has been saved.`
   and creates no Resource or association.
3. Open the DOI entry in two tabs and fetch separately. They must have different
   preview addresses. Cancel one, then refresh it: `This preview is no longer valid.
   Fetch metadata again.` The other preview remains usable; cancellation returns
   to the target Event.
4. Invalid DOI displays its field error and retains input. A new, valid DOI may
   contact real Crossref in development; this external scenario was **not** run
   by the assistant. If it returns missing title/URL, Check details must reject
   missing required fields; authors/year may stay empty. Provider failures offer
   correction/retry/manual entry. The automated suite covers these states without
   external access or adding development records.
5. Compare the Event detail API and Resource/link Admin lists before/after fetch,
   check and cancellation: business records and public reading remain unchanged.
   Use Check details and cancellation for this preview-only check; Save to event
   now publishes as described in step 25. Inspect the page at desktop and
   375 px, labels, readonly text, pending control and keyboard navigation.

If you have no suitable existing local account/event/DOI, use the automated
acceptance instead; its accounts and fixtures are disposable and do not populate
the development database. Do not create production accounts/data for this check.
Stop your runserver with Ctrl+C afterwards, and restore project PG17 only if you
started it for acceptance. Steps 24–25 are user-accepted, as described above.

Assistant browser evidence uses a temporary StaticLiveServerTestCase with
`test_psychtalk_step24_browser`, a test-only Admin and mocked provider. Eight
scenarios passed; desktop/mobile screenshots were inspected and business snapshots
were identical. `.tools/step24-browser` is ignored verification material, not a
new dependency or CI framework. It tests independent preview addresses; true
concurrent same-session requests are covered by the permanent PostgreSQL tests.
## Step 23 validation — concurrent DOI saves

Assistant evidence: **28 save tests / OK (5.199 s)**, Vite build (255 ms), clean
Django/migration checks and **211 full tests / OK (15.777 s)**. The user replied “通过” on 6 October 2026, confirming step 23 local acceptance. No new individual output was supplied; this handoff only updates documentation, with no test rerun, code/database change, process operation or publication. At that handoff there was no Admin DOI form; step 24 provides preview/check/cancel and step 25 above now provides confirmation.

### Targeted save and concurrency tests

Use the existing local PostgreSQL 17 instance. Check first:

~~~powershell
Set-Location G:\STUDY\psych-talk-hub\backend
.\.venv\Scripts\python.exe scripts/local_database.py status
~~~

If stopped, run `.\.venv\Scripts\python.exe scripts/local_database.py start`.
Do not run `init`. Then:

~~~powershell
$step23PreviousMode = $env:DJANGO_ENV
try {
    $env:DJANGO_ENV = 'test'
    .\.venv\Scripts\python.exe manage.py test events.tests.test_resource_save events.tests.test_resource_save_concurrency --noinput --verbosity 2
    if ($LASTEXITCODE -ne 0) { throw 'Step 23 save tests failed.' }
} finally {
    if ($null -eq $step23PreviousMode) {
        Remove-Item Env:DJANGO_ENV -ErrorAction SilentlyContinue
    } else {
        $env:DJANGO_ENV = $step23PreviousMode
    }
}
~~~

Expected: **28 tests / OK**, no system issues, and `test_psychtalk` destroyed.
This includes the 14 step 22 methods and 14 new methods in
[test_resource_save_concurrency.py](events/tests/test_resource_save_concurrency.py).
All require isolated PostgreSQL; tests block Requests HTTP. No install or schema
migration is needed. Stop the project instance afterwards only if you started it
for testing; leave a previously running instance running. Never test production.

| Case | Expected result |
| --- | --- |
| Two requests, new DOI, same talk | One Resource/one link; both return the same IDs and winner's fields |
| Two requests, new DOI, different talks | One Resource/two links; shared winner bibliography and each talk's own reason/order |
| Two requests, existing DOI, same talk | One link; current Resource fields/source/seed and winner's link preserved |
| Winner commits before loser's full_clean | Only the exact DOI/pair uniqueness error is recovered |
| One request loses DOI then link races | Both conflicts recovered after rollback; third attempt returns the saved link |
| Caller fails after recovered save | Its new link rolls back; independently committed winner remains |
| Other unique/check/NOT NULL/database or mixed validation failure | Original error propagates; no partial writes and connection remains usable |
| No saved winner or repeated same conflict | Error propagates; no unlimited retry |

The first three cases each run three coordinated rounds. TransactionTestCase
workers open independent connections, assert different PostgreSQL backend PIDs and
the same test database, and synchronize immediately before real INSERTs after
full_clean. PostgreSQL actually raises the unique error; it is not mocked.
Recovery probes and later queries use the same worker connection to verify rollback
completed. Model validation races use a coordinated commit before full_clean.
OperationalError is simulated; seed/primary-key/check errors use real PostgreSQL.

### Recovery boundary and complete regression

[resource_save.py](events/services/resource_save.py) catches errors outside each
atomic attempt. SQL recovery requires `23505`, the exact table and DOI/pair
constraint; model recovery requires only the exact uniqueness code and model/field
parameters. It then verifies a saved winner and rereads current records. Each
identity can be recovered once, giving at most three attempts. Other errors
propagate. Existing bibliography/reason/order remain unchanged; created flags
describe the successful attempt. Outer-transaction rollback still applies.

Follow the [complete regression commands below](#2-complete-regression-isolated-local-postgresql):
build the current frontend, use `DJANGO_ENV=test`, check Django and missing migrations,
and run the full isolated suite. Expected: **311 tests / OK**, `No changes detected`,
and test database destroyed. This service has no HTTP/session/route; Admin preview
is implemented in step 24; confirmation is implemented in step 25 above. Steps 23–25 are user-accepted; step 26 has not started and needs a new explicit implementation instruction.

## Step 22 validation — atomic DOI save and reuse

The assistant's local evidence is **14 save tests / OK (0.783 s)**, current Vite
build, clean Django/migration checks and **197 full tests / OK (13.510 s)**.
The user replied “通过” and later “通过22”, confirming step 22 local acceptance. No individual output was supplied; confirmation only updates documentation, with no test rerun, code/database change, process operation or publication. At the step 22 handoff there was no Admin import/save button;
validate the service directly with the tests below. No install or new migration
is required. Concurrent competing requests and uniqueness recovery were subsequently implemented in step 23 above;
Preview is implemented in step 24; confirmation is now implemented in step 25 above.

### Targeted save tests (isolated PostgreSQL 17 required)

Use the existing project instance. Check its status first:

~~~powershell
Set-Location G:\STUDY\psych-talk-hub\backend
.\.venv\Scripts\python.exe scripts/local_database.py status
~~~

If stopped, start only that existing instance with
`.\.venv\Scripts\python.exe scripts/local_database.py start`; do not run `init`.
Leave an already-running instance running. Then execute:

~~~powershell
$step22PreviousMode = $env:DJANGO_ENV
try {
    $env:DJANGO_ENV = 'test'
    .\.venv\Scripts\python.exe manage.py test events.tests.test_resource_save --noinput --verbosity 2
    if ($LASTEXITCODE -ne 0) { throw 'Step 22 save tests failed.' }
} finally {
    if ($null -eq $step22PreviousMode) {
        Remove-Item Env:DJANGO_ENV -ErrorAction SilentlyContinue
    } else {
        $env:DJANGO_ENV = $step22PreviousMode
    }
}
~~~

Expected: **14 tests / OK**, no system issues, and `test_psychtalk` destroyed.
Unlike the 44 lookup tests, all these new methods require PostgreSQL. If you
started the instance only for your testing, stop it afterwards with the project
tool; otherwise preserve its running state. Do not test against production.

Review the verbose test names in [test_resource_save.py](events/tests/test_resource_save.py):

| Acceptance case | Expected saved result |
| --- | --- |
| New DOI | One Resource and one EventResource; normalized DOI, reviewed fields, crossref source |
| Same DOI added to another talk | Same Resource; only one additional link with that talk's reason/order |
| Repeated save with changed fields/reason/order | Original link returned; no count or stored-field change |
| Existing link edited/cleared before retry | Current saved reason/order returned and preserved |
| DOI resource created or edited after preview | Current database bibliography reused, including deliberately empty optional values/source/seed identity |
| Existing DOI without preview fields | Saved resource reused without fetching or needing new bibliography |
| Invalid new bibliography or link values | ValidationError; no partial Resource/link, submitted mapping unchanged |
| Invalid DOI or deleted target | Refused before any new business record; invalid DOI has zero queries |
| Actual PostgreSQL link write fails | Newly inserted Resource rolled back; original error propagates and the connection can be reused |
| Caller transaction fails after service success | Both new records rolled back with the caller |

The after-preview cases simulate another save/edit sequentially; they do not
prove simultaneous requests. Every test blocks Requests HTTP. The database-error
case deliberately bypasses model validation to trigger PostgreSQL NOT NULL,
then verifies complete snapshots and a successful subsequent explicit save.

### Save service contract and remaining integration

[resource_save.py](events/services/resource_save.py) exposes keyword-only
`save_doi_to_event(event_id=..., doi=..., bibliography=..., recommendation=..., display_order=...)`.
`bibliography` is an optional mapping of reviewed values, such as `dataclasses.asdict`
of CrossrefMetadata with required fields supplemented. For a new DOI only
`title`, `authors`, `year`, `original_url`, `resource_type` initialize bibliography;
DOI comes from the separate normalized identity and source is fixed to `crossref`.
Extra fields (including submitted DOI/source/seed/id/abstract) are ignored. Model
validation still enforces required title/HTTP(S) URL and other saved-field rules.

Existing resources ignore all preview bibliography; existing links ignore new
recommendation/order. `DoiSaveResult` returns `resource`, `association`,
`resource_created`, `association_created`. These flags distinguish creation/reuse
without changing stored data. Other validation/database/target errors propagate
after rollback; step 23 above now recovers only verified identity conflicts. The service makes no HTTP request, does not store sessions, and
joins the step 25 outer transaction for confirmation-result persistence.

The step 25 Admin caller verifies permissions and trusted server preview/target
identity before calling; this service has no standalone public route. Preview
expiry and cancellation are implemented in step 24 above; successful-result
replay and removed-result rejection are now implemented in step 25 above. No concurrent-conflict handler or concurrency tests were
added in step 22. Step 22 is user-accepted; step 23 was subsequently implemented and user-accepted as described above.

### Full regression

Follow the [complete regression commands below](#2-complete-regression-isolated-local-postgresql):
build the current frontend first, use `DJANGO_ENV=test`, run Django checks,
migration omission check and the full suite on local isolated PostgreSQL.
Expected: **311 tests / OK**, `No changes detected` and the temporary database
destroyed. This includes 28 step 25 confirmation methods, 26 step 24 preview/session methods, 14 step 22 save methods, 14 step 23 concurrency/boundary methods and all previous 183 methods,
including the four PostgreSQL Crossref success/failure persistence checks.

## Step 21 validation — Crossref lookup errors

On 6 October 2026 the user asked the assistant to verify directly. The rerun
passed all 44 targeted tests (0.211 s), frontend build, Django/migration checks
and all 183 backend tests (12.824 s), including the failure/persistence checks.
The test database was destroyed and pre-existing PostgreSQL PID 6588 preserved.
No application fix was needed. The user subsequently replied “通过”, confirming
step 21 local acceptance. The confirmation only updates documentation, with no
test rerun, code/database changes or process operations. At that acceptance handoff, step 22 had not started. Its subsequent implementation and current acceptance guide are above.

Step 21 updated the lookup service only. Step 24 now connects the Admin DOI
form and recovery choices, as described above. No installation
or migration is required. Ordinary tests never contact real Crossref.

### Targeted DOI, conversion and failure tests (no PostgreSQL)

~~~powershell
Set-Location G:\STUDY\psych-talk-hub\backend
$step21PreviousMode = $env:DJANGO_ENV
try {
    $env:DJANGO_ENV = 'test'
    .\.venv\Scripts\python.exe manage.py test events.tests.test_doi events.tests.test_crossref_metadata.CrossrefConversionTests events.tests.test_crossref_metadata.CrossrefSuccessfulFetchTests events.tests.test_crossref_errors.CrossrefErrorTests --noinput --verbosity 2
    if ($LASTEXITCODE -ne 0) { throw 'Step 21 lookup tests failed.' }
} finally {
    if ($null -eq $step21PreviousMode) {
        Remove-Item Env:DJANGO_ENV -ErrorAction SilentlyContinue
    } else {
        $env:DJANGO_ENV = $step21PreviousMode
    }
}
~~~

Expected: **44 tests / OK**, no system issues and no database setup. This combines
the existing 32 DOI/conversion tests with 12 new database-free failure tests in
[test_crossref_errors.py](events/tests/test_crossref_errors.py).

| Simulated failure | Safe result and recovery |
| --- | --- |
| Invalid DOI | Existing `ValidationError`, code `invalid_doi`, `Enter a valid DOI or DOI link.`; no HTTP call |
| HTTP 404 | `CrossrefLookupError`, code `not_found`, `No publication was found for this DOI.`; correct input or add manually |
| HTTP 429 | Code `rate_limited`; explicit retry or manual entry, no automatic retry or Retry-After wait |
| HTTP 5xx | Code `upstream_error`; explicit retry or manual entry |
| Other non-200 status, redirects, bad JSON or wrong work envelope | Code `invalid_response`; explicit retry or manual entry |
| Connection, TLS or proxy failure | Code `connection_failed`; explicit retry or manual entry |
| Connection/read timeout | Code `timeout`; explicit retry or manual entry |
| Other Requests transport failures | Code `provider_unavailable`; explicit retry or manual entry |

Every provider failure except 404 uses the exact message:
**We couldn't fetch publication details. Please try again or add the resource manually.**
These are service messages and recovery flags; visible Admin actions remain later work.

`CrossrefLookupError.input_value` preserves the exact submitted value, including
case/outer whitespace, for a future bound form. `can_add_manually` is true for
provider errors; `can_retry` is false for 404 (correct the DOI first), true for
other lookup failures. Exception text contains only the safe message. No provider
body, URL or connection details are inserted; underlying JSON/transport exception
chains are suppressed. No service logging/session persistence is added.

Check verbose test names for: one actual Requests adapter call per fetch, fixed
encoded target/TLS/timeouts, no followed redirects or hidden retries, response
closure on failure, safe malformed/nested JSON, retained input, and a separate
explicit retry succeeding. Invalid input is rejected before HTTP. Valid but
incomplete work remains a reviewable success under step 20 rules. Unexpected
programming errors are not swallowed as provider errors.

### Full regression and unchanged business data (isolated PostgreSQL)

Follow the [complete regression commands below](#2-complete-regression-isolated-local-postgresql):
build the current frontend, check/start only the existing project PostgreSQL 17
if needed, select `DJANGO_ENV=test`, run Django/migration checks and all tests,
then preserve the prior PostgreSQL state.

Expected: **311 tests / OK**, `No changes detected`, and the temporary test database
destroyed. This includes all 14 new step 21 methods. In `CrossrefFailurePersistenceTests`,
both of these must pass:

- `test_all_http_and_response_failures_leave_counts_and_complete_fields_unchanged`
- `test_transport_failures_and_invalid_input_leave_all_business_data_unchanged`

They assert zero business queries during failed lookup and compare every stored
field in Event, Resource and EventResource before/after each case, covering both
new and saved DOI identities, shared/unlinked resources and edited/cleared data.
They require isolated PostgreSQL and are excluded from the 44-test command.

To run only all 14 step 21 tests, use
`manage.py test events.tests.test_crossref_errors --noinput --verbosity 2`
with the same isolated environment and running project PostgreSQL instance.

There is no confirmation/save action yet; confirmation avoiding Crossref must be
verified by the actual step 25 confirmation tests above. Atomic save/reuse is now implemented in
step 22 and preview UI in step 24; real integration remains step 29. The assistant's
checks and subsequent user acceptance are separate evidence. Step 21 is now
user-accepted; step 22 was subsequently implemented under a new instruction; see the current guide above.

## Step 20 validation — Crossref successful metadata conversion

Step 20 added backend conversion and a successful lookup service. The Admin
DOI form and preview are now implemented in step 24 above. No installation or
migration is required. Test fixtures are synthetic, not claims about real papers.

### Conversion and DOI regression without PostgreSQL or external HTTP

~~~powershell
Set-Location G:\STUDY\psych-talk-hub\backend
$step20PreviousMode = $env:DJANGO_ENV
try {
    $env:DJANGO_ENV = 'test'
    .\.venv\Scripts\python.exe manage.py test events.tests.test_doi events.tests.test_crossref_metadata.CrossrefConversionTests events.tests.test_crossref_metadata.CrossrefSuccessfulFetchTests --noinput --verbosity 2
    if ($LASTEXITCODE -ne 0) { throw 'Step 20 conversion tests failed.' }
} finally {
    if ($null -eq $step20PreviousMode) {
        Remove-Item Env:DJANGO_ENV -ErrorAction SilentlyContinue
    } else {
        $env:DJANGO_ENV = $step20PreviousMode
    }
}
~~~

Expected: **32 tests / OK**, no system issues and no database setup. Check the
verbose names in [test_crossref_metadata.py](events/tests/test_crossref_metadata.py):

- First nonempty title wins; empty/non-string entries are skipped, later titles
  are not joined. An overlength first title stays available for correction.
- Personal given/family names and organisation `name` entries retain source order,
  joined with `; `. Partial names work; absent authors remain `""`.
- Print, online, then issued provide the first integer year in 1–9999. Invalid
  preferred values fall back; booleans, strings and floats are not coerced.
  Missing dates become `None`; date ranges use the first start date only.
- Journal/proceedings articles become `research_paper`; other types become
  `article`. Source is always `crossref`; abstracts/summaries are excluded.
- Only the returned HTTP(S) `URL` is used. Missing/invalid URLs stay empty; there
  is no fabricated resolver or alternate-link fallback. Valid URL case, path,
  query and fragment remain intact after surrounding whitespace is trimmed.
- `missing_required_fields` marks title/URL requiring completion or correction.
  `needs_review` also flags missing optional authors/year, which remain valid
  optional values. These are service results; Admin notices are not connected yet.
- The requested normalized DOI remains the identity. A mocked successful fetch
  prepares one fixed encoded Crossref request with `(3, 7)` timeouts, TLS checking
  and redirects disabled, then closes its response. No automatic retry occurs.

### Complete regression and persistence boundary

Follow the [isolated PostgreSQL regression commands below](#2-complete-regression-isolated-local-postgresql):
build the current frontend first, preserve the project's prior PostgreSQL state,
select `DJANGO_ENV=test`, then run checks and the full test suite.

Expected now: **311 tests / OK**, `No changes detected` and the temporary test
database destroyed. The historical step 20 run passed 169 tests; the current
suite also includes 14 step 21, 14 step 22 and 14 step 23 tests. This includes all 18 step 20 tests. The two PostgreSQL
tests in `CrossrefPersistenceBoundaryTests` assert zero business queries during
fetch/conversion, unchanged complete Event/Resource/EventResource snapshots, and
actual model rejection of missing/invalid/overlength required metadata. Those two
tests are deliberately excluded from the 32-test database-free command above.

To run only step 20's 18 tests instead of the full suite, use
`manage.py test events.tests.test_crossref_metadata --noinput --verbosity 2`
with the same isolated environment and running PostgreSQL instance.

`crossref_metadata.py` contains the pure converter and immutable result;
`crossref.py` retains raw `request_doi` and adds `fetch_metadata`. The result can
be turned into ordinary field values with `dataclasses.asdict`; it is never saved
by the lookup service. Future forms must supplement required fields and revalidate
before persistence. Step 21 now maps expected provider/JSON/transport exceptions
to safe messages; see the current validation above. Real integration remains step 29.

The assistant's checks and user acceptance are separate evidence. The user
confirmed steps 20 and 21 on 6 October 2026. At that acceptance handoff, step 22 had not started.

## Step 19 validation — DOI normalization and fixed request target

Historical step 19 acceptance: the user replied “通过” on 5 October 2026 without
individual outputs. The assistant's step 19 checks were 16 targeted/151 complete
tests. The commands remain usable; the current complete suite discovers 311 tests,
all passed by the assistant during step 28 verification.

This step adds backend services and tests, with no new Admin form or public API.
At step 19, metadata conversion, preview and persistence were still planned.
Use the existing virtual environment; no installation or migration is required.

### 1. Targeted acceptance (no database or external HTTP)

~~~powershell
Set-Location G:\STUDY\psych-talk-hub\backend
$step19PreviousMode = $env:DJANGO_ENV
try {
    $env:DJANGO_ENV = 'test'
    .\.venv\Scripts\python.exe manage.py test events.tests.test_doi --noinput --verbosity 2
    if ($LASTEXITCODE -ne 0) { throw 'Step 19 tests failed.' }
} finally {
    if ($null -eq $step19PreviousMode) {
        Remove-Item Env:DJANGO_ENV -ErrorAction SilentlyContinue
    } else {
        $env:DJANGO_ENV = $step19PreviousMode
    }
}
~~~

Expected: **16 tests / OK**, no system issues and no database setup. Cases use
synthetic identifiers, not claims about real publications. Review the verbose
test names and [test_doi.py](events/tests/test_doi.py) for these acceptance groups:

- Bare DOI, HTTPS doi.org link, encoded path, case and surrounding whitespace
  produce the same identity. Registrants accept exactly 4–9 ASCII digits.
- Empty input, bad prefix/registrant, missing suffix and internal whitespace
  fail with `Enter a valid DOI or DOI link.` before HTTP is called.
- Reject alternate hosts/schemes, credentials, every explicit port (even 443 or
  an empty port), query and fragment delimiters (including bare `?` and `#`).
- Preserve suffix punctuation/plus. Decode link paths once, never bare DOI text;
  `%252F` becomes literal `%2f`, not `/`. Encoded whitespace is rejected.
- Encode the entire DOI under the fixed Crossref works endpoint. Real Requests
  preparation runs with the HTTP adapter mocked; punctuation cannot become a
  query, fragment or alternate target. Twenty redirect combinations make one
  adapter call each; automatic redirects are disabled for all destinations.

`normalize_doi` lives in services/doi.py and has no network/database access.
`request_doi` in services/crossref.py returns a raw Requests Response with
connection/read timeouts `(3, 7)`, TLS verification and no retries or redirects.
Callers must close raw responses and handle provider status/JSON. Step 20 now
provides `fetch_metadata` for successful conversion; the raw transport is unchanged.

### 2. Complete regression (isolated local PostgreSQL)

Build the current frontend first for the real-asset tests:

~~~powershell
Set-Location G:\STUDY\psych-talk-hub\frontend
& 'G:\Program Files\nodejs\npm.cmd' run build
if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed.' }
Set-Location G:\STUDY\psych-talk-hub\backend
.\.venv\Scripts\python.exe scripts/local_database.py status
~~~

If stopped, start only the existing project instance with
`.\.venv\Scripts\python.exe scripts/local_database.py start`; do not run `init`.
Then run:

~~~powershell
$regressionPreviousMode = $env:DJANGO_ENV
try {
    $env:DJANGO_ENV = 'test'
    .\.venv\Scripts\python.exe manage.py check --database default
    if ($LASTEXITCODE -ne 0) { throw 'Django checks failed.' }
    .\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
    if ($LASTEXITCODE -ne 0) { throw 'A migration is missing.' }
    .\.venv\Scripts\python.exe manage.py test --noinput --verbosity 1
    if ($LASTEXITCODE -ne 0) { throw 'Backend regression failed.' }
} finally {
    if ($null -eq $regressionPreviousMode) {
        Remove-Item Env:DJANGO_ENV -ErrorAction SilentlyContinue
    } else {
        $env:DJANGO_ENV = $regressionPreviousMode
    }
}
~~~

Expected now: no system issues, `No changes detected`, **311 tests / OK**, and the
test database destroyed. Some existing fault simulations log 404/500 responses;
the final test result determines success. Development business records are not
modified. If you started PostgreSQL for testing, stop it afterwards with the
project tool; otherwise preserve its existing running state. Step 21 is now
user-accepted; steps 22–25 are user-accepted; step 26 is user-accepted; step 27
passed assistant verification and user acceptance; step 28 passed assistant
verification and user acceptance. Step 29's real integration passed assistant
verification and user acceptance. Step 30's current 311-test regression passed;
current remote CI remains pending. The subsequent explicitly authorised step 31
state checks passed locally and are user-accepted; step 32 has not started.

## Historical step 17 handoff: user-confirmed on 5 October 2026

Last user-accepted step is 17. Step 17 adds the built React template, declared
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
The user subsequently authorised Free resource creation/deployment. Release
d8bdd29 is Live on Render; actual migrations preceded Gunicorn startup and
11 HTTP/six browser checks passed. The final build command's redeployment also
reached Live and all online checks passed again. The user confirmed step 17 on
5 October 2026;
step 18 was subsequently user-confirmed. Current step 19 checks are recorded above.
Older sections retain their historical counts/evidence; current results are in
[progress.md](../memory-bank/progress.md).

Both a174723 and actual release d8bdd29 have successful frontend/backend CI;
the release check is [Project checks 37242897644](https://github.com/1uxury/psych-talk-hub/actions/runs/37242897644).
The [live site](https://psych-talk-hub.onrender.com) uses one Free Python service
and Free PostgreSQL 17 in Frankfurt, with auto-deploy off. Subsequent user-authorised
TLS initialization created two fictional talks, six resources/links and a private
administrator; repeat import created nothing and preserved existing fields.
Ten nonempty browser checks and actual Admin login/CSRF/save/anonymous refresh
passed. Temporary recommendation text was restored, check sessions logged out and
external database access disabled again. Some source websites return 403 to
automated reads; no guarantee of freely accessible full text is implied.
Nonempty redeploy preservation, backup/restore and complete MVP acceptance remain
pending. See [deployment handoff](DEPLOYMENT.md) for the build PATH fix,
private login handoff and actual database expiry. This section retains step 17 evidence.

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
settings and actual resource/release evidence. Release d8bdd29 passed both CI
jobs and the Free Render deployment is Live, with real migrations/Gunicorn,
11 HTTP and six browser checks. The final build command's redeployment is also
Live; all online checks passed again. Empty Home is expected until controlled example/
private-admin initialization; authenticated publication, nonempty redeploy data
preservation and backup/restore remain pending. Local checks and these smoke
checks do not establish full online business acceptance. No paid feature, Shell,
pre-deploy command, seeding or admin initialization was added to deployment startup.

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
