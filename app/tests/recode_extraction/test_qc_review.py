import tempfile
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from recode_extraction.models import ExtractedAssertionModel, SourceDocument
from recode_extraction.services.runs import create_extraction_run


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class QcReviewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='curator-user',
            email='curator@example.com',
            password='pw-123456',
        )
        self.client.force_login(self.user)
        self.document = SourceDocument.objects.create(
            pdf_file=SimpleUploadedFile('qc.pdf', b'%PDF-1.4\ncontent', content_type='application/pdf'),
            title='QC Source',
            year=2024,
            uploader=self.user,
        )

    @mock.patch('recode_extraction.services.orchestrator.PdfToTextService.extract')
    def test_run_detail_filters_and_review_update(self, extract_mock):
        extract_mock.return_value = {
            'pages': [{'page_number': 1, 'text': 'Canis lupus body mass is 12 kg. Litter size is 4.'}],
            'full_text': 'Canis lupus body mass is 12 kg. Litter size is 4.',
            'extraction_warnings': [],
            'backend': 'pypdf',
        }
        run = create_extraction_run(self.document, actor_id=self.user.pk, dry_run=True)

        response = self.client.get(reverse('recode_extraction_run_detail', kwargs={'run_id': run.pk}), {'trait': 'body mass'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Summary')

        assertion = run.assertions.first()
        post_data = {
            'action': 'update_assertion',
            'assertion_id': assertion.pk,
            'review_status': ExtractedAssertionModel.ReviewStatus.REJECTED,
            'edited_value': '11',
            'edited_unit': 'kg',
            'mapped_trait_id': assertion.mapped_trait_id,
            'reviewer_note': 'reject for test',
        }
        response = self.client.post(reverse('recode_extraction_run_detail', kwargs={'run_id': run.pk}), data=post_data)
        self.assertEqual(response.status_code, 302)
        assertion.refresh_from_db()
        self.assertEqual(assertion.review_status, ExtractedAssertionModel.ReviewStatus.REJECTED)
        self.assertEqual(assertion.edited_value, '11')

    @mock.patch('recode_extraction.services.orchestrator.PdfToTextService.extract')
    @mock.patch('recode_extraction.services.review.EtsImporter.importRow')
    def test_approve_then_persist_only_approved(self, import_row_mock, extract_mock):
        extract_mock.return_value = {
            'pages': [{'page_number': 1, 'text': 'Canis lupus body mass is 12 kg. Litter size is 4.'}],
            'full_text': 'Canis lupus body mass is 12 kg. Litter size is 4.',
            'extraction_warnings': [],
            'backend': 'pypdf',
        }
        run = create_extraction_run(self.document, actor_id=self.user.pk, dry_run=True)
        assertions = list(run.assertions.order_by('id'))

        self.client.post(reverse('recode_extraction_run_detail', kwargs={'run_id': run.pk}), data={
            'action': 'update_assertion',
            'assertion_id': assertions[0].pk,
            'review_status': ExtractedAssertionModel.ReviewStatus.APPROVED,
            'edited_value': assertions[0].value_raw,
            'edited_unit': assertions[0].unit,
            'mapped_trait_id': assertions[0].mapped_trait_id,
            'reviewer_note': 'approve',
        })
        self.client.post(reverse('recode_extraction_run_detail', kwargs={'run_id': run.pk}), data={
            'action': 'update_assertion',
            'assertion_id': assertions[1].pk,
            'review_status': ExtractedAssertionModel.ReviewStatus.REJECTED,
            'edited_value': assertions[1].value_raw,
            'edited_unit': assertions[1].unit,
            'mapped_trait_id': assertions[1].mapped_trait_id,
            'reviewer_note': 'reject',
        })

        response = self.client.post(reverse('recode_extraction_run_detail', kwargs={'run_id': run.pk}), data={'action': 'persist_approved'})
        self.assertEqual(response.status_code, 302)

        approved = ExtractedAssertionModel.objects.get(pk=assertions[0].pk)
        rejected = ExtractedAssertionModel.objects.get(pk=assertions[1].pk)
        self.assertTrue(approved.ets_persisted)
        self.assertFalse(rejected.ets_persisted)
        self.assertEqual(import_row_mock.call_count, 1)

    @mock.patch('recode_extraction.services.orchestrator.PdfToTextService.extract')
    def test_bulk_approve_and_csv_export(self, extract_mock):
        extract_mock.return_value = {
            'pages': [{'page_number': 1, 'text': 'Canis lupus body mass is 12 kg. Litter size is 4.'}],
            'full_text': 'Canis lupus body mass is 12 kg. Litter size is 4.',
            'extraction_warnings': [],
            'backend': 'pypdf',
        }
        run = create_extraction_run(self.document, actor_id=self.user.pk, dry_run=True)

        response = self.client.post(reverse('recode_extraction_run_detail', kwargs={'run_id': run.pk}), data={
            'action': 'bulk_approve',
            'threshold': '0.5',
        })
        self.assertEqual(response.status_code, 302)
        self.assertGreater(
            ExtractedAssertionModel.objects.filter(extraction_run=run, review_status=ExtractedAssertionModel.ReviewStatus.APPROVED).count(),
            0,
        )

        response = self.client.get(reverse('recode_extraction_run_detail', kwargs={'run_id': run.pk}), {'export': 'csv'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('subject_taxon,trait_name', response.content.decode('utf-8'))


    @mock.patch('recode_extraction.services.orchestrator.PdfToTextService.extract')
    @mock.patch('recode_extraction.services.review.EtsMapper.map_single_assertion_data')
    @mock.patch('recode_extraction.services.review.EtsImporter.importRow')
    def test_persist_approved_uses_prefilled_ets_payload(self, import_row_mock, map_single_mock, extract_mock):
        extract_mock.return_value = {
            'pages': [{'page_number': 1, 'text': 'Canis lupus body mass is 12 kg.'}],
            'full_text': 'Canis lupus body mass is 12 kg.',
            'extraction_warnings': [],
            'backend': 'pypdf',
        }
        run = create_extraction_run(self.document, actor_id=self.user.pk, dry_run=True)
        assertion = run.assertions.first()
        assertion.review_status = ExtractedAssertionModel.ReviewStatus.APPROVED
        assertion.ets_payload = {
            'references': 'Ref',
            'verbatimScientificName': assertion.subject_taxon,
            'taxonRank': 'species',
            'verbatimTraitName': assertion.trait_name,
            'verbatimTraitUnit': assertion.unit or 'g',
            'verbatimTraitValue': assertion.value_raw or '12',
            'measurementValue_min': 12,
            'measurementValue_max': 12,
            'dispersion': 0,
            'statisticalMethod': 'point estimate',
            'individualCount': 0,
            'sex': 'nan',
            'lifeStage': 'nan',
            'measurementMethod': 'OpenAI two-pass extraction',
            'measurementRemarks': 'page=1',
            'measurementAccuracy': '',
            'measurementDeterminedBy': 'OpenAI two-pass extraction',
            'verbatimLocality': '',
            'author': '0000-0000-0000-0000',
            'associatedReferences': 'Ref',
        }
        assertion.save(update_fields=['review_status', 'ets_payload'])

        response = self.client.post(reverse('recode_extraction_run_detail', kwargs={'run_id': run.pk}), data={'action': 'persist_approved'})
        self.assertEqual(response.status_code, 302)
        assertion.refresh_from_db()
        self.assertTrue(assertion.ets_persisted)
        self.assertEqual(import_row_mock.call_count, 1)
        map_single_mock.assert_not_called()
