from abc import ABC, abstractmethod


class ExtractorAPI(ABC):
    @abstractmethod
    async def get_data(self, api_url: str) -> dict:
        """
        Asynchronously fetch data from the given API URL.

        :param api_url: The URL of the API endpoint to fetch data from.
        :return: A dictionary containing the fetched data.
        """
        pass
