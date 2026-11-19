import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    tenant_name: str
    user_email: str
    user_password: str
    site_name: str = "WIV_2527_KiKon"
    list_name: str = "BrandHunter_AutoLogo_Daten"
    client_id: str = "14d82eec-204b-4c2f-b7e8-296a70dab67e"
    authority: str = "https://login.microsoftonline.com/organizations"
    token_cache_file: Path = Path("token_cache.bin")
    download_dir: Path = Path("temp_scans")
    poll_interval_seconds: int = 3

    @property
    def sharepoint_host(self) -> str:
        return f"https://{self.tenant_name}.sharepoint.com"

    @property
    def site_url(self) -> str:
        return f"{self.sharepoint_host}/sites/{self.site_name}"

    @property
    def scopes(self) -> list[str]:
        return [f"{self.sharepoint_host}/AllSites.Write"]

    @classmethod
    def from_env(cls) -> "AppConfig":
        tenant = os.environ.get("Sharepoint_Tenant")
        email = os.environ.get("Sharepoint_Email")
        password = os.environ.get("Sharepoint_Password")

        if not tenant or not email or not password:
            raise RuntimeError(
                "Fehler: Sharepoint_Tenant, Sharepoint_Email oder Sharepoint_Passwort "
                "nicht in den Umgebungsvariablen gefunden!"
            )

        config = cls(
            tenant_name=tenant.strip(),
            user_email=email.strip(),
            user_password=password,
        )
        config.download_dir.mkdir(exist_ok=True)
        return config