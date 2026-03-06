from recode_extraction.adapters.openai_client import Pass2Output


def test_pass2_schema_has_closed_metadata_object():
    schema = Pass2Output.model_json_schema()
    metadata_ref = schema['properties']['metadata']['$ref']
    metadata_def = schema['$defs'][metadata_ref.split('/')[-1]]
    assert metadata_def.get('additionalProperties') is False
