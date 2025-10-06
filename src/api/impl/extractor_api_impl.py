import os
import aiohttp
from urllib.parse import urlencode
from dotenv import load_dotenv

from ..interface.extractor_api import ExtractorAPI

load_dotenv()


class ExtractorAPIImpl(ExtractorAPI):
    """
    Implementation of the Fitosanidad data extraction API.
    Performs asynchronous HTTP requests to configured endpoints.
    """

    def __init__(self):
        # API Configuration
        self.scheme: str = os.getenv("API_SCHEME", "http")
        self.host: str | None = os.getenv("API_HOST")
        self.port: str | None = os.getenv("API_PORT")
        self.base_path: str | None = os.getenv("API_BASE_PATH")

        # Authentication
        self.auth_type: str = os.getenv("API_AUTH_TYPE", "Basic")
        self.auth_token: str | None = os.getenv("API_AUTH_TOKEN")

        # Business Parameters
        self.fundo: str | None = os.getenv("API_FUNDO")
        self.cultivo: str | None = os.getenv("API_CULTIVO")
        self.ruc_empresa: str | None = os.getenv("API_RUC_EMPRESA")

        # Cartillas IDs
        self.cartilla_piquillo: str | None = os.getenv("CARTILLA_PROYECCION_PIQUILLO")
        self.cartilla_california: str | None = os.getenv(
            "CARTILLA_PROYECCION_CALIFORNIA"
        )
        self.cartilla_conteos_piquillo: str | None = os.getenv(
            "CARTILLA_CONTEOS_PIQUILLO"
        )
        self.cartilla_conteos_california: str | None = os.getenv(
            "CARTILLA_CONTEOS_CALIFORNIA"
        )

        # Validate configuration before building URLs
        self._validate_config()

        # Build URLs (after validation, we know values are not None)
        assert (
            self.host is not None
            and self.port is not None
            and self.base_path is not None
        )
        self.base_url = f"{self.scheme}://{self.host}:{self.port}{self.base_path}"
        self.endpoint = f"{self.base_url}/Fitosanidad/ZABG_RptEvaluacionesXVariable"

    def _validate_config(self) -> None:
        """Validates that all required environment variables are configured"""
        required_vars = {
            "API_HOST": self.host,
            "API_PORT": self.port,
            "API_BASE_PATH": self.base_path,
            "API_AUTH_TOKEN": self.auth_token,
            "API_FUNDO": self.fundo,
            "API_CULTIVO": self.cultivo,
            "API_RUC_EMPRESA": self.ruc_empresa,
        }

        missing = [key for key, value in required_vars.items() if not value]
        if missing:
            raise ValueError(f"Missing environment variables: {', '.join(missing)}")

    def _get_headers(self) -> dict[str, str]:
        """Generates authentication headers for requests"""
        assert self.auth_token is not None  # Validated in _validate_config
        return {
            "Authorization": f"{self.auth_type} {self.auth_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _build_params(self, cartilla: str, date: str) -> dict[str, str]:
        """
        Builds query parameters for the request.

        Args:
            cartilla: ID of the cartilla to query
            date: Date in YYYY-MM-DD format

        Returns:
            Dictionary with query parameters
        """
        # Assert ensures values are not None after _validate_config
        assert self.fundo is not None
        assert self.cultivo is not None
        assert self.ruc_empresa is not None

        return {
            "prmstrFundo": self.fundo,
            "prmintCartilla": cartilla,
            "prmintCultivo": self.cultivo,
            "prmdatFechaInicio": date,
            "prmdatFechaFin": date,
            "prmstrRUCEmpresa": self.ruc_empresa,
        }

    async def _fetch_data(self, cartilla: str, date: str) -> dict[str, str]:
        """
        Generic method to perform HTTP requests to the API.

        Args:
            cartilla: ID of the cartilla to query
            date: Date in YYYY-MM-DD format

        Returns:
            JSON response from API

        Raises:
            Exception: If there's an HTTP or processing error
        """
        params = self._build_params(cartilla, date)
        headers = self._get_headers()

        url = f"{self.endpoint}?{urlencode(params)}"

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientResponseError as e:
                raise Exception(f"HTTP Error {e.status}: {e.message}") from e
            except aiohttp.ClientError as e:
                raise Exception(f"Connection error: {str(e)}") from e
            except Exception as e:
                raise Exception(f"Unexpected error fetching data: {str(e)}") from e

    async def get_piquillo_projection_sheet_data(self, date: str) -> dict[str, str]:
        """
        Gets Piquillo projection sheet data.

        Args:
            date: Date in YYYY-MM-DD format (e.g., "2025-10-03")

        Returns:
            Dictionary with cartilla data
        """
        assert self.cartilla_piquillo is not None
        return await self._fetch_data(self.cartilla_piquillo, date)

    async def get_california_projection_sheet_data(self, date: str) -> dict[str, str]:
        """
        Gets California projection sheet data.

        Args:
            date: Date in YYYY-MM-DD format (e.g., "2025-10-03")

        Returns:
            Dictionary with cartilla data
        """
        assert self.cartilla_california is not None
        return await self._fetch_data(self.cartilla_california, date)

    async def get_piquillo_varieties_count_data(self, date: str) -> dict[str, str]:
        """
        Gets Piquillo varieties count data.

        Args:
            date: Date in YYYY-MM-DD format (e.g., "2025-10-03")

        Returns:
            Dictionary with count data
        """
        assert self.cartilla_conteos_piquillo is not None
        return await self._fetch_data(self.cartilla_conteos_piquillo, date)

    async def get_california_varieties_count_data(self, date: str) -> dict[str, str]:
        """
        Gets California varieties count data.

        Args:
            date: Date in YYYY-MM-DD format (e.g., "2025-10-03")

        Returns:
            Dictionary with count data
        """
        assert self.cartilla_conteos_california is not None
        return await self._fetch_data(self.cartilla_conteos_california, date)
