import requests

class AlienVaultAPI:
    """
    A class to interact with the AlienVault OTX API.
    """
    def __init__(self, api_key: str, base_url: str = "https://otx.alienvault.com/api/v1"):
        self.api_key = api_key
        self.base_url = base_url

    def get_subscribed_pulses(self):
        """
        Retrieve subscribed pulses from the OTX API.
        Returns:
            A list of pulse dictionaries.
        Raises:
            Exception: if the API request fails.
        """
        url = f"{self.base_url}/pulses/subscribed"
        headers = {"X-OTX-API-KEY": self.api_key}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get("results", [])
        else:
            raise Exception(f"Error fetching data: {response.status_code}")
