# Repository Guidelines

## Project Structure & Module Organization

Steps 01–08 have user-confirmed local acceptance, including Event, Resource, EventResource, their migrations, basic Admin management and 69 backend tests. Step 08 adds London form time, public addresses and deletion safeguards; local acceptance is based on the user's confirmation, without individual logs. PostgreSQL 17, environment configuration, health checks and backend CI are present. Stage commit 66b4140 was pushed to docs/clarify-implementation-plan; GitHub Actions run 37208404049 passed Linux dependency installation, checks, migrations and backend tests. Production startup/deployment remain unverified. Event APIs and React are not implemented. Step 09 has not started and requires a new user instruction. Read all `memory-bank/` documents before each step. Keep translations aligned; paths below are repository-relative. Validation is documented in `backend/README.md`.

Keep `memory-bank/architecture.md` and `memory-bank/progress.md` empty until step 01; then record actual architecture, verified progress and pending work.

Planned layout:

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
- `python manage.py test`: run backend tests.
- `python manage.py makemigrations --check --dry-run`: detect missing migrations.
- `python manage.py collectstatic --noinput`: collect production assets.

From `frontend/`:

- `npm ci`: install locked dependencies.
- `npm run dev`: start Vite with `/api/` proxied to Django.
- `npm run lint`: run the template ESLint configuration.
- `npm run build`: generate production assets.

## Coding Style & Naming Conventions

Use four-space Python and two-space JavaScript/CSS indentation; `snake_case` Python functions, `camelCase` JavaScript variables and `PascalCase` classes/components. Use plain CSS and scaffolded ESLint; no Python formatter is configured. Preserve English UI.

Event.save and Resource.save validate input. Empty seed_key/DOI values become NULL; Resource stores trimmed, lowercase bare DOIs. DOI-link parsing remains step 19. Bulk writes bypass validation; database constraints protect required values and unique identifiers, but do not fully validate URLs. Supply timezone-aware event times and HTTP(S) resource URLs. Manual records never merge by title or URL.

EventResource.save also validates input. Store recommendations/orders on links; each event/resource pair is unique. Read links via event_resources, ordered by display_order then id; negative orders are allowed. Event ORM deletion cascades only to links; linked Resource deletion is protected. Step 08 Admin disables all Resource deletion, including unlinked records and superusers, and confirms event deletion. Association creation requires Event change and Resource view permissions as well as EventResource add; existing link identities are read-only. Manual Admin creation does not accept DOI/source/seed values. London form parsing/display explicitly uses Europe/London. These basic Admin rules have user-confirmed local acceptance; full DOI permissions remain later steps.

## Product and API Rules

Follow `memory-bank/tech-stack.md` → Public API contract. Public APIs and existing DOI metadata during import are read-only. Previews use database sessions, separate tab identifiers and a fixed 15-minute lifetime; they never write Resource/EventResource. Event deletion retains resources; block Resource deletion, including superusers. Use model permissions and CSRF without event ownership rules.

## Testing Guidelines

Use Django/DRF, `unittest.mock` and PostgreSQL; name tests `test_*.py` / `test_<behaviour>`. Cover contracts, permissions, CSRF, DOI failures/conversion, preview expiry/cancellation/tabs, concurrent duplicates, rollback, deletion and repeat seeding. Mock Crossref in CI; verify real integration separately. No coverage percentage is required. Manually check search, navigation, keyboard access and mobile layouts.

## Commit & Pull Request Guidelines

Use feature branches and focused commits, e.g. `feat: add DOI import`. PRs include purpose, relevant issues, validation, UI screenshots and model migrations where applicable.

## Security & Configuration

Never commit `.env`, credentials or backups; provide `.env.example`. Lock dependencies immediately; establish CI early. Manually deploy verified commits to free Render only; migrate before Gunicorn. Initialise production data/admin separately through a controlled local connection. Record cold starts/expiry. Three-day delivery may defer online/video work; full acceptance requires every check.

重要提示

- 写任何代码前必须完整阅读 memory-bank/architecture.md
- 写任何代码前必须完整阅读 memory-bank/design-document.md
- 每完成一个重大功能或里程碑后，必须更新 memory-bank/architecture.md
