import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from src.main import app

client = TestClient(app)


class TestGroupController:
    @patch("src.services.group_service.GroupService.get_groups")
    @patch("src.middlewares.auth.AuthService.verify_token")
    def test_get_groups_success(self, mock_verify, mock_get_groups):
        """Testa endpoint de listagem de grupos."""
        mock_verify.return_value = {"id": "user123", "role": "user"}
        mock_get_groups.return_value = {
            "items": [{"id": "123", "name": "Group 1", "description": "Test Group"}]
        }

        response = client.get(
            "/app/groups", headers={"Authorization": "Bearer test_token"}
        )

        assert response.status_code == 200
        assert "items" in response.json()

    @patch("src.services.group_service.GroupService.create_group")
    @patch("src.middlewares.auth.AuthService.verify_token")
    def test_create_group_success(self, mock_verify, mock_create_group):
        """Testa endpoint de criação de grupo."""
        mock_verify.return_value = {"id": "admin123", "role": "admin"}
        mock_create_group.return_value = {
            "id": "123",
            "name": "New Group",
            "description": "New Description",
            "active": True,
        }

        response = client.post(
            "/app/groups",
            params={
                "name": "New Group",
                "description": "New Description",
                "active": True,
            },
            headers={"Authorization": "Bearer test_token"},
        )

        assert response.status_code == 200
        assert response.json()["name"] == "New Group"
