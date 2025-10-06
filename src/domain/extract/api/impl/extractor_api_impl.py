from urllib.parse import urlencode
import aiohttp
from src.core.config import Settings, get_settings
from ..interface import ExtractorAPI


class ExtractorAPIImpl(ExtractorAPI):
    def __init__(self, settings: Settings | None = None):
        # Use cached settings by default; Pydantic handles validation automatically
        self.settings = settings or get_settings()
        self.base_url = f"{self.settings.scheme}://{self.settings.host}:{self.settings.port}{self.settings.base_path}"
        self.endpoint = f"{self.base_url}/Fitosanidad/ZABG_RptEvaluacionesXVariable"

    def _get_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"{self.settings.auth_type} {self.settings.auth_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _build_params(self, cartilla: str, date: str) -> dict[str, str]:
        # Pydantic ensures all required fields are present and validated
        return {
            "prmstrFundo": self.settings.fundo,
            "prmintCartilla": cartilla,
            "prmintCultivo": self.settings.cultivo,
            "prmdatFechaInicio": date,
            "prmdatFechaFin": date,
            "prmstrRUCEmpresa": self.settings.ruc_empresa,
        }

    async def _fetch_data(self, cartilla: str, date: str) -> dict[str, str]:
        params = self._build_params(cartilla, date)
        headers = self._get_headers()
        url = f"{self.endpoint}?{urlencode(params)}"
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data

    async def get_piquillo_projection_sheet_data(self, date: str) -> dict[str, str]:
        result = await self._fetch_data(self.settings.cartilla_piquillo, date)
        return result

    async def get_california_projection_sheet_data(self, date: str) -> dict[str, str]:
        result = await self._fetch_data(self.settings.cartilla_california, date)
        return result

    async def get_piquillo_varieties_count_data(self, date: str) -> dict[str, str]:
        result = await self._fetch_data(self.settings.cartilla_conteos_piquillo, date)
        return result

    async def get_california_varieties_count_data(self, date: str) -> dict[str, str]:
        result = await self._fetch_data(self.settings.cartilla_conteos_california, date)
        return result
