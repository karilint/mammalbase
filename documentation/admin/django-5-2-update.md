# Django 5.2 admin update notes

## Admin behavior
Admin pages continue to respect the current locale for formatting dates and numbers.

## Verification
After deployment, verify admin login and standard CRUD workflows operate normally, including audit fields on export
records.

## Testing status
Admin workflows are covered by automated tests and CI checks for the upgrade, including audit field verification.

## Rollback plan
If issues are detected, revert to the previous deployment image and re-verify admin workflows.
