import msal
import requests
from src.config import settings


class PowerBIService:
    @staticmethod
    def acquire_bearer_token() -> str | None:
        """Adquire token de acesso do Azure para Power BI."""
        app_msal = msal.ConfidentialClientApplication(
            client_id=settings.AZURE_CLIENT_ID,
            authority=f"https://login.microsoftonline.com/{settings.AZURE_TENANT_ID}",
            client_credential=settings.AZURE_CLIENT_SECRET,
        )

        token_result = app_msal.acquire_token_for_client(
            scopes=["https://analysis.windows.net/powerbi/api/.default"]
        )

        if not token_result:
            return None

        if "access_token" in token_result:
            return token_result["access_token"]

    @staticmethod
    def get_dashboards() -> dict:
        """Retorna lista de dashboards do Power BI."""
        token = PowerBIService.acquire_bearer_token()
        groups = requests.get(
            "https://api.powerbi.com/v1.0/myorg/groups",
            headers={"Authorization": f"Bearer {token}"},
            verify=False,
        )

        dashboards = []
        if groups.status_code == 200:
            for group in groups.json().get("value", []):
                dashboards_response = requests.get(
                    f"https://api.powerbi.com/v1.0/myorg/groups/{group['id']}/reports",
                    headers={"Authorization": f"Bearer {token}"},
                    verify=False,
                )
                if dashboards_response.status_code == 200:
                    for report in dashboards_response.json().get("value", []):
                        dashboards.append(
                            {
                                "id": report.get("id"),
                                "name": report.get("name"),
                                "datasetId": report.get("datasetId"),
                                "description": report.get("description"),
                                "groupId": group.get("id"),
                                "groupName": group.get("name"),
                            }
                        )
                else:
                    return {"error": "Failed to retrieve dashboards"}

        return {"dashboards": dashboards}

    @staticmethod
    def get_groups() -> dict:
        """Retorna lista de grupos do Power BI."""
        token = PowerBIService.acquire_bearer_token()
        groups = requests.get(
            "https://api.powerbi.com/v1.0/myorg/groups",
            headers={"Authorization": f"Bearer {token}"},
            verify=False,
        )

        if groups.status_code == 200:
            return {"groups": groups.json().get("value", [])}
        else:
            return {"error": "Failed to retrieve groups"}

    @staticmethod
    def get_reports(group_id: str) -> dict:
        """Retorna lista de relatórios em um grupo específico do Power BI."""
        token = PowerBIService.acquire_bearer_token()
        reports = requests.get(
            f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/reports",
            headers={"Authorization": f"Bearer {token}"},
            verify=False,
        )

        if reports.status_code == 200:
            return {"reports": reports.json().get("value", [])}
        else:
            return {"error": "Failed to retrieve reports"}

    @staticmethod
    def get_report(group_id: str, report_id: str) -> dict:
        """Retorna um relatório específico de um grupo do Power BI."""
        token = PowerBIService.acquire_bearer_token()
        report = requests.get(
            f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/reports/{report_id}",
            headers={"Authorization": f"Bearer {token}"},
            verify=False,
        )

        return report.json()

    @staticmethod
    def delete_report(group_id: str, report_id: str, dataset_id: str) -> dict:
        """Deleta um relatório específico de um grupo do Power BI."""
        token = PowerBIService.acquire_bearer_token()
        report = requests.delete(
            f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/reports/{report_id}",
            headers={"Authorization": f"Bearer {token}"},
            verify=False,
        )

        dataset = requests.delete(
            f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/datasets/{dataset_id}",
            headers={"Authorization": f"Bearer {token}"},
            verify=False,
        )

        if dataset.status_code != 200:
            return {"error": "Failed to delete dataset"}

        if report.status_code == 200:
            return {"message": "Report deleted successfully"}
        else:
            return {"error": "Failed to delete report"}
