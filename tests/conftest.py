"""
Arquivo de configuração do pytest.
"""
import pytest
import sys
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH para imports absolutos
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))


@pytest.fixture
def mock_token():
    """Fixture que retorna um token de teste."""
    return "test_token_12345"


@pytest.fixture
def mock_user():
    """Fixture que retorna dados de um usuário de teste."""
    return {
        "id": "123",
        "username": "testuser",
        "email": "test@test.com",
        "role": "user",
        "active": True,
        "created": "2023-01-01T00:00:00Z",
        "updated": "2023-01-01T00:00:00Z",
    }


@pytest.fixture
def mock_group():
    """Fixture que retorna dados de um grupo de teste."""
    return {
        "id": "group123",
        "name": "Test Group",
        "description": "Test Description",
        "active": True,
        "created": "2023-01-01T00:00:00Z",
        "updated": "2023-01-01T00:00:00Z",
    }
