# Django 5.2 compatibility sweep

## Overview
This update removes deprecated settings and verifies the project aligns with Django 5.2 behavior changes.

## Runtime target
- Django 5.2 supports Python 3.10+; this project targets Python 3.11 for container images.
- Gunicorn 23 and mysqlclient 2.1 are compatible with Python 3.11.

## Environment changes and rollback
- Container images use Python 3.11; no docker-compose files require version changes.
- Rollback: revert the Dockerfile base images and Django version pin, then rebuild images and redeploy.

## Dependency notes
- `django-allauth` and `django-simple-history` are updated to versions compatible with Django 5.2.
- Review third-party release notes before any further upgrades.

## Review findings
- Settings and middleware references align with Django 5.2 defaults; documentation links updated to the 5.2 docs.
- Added `allauth.account.middleware.AccountMiddleware` to satisfy django-allauth 0.63+ requirements.
- URL routing remains on modern `path`/`re_path` usage; no deprecated routing APIs found.
- No deprecated ORM or template tags were detected in the current scan.
- Templates continue to extend `mb/base_generic.html`, which includes semantic landmarks (`main`, `article`, `aside`, `footer`).
- W3.CSS and Font Awesome assets remain referenced in the base template for consistent styling and iconography.
- No template content was changed in this pass, so existing i18n wrapping remains unchanged.
- django-filter usage remains in dedicated FilterSet modules with no Django 5.2-specific deprecations observed.
- No Django REST Framework serializers or viewsets were found in the current codebase (DRF remains disabled in settings).
- Pagination templates continue to include the shared `mb/pagination.html` partial from list views.

## Localization behavior
Django 5.2 no longer supports the `USE_L10N` setting. Localization is always enabled, so date/number formatting will follow active locale settings by default.

## Validation checklist
- Run system checks to confirm settings are valid.
- Execute the test suite with coverage requirements (pytest with coverage enabled).
- Run a migrations consistency check before release (MySQL in CI, SQLite in test settings).
- Use the SQLite test settings module when running local migration checks without MySQL.
- Run documentation lint/build steps expected by CI.
- Confirm admin and authentication workflows continue to behave as expected.
- Re-verify django-allauth login redirects and OAuth provider flows (ORCID) after upgrade.
- Validate admin registrations, permissions, and list views for core models.
- Confirm django-simple-history middleware loads and audit history tracking remains intact.
- Pay extra attention to timezone formatting and admin UI tests that depend on localization.
