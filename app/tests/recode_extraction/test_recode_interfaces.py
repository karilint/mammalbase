from pathlib import Path

from django.test import SimpleTestCase

from recode_extraction.adapters import CorpusAssetAdapter
from recode_extraction.mappers import EtsMapper
from recode_extraction.services import (
    ExtractionPipeline,
    PipelineContext,
    PipelineResult,
)


class RecodeInterfaceScaffoldingTests(SimpleTestCase):
    def test_pipeline_context_defaults(self):
        context = PipelineContext(upload_id='upload-1', pdf_path=Path('file.pdf'))

        assert context.actor_id is None
        assert context.metadata == {}

    def test_pipeline_result_defaults(self):
        result = PipelineResult(upload_id='upload-1')

        assert result.persisted_record_ids == []
        assert result.qc_summary == {}

    def test_interfaces_raise_not_implemented(self):
        pipeline = ExtractionPipeline()
        mapper = EtsMapper()
        adapter = CorpusAssetAdapter()

        with self.assertRaises(NotImplementedError):
            pipeline.run(PipelineContext(upload_id='upload-1', pdf_path=Path('file.pdf')))

        with self.assertRaises(NotImplementedError):
            mapper.map_candidates({})

        with self.assertRaises(NotImplementedError):
            adapter.load_corpus()

        with self.assertRaises(NotImplementedError):
            adapter.resolve_model_path()
