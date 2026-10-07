# Delivery record — 7 October 2026

Current stage: local core implementation and final checks passed; the current
release's GitHub CI and deployment are being verified. Last explicit user
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

- Current exact-commit remote CI, controlled redeploy, nonempty data preservation
  and production backup/isolated restore: pending current run.
- Current online public and private Admin checks: pending current run; local
  checks do not count as production acceptance.
- **Management video not recorded**; no video link is supplied.
- Full MVP acceptance remains pending until every design acceptance item and
  video is complete. This is a stage delivery record, not full completion.

Actual links: [GitHub](https://github.com/1uxury/psych-talk-hub),
[Demo](https://psych-talk-hub.onrender.com). Release evidence will be added after
the current commit passes CI and becomes Live.
