# Repository Guidelines

## Project Structure & Module Organization

This project currently contains documentation only; application code and dependency manifests are absent. Read `memory-bank/design-document.md`, its matching Chinese version `memory-bank/design-document.zh-CN.md`, `memory-bank/tech-stack.md`, and `memory-bank/implementation-plan.md` before implementing changes. Keep both design versions aligned. All directory paths below are relative to the repository root.

Keep implementation status and validation results in `memory-bank/progress.md`; maintain architecture decisions and actual module responsibilities in `memory-bank/architecture.md`. These two files start empty and must be populated during implementation, without claiming planned work is complete.

Use this planned layout when scaffolding:

- `backend/`: Django project configuration and `manage.py`.
- `backend/events/`: models, serializers, Admin forms, Crossref services, and `tests/`.
- `frontend/src/`: React pages, components, API helpers, CSS, and optional assets.
- `.github/workflows/`: CI checks.

Maintain one Django business application and two public React pages. Use Django Admin for management and PostgreSQL for persistence.

## Build, Test, and Development Commands

These commands become available after scaffolding and dependency installation; verify actual manifests before running them.

From `backend/`:

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

Use four-space Python indentation, `snake_case` functions, and `PascalCase` classes. Use two-space JavaScript/CSS indentation, `PascalCase` React components, and `camelCase` variables. Keep Crossref requests in a service module. Follow scaffolded ESLint rules; no Python formatter is configured yet. Preserve English UI copy and design tokens.

## Testing Guidelines

Use Django/DRF test clients and `unittest.mock`; name modules `test_*.py` and methods `test_<behaviour>`. Test permissions, CSRF, DOI failures, preview cancellation, duplicate associations, concurrent saves, and transaction rollback against PostgreSQL. Mock Crossref in CI. No numerical coverage threshold exists; cover each changed business rule and failure path. Manually check search, direct URL refresh, keyboard navigation, and mobile layouts.

## Commit & Pull Request Guidelines

Use focused commits such as `feat: add DOI import` or `docs: clarify resource ordering`. Use feature branches for changes after the initial repository commit. PRs should state purpose, link relevant issues when available, report validation, and include screenshots for UI changes. Include migrations with model changes.

## Security & Configuration

Keep public APIs read-only and protect Admin writes with sessions, permissions, and CSRF. Use fixed Crossref endpoints and explicit timeouts. Never commit `.env`, credentials, or database URLs; provide `.env.example`. Keep development, test, and production databases separate. Lock dependencies and document deployment changes.

重要提示

- 写任何代码前必须完整阅读 memory-bank/architecture.md
- 写任何代码前必须完整阅读 memory-bank/design-document.md
- 每完成一个重大功能或里程碑后，必须更新 memory-bank/architecture.md
