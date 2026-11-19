from pathlib import Path
import requests
from auth import SharePointAuth
from config import AppConfig


class SharePointClient:
    def __init__(self, config: AppConfig, auth: SharePointAuth):
        self.config = config
        self.auth = auth

    def _get_headers(self, is_update: bool = False) -> dict[str, str]:
        token = self.auth.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json;odata=nometadata",
        }
        if is_update:
            headers.update(
                {
                    "Content-Type": "application/json;odata=nometadata",
                    "IF-MATCH": "*",
                    "X-HTTP-Method": "MERGE",
                }
            )
        return headers

    def fetch_new_items(self) -> list[dict]:
        """Ruft alle Zeilen mit Status 'Neu' inklusive der angehängten Dateien ab."""
        url = (
            f"{self.config.site_url}/_api/web/lists/getbytitle('{self.config.list_name}')/items"
            f"?$filter=Status eq 'Neu'&$expand=AttachmentFiles"
        )
        response = requests.get(url, headers=self._get_headers(), timeout=15)
        response.raise_for_status()
        return response.json().get("value", [])

    def download_attachment(self, item_id: int, attachment_info: dict) -> Path:
        """Lädt einen SharePoint-Anhang herunter und gibt den lokalen Dateipfad zurück."""
        server_rel_url = attachment_info["ServerRelativeUrl"]
        file_name = attachment_info["FileName"]
        local_path = self.config.download_dir / f"{item_id}_{file_name}"

        url = (
            f"{self.config.site_url}/_api/web/"
            f"GetFileByServerRelativeUrl('{server_rel_url}')/$value"
        )
        response = requests.get(url, headers=self._get_headers(), timeout=30)
        response.raise_for_status()
        local_path.write_bytes(response.content)
        return local_path

    def update_item_result(
        self, item_id: int, status: str, brand: str, confidence: int
    ) -> None:
        """Schreibt Status, erkannte Marke und Konfidenz in die SharePoint-Zeile zurück."""
        url = (
            f"{self.config.site_url}/_api/web/lists/"
            f"getbytitle('{self.config.list_name}')/items({item_id})"
        )
        payload = {
            "Status": status,
            "ErkannteMarke": brand,
            "Konfidenz": confidence,
        }
        response = requests.post(
            url, headers=self._get_headers(is_update=True), json=payload, timeout=15
        )
        response.raise_for_status()