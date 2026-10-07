# Delivery record — 7 October 2026

Current stage: core implementation, final checks, exact-commit GitHub CI and
controlled deployment passed. Application release **06f98e2 is Live**. Last explicit user
acceptance is step 31. The latest instruction authorizes necessary finishing
steps without inventing individual acceptance replies for steps 32–40.

## Verified locally

- Clean Python 3.13.16 environment, locked dependencies, pip check; clean
  frontend dependency installation with Node 24.14.0/npm 11.9.0.
- Lint, 30 Node tests, build, Django/database check, migration omission check,
  static collection and **315 PostgreSQL backend tests / OK (43.307 s)**.
- Deliberate lint/test/migration failures reject the disposable clean copy;
  restoration passes. No injected errors remain in delivered source.
- Earlier actual Admin/CSRF/session/API/browser verification: 12 core groups
  plus 8 real Crossref groups; 13 public-state groups. See progress.md.
- Nine additional browser groups: London winter/summer/DST/start boundary in
  two device timezones, navigation/stale responses, 375/768/1280 px wrapping,
  measured contrast and keyboard search/clear/original-link operation.
  Nine text/background combinations range **5.86:1–13.27:1**. No JS exceptions.
- Health failure, lookup failure and save failure logs retain safe categories
  without passwords, preview IDs or provider payloads. Gunicorn access logs
  contain method/status/duration only.

## Review or record a short management demonstration

Use private local Admin credentials and disposable demonstration data, keeping
credentials, cookies, preview addresses and developer tools out of recordings.

1. Show both public groups, open a talk with three readings and search a title;
   Clear search restores the count/order. Open an original in a new tab.
2. In Admin open the target Event and Import reading by DOI. Fetch a new valid
   DOI; review source fields, fill missing title/URL and add a recommendation.
   Show that public readings remain unchanged before confirmation.
3. Save to event, then refresh the public page to show the reading. Repeat
   confirmation and import; the original link/reason/order stay unchanged.
4. Import the same DOI into another talk: shared fields are read-only; only
   its recommendation/order can change. Demonstrate independent previews and
   cancellation; expiry is tested at exactly 900 seconds by the backend suite.
5. Show the shared-edit warning, change only one link's reason/order, remove
   that link with confirmation, and delete the temporary talk with confirmation.
   The other talk and all shared resources remain; Resource Delete is absent.

## Remaining delivery items

- Full current production management matrix remains pending: new DOI actual
  creation, real 15-minute wait, low-permission matrix and destructive shared
  edit/remove/event-delete paths. These are verified locally in isolated data;
  current production checks cover the safe subset below.
- **Management video not recorded**; no video link is supplied.
- Full MVP acceptance remains pending until every design acceptance item and
  video is complete. This is a stage delivery record, not full completion.

Actual links: [GitHub](https://github.com/1uxury/psych-talk-hub),
[Demo](https://psych-talk-hub.onrender.com). Application release [06f98e2](https://github.com/1uxury/psych-talk-hub/commit/06f98e21e0d8ac3eb269d0bacc016c1c657ee0d7)
passed [CI 37552097967](https://github.com/1uxury/psych-talk-hub/actions/runs/37552097967)
and became Live on 7 October 2026 at 00:32:40 UTC.

## Current release evidence

- Existing Free Frankfurt service, auto-deploy off; actual migration-before-one-worker logs verified.
- Redeploy preserved every public business field, including IDs and existing dates/recommendations/order.
- Approved TLS backup stored privately outside Git; isolated local restore matched 2 events, 6 resources, 6 links, 1 administrator and 21 migration records. Restore database deleted, external access closed. See [backup procedure](backend/BACKUP.md).
- 11 production HTTP/Admin checks: database/HTTPS/static/API methods, secure private login/CSRF, independent existing-DOI previews/cancel and duplicate confirmation, real new DOI fetch/required fields/cancel, shared-edit warning and Resource Delete rejection. All public fields unchanged; sessions logged out.
- 7 fresh anonymous browser checks: two example talks in both date groups, three readings each, detail direct/refresh, title search/Clear/focus, safe original links, 375px/Back and friendly 404. No JS exceptions, assets 200; screenshots reviewed.
- Backup/restore initially required explicit sensitive-data approval; the user approved it. No paid resources, new production administrator or new business records were created.

Production database expiry remains **3 November 2026, 23:33 GMT**. Video and
complete online management acceptance remain explicit follow-ups; existing
local permission/CSRF/transaction/concurrency tests remain required.

The dedicated browser/fixture server are closed, disposable databases destroyed,
and the previously running local PostgreSQL 17 is preserved. Private dump files
are restricted to their owner, SYSTEM and Administrators. Final checks resolved
106 local links across 13 documents and found no current private credentials
in public source. Application code remains the verified Live commit; subsequent
documentation commits record evidence without redeploying the application.
