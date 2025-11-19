import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from src.main import app

client = TestClient(app)


class TestUserController:
    @patch("src.services.user_service.UserService.get_users")
    @patch("src.middlewares.auth.AuthService.verify_token")
    def test_get_users_success(self, mock_verify, mock_get_users):
        """Testa endpoint de listagem de usuários."""
        mock_verify.return_value = {"id": "admin123", "role": "admin"}
        mock_get_users.return_value = {
            "page": 1,
            "perPage": 30,
            "totalItems": 2,
            "totalPages": 1,
            "users": [
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

        response = client.get(
            "/users", headers={"Authorization": "Bearer test_token"}
        )

        assert response.status_code == 200
        assert "users" in response.json()

    @patch("src.services.user_service.UserService.get_user")
    @patch("src.middlewares.auth.AuthService.verify_token")
    def test_get_user_by_id(self, mock_verify, mock_get_user):
        """Testa endpoint de obtenção de usuário por ID."""
        mock_verify.return_value = {"id": "admin123", "role": "admin"}
        mock_get_user.return_value = {
            "id": "123",
            "username": "testuser",
            "email": "test@test.com",
        }

        response = client.get(
            "/user/123", headers={"Authorization": "Bearer test_token"}
        )

        assert response.status_code == 200
        assert response.json()["id"] == "123"
