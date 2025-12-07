import requests
from datetime import datetime, timezone
from fastapi import HTTPException
from config import settings


class AirflowService:
    @staticmethod
    def acquire_bearer_token() -> dict:
        """Adquire token de acesso do Airflow."""
        if (
            not settings.AIRFLOW_URL
            or not settings.AIRFLOW_USERNAME
            or not settings.AIRFLOW_PASSWORD
        ):
            return {"error": "Failed to retrieve Airflow credentials"}

        token_url = f"{settings.AIRFLOW_URL}/auth/token"
        payload = {
            "username": settings.AIRFLOW_USERNAME,
            "password": settings.AIRFLOW_PASSWORD,
        }
        response = requests.post(token_url, json=payload, verify=False)

        if response.status_code in [200, 201]:
            try:
                return response.json()
            except Exception:
                return {
                    "error": "Failed to parse Airflow token response",
                    "details": response.text,
                }
        else:
            return {
                "error": "Failed to acquire Airflow token",
                "status_code": response.status_code,
                "response": response.text,
            }

    @staticmethod
    def get_pipelines() -> dict:
        """Retorna lista de pipelines (DAGs) do Airflow."""
        endpoint = f"{settings.AIRFLOW_URL}/api/v2/dags"
        airflow_token_response = AirflowService.acquire_bearer_token()
        access_token = airflow_token_response.get("access_token")

        if not access_token:
            return {
                "error": "Failed to acquire Airflow token",
                "details": airflow_token_response,
            }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }
        response = requests.get(endpoint, headers=headers, verify=False)

        if response.status_code == 200:
            dags = []
            for dag in response.json().get("dags", []):
                dags.append(
                    {
                        "id": dag.get("dag_id"),
                        "description": dag.get("description"),
                        "timetable_description": dag.get("timetable_description"),
                    }
                )
            return {"dags": dags}
        else:
            return {
                "error": "Failed to retrieve DAGs",
                "status_code": response.status_code,
                "response": response.text,
            }

    @staticmethod
    def refresh_pipeline(pipeline_id: str) -> dict:
        """Executa (refresh) uma pipeline específica."""
        airflow_token_response = AirflowService.acquire_bearer_token()
        access_token = airflow_token_response.get("access_token")

        if not access_token:
            raise HTTPException(
                status_code=401, detail="Failed to acquire Airflow token"
            )

        endpoint = f"{settings.AIRFLOW_URL}/api/v2/dags/{pipeline_id}/dagRuns"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }
        payload = {
            "logical_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

        response = requests.post(endpoint, headers=headers, json=payload, verify=False)

        if response.status_code not in [200, 201]:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to refresh pipeline: {response.text}",
            )

        return {"message": "Pipeline refreshed successfully"}

    @staticmethod
    def get_all_pipeline_associations() -> dict:
        """Retorna todas as associações entre pipelines e dashboards."""
        try:
            response = requests.get(
                settings.POCKETBASE_URL
                + "/api/collections/pipelines_dashboards/records",
                headers={"Content-Type": "application/json"},
                verify=False,
            ).json()

            if "items" not in response:
                raise HTTPException(
                    status_code=404, detail="No pipeline associations found"
                )

            return response

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

    @staticmethod
    def get_dashboard_pipeline_association(dashboard_id: str) -> dict:
        """Retorna a associação de pipeline para um dashboard específico."""
        try:
            response = requests.get(
                settings.POCKETBASE_URL
                + f"/api/collections/pipelines_dashboards/records?filter=dashboard_id='{dashboard_id}'",
                headers={"Content-Type": "application/json"},
                verify=False,
            ).json()

            if "items" not in response:
                raise HTTPException(
                    status_code=404, detail="No pipeline found for this dashboard"
                )

            return response

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

    @staticmethod
    def get_pipeline_association(pipeline_id: str) -> dict:
        """Retorna a associação de dashboard para uma pipeline específica."""
        try:
            response = requests.get(
                settings.POCKETBASE_URL
                + f"/api/collections/pipelines_dashboards/records?filter=pipeline_id='{pipeline_id}'",
                headers={"Content-Type": "application/json"},
                verify=False,
            ).json()

            if "items" not in response:
                raise HTTPException(
                    status_code=404, detail="No dashboard found for this pipeline"
                )

            return response

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

    @staticmethod
    def create_pipeline_association(dashboard_id: str, pipeline_id: str) -> dict:
        """Cria uma associação entre pipeline e dashboard."""
        try:
            response = requests.post(
                settings.POCKETBASE_URL
                + "/api/collections/pipelines_dashboards/records",
                headers={"Content-Type": "application/json"},
                json={"dashboard_id": dashboard_id, "pipeline_id": pipeline_id},
                verify=False,
            ).json()

            if "error" in response:
                raise HTTPException(
                    status_code=400, detail=f"Error: {response['error']}"
                )

            return response

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

    @staticmethod
    def delete_pipeline_association(dashboard_id: str) -> dict:
        """Deleta a associação de pipeline para um dashboard."""
        try:
            response = requests.delete(
                settings.POCKETBASE_URL
                + f"/api/collections/pipelines_dashboards/records?filter=dashboard_id='{dashboard_id}'",
                headers={"Content-Type": "application/json"},
                verify=False,
            )

            if response.status_code == 204:
                return {"message": "Pipeline association removed successfully"}
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to remove pipeline association",
                )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
