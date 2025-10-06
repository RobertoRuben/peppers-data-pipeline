import asyncio
from unittest.mock import patch

from src.domain.extract.api.interface import ExtractorAPI
from src.domain.extract.api.impl import ExtractorAPIImpl


def test_get_piquillo_projection_sheet_data_calls_fetch_with_correct_params():
    async def _run():
        api: ExtractorAPI = ExtractorAPIImpl()
        expected_data = {"ok": True, "data": "test_piquillo_projection"}
        
        # Mock the internal _fetch_data method instead of aiohttp
        with patch.object(api, '_fetch_data', return_value=expected_data) as mock_fetch:
            date = "2025-10-06"
            result = await api.get_piquillo_projection_sheet_data(date)
            
            # Verify the method was called with correct parameters
            mock_fetch.assert_called_once_with(api.settings.cartilla_piquillo, date)
            
            # Verify the result
            assert result == expected_data
            assert result.get("ok") is True

    asyncio.run(_run())


def test_get_california_varieties_count_data_calls_fetch_with_correct_params():
    async def _run():
        api: ExtractorAPI = ExtractorAPIImpl()
        expected_data = {"ok": True, "data": "test_california_count"}
        
        # Mock the internal _fetch_data method
        with patch.object(api, '_fetch_data', return_value=expected_data) as mock_fetch:
            date = "2025-10-06"
            result = await api.get_california_varieties_count_data(date)
            
            # Verify the method was called with correct parameters
            mock_fetch.assert_called_once_with(api.settings.cartilla_conteos_california, date)
            
            # Verify the result
            assert result == expected_data
            assert result.get("ok") is True

    asyncio.run(_run())


def test_get_california_projection_sheet_data_and_piquillo_varieties_count_data_return_payload():
    async def _run():
        api: ExtractorAPI = ExtractorAPIImpl()
        
        expected_data1 = {"ok": True, "data": "test_california_projection"}
        expected_data2 = {"ok": True, "data": "test_piquillo_count"}

        with patch.object(api, '_fetch_data', side_effect=[expected_data1, expected_data2]) as mock_fetch:
            date = "2025-10-06"
            res1 = await api.get_california_projection_sheet_data(date)
            res2 = await api.get_piquillo_varieties_count_data(date)

            # Verify both methods were called with correct parameters
            assert mock_fetch.call_count == 2
            mock_fetch.assert_any_call(api.settings.cartilla_california, date)
            mock_fetch.assert_any_call(api.settings.cartilla_conteos_piquillo, date)
            
            # Verify results
            assert res1 == expected_data1
            assert res2 == expected_data2
            assert res1.get("ok") is True
            assert res2.get("ok") is True

    asyncio.run(_run())


def test_headers_are_built_correctly():
    """Test that the headers are built correctly with auth token."""
    api = ExtractorAPIImpl()
    headers = api._get_headers()
    
    expected_auth = f"{api.settings.auth_type} {api.settings.auth_token}"
    assert headers["Authorization"] == expected_auth
    assert headers["Content-Type"] == "application/json"
    assert headers["Accept"] == "application/json"


def test_params_are_built_correctly():
    """Test that URL parameters are built correctly."""
    api = ExtractorAPIImpl()
    cartilla = "test_cartilla"
    date = "2025-10-06"
    
    params = api._build_params(cartilla, date)
    
    assert params["prmstrFundo"] == api.settings.fundo
    assert params["prmintCartilla"] == cartilla
    assert params["prmintCultivo"] == api.settings.cultivo
    assert params["prmdatFechaInicio"] == date
    assert params["prmdatFechaFin"] == date
    assert params["prmstrRUCEmpresa"] == api.settings.ruc_empresa
