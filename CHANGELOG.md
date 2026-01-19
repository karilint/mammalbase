# Changelog

## Unreleased
- Update Django to 5.2.2 LTS.
- Remove deprecated localization settings for Django 5.2.
- Add Django 5.2 upgrade testing and documentation notes.
- Document Python 3.11 runtime target and rollback guidance for the upgrade.
- Update django-allauth and django-simple-history for Django 5.2 compatibility.
- Record template and i18n review notes for the Django 5.2 sweep.
- Add verification checklist items for auth flows, admin permissions, and history tracking.
- Document django-filter/pagination review and DRF status notes.
- Clarify migration checks for MySQL and SQLite in upgrade notes.
- Add allauth AccountMiddleware required for the upgrade.
- Add a SQLite test settings module for migration checks.
- Add release gating and rollback guidance for the Django 5.2 upgrade.
- Align BaseModel audit fields with AutoUserForeignKey for automatic user attribution.
- Ensure export requests populate audit user fields on creation.
- Add export permission and audit coverage in tests and update validation notes.
- Document test import conventions and Django test runner guidance for current app packages.
