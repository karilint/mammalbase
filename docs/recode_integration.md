# RECODE Integration Architecture (Scaffolding Phase)

## End-user and contributor guide
For operational usage and extension workflows, see `docs/recode_user_guide.md`.

## Goal
Integrate **RECODE: Relational Ecological COrpus for Data Extraction** as an internal pipeline for uploaded PDFs while reusing MammalBase ETS import conventions.

## Pipeline Stages and Planned Code Locations

1. **PDF upload ingestion**
   - Planned integration point: existing upload/import request handling layer.
   - Orchestration entrypoint: `recode_extraction.services.pipeline.ExtractionPipeline.run(context)`.

2. **Text extraction from PDF**
   - Planned location: `recode_extraction.adapters`.
   - Adapter contract: `recode_extraction.adapters.corpus.CorpusAssetAdapter`.

3. **Trait candidate extraction (RECODE corpus/model)**
   - Planned location: `recode_extraction.services` with adapter support from `recode_extraction.adapters`.
   - Adapter contract methods:
     - `CorpusAssetAdapter.load_corpus()`
     - `CorpusAssetAdapter.resolve_model_path()`

4. **ETS mapping**
   - Planned location: `recode_extraction.mappers.ets`.
   - Mapper contract: `recode_extraction.mappers.ets.EtsMapper.map_candidates(extraction_payload)`.

5. **Persistence**
   - Planned location: `recode_extraction.services`.
   - Reuse strategy: mapped ETS payload will be normalized through existing ETS import/validation conventions before writing `SourceMeasurementValue` and related source tables.

6. **Quality control (QC)**
   - Planned location: `recode_extraction.services`.
   - Output envelope: `recode_extraction.services.pipeline.PipelineResult.qc_summary`.

## Interface Signatures Introduced in This Phase

### Service layer
- `PipelineContext(upload_id: str, pdf_path: Path, actor_id: int | None = None, metadata: dict[str, Any] = {})`
- `PipelineResult(upload_id: str, persisted_record_ids: list[int] = [], qc_summary: dict[str, Any] = {})`
- `ExtractionPipeline.run(context: PipelineContext) -> PipelineResult`

### Adapter layer
- `CorpusAssetAdapter.load_corpus() -> Any`
- `CorpusAssetAdapter.resolve_model_path() -> Path`

### Mapper layer
- `EtsMapper.map_candidates(extraction_payload: dict[str, Any]) -> list[dict[str, Any]]`

## Existing MammalBase ETS Import Structures and Paths

### ETS data structures currently used
Current ETS-style imports persist into the source-model layer centered around:
- Source measurement records
- Source attributes
- Source entities
- Source references
- Source units
- Source statistics
- Controlled vocabulary values (for ETS categorical fields such as sex/life stage)

### Existing ETS import code path
Current ETS import flow is:
1. Import endpoint dispatches to ETS handler in the imports view layer.
2. Request is processed by shared import wrapper.
3. ETS validator applies field and format validation rules.
4. ETS importer resolves/creates source reference data and persists source measurement values.

### Validator/normalizer reuse plan
RECODE persistence will reuse the ETS import path principles by:
- emitting mapper output in ETS-shaped dictionaries,
- validating required ETS fields with existing ETS validation semantics,
- normalizing null-like values and vocabulary fields consistently with existing importer behavior,
- persisting through the same source-model table family used by current ETS imports.

## Scaffolding Added
- New app: `recode_extraction`
- New packages:
  - `recode_extraction/services/`
  - `recode_extraction/adapters/`
  - `recode_extraction/mappers/`
- New tests package: `tests/recode_extraction/`

This phase intentionally includes architecture and interfaces only, without business logic.

## Phase 2A: RECODE corpus acquisition and local asset management

A management command is provided for reproducible local asset setup:

- Command: `python manage.py recode_fetch_assets`
- Default source: Zenodo record `15254437`, archive `recode.zip`
- Default checksum verification: MD5 `6a371db866c1589d5711ac00797767ad`
- Output layout under `var/recode_assets/`:
  - `recode.zip`
  - `unpacked/`
  - `index.json`

### Index contents (`var/recode_assets/index.json`)
Each indexed TSV entry includes:

- `doc_id`
- `focus_taxon`
- `taxon_group` (`araneae` or `insecta`)
- `annotator` (null when file is under `all/`)
- `tsv_path`
- `metadata` (row from `recode/metadata.csv` when matched by document identifier)

### Folder convention handling
- Under `recode/araneae` and `recode/insecta`, the indexer supports:
  - files under `all/` (no annotator)
  - files nested under annotator directories (annotator inferred from first path segment)
- TSV filename stems are interpreted as `<focus_taxon>_<doc_id>` for index fields.

## Phase 3: PDF ingestion and source persistence

A minimal source-ingestion flow is available in the `recode_extraction` app:

- `SourceDocument` stores uploaded PDF and source metadata (title, authors, year, DOI, uploader, created timestamp).
- `SourceExtractionRun` stores extraction run lifecycle metadata (status, timestamps, logs, model version, parameters) linked to a source document.

### UI endpoints
- List sources: `recode/sources/`
- Upload source PDF: `recode/sources/upload/`
- Source detail + run trigger: `recode/sources/<id>/`
- Run trigger POST endpoint: `recode/sources/<id>/run/`

### Current run behavior
The “Run RECODE Extraction” button creates a queued `SourceExtractionRun` record through a placeholder service call.
Pipeline execution remains intentionally unimplemented in this phase.

## Phase 4: PDF text extraction and canonical text package

`PdfToTextService` provides canonical extraction output:

- `pages`: list of page objects with `page_number` and extracted `text`
- `full_text`: concatenated text from all pages
- `extraction_warnings`: warnings collected during extraction

### Backends
- Default backend: `pypdf`.
- Optional backend: `pdftotext` system command, automatically used when explicitly preferred and available, or as fallback if `pypdf` is unavailable.

### Persistence
`SourceExtractionRun` stores extracted output in `extracted_text_package` and records status/log updates from the text extraction stage.

## Phase 5: RECODE-style information extraction layer

### Corpus reader
`RecodeTsvReader` consumes `index.json` and loads referenced TSV annotations into dataclasses:

- `Entity` (`entity_type`, `text`, span offsets, `doc_id`)
- `Relation` (`head_entity_id`, `tail_entity_id`, `relation_type`, `doc_id`)
- `AnnotatedDocument` (entities + relations + provenance such as annotator)

The reader supports mixed TSV schemas by normalizing common column variants for entity/relation tables.

### Extraction engine
`ExtractionEngine` exposes pluggable backends:

- `BaselineRuleExtractor`: regex-based extraction for mammal trait patterns (for example body mass, adult mass, length, litter size, zygomatic breadth, dietary class)
- `LlmAssistedExtractor`: integration stub for future model-assisted extraction

The stable intermediate output dataclass is `ExtractedAssertion` with:

- `subject_taxon`
- `trait_name`
- `value`
- `unit`
- `context`
- `confidence`
- `evidence_spans` (offset ranges)

## Phase 6: ETS mapping from extracted assertions

`EtsMapper` maps `ExtractedAssertion` objects into ETS import-compatible records.

### Mapping behavior
- Maps normalized `trait_name` values to MammalBase trait definition identifiers (`traitID`).
- Normalizes numeric values from point estimates, ranges (`min-max`), and mean±sd (`x ± y`) into ETS measurement fields.
- Avoids irrelevant units by applying trait-specific allowed-unit sets.
- Produces provenance fields for curator traceability:
  - `source_document_id`
  - `source_extraction_run_id`
  - `evidence_snippet`
  - `evidence_page_number`
  - `evidence_offsets`

### Validation and curation support
- Invalid numeric values are rejected from ETS record output.
- Unmapped trait names are captured separately as `unmapped_traits` for curator review.

## Phase 7: persistence layer for entities, assertions, ETS records

### Persistent extraction models
- `ExtractedEntity`: persisted taxon/trait/value mentions linked to `SourceExtractionRun`
- `ExtractedAssertionModel`: persisted extracted assertions linked to `SourceExtractionRun`, including ETS mapping payload and persistence flags

### Pipeline persistence behavior
- Pipeline always stores extracted entities and assertions.
- ETS record persistence reuses existing MammalBase ETS import path by feeding mapped records into the existing importer.
- Dry-run mode (`dry_run=True`) stores entities/assertions and mapping data but skips ETS table writes.

### Transactional safety
- ETS persistence executes in a single database transaction per run.
- If ETS persistence fails, run status is set to `failed` and assertion-level ETS persisted flags remain false (no partial success state).

## Phase 8: pipeline orchestration and background execution

`RecodePipelineRunner.run(source_document_id, run_params)` now orchestrates the full flow:

1. PDF text extraction
2. information extraction
3. ETS mapping
4. ETS persistence (unless dry-run)

### Status/progress tracking
Each run updates:
- `status`
- `current_stage`
- `progress_percent`
- `logs`
- `parameters` (backend, threshold, mapping version, dry-run, context)

### Background execution
- Celery task: `run_recode_pipeline(source_document_id, run_params)`
- View behavior:
  - if `RECODE_ASYNC=1`, queue background task
  - otherwise run synchronously via `create_extraction_run` wrapper

This keeps a synchronous fallback while exposing a clean async execution interface.

## Phase 9: curator QC review UI

### Extraction run detail page
A curator-facing run detail page is available at `recode/runs/<run_id>/` with:
- summary counts (`entities`, `assertions`, `mapped`, `unmapped`)
- filters by trait, taxon, confidence, page, and review status
- CSV export of the filtered review table

### Assertion review workflow
Per-assertion review supports:
- approve/reject/pending status
- edit value and unit
- add reviewer notes
- map `trait_name` to an ETS `traitID` for previously unmapped rows

### Bulk actions
- Approve all pending assertions above a confidence threshold
- Persist approved assertions to ETS

Rejected assertions remain stored for traceability and are excluded from ETS persistence.

## Phase 10: evaluation and regression tooling

A management command `python manage.py recode_eval` is available to run fast evaluation on RECODE-style indexed subsets.

### Supported RECODE conventions
- Reads `index.json` generated from the RECODE structure with `recode/metadata.csv`, taxon partitions (`araneae`, `insecta`), and TSV files under annotator subfolders or `all/`.
- Evaluates a subset of annotated docs and compares predictions against TSV-derived entities/relations.

### Metrics output
- Precision/recall/F1 by entity type
- Precision/recall/F1 by relation type
- Stable machine-readable JSON printed to console and optionally written to a JSON file via `--output-json`.

### CI regression coverage
`django.yml` now includes a dedicated RECODE regression test step to ensure corpus reader compatibility and metric execution remain operational.

## OpenAI Two-Pass Extraction (PASS1 evidence → PASS2 ETS)

MammalBase now supports a production two-pass ChatGPT extraction pipeline aligned with the internal Two-Pass ETS+DwC spec.

### Required settings/env vars
- `RECODE_ENABLE_OPENAI_BACKEND` (default `False`)
- `OPENAI_API_KEY`
- `RECODE_OPENAI_MODEL_PASS1` / `RECODE_OPENAI_MODEL_PASS2`
- `RECODE_OPENAI_TIMEOUT_SECONDS`
- `RECODE_OPENAI_MAX_RETRIES`
- `RECODE_OPENAI_MAX_PAGE_CHARS`
- `RECODE_OPENAI_PASS1_MAX_ITEMS_PER_BUCKET` (default 120)
- `RECODE_OPENAI_PASS1_MAX_ITEM_CHARS` (default 2500)
- `RECODE_OPENAI_PASS1_MAX_TABLE_ITEM_CHARS` (default 12000)

### Vocabulary construction
Trait vocabulary is built dynamically from MammalBase:
- Abbreviation dictionary from `MasterAttribute.name` and `SourceAttribute.name`
- Trait list from Taxon-scoped `MasterAttribute` and frequent `SourceAttribute`
- A small bootstrap dictionary is used only if DB-derived abbreviations are sparse

### Pipeline and stored artifacts
1. `extracted_text_package` is always stored from `PdfToTextService`
2. PASS1 evidence JSON is persisted to `pass1_evidence_package`
3. PASS2 trait record JSON is persisted to `pass2_structured_package`
4. Deterministic QC + normalization runs before import and stores `qc_summary`
5. Candidate rows are stored in `ExtractedAssertionModel` with pending review
6. Final source-table persistence happens only from approved assertions using ETS importer flow
- PASS1 evidence is compacted before PASS2: non-morphology analytical content (PCA/factor loadings/eigenvalues and genetic-distance/phylogenetic snippets like K2P/Cyt b/COI) is filtered out; per-bucket item count and item length are capped to reduce token usage and 429 TPM errors.
- QC enforces canonical article-level `references` (authors, year, title) when model output contains non-citation labels (e.g., `PAGE 5: Table 1`), while `associatedReferences` is kept for trait-level support (`Original study` fallback).

### Testing
Run:
- `DJANGO_SETTINGS_MODULE=app.config.settings python -m pytest app/tests/recode_extraction/test_openai_two_pass_pipeline.py`
- `DJANGO_SETTINGS_MODULE=app.config.settings python -m pytest app/tests/recode_extraction/test_openai_qc_normalization.py`
- `DJANGO_SETTINGS_MODULE=app.config.settings python -m pytest app/tests/recode_extraction/test_openai_schema.py`
- `DJANGO_SETTINGS_MODULE=app.config.settings python -m pytest app/tests/recode_extraction/test_openai_client_adapter.py`
- `DJANGO_SETTINGS_MODULE=app.config.settings python -m pytest app/tests/recode_extraction/test_qc_review.py`

Notes:
- In restricted containers, `PytestCacheWarning` for `.pytest_cache` is non-functional noise and does not indicate test failures.
- OpenAI API calls must be mocked in unit tests; do not run live external API calls in test suites.
- Adapter-level mocking pattern is implemented in `app/tests/recode_extraction/conftest.py` (`mock_openai` fixture) and `test_openai_client_adapter.py`.

References:
- OpenAI Python SDK: https://github.com/openai/openai-python
- Structured outputs guide: https://developers.openai.com/api/docs/guides/structured-outputs/

## Migration note: legacy `recode_extraction_extractedassertionmodel.coord_text` schema drift

Some older MammalBase deployments may still contain a legacy `coord_text` column on
`recode_extraction_extractedassertionmodel` that is `NOT NULL` without a default.
The current `ExtractedAssertionModel` does not define this column, so assertion
inserts in the RECODE pipeline can fail with:

- `(1364, "Field 'coord_text' doesn't have a default value")`

A compatibility migration
(`recode_extraction.0008_fix_legacy_extractedassertion_coord_text`) drops the
obsolete column when present. This is safe for RECODE ETS extraction because that flow
does not persist coordinate fields on `ExtractedAssertionModel`.

Run:

- `python manage.py migrate recode_extraction`

Then verify that creating extraction assertions succeeds and no longer errors on
`coord_text`.
