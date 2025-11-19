import pytest
from unittest.mock import Mock, patch
from src.services.airflow_service import AirflowService
from fastapi import HTTPException


class TestAirflowService:
    @patch("src.services.airflow_service.requests.post")
    def test_acquire_bearer_token_success(self, mock_post):
        """Testa aquisição de token do Airflow."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "test_token"}
        mock_post.return_value = mock_response

        result = AirflowService.acquire_bearer_token()

        assert result["access_token"] == "test_token"

    @patch("src.services.airflow_service.AirflowService.acquire_bearer_token")
    @patch("src.services.airflow_service.requests.get")
    def test_get_pipelines_success(self, mock_get, mock_token):
        """Testa obtenção de pipelines do Airflow."""
        mock_token.return_value = {"access_token": "test_token"}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "dags": [
                {
                    "dag_id": "dag1",
                    "description": "Test DAG",
                    "timetable_description": "Daily",
                }
            ]
        }
        mock_get.return_value = mock_response

        result = AirflowService.get_pipelines()

        assert "dags" in result
        assert len(result["dags"]) == 1
        assert result["dags"][0]["id"] == "dag1"

    @patch("src.services.airflow_service.AirflowService.acquire_bearer_token")
    @patch("src.services.airflow_service.requests.post")
    def test_refresh_pipeline_success(self, mock_post, mock_token):
        """Testa execução de pipeline."""
        mock_token.return_value = {"access_token": "test_token"}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = AirflowService.refresh_pipeline("dag123")

        assert result["message"] == "Pipeline refreshed successfully"

    @patch("src.services.airflow_service.AirflowService.acquire_bearer_token")
    @patch("src.services.airflow_service.requests.post")
    def test_refresh_pipeline_failure(self, mock_post, mock_token):
        """Testa falha na execução de pipeline."""
        mock_token.return_value = {"access_token": "test_token"}
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        with pytest.raises(HTTPException) as exc_info:
            AirflowService.refresh_pipeline("dag123")

        assert exc_info.value.status_code == 500

    @patch("src.services.airflow_service.requests.get")
    def test_get_all_pipeline_associations_success(self, mock_get):
        """Testa obtenção de associações pipeline-dashboard."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "items": [
                {"id": "1", "pipeline_id": "dag1", "dashboard_id": "dash1"}
            ]
        }
        mock_get.return_value = mock_response

        result = AirflowService.get_all_pipeline_associations()

        assert "items" in result
        assert len(result["items"]) == 1

    @patch("src.services.airflow_service.requests.post")
    def test_create_pipeline_association_success(self, mock_post):
        """Testa criação de associação pipeline-dashboard."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "123",
            "pipeline_id": "dag1",
            "dashboard_id": "dash1",
        }
        mock_post.return_value = mock_response

        result = AirflowService.create_pipeline_association("dash1", "dag1")

        assert result["pipeline_id"] == "dag1"
        assert result["dashboard_id"] == "dash1"

    @patch("src.services.airflow_service.requests.delete")
    def test_delete_pipeline_association_success(self, mock_delete):
        """Testa exclusão de associação pipeline-dashboard."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_delete.return_value = mock_response

        result = AirflowService.delete_pipeline_association("dash123")

        assert result["message"] == "Pipeline association removed successfully"
