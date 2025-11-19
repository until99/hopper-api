import pytest
from unittest.mock import Mock, patch
from src.services.auth_service import AuthService
from fastapi import HTTPException


class TestAuthService:
    @patch("src.services.auth_service.requests.post")
    def test_verify_token_success(self, mock_post):
        """Testa verificação de token bem-sucedida."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "123", "email": "test@test.com"}
        mock_post.return_value = mock_response

        result = AuthService.verify_token("valid_token")

        assert result["id"] == "123"
        assert result["email"] == "test@test.com"

    @patch("src.services.auth_service.requests.post")
    def test_verify_token_invalid(self, mock_post):
        """Testa verificação de token inválido."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response

        with pytest.raises(HTTPException) as exc_info:
            AuthService.verify_token("invalid_token")

        assert exc_info.value.status_code == 401

    @patch("src.services.auth_service.requests.post")
    def test_login_success(self, mock_post):
        """Testa login bem-sucedido."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "token": "test_token",
            "record": {
                "id": "123",
                "username": "testuser",
                "email": "test@test.com",
                "role": "user",
                "created": "2023-01-01",
                "updated": "2023-01-01",
            },
        }
        mock_post.return_value = mock_response

        result = AuthService.login("test@test.com", "password123")

        assert result["token"] == "test_token"
        assert result["record"]["email"] == "test@test.com"

    @patch("src.services.auth_service.requests.post")
    def test_login_invalid_credentials(self, mock_post):
        """Testa login com credenciais inválidas."""
        mock_response = Mock()
        mock_response.json.return_value = {"error": "Invalid credentials"}
        mock_post.return_value = mock_response

        result = AuthService.login("test@test.com", "wrong_password")

        assert "error" in result

    @patch("src.services.auth_service.requests.post")
    def test_register_success(self, mock_post):
        """Testa registro bem-sucedido."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "123"}
        mock_post.return_value = mock_response

        result = AuthService.register(
            "testuser", "test@test.com", "password123", "password123", "user"
        )

        assert result["message"] == "User registered"
        assert result["user_id"] == "123"

    def test_register_password_mismatch(self):
        """Testa registro com senhas diferentes."""
        with pytest.raises(HTTPException) as exc_info:
            AuthService.register(
                "testuser", "test@test.com", "password123", "different", "user"
            )

        assert exc_info.value.status_code == 400
