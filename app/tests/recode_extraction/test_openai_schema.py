import unittest

from recode_extraction.adapters.openai_client import Pass2Output


class OpenAISchemaTests(unittest.TestCase):
    def test_pass2_schema_has_closed_metadata_object(self):
        schema = Pass2Output.model_json_schema()
        metadata_ref = schema['properties']['metadata']['$ref']
        metadata_def = schema['$defs'][metadata_ref.split('/')[-1]]
        self.assertEqual(metadata_def.get('additionalProperties'), False)


if __name__ == '__main__':
    unittest.main()
