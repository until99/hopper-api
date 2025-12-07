import requests
from fastapi import HTTPException
from config import settings


class GroupService:
    @staticmethod
    def get_group(group_id: str) -> dict:
        """Retorna os dados de um grupo específico."""
        group = requests.get(
            settings.POCKETBASE_URL + f"/api/collections/groups/records/{group_id}",
            headers={"Content-Type": "application/json"},
            verify=False,
        ).json()
        return group

    @staticmethod
    def get_groups() -> dict:
        """Retorna lista de grupos."""
        groups = requests.get(
            settings.POCKETBASE_URL + "/api/collections/groups/records",
            verify=False,
        )
        return groups.json()

    @staticmethod
    def create_group(name: str, description: str, active: bool = True) -> dict:
        """Cria um novo grupo."""
        group = requests.post(
            settings.POCKETBASE_URL + "/api/collections/groups/records",
            headers={"Content-Type": "application/json"},
            json={"name": name, "description": description, "active": active},
            verify=False,
        ).json()
        return group

    @staticmethod
    def update_group(group_id: str, update_data: dict) -> dict:
        """Atualiza os dados de um grupo."""
        group = requests.patch(
            settings.POCKETBASE_URL + f"/api/collections/groups/records/{group_id}",
            headers={"Content-Type": "application/json"},
            json=update_data,
            verify=False,
        ).json()
        return group

    @staticmethod
    def delete_group(group_id: str) -> dict:
        """Deleta um grupo."""
        response = requests.delete(
            settings.POCKETBASE_URL + f"/api/collections/groups/records/{group_id}",
            headers={"Content-Type": "application/json"},
            verify=False,
        )

        if response.status_code == 204:
            return {"message": "Group deleted successfully"}
        else:
            return {"error": "Failed to delete group"}

    @staticmethod
    def get_group_users(group_id: str) -> list:
        """Retorna lista de usuários de um grupo."""
        group_users = requests.get(
            settings.POCKETBASE_URL
            + f"/api/collections/groups_users/records?filter=(group_id='{group_id}')",
            headers={"Content-Type": "application/json"},
            verify=False,
        ).json()

        users = []
        for user in group_users["items"]:
            user_record = requests.get(
                settings.POCKETBASE_URL
                + f"/api/collections/auth_users/records/{user['user_id']}",
                headers={"Content-Type": "application/json"},
                verify=False,
            ).json()

            users.append(
                {
                    "id": user["id"],
                    "user_id": user_record["id"],
                    "username": user_record["username"],
                    "email": user_record["email"],
                    "role": user_record["role"],
                    "active": user_record["active"],
                    "created": user_record["created"],
                    "updated": user_record["updated"],
                }
            )

        return users

    @staticmethod
    def get_group_dashboards(group_id: str, all_dashboards: list) -> list:
        """Retorna lista de dashboards de um grupo."""
        group_dashboards = requests.get(
            settings.POCKETBASE_URL
            + f"/api/collections/groups_dashboards/records?filter=(group_id='{group_id}')",
            headers={"Content-Type": "application/json"},
            verify=False,
        ).json()

        dashboards: list[dict] = []
        for group_dashboard in group_dashboards["items"]:
            dashboard_id = group_dashboard.get("dashboard_id")

            for dashboard in all_dashboards:
                if dashboard.get("id") == dashboard_id:
                    dashboards.append(dashboard)
                    break

        return dashboards

    @staticmethod
    def add_user_to_group(group_id: str, user_id: str) -> dict:
        """Adiciona um usuário a um grupo."""
        association = requests.post(
            settings.POCKETBASE_URL + "/api/collections/groups_users/records",
            headers={"Content-Type": "application/json"},
            json={"group_id": group_id, "user_id": user_id},
            verify=False,
        ).json()
        return association

    @staticmethod
    def remove_user_from_group(group_id: str, user_id: str) -> dict:
        """Remove um usuário de um grupo."""
        try:
            group_users = requests.get(
                settings.POCKETBASE_URL
                + f"/api/collections/groups_users/records?filter=(group_id='{group_id}')",
                headers={"Content-Type": "application/json"},
                verify=False,
            ).json()

            for group_user in group_users["items"]:
                if group_user["user_id"] == user_id:
                    response = requests.delete(
                        settings.POCKETBASE_URL
                        + f"/api/collections/groups_users/records/{group_user['id']}",
                        headers={"Content-Type": "application/json"},
                        verify=False,
                    ).json()
                    return response

            return group_users

        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def add_dashboard_to_group(group_id: str, dashboard_id: str) -> dict:
        """Adiciona um dashboard a um grupo."""
        association = requests.post(
            settings.POCKETBASE_URL + "/api/collections/groups_dashboards/records",
            headers={"Content-Type": "application/json"},
            json={"group_id": group_id, "dashboard_id": dashboard_id},
            verify=False,
        ).json()
        return association

    @staticmethod
    def remove_dashboard_from_group(group_id: str, dashboard_id: str) -> dict:
        """Remove um dashboard de um grupo."""
        try:
            group_dashboards = requests.get(
                settings.POCKETBASE_URL
                + f"/api/collections/groups_dashboards/records?filter=(group_id='{group_id}')",
                headers={"Content-Type": "application/json"},
                verify=False,
            ).json()

            if "items" not in group_dashboards:
                raise HTTPException(
                    status_code=404, detail="No dashboards found for this group"
                )

            for group_dashboard in group_dashboards["items"]:
                if group_dashboard.get("dashboard_id") == dashboard_id:
                    response = requests.delete(
                        settings.POCKETBASE_URL
                        + f"/api/collections/groups_dashboards/records/{group_dashboard['id']}",
                        headers={"Content-Type": "application/json"},
                        verify=False,
                    )

                    if response.status_code == 204:
                        return {"message": "Dashboard removed from group successfully"}
                    else:
                        raise HTTPException(
                            status_code=response.status_code,
                            detail="Failed to remove dashboard",
                        )

            raise HTTPException(
                status_code=404, detail="Dashboard not found in this group"
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
