import os
import asyncio
from unittest.mock import patch

from src.api.interface import ExtractorAPI
from src.api.impl import ExtractorAPIImpl


class FakeResponse:
    def __init__(self, payload, status=200):
        self._payload = payload
        self.status = status

    async def json(self):
        return self._payload

    def raise_for_status(self):
        if not (200 <= self.status < 300):
            raise Exception(f"HTTP {self.status}")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class FakeSession:
    def __init__(self, *args, **kwargs):
        self.calls = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    def get(self, url, headers=None, timeout=None, **kwargs):
        self.calls.append(
            {
                "url": url,
                "headers": headers,
                "timeout": timeout,
                **kwargs,
            }
        )
        return FakeResponse({"ok": True, "url": url})


def test_get_piquillo_projection_sheet_data_builds_correct_request_and_returns_result():
    async def _run():
        api: ExtractorAPI = ExtractorAPIImpl()

        with patch(
            "src.api.impl.extractor_api_impl.aiohttp.ClientSession", FakeSession
        ) as _:
            date = "2025-10-06"
            result = await api.get_piquillo_projection_sheet_data(date)

            assert isinstance(result, dict)
            assert result.get("ok") is True
            expected_base = f"{os.getenv('API_SCHEME', 'http')}://{os.getenv('API_HOST')}:{os.getenv('API_PORT')}{os.getenv('API_BASE_PATH')}"
            assert result["url"].startswith(
                f"{expected_base}/Fitosanidad/ZABG_RptEvaluacionesXVariable?"
            )
            assert f"prmstrFundo={os.getenv('API_FUNDO')}" in result["url"]
            assert (
                f"prmintCartilla={os.getenv('CARTILLA_PROYECCION_PIQUILLO')}"
                in result["url"]
            )
            assert f"prmintCultivo={os.getenv('API_CULTIVO')}" in result["url"]
            assert f"prmdatFechaInicio={date}" in result["url"]
            assert f"prmdatFechaFin={date}" in result["url"]
            assert f"prmstrRUCEmpresa={os.getenv('API_RUC_EMPRESA')}" in result["url"]

    asyncio.run(_run())


def test_get_california_varieties_count_data_uses_auth_header_and_returns_result():
    async def _run():
        api: ExtractorAPI = ExtractorAPIImpl()

        session_holder = {"session": None}

        class InspectableFakeSession(FakeSession):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                session_holder["session"] = self

        with patch(
            "src.api.impl.extractor_api_impl.aiohttp.ClientSession",
            InspectableFakeSession,
        ) as _:
            date = "2025-10-06"
            result = await api.get_california_varieties_count_data(date)

            assert result["ok"] is True

            calls = session_holder["session"].calls
            assert len(calls) == 1
            headers = calls[0]["headers"]
            assert (
                headers["Authorization"]
                == f"{os.getenv('API_AUTH_TYPE', 'Basic')} {os.getenv('API_AUTH_TOKEN')}"
            )
            assert headers["Content-Type"] == "application/json"
            assert headers["Accept"] == "application/json"

    asyncio.run(_run())


def test_get_california_projection_sheet_data_and_piquillo_varieties_count_data_return_payload():
    async def _run():
        api: ExtractorAPI = ExtractorAPIImpl()

        with patch(
            "src.api.impl.extractor_api_impl.aiohttp.ClientSession", FakeSession
        ):
            date = "2025-10-06"
            res1 = await api.get_california_projection_sheet_data(date)
            res2 = await api.get_piquillo_varieties_count_data(date)

            assert res1.get("ok") is True
            assert res2.get("ok") is True

    asyncio.run(_run())
