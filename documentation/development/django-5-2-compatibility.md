# Django 5.2 compatibility sweep

## Overview
This update removes deprecated settings and verifies the project aligns with Django 5.2 behavior changes.

## Localization behavior
Django 5.2 no longer supports the `USE_L10N` setting. Localization is always enabled, so date/number formatting will follow active locale settings by default.

## Validation checklist
- Run system checks to confirm settings are valid.
- Execute the test suite with coverage requirements.
- Confirm admin and authentication workflows continue to behave as expected.
