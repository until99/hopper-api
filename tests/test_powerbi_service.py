import pytest
from unittest.mock import Mock, patch, MagicMock
from src.services.powerbi_service import PowerBIService


class TestPowerBIService:
    @patch("src.services.powerbi_service.msal.ConfidentialClientApplication")
    def test_acquire_bearer_token_success(self, mock_msal):
        """Testa aquisição de token do Azure."""
        mock_app = Mock()
        mock_app.acquire_token_for_client.return_value = {
            "access_token": "test_token"
        }
        mock_msal.return_value = mock_app

        result = PowerBIService.acquire_bearer_token()

        assert result == "test_token"

    @patch("src.services.powerbi_service.PowerBIService.acquire_bearer_token")
    @patch("src.services.powerbi_service.requests.get")
    def test_get_dashboards_success(self, mock_get, mock_token):
        """Testa obtenção de dashboards do Power BI."""
        mock_token.return_value = "test_token"

        # Mock para grupos
        mock_groups_response = Mock()
        mock_groups_response.status_code = 200
        mock_groups_response.json.return_value = {
            "value": [{"id": "group1", "name": "Group 1"}]
        }

        # Mock para relatórios
        mock_reports_response = Mock()
        mock_reports_response.status_code = 200
        mock_reports_response.json.return_value = {
            "value": [
                {
                    "id": "report1",
                    "name": "Report 1",
                    "datasetId": "dataset1",
                    "description": "Test Report",
                }
            ]
        }

        mock_get.side_effect = [mock_groups_response, mock_reports_response]

        result = PowerBIService.get_dashboards()

        assert "dashboards" in result
        assert len(result["dashboards"]) == 1
        assert result["dashboards"][0]["id"] == "report1"

    @patch("src.services.powerbi_service.PowerBIService.acquire_bearer_token")
    @patch("src.services.powerbi_service.requests.get")
    def test_get_groups_success(self, mock_get, mock_token):
        """Testa obtenção de grupos do Power BI."""
        mock_token.return_value = "test_token"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "value": [{"id": "group1", "name": "Group 1"}]
        }
        mock_get.return_value = mock_response

        result = PowerBIService.get_groups()

        assert "groups" in result
        assert len(result["groups"]) == 1

    @patch("src.services.powerbi_service.PowerBIService.acquire_bearer_token")
    @patch("src.services.powerbi_service.requests.get")
    def test_get_reports_success(self, mock_get, mock_token):
        """Testa obtenção de relatórios de um grupo."""
        mock_token.return_value = "test_token"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "value": [{"id": "report1", "name": "Report 1"}]
        }
        mock_get.return_value = mock_response

        result = PowerBIService.get_reports("group123")

        assert "reports" in result
        assert len(result["reports"]) == 1

    @patch("src.services.powerbi_service.PowerBIService.acquire_bearer_token")
    @patch("src.services.powerbi_service.requests.delete")
    def test_delete_report_success(self, mock_delete, mock_token):
        """Testa exclusão de relatório do Power BI."""
        mock_token.return_value = "test_token"

        mock_report_response = Mock()
        mock_report_response.status_code = 200

        mock_dataset_response = Mock()
        mock_dataset_response.status_code = 200

        mock_delete.side_effect = [mock_report_response, mock_dataset_response]

        result = PowerBIService.delete_report("group123", "report123", "dataset123")

        assert result["message"] == "Report deleted successfully"
