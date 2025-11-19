import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from src.main import app

client = TestClient(app)


class TestAuthController:
    @patch("src.services.auth_service.AuthService.login")
    def test_login_success(self, mock_login):
        """Testa endpoint de login."""
        mock_login.return_value = {
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

        response = client.post(
            "/user/auth", json={"email": "test@test.com", "password": "password123"}
        )

        assert response.status_code == 200
        assert response.json()["token"] == "test_token"

    @patch("src.services.auth_service.AuthService.register")
    def test_register_success(self, mock_register):
        """Testa endpoint de registro."""
        mock_register.return_value = {"message": "User registered", "user_id": "123"}

        response = client.post(
            "/user/register",
            json={
                "username": "newuser",
                "email": "new@test.com",
                "password": "password123",
                "confirm_password": "password123",
                "role": "user",
            },
        )

        assert response.status_code == 200
        assert response.json()["message"] == "User registered"
