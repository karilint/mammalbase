import json
from pathlib import Path

from django.core.management import call_command
from django.test import SimpleTestCase

from recode_extraction.services.evaluation import RecodeEvaluationService


FIXTURE_ROOT = Path(__file__).resolve().parent / 'assets' / 'recode_fixture'


class RecodeEvalTests(SimpleTestCase):
    def test_evaluation_service_runs_and_returns_metrics(self):
        service = RecodeEvaluationService(
            index_path=FIXTURE_ROOT / 'index.json',
            text_root=FIXTURE_ROOT / 'text',
            subset=2,
        )

        result = service.evaluate()

        self.assertEqual(result['documents_evaluated'], 2)
        self.assertIn('entity_type_metrics', result)
        self.assertIn('relation_type_metrics', result)
        self.assertTrue(result['entity_type_metrics'])

    def test_management_command_outputs_json_and_writes_file(self):
        output_path = FIXTURE_ROOT / 'eval_metrics.json'
        if output_path.exists():
            output_path.unlink()

        from io import StringIO

        out = StringIO()
        call_command(
            'recode_eval',
            '--index-path',
            str(FIXTURE_ROOT / 'index.json'),
            '--text-root',
            str(FIXTURE_ROOT / 'text'),
            '--subset',
            '2',
            '--output-json',
            str(output_path),
            stdout=out,
        )

        stdout = out.getvalue()
        self.assertIn('RECODE evaluation complete', stdout)
        self.assertTrue(output_path.exists())

        payload = json.loads(output_path.read_text(encoding='utf-8'))
        self.assertEqual(payload['documents_evaluated'], 2)
        output_path.unlink()
