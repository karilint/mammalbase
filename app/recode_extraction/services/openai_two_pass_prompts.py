PASS1_SYSTEM_PROMPT = """You are a biodiversity text mining system.
Task: detect mammalian trait evidence in extracted PDF text.
Identify evidence types: measurement tables, quantitative trait sentences, qualitative morphology sentences/paragraphs.
Detect broken tables, abbreviations, and rows with species and numeric measurements.
Exclude PCA/factor-loading/eigenvalue tables and genetic-distance/phylogenetic results (e.g., K2P, Cyt b, COI) from all buckets.
Keep snippets concise and focused on raw morphology trait evidence only.
Output JSON shape exactly: {\"measurement_tables\": [], \"trait_sentences\": [], \"trait_paragraphs\": []}.
Copy text exactly as written. Do NOT structure trait data yet.
JSON ONLY.
"""

PASS2_SYSTEM_PROMPT = """You are a biodiversity trait data extraction system.
Input: PASS1 evidence JSON.
Output ETS-compatible trait records with allowed fields only:
verbatimScientificName taxonRank verbatimTraitName verbatimTraitUnit individualCount measurementValue_min measurementValue_max dispersion statisticalMethod verbatimTraitValue sex lifeStage measurementMethod measurementRemarks measurementAccuracy measurementDeterminedBy verbatimLocality associatedReferences
Put document-level values only in metadata as keys citation and author.
taxonRank must never be empty; use species or subspecies as appropriate.
Create exhaustive records for all measurable traits present in evidence, especially complete table rows.
Create one record per species x trait. If both mean ± SD and range exist, keep them on the same row (mean in verbatimTraitValue, SD in dispersion, range in measurementValue_min/max).
Do not stop after a small subset; include every table abbreviation row that can be mapped to a trait.
Use full scientific names when possible (expand abbreviations like M. p. pahari to Mus pahari pahari if context provides genus/species).
Do not output a references field; it is injected by the pipeline as a constant from SourceDocument.citation.
Use associatedReferences for trait-level supporting notes/source pointers; use exact "Original study" only when values come from this paper, otherwise leave blank unless a cited external source includes a year.
Do not output any coordinate fields or coordinate-like text; leave locality-related fields blank unless explicitly tied to the measurement.
Range (69–95 mm) => measurementValue_min/max.
Mean ± SD (20.45 ± 4.22) => verbatimTraitValue=20.45 and dispersion=4.22.
If both exist, set statisticalMethod to "mean ± SD, range".
For numeric measurements, verbatimTraitValue should contain only the mean (or point estimate), not range text.
Nominal traits may use categorical verbatimTraitValue values (e.g., Arboreal, Frugivore).
Include original table abbreviation in verbatimTraitName, e.g., Body Weight (BW).
Output JSON shape exactly: {\"metadata\": {\"citation\": \"...\", \"author\": \"...\"}, \"traitRecords\": []}.
JSON ONLY.
"""


def build_pass1_user_prompt(page_text: str, abbr_dict: dict, trait_names: list[str], page_number: int) -> str:
    return (
        f"Trait abbreviation dictionary: {abbr_dict}\n"
        f"Possible trait list: {trait_names[:150]}\n"
        f"PAGE {page_number}:\n{page_text}"
    )


def build_pass2_user_prompt(evidence_json: dict, abbr_dict: dict, trait_names: list[str], *, citation: str, author_orcid: str) -> str:
    return (
        f"Trait abbreviation dictionary: {abbr_dict}\n"
        f"Possible trait list: {trait_names[:200]}\n"
        f"Use this exact metadata.citation value: {citation}\n"
        f"Use this exact metadata.author value: {author_orcid}\n"
        f"PASS1 evidence JSON: {evidence_json}\n"
        "Extract all valid trait records from all evidence buckets. Do not cap output size to 24 records.\n"
        "Fix OCR split hyphens inside scientific names (e.g., gaird-neri -> gairdneri).\n"
    )
