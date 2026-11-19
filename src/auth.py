import msal
from config import AppConfig


class SharePointAuth:
    def __init__(self, config: AppConfig):
        self.config = config
        self.cache = msal.SerializableTokenCache()
        self._load_cache()

        self.app = msal.PublicClientApplication(
            client_id=self.config.client_id,
            authority=self.config.authority,
            token_cache=self.cache,
        )

    def _load_cache(self) -> None:
        if self.config.token_cache_file.exists():
            content = self.config.token_cache_file.read_text(encoding="utf-8")
            self.cache.deserialize(content)

    def _save_cache(self) -> None:
        if self.cache.has_state_changed:
            self.config.token_cache_file.write_text(
                self.cache.serialize(), encoding="utf-8"
            )

    def get_access_token(self) -> str:
        accounts = self.app.get_accounts(username=self.config.user_email)
        result = None

        # 1. Versuch: Gültigen Token aus dem lokalen Cache holen
        if accounts:
            result = self.app.acquire_token_silent(
                self.config.scopes, account=accounts[0]
            )

        # 2. Versuch: Direkter Login per Umgebungsvariablen (ROPC)
        if not result:
            result = self.app.acquire_token_by_username_password(
                username=self.config.user_email,
                password=self.config.user_password,
                scopes=self.config.scopes,
            )

        # 3. Fallback: Falls noch keine Einwilligung vorliegt (AADSTS65001), einmalig im Browser zustimmen
        if "access_token" not in result and "AADSTS65001" in result.get(
            "error_description", ""
        ):
            print(
                "Einmalige Berechtigung erforderlich – bitte im Browserfenster zustimmen..."
            )
            result = self.app.acquire_token_interactive(
                scopes=self.config.scopes,
                login_hint=self.config.user_email,
            )

        self._save_cache()

        if "access_token" not in result:
            raise RuntimeError(
                f"Login fehlgeschlagen ({result.get('error')}): "
                f"{result.get('error_description')}"
            )

        return result["access_token"]