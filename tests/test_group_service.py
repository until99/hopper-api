import pytest
from unittest.mock import Mock, patch
from src.services.group_service import GroupService


class TestGroupService:
    @patch("src.services.group_service.requests.get")
    def test_get_group_success(self, mock_get):
        """Testa obtenção de grupo por ID."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "123",
            "name": "Test Group",
            "description": "Test Description",
        }
        mock_get.return_value = mock_response

        result = GroupService.get_group("123")

        assert result["id"] == "123"
        assert result["name"] == "Test Group"

    @patch("src.services.group_service.requests.get")
    def test_get_groups_success(self, mock_get):
        """Testa listagem de grupos."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "items": [
                {"id": "123", "name": "Group 1"},
                {"id": "456", "name": "Group 2"},
            ]
        }
        mock_get.return_value = mock_response

        result = GroupService.get_groups()

        assert len(result["items"]) == 2

    @patch("src.services.group_service.requests.post")
    def test_create_group_success(self, mock_post):
        """Testa criação de grupo."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "123",
            "name": "New Group",
            "description": "New Description",
            "active": True,
        }
        mock_post.return_value = mock_response

        result = GroupService.create_group("New Group", "New Description", True)

        assert result["id"] == "123"
        assert result["name"] == "New Group"

    @patch("src.services.group_service.requests.patch")
    def test_update_group_success(self, mock_patch):
        """Testa atualização de grupo."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "123",
            "name": "Updated Group",
            "description": "Updated Description",
        }
        mock_patch.return_value = mock_response

        update_data = {"name": "Updated Group"}
        result = GroupService.update_group("123", update_data)

        assert result["name"] == "Updated Group"

    @patch("src.services.group_service.requests.delete")
    def test_delete_group_success(self, mock_delete):
        """Testa exclusão de grupo."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_delete.return_value = mock_response

        result = GroupService.delete_group("123")

        assert result["message"] == "Group deleted successfully"

    @patch("src.services.group_service.requests.post")
    def test_add_user_to_group_success(self, mock_post):
        """Testa adição de usuário a grupo."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "assoc123",
            "group_id": "group123",
            "user_id": "user123",
        }
        mock_post.return_value = mock_response

        result = GroupService.add_user_to_group("group123", "user123")

        assert result["group_id"] == "group123"
        assert result["user_id"] == "user123"

    @patch("src.services.group_service.requests.post")
    def test_add_dashboard_to_group_success(self, mock_post):
        """Testa adição de dashboard a grupo."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "assoc123",
            "group_id": "group123",
            "dashboard_id": "dash123",
        }
        mock_post.return_value = mock_response

        result = GroupService.add_dashboard_to_group("group123", "dash123")

        assert result["group_id"] == "group123"
        assert result["dashboard_id"] == "dash123"
