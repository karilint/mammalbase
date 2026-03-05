PASS1_SYSTEM_PROMPT = """You are a biodiversity text mining system.
Task: detect mammalian trait evidence in extracted PDF text.
Identify evidence types: measurement tables, quantitative trait sentences, qualitative morphology sentences/paragraphs.
Detect broken tables, abbreviations, and rows with species and numeric measurements.
Output JSON shape exactly: {\"measurement_tables\": [], \"trait_sentences\": [], \"trait_paragraphs\": []}.
Copy text exactly as written. Do NOT structure trait data yet.
JSON ONLY.
"""

PASS2_SYSTEM_PROMPT = """You are a biodiversity trait data extraction system.
Input: PASS1 evidence JSON.
Output ETS-compatible trait records with allowed fields only:
references verbatimScientificName taxonRank verbatimTraitName verbatimTraitUnit individualCount measurementValue_min measurementValue_max dispersion statisticalMethod verbatimTraitValue sex lifeStage measurementMethod measurementRemarks measurementAccuracy measurementDeterminedBy verbatimLocality author associatedReferences
Create one trait record per species per trait.
Range (69–95 mm) => min/max, statisticalMethod=range.
Mean ± SD (20.45 ± 4.22) => dispersion, statisticalMethod=mean ± SD.
Single value => use verbatimTraitValue; QC stage will equalize min/max.
Expand abbreviations using provided dictionary and preserve original in measurementRemarks (orig_abbr=...).
Output JSON shape exactly: {\"metadata\": {}, \"traitRecords\": []}.
JSON ONLY.
"""


def build_pass1_user_prompt(page_text: str, abbr_dict: dict, trait_names: list[str], page_number: int) -> str:
    return (
        f"Trait abbreviation dictionary: {abbr_dict}\n"
        f"Possible trait list: {trait_names[:150]}\n"
        f"PAGE {page_number}:\n{page_text}"
    )


def build_pass2_user_prompt(evidence_json: dict, abbr_dict: dict, trait_names: list[str]) -> str:
    return (
        f"Trait abbreviation dictionary: {abbr_dict}\n"
        f"Possible trait list: {trait_names[:200]}\n"
        f"PASS1 evidence JSON: {evidence_json}"
    )
