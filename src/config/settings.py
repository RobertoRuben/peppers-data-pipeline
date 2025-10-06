import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self):
        self.scheme = os.getenv("API_SCHEME", "http")
        self.host = os.getenv("API_HOST")
        self.port = os.getenv("API_PORT")
        self.base_path = os.getenv("API_BASE_PATH")
        self.auth_type = os.getenv("API_AUTH_TYPE", "Basic")
        self.auth_token = os.getenv("API_AUTH_TOKEN")
        self.fundo = os.getenv("API_FUNDO")
        self.cultivo = os.getenv("API_CULTIVO")
        self.ruc_empresa = os.getenv("API_RUC_EMPRESA")
        self.cartilla_piquillo = os.getenv("CARTILLA_PROYECCION_PIQUILLO")
        self.cartilla_california = os.getenv("CARTILLA_PROYECCION_CALIFORNIA")
        self.cartilla_conteos_piquillo = os.getenv("CARTILLA_CONTEOS_PIQUILLO")
        self.cartilla_conteos_california = os.getenv("CARTILLA_CONTEOS_CALIFORNIA")

    def validate(self):
        required = [
            "host",
            "port",
            "base_path",
            "auth_token",
            "fundo",
            "cultivo",
            "ruc_empresa",
        ]
        missing = [attr for attr in required if getattr(self, attr) is None]
        if missing:
            raise ValueError(f"Missing environment variables: {', '.join(missing)}")


# Singleton accessor to return a validated Settings instance
_settings_instance: Settings | None = None


def get_settings() -> Settings:
    """Return a singleton, validated Settings instance.

    This helps consumers who prefer to obtain an instance directly from config.
    """
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
        _settings_instance.validate()
    return _settings_instance
