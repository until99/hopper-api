import pytest
from unittest.mock import Mock, patch
from src.services.user_service import UserService


class TestUserService:
    @patch("src.services.user_service.requests.get")
    def test_get_user_success(self, mock_get):
        """Testa obtenção de usuário por ID."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "123",
            "username": "testuser",
            "email": "test@test.com",
        }
        mock_get.return_value = mock_response

        result = UserService.get_user("123")

        assert result["id"] == "123"
        assert result["username"] == "testuser"

    @patch("src.services.user_service.requests.get")
    def test_get_users_paginated(self, mock_get):
        """Testa listagem paginada de usuários."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "page": 1,
            "perPage": 30,
            "totalItems": 100,
            "totalPages": 4,
            "items": [
                {
                    "id": "123",
                    "username": "user1",
                    "email": "user1@test.com",
                    "role": "user",
                    "active": True,
                    "created": "2023-01-01",
                    "updated": "2023-01-01",
                }
            ],
        }
        mock_get.return_value = mock_response

        result = UserService.get_users(page=1, per_page=30)

        assert result["page"] == 1
        assert result["totalItems"] == 100
        assert len(result["users"]) == 1

    @patch("src.services.user_service.requests.post")
    def test_create_user_success(self, mock_post):
        """Testa criação de usuário."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "123",
            "username": "newuser",
            "email": "new@test.com",
        }
        mock_post.return_value = mock_response

        result = UserService.create_user(
            "newuser", "new@test.com", "password", "password", "user"
        )

        assert result["id"] == "123"
        assert result["username"] == "newuser"

    def test_create_user_password_mismatch(self):
        """Testa criação de usuário com senhas diferentes."""
        result = UserService.create_user(
            "newuser", "new@test.com", "password", "different", "user"
        )

        assert "error" in result

    @patch("src.services.user_service.requests.patch")
    def test_update_user_success(self, mock_patch):
        """Testa atualização de usuário."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "123",
            "username": "updateduser",
            "email": "updated@test.com",
        }
        mock_patch.return_value = mock_response

        update_data = {"username": "updateduser"}
        result = UserService.update_user("123", update_data)

        assert result["username"] == "updateduser"

    @patch("src.services.user_service.requests.delete")
    def test_delete_user_success(self, mock_delete):
        """Testa exclusão de usuário."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_delete.return_value = mock_response

        result = UserService.delete_user("123")

        assert result["message"] == "User deleted successfully"
