# Auditing fields (created_by / modified_by)

MammalBase models that inherit the shared base model capture the user who
created and last modified a record. These fields are populated automatically
when a request is handled by Django and `request.user` is available.

## How it works

- The audit fields are set automatically during model save operations when
  a request-bound user is available.
- For background jobs (for example Celery tasks), there is no request context,
  so audit fields must be set before scheduling work, or left unchanged when
  jobs update existing records.

## Usage guidance

- Create records in request-bound views, forms, or serializers so audit fields
  are applied automatically.
- For async workflows, create the database record first, then pass the record
  ID to the task for processing.
- Avoid duplicating audit logic in each app; prefer the shared base model
  behavior so all audited models are consistent.

## Export workflow note

Exports should create the database record in the request cycle before
enqueueing background work. This guarantees the audit fields are populated
consistently even when the export is processed asynchronously.
