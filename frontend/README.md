# PsychTalk Hub frontend

## Current handoff: step 17 local checks passed, awaiting user confirmation

Step 16 remains the last user-accepted step. Step 17 adds production asset
integration: build URLs use /static/frontend/ while Vite development remains at
/. Django now serves the generated entry on Home/numeric details and WhiteNoise
serves collected React/Admin assets. No frontend dependencies or test definitions
changed: the suite remains 30. Backend now defines 135 tests, including actual
bundle/static checks; **build the frontend before running backend tests**.
At the user's request the assistant passed lint, all 30 tests and build, plus
135 backend tests and static collection. Fifteen browser scenarios verify actual
built pages/static files, refresh/navigation, keyboard, responsive layout, errors
and Admin styles; five more verify real Admin/CSRF/anonymous publication in a
disposable database. Screenshots were reviewed; no application JS exceptions were
captured. Step 17 still awaits user confirmation. Test-only processes were closed
and project PostgreSQL 17 restored to its prior stopped state.
Full commands and the DEBUG=False, Vite-stopped walkthrough are in
[backend Step 17 validation](../backend/README.md#step-17-validation--run-by-the-user).
[Free deployment status/settings](../backend/DEPLOYMENT.md) record the external
account/resource blocker; no remote deployment occurred. Steps 09–17 were
committed/pushed as a174723 on 5 October 2026 (London); both jobs passed in
[Project checks 37242589180](https://github.com/1uxury/psych-talk-hub/actions/runs/37242589180).
The frontend build was transferred to the successful backend job. Actual
Gunicorn/Render startup remains unverified. Step 18 search has not started.

### Historical step 16 handoff

Step 13 has user-confirmed local acceptance on 4 October 2026. Step 14 now
replaces the temporary connection button and detail placeholder with automatic
read-only requests, shared loading/success/not-found/error states, cancellation,
retry and an unknown-page route. At the user's subsequent request to check it,
the assistant ran lint, all 18 request tests, build and 14 isolated browser
scenarios: **all passed locally on 4 October 2026**. The user then replied
“通过”, confirming step 14 local acceptance.

Step 15 now groups Home into Upcoming talks and Past talks with cards, London
dates, optional topic/speaker, resource counts and Explore resources links.
Both group headings remain visible on empty success. A single snapshot when the
successful list mounts classifies starts_at > now as upcoming and all other
instants as past; re-entering Home, refreshing or retrying obtains a fresh
snapshot. There is no live timer. Upcoming sorts ascending, past descending,
equal instants by numeric ID ascending; the API array is not mutated.
At the step 15 handoff, detail success showed only the real title/count.
**The user confirmed step 15,
then explicitly requested assistant checks: lint, all 28 tests, build and 19
isolated browser scenarios passed on 4 October 2026.**
The user then explicitly requested step 16. Detail now renders its status,
London time, optional event information and single-column reading cards in API
association order. Missing authors/year use the specified text, other empty
optional blocks are omitted, and original links open a new tab with an accessible
hint. Example disclosures and the shared independent-project footer remain.
The user replied **“通过” on 4 October 2026**, confirming step 16 local acceptance
after receiving the lint/30-test/build and browser checklist below. No individual
logs, screenshots or measurements were supplied; the assistant only read/edited
files and did not independently run this version's checks. The earlier 28-test
pass remains historical step 15 evidence. Progress records last accepted step 16;
step 17 was then unstarted; the current implementation is described above.
Search remains step 18.
The old **Check backend connection**, **Open route placeholder** and **Talk page**
instructions describe historical step 13 and no longer apply to this version.

GitHub CI success for f203069 covers steps 01–08 only. Steps 09–16 remain
uncommitted/unpushed; the frontend job now includes unit tests, but has no remote
verification. Steps 15–16 change no backend runtime/schema, dependencies or lockfile.

## Runtime and locked dependencies

Use **Node 24.14.0 and npm 11.9.0**, as pinned in the root .node-version,
package.json and CI. On Windows use npm.cmd to avoid npm.ps1 policy issues.
Existing installations and permanent PATH were preserved.

Exact dependencies remain React/React DOM 19.3.0, React Router 7.18.4, Vite
8.3.2, React plugin 6.1.1 and ESLint 10.12.0. package-lock.json fixes transitive
dependencies/integrity. Step 14 adds no dependency and does not change the lock.
Steps 15–16 also add no dependencies. Tests use Node's built-in test runner,
assertions and mocks, with no browser automation framework. The official
create-vite 8.2.0 ESLint recommended/hooks/
refresh rules remain; only the test directory receives Node globals.

Version/peer information was checked against official npm metadata on 4 October
2026 during step 13. Router stays on the planned 7.x series; the newest template's
Oxlint is not used. No TypeScript, state library, HTTP client, CORS package or Node
application backend is introduced.

## Files and responsibilities

| File | Responsibility |
| --- | --- |
| index.html / src/main.jsx | English entry, StrictMode and declarative BrowserRouter |
| src/App.jsx | Home/detail routes, numeric-ID guard, keyed detail identity and wildcard not-found route |
| src/pages/HomePage.jsx | Automatic list read; successful-list time snapshot, ordered groups and all three empty messages |
| src/components/TalkCard.jsx | Semantic card, optional topic/speaker, example label, London time, accurate count and accessible detail link |
| src/utils/talks.js | Shared Home/detail classification against an explicit instant; non-mutating grouping/sort; Europe/London Intl display |
| src/pages/TalkPage.jsx | Real detail read and successful-load time snapshot, status/event information, ordered readings, no-reading state and disclosures |
| src/components/ResourceCard.jsx | Association-keyed card, type/title, author/year placeholders, optional recommendation and accessible new-tab original link |
| src/pages/NotFoundPage.jsx | Unknown page or non-numeric talk route; no API request; Back to talks |
| src/components/RequestState.jsx | Shared English loading/not-found/failure messages, live status/alert and Retry |
| src/api/client.js | Relative GET with JSON Accept, HTTP/content-type checks, basic shape/identity checks, safe error classification, abort plus late-result suppression |
| src/hooks/useApiRequest.js | Effect-owned request lifecycle, cleanup, request/retry identity and immediately hiding older results |
| src/api/types.js | JSDoc reference to the existing API contract, including empty strings and nullable year/DOI |
| tests/api-client.test.js | 20 isolated request/lifecycle tests; detail order/null preservation and rejection of bad metadata/unsafe original URLs; no React DOM coverage |
| tests/talks.test.js | Ten time/grouping tests; shared Home/detail boundary, ties, immutability, empty groups, London DST and browser name fallbacks |
| src/index.css | Visual base, states, responsive activity grid, always-single-column reading list, text line breaks/wrapping and visible focus |
| vite.config.js | Development base /, localhost:5173/strictPort and unchanged /api proxy; build base /static/frontend/ |
| package.json / package-lock.json / .npmrc | Runtime, exact dependencies, dev/lint/test/build/preview and installation policy |
| ../.github/workflows/backend.yml | Existing PostgreSQL backend job plus frontend locked install/lint/test/build |

Basic shape checks catch an unexpected envelope, missing resources, malformed
JSON or wrong detail identity. Step 15 also rejects invalid start times, counts
and required card field types before rendering, so malformed data follows the
existing error/Retry path. They do not duplicate full server validation or
convert missing metadata to invented values. HTTP 404 is not-found; other HTTP,
network, content-type or decoding failures are errors. Error response bodies and
internal exception messages are not shown to visitors.

Cleanup cancels both the fetch and its right to update state. A response/body
that ignores abort is still discarded. Each detail ID has a separate component
lifetime; hook results also carry loader/argument/retry identity, so an old result
is not displayed during the transition. Retry is user-triggered, with no polling
or automatic retry loop. StrictMode's development setup/cleanup is supported.

References: [React effect cleanup](https://react.dev/reference/react/useEffect),
[AbortController](https://developer.mozilla.org/en-US/docs/Web/API/AbortController/abort),
[Router routing](https://reactrouter.com/7.18.4/start/declarative/routing).

Step 17 implements the production entry/asset prefix/WhiteNoise path, awaiting
the user's validation. Vite preview still has no development API proxy; use
Django for integrated checks. Unknown routes reached within React display its
not-found page, but directly opening an unknown server path gives Django 404.
Only Home and numeric /events/{id} have server entry routes. Unknown /api paths
remain JSON 404; no broad SPA fallback or trailing-slash alias is introduced.

## Step 16 validation 1: lint, all tests and build

These are instructions for the user, not recorded successes. Reuse the locked
dependencies. In the frontend terminal, stop Vite with Ctrl+C before these checks:

~~~powershell
Set-Location G:\STUDY\psych-talk-hub\frontend
npm.cmd run lint
if ($LASTEXITCODE -ne 0) { throw 'Frontend lint failed.' }
npm.cmd test
if ($LASTEXITCODE -ne 0) { throw 'Frontend tests failed.' }
npm.cmd run build
if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed.' }
~~~

Expected: no lint warnings/errors, **30 top-level tests, 0 failures**, and a
successful build. There are 20 request tests and ten time/grouping tests. New
coverage protects the shared Home/detail boundary and safe rejection of malformed
detail metadata or non-HTTP(S) original links. The existing null/order test now
uses three associations with different resource IDs, equal/negative order values,
both types, optional nulls and multiline text. The request layer returns the
received array unchanged. Tests never access Django, Crossref or a database;
they do not prove React rendering, link behaviour or layout. Complete the checks
below before confirming step 16. No dependency reinstall or migration is required.

## Step 16 validation 2: real event and ordered reading

Keep Django running. Restart Vite after validation 1 with npm.cmd run dev. If
services are stopped, use **Step 14 validation 2** below to restart the existing
project database, Django and Vite; do not initialise a new database.

1. Open http://localhost:5173/ and select Explore resources for a real activity.
   Check Back to talks, Upcoming/Past, title, non-empty topic/speaker/description
   and London-local time with GMT/BST. Match these to Network's JSON detail
   response and the Home card. Reloading/re-entering/retrying snapshots a fresh
   instant; the page does not continuously update while left open.
2. Under Related reading, compare every card to resources in that response:
   type, title, authors, year and the current association's recommendation.
   research_paper displays Research paper; article displays Article / web resource.
   Card order must exactly match the API array, including equal display_order
   values, and must not be resorted by resource ID/title/year. Counts use the
   API's resource_count and singular/plural correctly.
3. Only example events show Example event and Reading selections are illustrative;
   these talks are fictional. The footer on both pages says Independent portfolio
   prototype. Not affiliated with Conn8cting. No administrator credentials appear.
4. Refresh the detail URL, select Back to talks, then try browser Back/Forward.
   The correct event and readings return; no other activity's reason appears.
   A nonexistent numeric event shows the existing not-found state, not no readings.

If no real activity/readings exist, record the real browsing check as pending.
Use existing development data or the explicit development-only seed instructions
below. A browser fixture is not proof of real stored data or production behaviour.

## Step 16 validation 3: original links and layout

1. Click Read original for a real paper and article. Each opens its exact
   original_url in a new tab; the PsychTalk Hub tab remains on the same detail.
   Publisher login/paywalls are external access rules, not a local application
   failure. The platform does not promise free full text.
2. In developer tools, inspect an original link: target is _blank, rel contains
   noopener and noreferrer, and its accessible name includes the reading title
   and opens in a new tab. Press Tab to reach each link with a visible focus
   outline; Enter opens the original. The visible action remains Read original.
3. At 375 px, 768 px and 1280 px, readings stay one column, while Home retains
   its existing responsive activity grid. Long titles, author lists and reasons
   wrap without horizontal scrolling. Description/recommendation line breaks
   are preserved as plain text. Original actions are at least 44 px high.
   Comprehensive contrast testing remains step 33.

## Step 16 validation 4: missing optional fields and zero readings

Use an existing activity with these cases, or the following browser-only fixture
without editing/deleting database records. For each scenario, freshly load Home
and paste this in its developer-tools Console. Replace step16Id with an ID from
the real list, select missing, empty or ordinary, then click that activity's
Explore resources. Reload Home before repeating; do not reload detail while
testing the fixture, since reload removes the override. Native fetch is restored
by any full reload. This overrides only that detail GET in this tab and does not
alter the event/list, Admin, the database or other tabs.

~~~javascript
const step16Id = '1' // Replace with a real event ID.
const step16Scenario = 'missing' // Repeat with 'empty' and 'ordinary'.
const step16Fetch = window.fetch.bind(window)
const step16Path = `/api/events/${encodeURIComponent(step16Id)}/`
const step16Response = await step16Fetch(step16Path, { headers: { Accept: 'application/json' } })
if (!step16Response.ok) throw new Error('Choose an existing event ID.')
const step16Actual = await step16Response.json()
if (step16Scenario === 'missing' && step16Actual.resources.length === 0) {
  throw new Error('Choose an event with at least one reading for the missing-field check.')
}
const step16Fixture = {
  ...step16Actual,
  ...(step16Scenario === 'ordinary' ? { is_example: false } : {
    description: '', topic: '', speaker: '',
  }),
  ...(step16Scenario === 'empty' ? { resource_count: 0, resources: [] } : {}),
  ...(step16Scenario === 'missing' ? {
    resources: step16Actual.resources.map((reading) => ({
      ...reading, authors: '', year: null, recommendation: '',
    })),
  } : {}),
}
console.log('Expected reading order:', step16Fixture.resources.map((reading) => reading.association_id))
window.fetch = (input, options) => {
  const url = new URL(typeof input === 'string' ? input : input.url, location.href)
  if (url.origin === location.origin && url.pathname === step16Path
      && (options?.method ?? 'GET') === 'GET') {
    return Promise.resolve(new Response(JSON.stringify(step16Fixture), {
      status: 200, headers: { 'Content-Type': 'application/json' },
    }))
  }
  return step16Fetch(input, options)
}
~~~

| Scenario | Expected detail |
| --- | --- |
| missing | Each card shows Author not provided and Year not provided; no Why this reading? block. Empty topic/speaker/description have no blank labelled region. Real titles/URLs, count and association order remain unchanged. |
| empty | Title, time/status and applicable example disclosures remain; Related reading shows 0 reading resources and Reading resources will be added here soon. No reading cards, original links or search input. |
| ordinary | No Example event badge or fictional-reading disclosure; the independent-project footer remains. Only the example flag is overridden, so seeded title/description may still contain example words. |

Restore native behaviour by reloading Home, then open a real detail and confirm
normal content returns. If fixtures are unavailable, use local response overrides
or record the unmet case as pending; do not claim all empty-state cases passed.

## Step 16 validation 5: request regression and acceptance boundary

Repeat the existing Step 14 loading/offline/Retry and rapid-navigation checks
below. During a pending/failed detail read, do not retain another event's cards,
display the zero-reading message or show a successful Related reading section.
Retry must load that route's real metadata/cards. Bad JSON/invalid dates or
unsupported original-link schemes become the safe request error, not a rendering
crash or an active unsafe link; automated rejection scenarios are in the new test.
There must be no uncaught application exceptions.

Step 16 local acceptance is user-confirmed on 4 October 2026 after the checklist
was supplied. No individual outputs were supplied; the assistant did not run
lint, the current 30 tests, build or browser checks. Do not infer fixture use,
timings, measured layout or independent DOM evidence from that confirmation.
The unchanged 116-method backend suite was not rerun; no new backend migration
is required. After confirmation, progress.md was requested open (queued) and
updated first, then architecture received acceptance/file-role insights and
guides were synchronised. Progress's last accepted step is 16. This confirmation
handoff only changed documentation. Step 17 production integration/deployment
has not started and needs a new instruction; no database write, dependency
install, commit/push or deployment was performed.

## Step 15 regression: historical acceptance and Home checks

The following preserves step 15's 28-test acceptance evidence. Use the current
30-test expectation above when running the complete suite after step 16.

## Step 15 validation 1: lint, all unit tests and build

These are instructions for user execution, not successful results. Run the
following from the frontend terminal; keep the existing locked dependencies.
If Vite is already running, stop it first with Ctrl+C.

~~~powershell
Set-Location G:\STUDY\psych-talk-hub\frontend
npm.cmd run lint
if ($LASTEXITCODE -ne 0) { throw 'Frontend lint failed.' }
npm.cmd test
if ($LASTEXITCODE -ne 0) { throw 'Frontend tests failed.' }
npm.cmd run build
if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed.' }
~~~

At step 15 the expectation was **28 top-level tests, 0 failures**, no lint
warnings/errors and build success. The current runner after step 16 defines 30
tests; use validation 1 above. The historical 28 included 18 existing tests, one new card-response validation
test and nine new grouping/time tests. No test connects to a database or real
API. Fixed now is 4 October 2026, 12:00 UTC: +1 millisecond is Upcoming; equality
and -1 millisecond are Past. Both sort directions and numeric ID ties (2 before
20, 3 before 12) are checked, with frozen input to catch mutation. Empty/single
groups, winter/summer times, midnight rollover and both DST changes are covered.
The latest user screenshot showed GMT+0 for a winter card. Formatting now
normalises offset-name fallbacks to GMT/BST through Intl's timeZoneName part,
preserving the date/time and London timezone calculation. A regression test
mocks browser GMT+0/GMT+1 variants. The initial acceptance was user-confirmed
without assistant execution or a post-fix screenshot; later authorised checks
and screenshots below independently verify the corrected labels.
Unit tests validate logic; the following checks validate the rendered page.

Subsequent authorised assistant verification passed lint/build (exit 0), all 28
Node tests (0 failed/cancelled/skipped), and 19 Headless Edge 154 scenarios.
At 1280 px, real Home's two grids each have two 504 px columns with a 24 px gap.
Each real group currently has one card, leaving its right column empty. Upcoming
and Past are separate vertically stacked sections, not two cards sharing a row.
Browser-only fixtures with multiple cards per group verified two columns at
1280/768 px and one at 767/375 px, with no overflow. These fixtures did not alter
database records. Winter GMT and summer BST, device-zone independence, long
wrapping, keyboard/Enter, navigation/reload, empty groups, loading, offline/Retry,
HTTP 500 and malformed-time errors also passed. No app code changes were needed.
Evidence timestamp: 2026-10-04T20:39:58.180Z; ignored tools/results/screenshots
are under .tools/step15-browser. Overrides were cleared and the isolated browser
closed; existing services were retained. Backend/remote CI/deployment were not run.

## Step 15 validation 2: real Home, cards and navigation

Use existing Django and Vite services, or start them using **Step 14 validation
2: start existing development services** below.

1. Open http://localhost:5173/. Confirm the existing introduction, then Upcoming
   talks above Past talks. Compare Network's GET /api/events/ response with the
   cards; every activity appears once in the correct group, with the expected
   time/ID order. Zero-reading activities must still have Explore resources.
2. Match each title, topic, speaker and resource count to JSON. Empty topic and
   speaker omit their lines. Counts use 0/1/plural correctly; only is_example:
   true receives Example event. The independent-project footer remains.
3. Check London-local time with an explicit GMT/BST suffix, even if the device
   zone differs. Winter 2026-01-15T18:30:00Z displays 15 Jan 2026, 18:30 GMT;
   summer 2026-07-15T18:30:00Z displays 15 Jul 2026, 19:30 BST. Fixed-time unit
   cases cover exact boundaries without changing the machine clock or database.
4. Click Explore resources; the URL uses that card's ID and detail still displays
   its real title/count. Refresh, Back to talks and browser Back/Forward work.
   Reading cards were not expected at step 15; the current version must satisfy
   the step 16 reading checks above.
5. At 375 px the grid is one column; at 768 px and 1280 px it is two. Long
   text wraps. Tab reaches each Explore resources link with visible focus;
   Enter opens the corresponding detail. No uncaught application exceptions.
   Comprehensive two-page contrast/accessibility acceptance remains step 33.

## Step 15 validation 3: single-group and completely empty Home

Check all three successful response cases without deleting or changing records.
The following **optional browser-console fixture** overrides only the list GET
inside the current local browser tab. It is not product code or saved demo data.
For each case, first directly open a real detail URL from the actual list. In
developer tools' Console, paste this block, changing scenario to upcoming, past
or empty, then click **Back to talks**. Reload a real detail URL before the next
case, so the previous override is cleared. All labels below are test content.

~~~javascript
const scenario = 'upcoming' // Repeat with 'past' and 'empty'.
const originalFetch = window.fetch.bind(window)
const fixture = {
  id: 999999999, title: 'Example event: Home state check', description: '',
  topic: '', speaker: '', is_example: true, resource_count: 0,
  starts_at: scenario === 'past' ? '2000-01-15T18:30:00Z' : '2099-07-15T18:30:00Z',
}
window.fetch = (input, options) => {
  const url = new URL(typeof input === 'string' ? input : input.url, location.href)
  if (url.origin === location.origin && url.pathname === '/api/events/'
      && (options?.method ?? 'GET') === 'GET') {
    return Promise.resolve(new Response(JSON.stringify(scenario === 'empty' ? [] : [fixture]), {
      status: 200, headers: { 'Content-Type': 'application/json' },
    }))
  }
  return originalFetch(input, options)
}
~~~

| Scenario | Expected rendered Home |
| --- | --- |
| upcoming | Card only in Upcoming; Past heading plus No past talks yet. |
| past | Upcoming heading plus No upcoming talks yet. Explore past talks below.; card only in Past |
| empty | Talks will appear here when they are added. below the introduction, plus both headings and their empty messages |

Fixture cards omit blank topic/speaker, display 0 reading resources and retain
the detail link. The fixture ID may not exist; do not use its detail as evidence
of a real activity. For long wrapping, repeat a case with a long fixture title.
**Reload to restore native fetch**, then return Home and confirm real data.
Changing system time, deleting events, importing data or editing production is
not necessary for these checks. If console fixtures are unavailable, use local
developer-tools response overrides and record any unchecked scenario as pending.

## Step 15 validation 4: request-state regression and handoff

Repeat step 14 validation 4 below for Home loading, network failure and Retry.
During loading/failure, neither cards nor successful empty messages appear.
After recovery the correct groups return. Existing detail routing/cancellation
checks remain available below and unchanged in scope.

At initial implementation/acceptance, the assistant only read/edited files and did not run lint, the 28
tests, build, browser scenarios, backend regression or remote CI. The user's
“通过” after the fix/recheck instructions confirms local acceptance; no individual
command output, timing or post-fix screenshot was supplied. The earlier screenshot
shows both groups/cards and counts 4/3, but retains the pre-fix GMT+0 label.
After confirmation, progress.md was requested open (queued) and updated first,
then architecture insights and guides were synchronised. Progress's last accepted
step was 15; at that handoff step 16 awaited a new instruction. This handoff changed documentation
only. The later authorised assistant checks are recorded above and in progress.md;
historical non-execution statements do not describe that subsequent verification.
No dependency install, database write, commit/push or deployment was performed.

## Step 14 regression 1: locked installation and request tests

If Vite is running, stop it with Ctrl+C (confirm Y if Windows asks to terminate
the batch job). Existing step-13 dependencies can be reused; a clean reinstall
is optional for this step and must happen before restarting Vite:

~~~powershell
Set-Location G:\STUDY\psych-talk-hub\frontend
# Optional locked reinstall, only with Vite stopped:
# npm.cmd ci --no-audit --no-fund --cache ..\.tools\npm-cache
npm.cmd run lint
if ($LASTEXITCODE -ne 0) { throw 'Frontend lint failed.' }
npm.cmd test
if ($LASTEXITCODE -ne 0) { throw 'Frontend request tests failed.' }
npm.cmd run build
if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed.' }
~~~

Step 14 originally contained 18 tests; step 15 contained 28. The current full
runner defines **30 tests** after step 16; expect 0 failures, no lint errors/warnings
and build success. The current version has not yet been executed by the assistant.
The tests mock fetch and never access Django, Crossref or a database. They cover
relative GET/signal/Accept, unchanged nulls/order, HTTP 404/500, malformed JSON,
HTML or wrong shapes/identity, empty and zero-reading success, error/retry,
pending requests, late body results, old/new response order, silent cancellation
and immediate setup/cleanup/setup. These tests do not replace the browser checks
below. Build outputs and dependencies remain ignored.

Windows EPERM during npm ci may mean a native Rolldown binding is still loaded.
Stop the frontend process first; keep package-lock.json and do not change global
permissions or kill unrelated Node processes.

## Step 14 validation 2: start existing development services

Reuse running services if already available. Otherwise, in the Django terminal:

~~~powershell
Set-Location G:\STUDY\psych-talk-hub\backend
$env:DJANGO_ENV = 'development'
.\.venv\Scripts\python.exe scripts/local_database.py status
~~~

Only if the project PostgreSQL instance is stopped:

~~~powershell
.\.venv\Scripts\python.exe scripts/local_database.py start
~~~

Start Django (do not initialise a new database or use production):

~~~powershell
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
~~~

In a separate frontend terminal:

~~~powershell
Set-Location G:\STUDY\psych-talk-hub\frontend
npm.cmd run dev
~~~

Keep both terminals running during the browser checks.

## Step 14 validation 3: real success and navigation

1. Open http://localhost:5173/. Without clicking a connection button, Network
   must show GET /api/events/ and the page must show the real talk links. An empty
   array is successful and displays **Talks will appear here when they are added.**
2. For detail/navigation checks, use real IDs from that response. Click a talk:
   Network must show GET /api/events/{id}/; the returned title/count must match
   the visible page. A real talk with zero readings remains success, not not-found.
   Optional-field metadata remains unchanged in JSON; the current full rendering
   must also satisfy the step 16 checks above.
3. Refresh that detail URL. Use **Back to talks**, browser Back and Forward.
   The correct route/title must return; no old placeholder or uncaught JS error.
4. Example events show **Example event** and the fictional-reading explanation;
   the independent-project footer remains. Tab reaches product/talk/back links.

If no events exist, checks involving real activities remain unverified until
development-only data is available. You may explicitly run the existing
seed_demo command with DJANGO_ENV=development in a separate terminal; it only
fills missing demo records/links and preserves edits. Do not run it against
production or infer IDs from the examples in this README.

## Step 14 validation 4: loading, failures, retry and missing routes

Use browser developer tools' Network panel; enable Disable cache while it is open.

1. Choose Slow 3G or a custom network profile with about 2 seconds latency.
   Navigate from Home to a real talk. Expect **Loading resources…** before its
   title/count, with no empty-resource or not-found message during the wait.
   Return Home and confirm **Loading talks…** before the list/empty success.
2. With the React page already loaded, select Offline in Network, then navigate
   to a talk or Home using an in-app link. Do not refresh the entire browser while
   offline, since that would prevent loading the application itself.
   Expect **We couldn't load this page. Please try again.** with **Retry**.
   The list/previous talk/empty-success message must not remain visible.
3. Select No throttling (online), click **Retry**, and confirm loading followed by
   the real title or list; the error must disappear. Repeat on the other page.
   As an alternative, stop only your Django dev server, navigate/retry to observe
   the proxy's non-success response, restart Django, then retry. A proxy HTTP
   failure must be an error, never an empty success.
4. Pick a positive numeric ID absent from the actual list, such as 999999999
   after checking it is absent. Open /events/{that-id}. Expect a JSON 404 in Network
   and **We couldn't find this talk.** with **Back to talks**. It must not show
   **0 reading resource(s)**, an empty-reading message or a generic network error.
5. Open http://localhost:5173/events/not-a-number and
   http://localhost:5173/unknown-page. Expect the appropriate not-found message
   and a working **Back to talks**. These pages must not fetch the event API.
6. Open http://localhost:5173/api/unknown/. It must remain JSON 404, not React HTML.
   A page route and API error are different boundaries.

Browser Network may show expected failed/404/cancelled request entries during
these checks. Acceptance requires no uncaught application exception; intentional
network failures are not evidence of a rendering crash.

## Step 14 validation 5: cancellation and old-response protection

With two real events A and B and Slow 3G/custom latency:

1. From Home open A; while its detail request is pending, click Back to talks.
   In Network, A's pending request should be cancelled if still in flight.
   Abandoning it must not show a failure banner on Home.
2. As soon as Home's list returns, open B. Its loading region must not show A's
   title/count; after loading only B's title/count should appear.
3. Wait longer than the original delay. A must not replace B. Use browser Back/
   Forward and repeat B then A; each route shows its own response.
4. Check the console for uncaught errors. Restore No throttling/normal networking
   after testing.

The unit test **a late old event cannot replace the newer event even if fetch
ignores abort** deterministically releases B before A, while the browser sequence
checks React cleanup and rendering. The late-body and cancelled-rejection tests
cover cancellation after fetch resolution and rejected requests. Unit tests alone
cannot prove DOM navigation; if fewer than two events exist, record that browser
scenario as pending instead of claiming it passed.

## Handoff and remote verification

Actual step 14 check evidence: lint and build exited 0; Node reported 18 passed,
0 failed/skipped/cancelled. Isolated Headless Edge 154 verified real list/detail
reads, reload/Back/Forward, missing/unknown routes, JSON API 404, delayed loading,
offline failures and Retry on both pages, rapid A→Home→B cancellation, keyboard
Tab/Enter with visible 3 px focus and no uncaught application exceptions.
Empty list, zero-reading detail and HTTP 500 used browser-only response overrides;
they are controlled UI scenarios, not database writes or actual empty database
evidence. The real list then contained IDs 1/2 with resource counts 4/3.
Temporary scripts/screenshots/results are ignored under .tools/step14-browser;
checks used existing services without Admin login or business writes. Overrides
and network emulation were cleared and that isolated browser was closed.
No application failures required code changes. The existing backend tests were
not rerun, and no production or remote CI checks were performed.

After these successful checks, progress.md was requested open (queued) and the
actual assistant results were recorded first, followed by architecture insights
and guide updates. The user subsequently confirmed acceptance with “通过”.

After that confirmation, progress.md was again requested open (queued) and updated
first, then architecture.md received acceptance/file insights and guides were
synchronised. This handoff changed documentation only; no checks were rerun.
That historical handoff left progress at 14. The later step 15 implementation
and user confirmation are described above. Step 16 also has user-confirmed local
acceptance; progress's last accepted step is 16, and step 17 has not started.
No backend runtime/schema/dependency changes were made; the existing 116 backend
tests are unchanged. A full backend regression can be run using backend/README.md,
but frontend unit tests have no database dependency.

CI runs frontend lint, all frontend tests (now 30) and build. After a separately
authorised commit/push, check successful backend and frontend jobs for that exact
commit; the historical backend result cannot verify these new changes. No commit,
push or deployment was performed for this step.

[Design](../memory-bank/design-document.md) ·
[Technology/API contract](../memory-bank/tech-stack.md) ·
[Implementation plan](../memory-bank/implementation-plan.md) ·
[Progress](../memory-bank/progress.md)
