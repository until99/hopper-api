import requests
import base64
from datetime import datetime, timezone
from fastapi import HTTPException
from requests.auth import HTTPBasicAuth
from config import settings


class AirflowService:
    @staticmethod
    def get_auth() -> HTTPBasicAuth:
        """Retorna autenticação básica para o Airflow."""
        username = settings.AIRFLOW_USERNAME if settings.AIRFLOW_USERNAME else "admin"
        password = settings.AIRFLOW_PASSWORD if settings.AIRFLOW_PASSWORD else "admin"
        return HTTPBasicAuth(username, password)
    
    @staticmethod
    def get_auth_header() -> dict:
        """Retorna header de autenticação básica para o Airflow."""
        username = settings.AIRFLOW_USERNAME if settings.AIRFLOW_USERNAME else "admin"
        password = settings.AIRFLOW_PASSWORD if settings.AIRFLOW_PASSWORD else "admin"
        credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
        return {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json"
        }
    
    @staticmethod
    def get_session():
        """Cria uma sessão com autenticação para reutilizar."""
        session = requests.Session()
        session.headers.update(AirflowService.get_auth_header())
        session.verify = False
        return session

    @staticmethod
    def get_pipelines() -> dict:
        """Retorna lista de pipelines (DAGs) do Airflow."""
        if not settings.AIRFLOW_URL:
            return {"error": "AIRFLOW_URL not configured"}
            
        # Busca todas as DAGs (paused e unpaused) com limite alto
        endpoint = f"{settings.AIRFLOW_URL}/api/v1/dags?limit=100"
        
        try:
            session = AirflowService.get_session()
            response = session.get(endpoint, timeout=30)

            if response.status_code == 200:
                dags = []
                response_data = response.json()
                all_dags = response_data.get("dags", [])
                
                for dag in all_dags:
                    dags.append(
                        {
                            "id": dag.get("dag_id"),
                            "description": dag.get("description"),
                            "timetable_description": dag.get("timetable_description"),
                            "is_paused": dag.get("is_paused", False),
                            "is_active": dag.get("is_active", True),
                            "file_token": dag.get("file_token"),
                        }
                    )
                
                return {
                    "dags": dags,
                    "total_entries": response_data.get("total_entries", len(dags)),
                    "total_returned": len(dags)
                }
            else:
                # Adiciona informações sobre a autenticação para debug
                auth_info = {
                    "username": settings.AIRFLOW_USERNAME if settings.AIRFLOW_USERNAME else "admin (default)",
                    "password_set": "yes" if settings.AIRFLOW_PASSWORD else "using default"
                }
                return {
                    "error": "Failed to retrieve DAGs",
                    "status_code": response.status_code,
                    "response": response.text,
                    "endpoint": endpoint,
                    "auth_info": auth_info
                }
        except Exception as e:
            return {
                "error": "Exception while retrieving DAGs",
                "details": str(e),
                "endpoint": endpoint
            }

    @staticmethod
    def refresh_pipeline(pipeline_id: str) -> dict:
        """Executa (refresh) uma pipeline específica."""
        if not settings.AIRFLOW_URL:
            raise HTTPException(
                status_code=500, detail="AIRFLOW_URL not configured"
            )

        endpoint = f"{settings.AIRFLOW_URL}/api/v1/dags/{pipeline_id}/dagRuns"
        
        # Gera um dag_run_id único baseado no timestamp
        dag_run_id = f"manual__{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}"
        
        payload = {
            "dag_run_id": dag_run_id,
            "logical_date": datetime.now(timezone.utc).isoformat(),
            "conf": {}
        }

        try:
            session = AirflowService.get_session()
            response = session.post(endpoint, json=payload, timeout=30)

            if response.status_code not in [200, 201]:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to refresh pipeline: {response.text}",
                )

            result = response.json()
            return {
                "message": "Pipeline refreshed successfully",
                "dag_run_id": result.get("dag_run_id"),
                "logical_date": result.get("logical_date"),
                "state": result.get("state")
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Exception while refreshing pipeline: {str(e)}"
            )

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
            url = (
                settings.POCKETBASE_URL
                + f"/api/collections/pipelines_dashboards/records?filter=(dashboard_id='{dashboard_id}')"
            )
            response = requests.get(
                url,
                headers={"Content-Type": "application/json"},
                verify=False,
            ).json()

            if "items" not in response or len(response["items"]) == 0:
                # Retorna None ao invés de erro para não poluir logs
                return None

            # Retorna o primeiro item encontrado
            return response["items"][0]

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
            # Primeiro busca a associação para obter o ID do registro
            search_response = requests.get(
                settings.POCKETBASE_URL
                + f"/api/collections/pipelines_dashboards/records?filter=dashboard_id='{dashboard_id}'",
                headers={"Content-Type": "application/json"},
                verify=False,
            ).json()

            if "items" not in search_response or len(search_response["items"]) == 0:
                raise HTTPException(
                    status_code=404, detail="No pipeline associated with this dashboard"
                )

            # Pega o ID do primeiro registro encontrado
            record_id = search_response["items"][0]["id"]

            # Deleta o registro usando o ID
            delete_response = requests.delete(
                settings.POCKETBASE_URL
                + f"/api/collections/pipelines_dashboards/records/{record_id}",
                headers={"Content-Type": "application/json"},
                verify=False,
            )

            if delete_response.status_code == 204:
                return {"message": "Pipeline association removed successfully"}
            else:
                raise HTTPException(
                    status_code=delete_response.status_code,
                    detail="Failed to remove pipeline association",
                )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
