# Repository Guidelines

## Project Structure & Module Organization

Steps 01–16 have user-confirmed local acceptance. Step 17 implements production page/static integration and guarded Linux startup. User-authorised local checks passed frontend lint/30 tests/build, pip/Django/migration checks, all 135 backend tests, collectstatic and 20 browser scenarios, including real Admin/CSRF/anonymous publication in a disposable database. On 5 October 2026 (London), steps 09–17 were committed/pushed as a174723; Project checks 37242589180 passed both frontend/backend jobs on Linux. Step 17 awaits user confirmation; do not start step 18 before confirmation and a subsequent instruction. No merge or PR was created. Render account/authorised free resources are unavailable to this session, so deployment and real Gunicorn startup remain unverified. Read all `memory-bank/` documents before each step. Keep translations aligned; paths below are repository-relative. Current validation is in `backend/README.md`, deployment settings/status in `backend/DEPLOYMENT.md`. Test-only browser/server processes were closed and project PostgreSQL 17 restored to its prior stopped state.

Maintain `memory-bank/architecture.md` and `memory-bank/progress.md` with actual architecture, validation sources and pending work. User confirmation determines local step acceptance; after confirmation update progress first, then architecture.

Layout (future services/pages remain planned):

- `backend/`: Django configuration and `manage.py`.
- `backend/events/`: models, serializers, Admin, Crossref services and `tests/`.
- `frontend/src/`: React pages, components, API helpers, CSS and assets.
- `.github/workflows/`: CI checks.

Use one Django app, two React pages and Django Admin. Preserve existing installations; isolate Python 3.13/PostgreSQL 17 and development, test and production databases. Local PostgreSQL 17 uses 127.0.0.1:5433; keep PostgreSQL 11 on 5432 untouched.

## Build, Test, and Development Commands

After scaffolding and installation, verify manifests first.

From `backend/`:

Select `DJANGO_ENV=development` or `test`; the corresponding private environment file is read. Production reads process variables only. Tests use a separate database; never use production configuration for them.

- `python manage.py migrate`: apply database migrations.
- `python manage.py runserver`: start local Django development.
- `python manage.py test`: run 135 backend tests after building the current frontend; real-bundle checks must not skip missing output.
- `python manage.py makemigrations --check --dry-run`: detect missing migrations.
- `python manage.py seed_demo`: explicitly fill missing demo records; never updates existing records or runs during startup/deployment.
- `python manage.py collectstatic --noinput`: collect production assets.

From `frontend/`, use Node 24.14.0 and npm 11.9.0 as pinned in `.node-version`, the manifest and CI. On Windows use `npm.cmd`; do not change the user's global runtime or PATH.

- `npm ci`: install locked dependencies.
- `npm run dev`: start Vite with `/api/` proxied to Django.
- `npm run lint`: run the template ESLint configuration.
- `npm test`: run 30 dependency-free Node tests for requests/lifecycles, safe detail links and grouping/London time; no database or external network. Step 16 local acceptance is user-confirmed, not assistant execution.
- `npm run build`: generate production assets.

Home and detail read JSON through api/client.js and hooks/useApiRequest.js. Cleanup aborts and suppresses late results; request identity hides old content and keyed details isolate IDs. Do not show cancellation as an error or 404 as empty success. Each successful-page mount snapshots one instant; utils/talks.js shares classification and Europe/London formatting. TalkCard renders Home; ResourceCard renders detail associations in API order, always one column. Use association_id for card identity, specified author/year placeholders, optional-block omission and plain text. Original links require HTTP(S), a new-tab hint and noopener/noreferrer. Do not add visitor search before step 18. Preserve ESLint recommended/hooks/refresh rules and Node test globals.

Production uses frontend/dist/index.html as a configured Django template and collects only dist/assets under /static/frontend/assets/. Vite development stays at /. config/public_pages.py serves only Home/numeric detail GET/HEAD, never API/Admin fallbacks. WhiteNoise compressed storage preserves Vite hashes. scripts/deploy.py requires explicit production/pinned runtimes, checks assets, migrates successfully before one Gunicorn worker, and never seeds or creates accounts. CI transfers the frontend build into the backend job for real DEBUG=False static tests. Do not use the Linux deployment entry to run Windows browser checks; follow the isolated development-database walkthrough.

## Coding Style & Naming Conventions

Use four-space Python and two-space JavaScript/CSS indentation; `snake_case` Python functions, `camelCase` JavaScript variables and `PascalCase` classes/components. Use plain CSS and scaffolded ESLint; no Python formatter is configured. Preserve English UI.

Event.save and Resource.save validate input. Empty seed_key/DOI values become NULL; Resource stores trimmed, lowercase bare DOIs. DOI-link parsing remains step 19. Bulk writes bypass validation; database constraints protect required values and unique identifiers, but do not fully validate URLs. Supply timezone-aware event times and HTTP(S) resource URLs. Manual records never merge by title or URL.

EventResource.save also validates input. Store recommendations/orders on links; each event/resource pair is unique. Read links via event_resources, ordered by display_order then id; negative orders are allowed. Event ORM deletion cascades only to links; linked Resource deletion is protected. Step 08 Admin disables all Resource deletion, including unlinked records and superusers, and confirms event deletion. Association creation requires Event change and Resource view permissions as well as EventResource add; existing link identities are read-only. Manual Admin creation does not accept DOI/source/seed values. London form parsing/display explicitly uses Europe/London. These basic Admin rules have user-confirmed local acceptance; full DOI permissions remain later steps.

Demo content lives in events/data/demo_reading.json; verified source URLs accompany the bibliography. events/demo_seed.py uses DOI or stable seed_key identity and one transaction. Preserve edits, cleared values, existing dates and unrelated records; only create missing records/links. First dates use one import instant (+30/-7 days). Keep identities stable. Never add seeding to migrations, AppConfig, CI or deployment startup; preserve the public disclosures accepted in steps 15–16.

## Product and API Rules

Follow `memory-bank/tech-stack.md` → Public API contract. Public APIs and existing DOI metadata during import are read-only. Previews use database sessions, separate tab identifiers and a fixed 15-minute lifetime; they never write Resource/EventResource. Event deletion retains resources; block Resource deletion, including superusers. Use model permissions and CSRF without event ownership rules.

Detail output reuses the list's UTC fields and flattens ordered EventResource links with shared Resource metadata. Preload links/resources; never query per reading. API fallback routes must remain after valid endpoints and before any future page fallback. config/api_errors.py masks API faults only; keep Admin and public-page error behaviour separate. Both endpoints allow only GET/HEAD/OPTIONS, including with an Admin session; keep Allow and OPTIONS free of write capabilities. Step 12 tests real session login, rejected methods and unchanged business fields; local acceptance is user-confirmed. OPTIONS parser formats are request-format metadata, not write actions. Unknown API routes remain JSON 404.

## Testing Guidelines

Use Django/DRF, `unittest.mock` and PostgreSQL; name tests `test_*.py` / `test_<behaviour>`. Frontend tests are `frontend/tests/*.test.js`, using node:test for mocked requests/lifecycles and fixed-instant grouping/London display, not React DOM. Validate cards, empty groups, routes/loading/retry/Back and rapid switching manually as documented. Cover permissions, CSRF, DOI failures/conversion, preview expiry/tabs, concurrent duplicates, rollback, deletion and repeat seeding. Mock Crossref in CI; verify real integration separately. No coverage percentage is required.

## Commit & Pull Request Guidelines

Use feature branches and focused commits, e.g. `feat: add DOI import`. PRs include purpose, relevant issues, validation, UI screenshots and model migrations where applicable.

## Security & Configuration

Never commit `.env`, credentials or backups; provide `.env.example`. Lock dependencies immediately; establish CI early. Manually deploy verified commits to free Render only; migrate before Gunicorn. Initialise production data/admin separately through a controlled local connection. Record cold starts/expiry. Three-day delivery may defer online/video work; full acceptance requires every check.

重要提示

- 写任何代码前必须完整阅读 memory-bank/architecture.md
- 写任何代码前必须完整阅读 memory-bank/design-document.md
- 每完成一个重大功能或里程碑后，必须更新 memory-bank/architecture.md
