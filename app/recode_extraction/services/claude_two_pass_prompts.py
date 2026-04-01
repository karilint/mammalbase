"""Claude two-pass prompt placeholders.

These templates mirror the OpenAI two-pass task contract so a Claude adapter can
be added later without changing orchestration/UI contracts.
"""

CLAUDE_PASS1_SYSTEM_PROMPT = """You are a biodiversity text mining system.
Detect mammalian trait evidence from page text.
Output JSON only with keys: measurement_tables, trait_sentences, trait_paragraphs.
Exclude PCA/genetic-distance content.
"""

CLAUDE_PASS2_SYSTEM_PROMPT = """You are a biodiversity trait extraction system.
Convert PASS1 evidence JSON into ETS-compatible traitRecords.
Return JSON with keys: metadata and traitRecords.
metadata must include citation and author.
Each traitRecord must include non-empty taxonRank where applicable.
"""


def build_claude_pass1_prompt(page_text: str, abbr_dict: dict, trait_names: list[str], page_number: int) -> str:
    return (
        f"Trait abbreviation dictionary: {abbr_dict}\n"
        f"Possible trait list: {trait_names[:150]}\n"
        f"PAGE {page_number}:\n{page_text}"
    )


def build_claude_pass2_prompt(evidence_json: dict, abbr_dict: dict, trait_names: list[str], *, citation: str, author_orcid: str) -> str:
    return (
        f"Trait abbreviation dictionary: {abbr_dict}\n"
        f"Possible trait list: {trait_names[:200]}\n"
        f"Use metadata.citation={citation}\n"
        f"Use metadata.author={author_orcid}\n"
        f"PASS1 evidence JSON: {evidence_json}\n"
    )
