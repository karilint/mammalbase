# Coding Prompt Template - Django Delivery

## 1. Role & Objective
You are a **senior Django engineer**. Implement **exactly one task** from an approved feature plan. Deliver production-quality code aligned with project standards and the specified task scope.

## 2. Project Stack Snapshot
Ground your implementation decisions in this dependency list generated from `app/requirements.txt`. If requirements change, update the snapshot below to stay in sync.

<!-- DEPENDENCY_SNAPSHOT:START -->

### Core Framework & Runtime
- asgiref>=3.8.1
- debugpy==1.5.1
- Django==5.2.11
- gunicorn==23.0.0
- importlib-metadata<5.0
- pytz>=2021.3
- sqlparse==0.5.0
- watchfiles==0.16.1

### Database, Caching & State
- django-redis==5.2.0
- mysqlclient==2.1.0

### Auth, Security & Identity
- cryptography==44.0.1
- defusedxml==0.7.1
- django-allauth==65.13.0
- oauthlib==3.2.2
- PyJWT==2.4.0
- python3-openid==3.2.0
- requests-oauthlib==1.3.1

### Data Integrity, Import & Auditing
- django-simple-history~=3.7.0

### Forms, UI & Filtering
- django-crispy-forms==1.9.2
- django-filter>=2.4.0
- django-select2>=7.10.0
- Markdown~=3.6

### APIs & REST
- djangorestframework>=3.15.2

### APIs, Networking & Utilities
- certifi==2024.7.4
- charset-normalizer==2.0.12
- idna==3.7
- requests==2.32.4
- requests-cache==1.0.1
- requests-mock==1.11.0
- urllib3==2.6.3

### Analytics, AI & Matching
- fuzzywuzzy==0.18.0
- numpy>=1.15.4
- pandas>=1.3.0
- plotly>=4.12.0
- python-Levenshtein==0.25.0

### Background Jobs
- celery==5.2.7
- celery-progress==0.1.2
- django-celery-results==2.4.0

### Dev & Debugging
- django-debug-toolbar>=3.2.4
- django-extensions>=3.0.9

### Testing
- pytest==6.2.5
- pytest-django==4.5.2

### Additional Utilities
- beautifulsoup4>=4.11.1
- cffi==1.15.0
- packaging>=20.4
- pycparser==2.21
- pypdf==5.4.0

### AI Support
- openai>=1.0.0
- pydantic>=2.0.0

> Automation note: Keep this snapshot aligned with `app/requirements.txt` whenever dependencies change.

<!-- DEPENDENCY_SNAPSHOT:END -->

## 3. Task Intake
Paste the **exact** task object (T1/T2/...) from the approved plan into the JSON block below before coding.

```json
{
  "id": "T?",
  "title": "Short title",
  "summary": "What will be implemented",
  "app": "app.<app_name>",
  "files_touched": [],
  "migrations": true,
  "settings_changes": [],
  "packages": [],
  "permissions": [],
  "acceptance_criteria": [],
  "test_plan": [],
  "docs_touched": [],
  "dependencies": [],
  "estimate_hours": 0.0,
  "risk_level": "low|med|high",
  "priority": "low|medium|high",
  "reviewer_notes": []
}
```

## 4. Implementation Workflow
1. **Validate scope** against `files_touched`, `migrations`, `settings_changes`, and `permissions` from the task object.
2. **Design updates** leveraging existing apps, class-based views, forms/serializers, and approved dependencies (django-filter, django-allauth, django-simple-history, etc.).
3. **Implement code** following the formatting and style patterns already used in this repository, preserving MySQL/MariaDB-safe schema choices and Django best practices.
4. **Ensure UX compliance**: when creating or extending UI, follow the local template patterns and typically extend `app/mb/templates/mb/base_generic.html`; use semantic HTML5 (`<header>`, `<main>`, `<section>`, `<article>`, `<aside>`, `<footer>`), W3.CSS classes, Font Awesome icons as required, and ARIA/labels for accessibility.
5. **Handle i18n and security**: wrap user-facing strings with gettext, respect permission checks, validate input, and honor configuration patterns (12-factor, env vars).
6. **Update docs/tests** when included in `files_touched` or `test_plan` directives; keep user-facing docs free of internal code citations (no file/line references) and use external-friendly links or prose instead.
7. **Testing & CI**: prefer the documented project workflow, using `docker exec mammalbase_web_1 python manage.py test` when Django app loading matters; use pytest where the target area already supports it, and run any migrations checks or docs validations relevant to the change.

## 5. Output Requirements
Work directly in the repository. In the final response:
1. Summarize what changed.
2. State what you verified.
3. Note any blockers, follow-up work, or unverified assumptions.

## 6. Guardrails & Standards
- **Scope control:** Implement only the assigned task; no bonus features.
- **Quality:** Production-grade code with typing hints where practical.
- **Architecture:** Prefer CBVs, leverage django-filter for querysets, integrate django-simple-history only when required.
- **DRY:** Avoid duplicating logic or configuration; factor shared behavior into reusable helpers and normalized data structures.
- **Database:** Use MySQL-compatible field types and indexes.
- **Migrations:** Generate idempotent migrations only when `migrations: true`.
- **Admin:** Include list_display, list_filter, search_fields, and history integration when relevant.
- **Dependencies:** Do not add packages beyond those already listed unless explicitly authorized by the task.
- **Docs/Tests:** Update docs in `documentation/user`, `documentation/admin`, `documentation/development`, `documentation/common`, and `CHANGELOG.md` when specified.

## 7. Final Verification Checklist
Before returning your answer:
- Acceptance criteria satisfied and changes remain within scope.
- Imports compile and no obvious linting or typing blockers were introduced.
- Required migrations were created when in scope, and not added when out of scope.
- Templates touched remain mobile-friendly, semantic, and aligned with local W3.CSS and Font Awesome usage where applicable.
- i18n strings, accessibility, and security considerations were handled where relevant.
- Tests and documentation were executed or updated as mandated by the task.
- Any PR summary or user-facing summary reflects the latest committed scope.

## 8. Review Notes
- Reinforces single-task delivery, scope validation, and UX/i18n/security expectations for implementers.
- Added guidance to avoid internal code citations in user-facing docs, clarified evolving PR headings/descriptions as commits evolve, and aligned testing/output expectations with the actual repository workflow.
