# Django 5.2 compatibility sweep

## Overview
This update removes deprecated settings and verifies the project aligns with Django 5.2 behavior changes.

## Runtime target
- Django 5.2 supports Python 3.10+; this project targets Python 3.11 for container images.
- Gunicorn 23 and mysqlclient 2.1 are compatible with Python 3.11.

## Environment changes and rollback
- Container images use Python 3.11; no docker-compose files require version changes.
- Rollback: revert the Dockerfile base images and Django version pin, then rebuild images and redeploy.

## Localization behavior
Django 5.2 no longer supports the `USE_L10N` setting. Localization is always enabled, so date/number formatting will follow active locale settings by default.

## Validation checklist
- Run system checks to confirm settings are valid.
- Execute the test suite with coverage requirements (pytest with coverage enabled).
- Run a migrations consistency check before release.
- Run documentation lint/build steps expected by CI.
- Confirm admin and authentication workflows continue to behave as expected.
