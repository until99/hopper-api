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
        # Busca todas as DAGs (paused e unpaused) com limite alto
        endpoint = f"{settings.AIRFLOW_URL}/api/v1/dags?limit=100"
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
            return {
                "error": "Failed to retrieve DAGs",
                "status_code": response.status_code,
                "response": response.text,
                "endpoint": endpoint
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

        endpoint = f"{settings.AIRFLOW_URL}/api/v1/dags/{pipeline_id}/dagRuns"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }
        
        # Gera um dag_run_id único baseado no timestamp
        dag_run_id = f"manual__{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}"
        
        payload = {
            "dag_run_id": dag_run_id,
            "logical_date": datetime.now(timezone.utc).isoformat(),
            "conf": {}
        }

        response = requests.post(endpoint, headers=headers, json=payload, verify=False)

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
                # Busca todas as associações para debug
                all_records = requests.get(
                    settings.POCKETBASE_URL
                    + "/api/collections/pipelines_dashboards/records",
                    headers={"Content-Type": "application/json"},
                    verify=False,
                ).json()
                
                raise HTTPException(
                    status_code=404,
                    detail={
                        "message": "No pipeline found for this dashboard",
                        "dashboard_id": dashboard_id,
                        "total_associations": len(all_records.get("items", [])),
                        "available_dashboards": [item.get("dashboard_id") for item in all_records.get("items", [])]
                    }
                )

            # Retorna o primeiro item encontrado
            return response["items"][0]

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
