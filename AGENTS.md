# MammalBase Agent Instructions

## Purpose

This file defines the default working instructions for coding agents operating in this repository. Use it together with the project documentation under `documentation/`, especially:

- `documentation/common/instructions.md`
- `documentation/common/testing.md`
- `documentation/common/deploy.md`
- `documentation/development/mb planning prompt.md`
- `documentation/development/mb coding prompt.md`

## Repository Shape

- Django project code lives under `app/`.
- The main shared Django project config is under `app/config/`.
- Django apps live directly under `app/` as packages such as `mb`, `imports`, `exports`, `main`, `matchtools`, `tdwg`, `wdpa`, `tgn`, and others.
- Shared tests live under `app/tests/`.
- Documentation lives under `documentation/`, not `docs/`.
- The main base template is `app/mb/templates/mb/base_generic.html`.
- Container orchestration is defined in `docker-compose.yml` with services including `web`, `db`, `redis`, `celery`, `celery-beat`, `phpmyadmin`, and `test`.

## Current Stack Assumptions

- Django `5.2.11`
- MariaDB `10.9.x` via Docker
- `django-allauth==65.13.0`
- `django-simple-history~=3.7.0`
- `django-filter>=2.4.0`
- `djangorestframework>=3.15.2`
- Celery with Redis

Always prefer the versions in `app/requirements.txt` over any stale documentation text.

## Working Rules

- Reuse existing app structure before creating new packages.
- Prefer class-based Django views unless the surrounding code clearly uses function-based views for that area.
- Keep changes scoped to the task. Do not fold unrelated cleanup into the same patch.
- Preserve MySQL/MariaDB compatibility in schema and query choices.
- Keep user-facing documentation free of internal code citations like file paths or line references.
- Follow existing template patterns when editing UI. If creating a new page, extend `app/mb/templates/mb/base_generic.html` unless the local feature area already uses another established base.
- Wrap user-facing strings for translation where the surrounding code does so.
- Respect existing auth and group-based permission patterns.
- Do not add new dependencies unless they are necessary and justified.

## Planning Guidance

When preparing a plan:

- Ground recommendations in the actual repository layout under `app/` and `documentation/`.
- Call out impacted Django apps explicitly.
- Distinguish reused components from net-new models, forms, views, filters, serializers, tasks, or admin classes.
- Include testing, migrations, documentation, deployment, rollback, accessibility, localization, and security implications.
- Assume Django `5.2.x`, not Django `4.2`.

## Coding Guidance

When implementing:

- Validate the requested scope against the approved task or user request.
- Favor local consistency over generic framework advice.
- Update tests and documentation when the change materially affects behavior, workflows, or operator knowledge.
- Keep admin, filters, history tracking, and permissions aligned with adjacent features when relevant.

## Testing Guidance

Prefer the documented project workflow:

- Run all tests with `docker exec mammalbase_web_1 python manage.py test` when that container naming convention is present.
- The compose file also defines a `test` service running `pytest -q`, so pytest can be used when the target tests are already compatible with that path.
- Use the Django test runner when app loading or registry initialization matters.
- If coverage is needed, follow `documentation/common/testing.md`.

Do not claim coverage thresholds were met unless you actually ran and verified them.

## Documentation Targets

When docs must be updated, prefer the current directories:

- `documentation/user/`
- `documentation/admin/`
- `documentation/development/`
- `documentation/common/`
- `CHANGELOG.md`

Do not refer to nonexistent `docs/...` paths.

## Delivery Expectations

- In this environment, make the code changes directly in the workspace.
- Summarize what changed, what was verified, and any remaining risks or blockers.
- Do not use a “return only file blocks” format unless a user explicitly asks for that output style.
