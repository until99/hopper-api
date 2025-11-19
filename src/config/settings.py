import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # PocketBase
    POCKETBASE_URL: str = os.getenv("POCKETBASE_URL", "")

    # Azure
    AZURE_TENANT_ID: str = os.getenv("AZURE_TENANT_ID", "")
    AZURE_CLIENT_ID: str = os.getenv("AZURE_CLIENT_ID", "")
    AZURE_CLIENT_SECRET: str = os.getenv("AZURE_CLIENT_SECRET", "")

    # Airflow
    AIRFLOW_URL: str = os.getenv("AIRFLOW_URL", "")
    AIRFLOW_USERNAME: str = os.getenv("AIRFLOW_USERNAME", "")
    AIRFLOW_PASSWORD: str = os.getenv("AIRFLOW_PASSWORD", "")

    # API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))


settings = Settings()
