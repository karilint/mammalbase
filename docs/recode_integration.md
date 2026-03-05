# RECODE → MammalBase NE/RE Workflow

This implementation uses a graph-driven extraction workflow: parse/predict spans and relation arcs, persist them, build TraitVal-centered candidates, then map to ETS rows.

## WebAnno TSV 3.3 parsing
- Parser: `app/recode_extraction/adapters/webanno_parser.py`
- Header-driven parsing of `#FORMAT`, `#T_SP`, `#T_RL` (no hard-coded annotation column indices).
- Handles stacked annotations (`|`), missing relation columns, disambiguation IDs (`Species[1]`), and arc endpoints with optional `[src_tgt]` disambiguation.
- UTF-16 code-unit offsets are stored as-is (`start_offset_utf16`, `end_offset_utf16`).

## Models
- `ExtractedEntity`: free-form `entity_type`, `span_external_id`, `token_ids`, UTF-16 offsets, `page_number`, `snippet`.
- `ExtractedRelation`: typed edges between persisted entities with provenance.
- `ExtractedAssertionModel`: QC candidate/status model with optional context columns and ETS import linkage.

## Running tests
```bash
python manage.py test recode_extraction
```

## Fixture parser example
```bash
python manage.py shell -c "from recode_extraction.adapters.webanno_parser import parse_webanno_tsv33; print(len(parse_webanno_tsv33('recode_extraction/tests/fixtures/webanno_tsv33/simple_trait_measurement.tsv').spans))"
```

## References
- WebAnno TSV 3.3 spec: https://webanno.github.io/webanno/releases/3.6.11/docs/user-guide.html
- RECODE Zenodo: https://zenodo.org/records/15254437
- arete (CRAN), functions `webanno_open`, `labels`, `labels_unique`: https://cran.r-project.org/package=arete
