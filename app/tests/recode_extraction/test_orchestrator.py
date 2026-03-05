import tempfile
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from recode_extraction.models import SourceDocument, SourceExtractionRun
from recode_extraction.services.orchestrator import RecodePipelineRunner


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class RecodePipelineRunnerTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='runner-user',
            email='runner@example.com',
            password='pw-123456',
        )
        self.document = SourceDocument.objects.create(
            pdf_file=SimpleUploadedFile('runner.pdf', b'%PDF-1.4\ncontent', content_type='application/pdf'),
            title='Runner Source',
            year=2024,
            uploader=self.user,
        )

    @mock.patch('recode_extraction.services.orchestrator.PdfToTextService.extract')
    def test_runner_completes_and_updates_progress(self, extract_mock):
        extract_mock.return_value = {
            'pages': [{'page_number': 1, 'text': 'Canis lupus body mass is 12 kg.'}],
            'full_text': 'Canis lupus body mass is 12 kg.',
            'extraction_warnings': [],
            'backend': 'pypdf',
        }

        run = RecodePipelineRunner().run(
            self.document.pk,
            run_params={
                'actor_id': self.user.pk,
                'dry_run': True,
                'extraction_backend': 'baseline',
                'confidence_threshold': 0.0,
                'mapping_version': 'v1',
            },
        )

        run.refresh_from_db()
        self.assertEqual(run.status, SourceExtractionRun.Status.COMPLETED)
        self.assertEqual(run.current_stage, 'completed')
        self.assertEqual(run.progress_percent, 100)
        self.assertEqual(run.parameters['extraction_backend'], 'baseline')

    @override_settings(RECODE_ENABLE_LLM_BACKEND=False)
    @mock.patch('recode_extraction.services.orchestrator.PdfToTextService.extract')
    def test_runner_fails_when_llm_backend_disabled(self, extract_mock):
        extract_mock.return_value = {
            'pages': [{'page_number': 1, 'text': 'Canis lupus body mass is 12 kg.'}],
            'full_text': 'Canis lupus body mass is 12 kg.',
            'extraction_warnings': [],
            'backend': 'pypdf',
        }

        run = RecodePipelineRunner().run(
            self.document.pk,
            run_params={'actor_id': self.user.pk, 'dry_run': True, 'extraction_backend': 'llm'},
        )

        run.refresh_from_db()
        self.assertEqual(run.status, SourceExtractionRun.Status.FAILED)
        self.assertIn('LLM extraction backend is disabled', run.logs)


    @override_settings(RECODE_ENABLE_OPENAI_BACKEND=True)
    @mock.patch('recode_extraction.services.orchestrator.TraitVocabularyService.get_vocab')
    @mock.patch('recode_extraction.services.orchestrator.OpenAITwoPassClient')
    @mock.patch('recode_extraction.services.orchestrator.PdfToTextService.extract')
    def test_runner_completes_with_openai_two_pass_backend(self, extract_mock, client_cls, vocab_mock):
        extract_mock.return_value = {
            'pages': [{'page_number': 1, 'text': 'Mus musculus BW 20.4'}],
            'full_text': 'Mus musculus BW 20.4',
            'extraction_warnings': [],
            'backend': 'pypdf',
        }
        vocab_mock.return_value = mock.Mock(abbr_dict={'BW': {'trait_name': 'body weight', 'unit': 'g'}}, trait_names=['body weight'])
        client = client_cls.return_value
        client.extract_pass1.return_value = mock.Mock(measurement_tables=['PAGE 1: BW 20.4'], trait_sentences=[], trait_paragraphs=[])
        client.extract_pass2.return_value = mock.Mock(
            traitRecords=[mock.Mock(model_dump=lambda exclude_none=True: {
                'verbatimScientificName': 'Mus musculus',
                'taxonRank': 'species',
                'verbatimTraitName': 'body weight',
                'verbatimTraitUnit': 'g',
                'verbatimTraitValue': '20.4',
                'references': 'Ref',
                'author': '0000-0000-0000-0000',
                'measurementRemarks': 'page=1',
            })],
            model_dump=lambda: {'metadata': {}, 'traitRecords': [{'verbatimTraitName': 'body weight'}]},
        )

        run = RecodePipelineRunner().run(self.document.pk, run_params={'dry_run': True, 'extraction_backend': 'openai_two_pass'})
        run.refresh_from_db()
        self.assertEqual(run.status, SourceExtractionRun.Status.COMPLETED)
