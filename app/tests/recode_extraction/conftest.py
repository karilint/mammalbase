from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_openai(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY', 'test-key')
    with patch('openai.OpenAI') as openai_cls:
        mock_client = MagicMock()
        openai_cls.return_value = mock_client
        yield mock_client
