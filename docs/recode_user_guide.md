# RECODE Extraction User Guide & Contributor Playbook

This guide explains how to run the RECODE extraction feature locally, review results, and extend the pipeline safely.

> **Authoritative corpus source:** RECODE Zenodo record **15254437** (`recode.zip`) is the canonical source for corpus file structure and content. Always align local expectations with that record before changing parser/index logic.

---

## 1) Local setup (developer quickstart)

From repository root:

```bash
cd app
python manage.py migrate
python manage.py check
```

Recommended environment defaults:

```bash
export RECODE_ASSETS_DIR="$(pwd)/var/recode_assets"
export RECODE_ENABLE_LLM_BACKEND=0
export RECODE_MAX_PDF_MB=25
export RECODE_TIMEOUT_SECONDS=120
```

Run server:

```bash
python manage.py runserver 0.0.0.0:8000
```

---

## 2) Acquire RECODE corpus assets (Phase 2A)

### 2.1 Fetch from Zenodo

```bash
python manage.py recode_fetch_assets
```

This command downloads `recode.zip`, verifies checksum, unpacks it, and writes an `index.json`.

If your environment blocks outbound access to Zenodo, use local-archive mode:

```bash
python manage.py recode_fetch_assets --assets-root /path/to/assets --skip-download --md5 <archive_md5>
```

### 2.2 Directory layout

Under `$RECODE_ASSETS_DIR` (default `app/var/recode_assets`):

- `recode.zip`
- `unpacked/recode/metadata.csv`
- `unpacked/recode/araneae/.../*.tsv`
- `unpacked/recode/insecta/.../*.tsv`
- `index.json`

`index.json` entries include:

- `doc_id`
- `focus_taxon`
- `taxon_group` (`araneae`/`insecta`)
- `annotator` (or `null` for `all/` folders)
- `tsv_path`
- `metadata` (from `metadata.csv` when matched)

---

## 3) Upload a PDF source

1. Sign in to MammalBase.
2. Open: `http://localhost:8000/recode/sources/`
3. Click **Upload PDF Source**.
4. Fill in title (+ optional authors/year/DOI) and choose PDF.
5. Submit.

Validation and security checks:

- File extension must be `.pdf`
- Magic bytes must start with `%PDF-`
- File size must be <= `RECODE_MAX_PDF_MB`
- Filename is sanitized before storage

Stored records:

- `SourceDocument` DB row
- uploaded file under `MEDIA_ROOT/recode_sources/`

---

## 4) Run extraction

From the source detail page (`/recode/sources/<id>/`):

- choose backend (`baseline` or `llm`)
- set confidence threshold
- click **Run RECODE Extraction** or **Run Dry-Run Extraction**

Behavior:

- Sync path (default): request runs pipeline immediately.
- Async path: set `RECODE_ASYNC=1` and Celery task is queued.

### Backend selection

- `baseline`: regex rule backend (always available)
- `llm`: disabled by default; requires `RECODE_ENABLE_LLM_BACKEND=1`

If LLM is disabled and selected, the run is marked failed with a clear log message.

---

## 5) Review results (curator UI)

Open run detail page: `/recode/runs/<run_id>/`

Capabilities:

- summary stats (`entities/assertions/mapped/unmapped`)
- filtering by trait/taxon/page/confidence/review status
- per-row edits: value/unit/trait mapping + approve/reject
- bulk approve above threshold
- export filtered CSV
- persist approved assertions to ETS

---

## 6) How ETS records are created

1. Extraction produces `ExtractedAssertionModel` rows.
2. Mapper (`EtsMapper`) converts assertions to ETS-shaped dictionaries.
3. Review flow can override values/units/mapped trait IDs.
4. `persist_approved_assertions_to_ets` validates with `Ets_validation`.
5. Valid rows are persisted through existing `EtsImporter`.

Rejected assertions remain stored for provenance and audit, but are not persisted to ETS.

---

## 7) Contributor playbook

## 7.1 Add new trait extraction rules

Edit:

- `recode_extraction/services/extraction.py`

Update `BaselineRuleExtractor.TRAIT_PATTERNS` with careful regex + unit handling.

Then add tests in:

- `tests/recode_extraction/test_extraction_engine.py`

## 7.2 Add/update trait mapping to ETS

Edit:

- `recode_extraction/mappers/ets.py`

Ensure:

- trait name maps to valid ETS trait IDs
- numeric normalization still passes ETS validation
- unmapped trait behavior remains explicit

Add/adjust tests:

- `tests/recode_extraction/test_ets_mapper.py`

## 7.3 Switch extraction backend

- UI sends backend name (`baseline`/`llm`) from source detail form.
- Orchestrator chooses backend accordingly.
- LLM backend is feature-gated by `RECODE_ENABLE_LLM_BACKEND`.

For future providers, keep API credentials external (env/secret manager) and never hardcode keys.

## 7.4 Create fixture PDFs and TSVs

### Minimal PDF fixture (single page)

```bash
python - <<'PY'
from pypdf import PdfWriter
from pathlib import Path

out = Path('tests/recode_extraction/assets/generated_single_page.pdf')
out.parent.mkdir(parents=True, exist_ok=True)
writer = PdfWriter()
writer.add_blank_page(width=300, height=300)
with out.open('wb') as fh:
    writer.write(fh)
print(out)
PY
```

For realistic text extraction tests, commit small deterministic PDFs and assert exact expected snippets/page counts.

### Minimal TSV fixture

```bash
mkdir -p tests/recode_extraction/assets/recode_fixture/unpacked/recode/araneae/all
cat > tests/recode_extraction/assets/recode_fixture/unpacked/recode/araneae/all/example_DOC999.tsv <<'TSV'
entity_id	entity_type	text	doc_id	start	end
E1	TAXON	Canis lupus	DOC999	0	11
E2	TRAIT	body mass	DOC999	12	21
E3	VALUE	12 kg	DOC999	22	27
head_entity	tail_entity	relation_type	doc_id
E1	E3	has_trait	DOC999
TSV
```

Then add a matching entry in `tests/recode_extraction/assets/recode_fixture/index.json`.

---

## 8) Useful management commands

```bash
python manage.py recode_fetch_assets --help
python manage.py recode_eval --help
python manage.py recode_purge_old_runs --help
```

Example purge old runs (safe preview):

```bash
python manage.py recode_purge_old_runs --days 30 --dry-run
```

---

## 9) Production hardening checklist

- Set `DEBUG=False`
- Configure persistent `MEDIA_ROOT`
- Set `RECODE_ASSETS_DIR` on shared storage
- Keep `RECODE_ENABLE_LLM_BACKEND=0` until provider integration is production-ready
- Tune `RECODE_MAX_PDF_MB` and `RECODE_TIMEOUT_SECONDS` for infrastructure limits
- Schedule `recode_purge_old_runs` via cron/Celery beat for housekeeping
