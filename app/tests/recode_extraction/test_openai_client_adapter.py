from types import SimpleNamespace

from recode_extraction.adapters.openai_client import OpenAITwoPassClient, Pass1Evidence, Pass2Output


def _vocab():
    return SimpleNamespace(abbr_dict={'BW': {'trait_name': 'body weight', 'unit': 'g'}}, trait_names=['body weight'])


def test_extract_pass1_uses_mocked_openai_client(mock_openai):
    mocked_response = SimpleNamespace(output_parsed=Pass1Evidence(measurement_tables=['PAGE 1: BW 20.4'], trait_sentences=[], trait_paragraphs=[]))
    mock_openai.responses.parse.return_value = mocked_response

    client = OpenAITwoPassClient(max_retries=1)
    result = client.extract_pass1('BW 20.4', model='gpt-4.1', vocab=_vocab(), timeout_s=10, page_number=1, run_id=123)

    assert result.measurement_tables == ['PAGE 1: BW 20.4']
    assert mock_openai.responses.parse.call_count == 1
    call_kwargs = mock_openai.responses.parse.call_args.kwargs
    assert call_kwargs['text_format'] is Pass1Evidence
    assert call_kwargs['model'] == 'gpt-4.1'


def test_extract_pass2_uses_mocked_openai_client(mock_openai):
    mocked_response = SimpleNamespace(output_parsed=Pass2Output())
    mock_openai.responses.parse.return_value = mocked_response

    client = OpenAITwoPassClient(max_retries=1)
    result = client.extract_pass2({'measurement_tables': [], 'trait_sentences': [], 'trait_paragraphs': []}, model='gpt-4.1', vocab=_vocab(), timeout_s=10, run_id=123)

    assert isinstance(result, Pass2Output)
    assert mock_openai.responses.parse.call_count == 1
    call_kwargs = mock_openai.responses.parse.call_args.kwargs
    assert call_kwargs['text_format'] is Pass2Output
    assert call_kwargs['model'] == 'gpt-4.1'
