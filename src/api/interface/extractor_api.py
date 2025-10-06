from abc import ABC, abstractmethod


class ExtractorAPI(ABC):
    @abstractmethod
    async def get_piquillo_projection_sheet_data(self, date: str) -> dict[str, str]:
        pass

    @abstractmethod
    async def get_california_projection_sheet_data(self, date: str) -> dict[str, str]:
        pass

    @abstractmethod
    async def get_piquillo_varieties_count_data(self, date: str) -> dict[str, str]:
        pass

    @abstractmethod
    async def get_california_varieties_count_data(self, date: str) -> dict[str, str]:
        pass
