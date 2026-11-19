import time
from auth import SharePointAuth
from classifier import LogoClassifier
from config import AppConfig
from sharepoint_client import SharePointClient


class BrandHunterWorker:
    def __init__(
        self,
        config: AppConfig,
        sp_client: SharePointClient,
        classifier: LogoClassifier,
    ):
        self.config = config
        self.sp_client = sp_client
        self.classifier = classifier

    def process_once(self) -> None:
        items = self.sp_client.fetch_new_items()

        for item in items:
            item_id = item["Id"]
            title = item.get("Title", f"Eintrag_{item_id}")
            attachments = item.get("AttachmentFiles", [])

            print(f"Neuer Eintrag gefunden: ID={item_id} | Titel={title}")

            if not attachments:
                print(f"   -> Warnung: Kein Bild-Anhang bei ID={item_id} vorhanden.")
                self.sp_client.update_item_result(
                    item_id=item_id,
                    status="Fehler",
                    brand="Kein Bild",
                    confidence=0,
                )
                continue

            local_image = self.sp_client.download_attachment(item_id, attachments[0])
            brand, confidence = self.classifier.predict(local_image)

            self.sp_client.update_item_result(
                item_id=item_id,
                status="Fertig",
                brand=brand,
                confidence=confidence,
            )
            print(f"   -> Fertig! Ergebnis: {brand} ({confidence} %)")

    def run_forever(self) -> None:
        print(
            f"Starte BrandHunter SharePoint-Worker als {self.config.user_email} "
            f"(Beenden mit Strg+C)..."
        )
        while True:
            try:
                self.process_once()
            except Exception as e:
                print(f"Fehler im Durchlauf: {e}")
            time.sleep(self.config.poll_interval_seconds)


if __name__ == "__main__":
    app_config = AppConfig.from_env()
    sp_auth = SharePointAuth(app_config)
    client = SharePointClient(app_config, sp_auth)
    logo_classifier = LogoClassifier()

    worker = BrandHunterWorker(app_config, client, logo_classifier)
    worker.run_forever()