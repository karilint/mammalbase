import tempfile
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from recode_extraction.models import ExtractedAssertionModel, SourceDocument, SourceExtractionRun
from recode_extraction.services.orchestrator import RecodePipelineRunner


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(), RECODE_ENABLE_OPENAI_BACKEND=True)
class OpenAITwoPassPipelineTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username='oa', email='oa@example.com', password='pw')
        self.document = SourceDocument.objects.create(
            pdf_file=SimpleUploadedFile('runner.pdf', b'%PDF-1.4\ncontent', content_type='application/pdf'),
            title='Runner Source',
            year=2024,
            uploader=user,
        )

    @mock.patch('recode_extraction.services.orchestrator.TraitVocabularyService.get_vocab')
    @mock.patch('recode_extraction.services.orchestrator.OpenAITwoPassClient')
    @mock.patch('recode_extraction.services.orchestrator.PdfToTextService.extract')
    def test_pipeline_creates_pending_candidate(self, extract_mock, client_cls, vocab_mock):
        extract_mock.return_value = {'pages': [{'page_number': 1, 'text': 'BW HB TL\n20.4 82.9 87.4'}], 'full_text': 'x'}
        vocab_mock.return_value = mock.Mock(abbr_dict={'BW': {'trait_name': 'body weight', 'unit': 'g'}}, trait_names=['body weight'])

        client = client_cls.return_value
        client.extract_pass1.return_value = mock.Mock(measurement_tables=['PAGE 1:\nBW HB TL\n20.4 82.9 87.4'], trait_sentences=['PAGE 1: The species has a head-body length of 69–95 mm.'], trait_paragraphs=[])
        client.extract_pass2.return_value = mock.Mock(
            traitRecords=[mock.Mock(model_dump=lambda exclude_none=True: {
                'verbatimScientificName': 'Mus musculus',
                'taxonRank': 'species',
                'verbatimTraitName': 'body weight',
                'verbatimTraitUnit': 'g',
                'verbatimTraitValue': '20.45 ± 4.22',
                'individualCount': 33,
                'statisticalMethod': 'mean ± SD',
                'references': 'Doe 2024 Mammal Journal',
                'author': '0000-0000-0000-0000',
                'associatedReferences': 'Original study',
                'measurementRemarks': 'page=1 evidence=BW value row',
            })],
            model_dump=lambda: {'metadata': {}, 'traitRecords': [{'verbatimTraitName': 'body weight'}]},
        )

        run = RecodePipelineRunner().run(self.document.pk, run_params={'dry_run': True, 'extraction_backend': 'openai_two_pass'})
        run.refresh_from_db()
        self.assertEqual(run.status, SourceExtractionRun.Status.COMPLETED)
        self.assertTrue(run.pass1_evidence_package['measurement_tables'])
        self.assertEqual(len(run.pass2_structured_package['traitRecords']), 1)
        self.assertEqual(ExtractedAssertionModel.objects.filter(extraction_run=run).count(), 1)
        assertion = ExtractedAssertionModel.objects.get(extraction_run=run)
        self.assertEqual(assertion.subject_taxon, 'Mus musculus')
        self.assertEqual(assertion.trait_name, 'body weight')
        self.assertIn('20.45', assertion.value_raw)
        self.assertEqual(assertion.ets_payload['verbatimTraitName'], 'body weight')
        self.assertIn('page=1', assertion.ets_payload['measurementRemarks'])
        self.assertIn('run_id=', assertion.ets_payload['measurementRemarks'])
