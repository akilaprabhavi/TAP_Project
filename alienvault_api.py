import requests
import time
from secret_manager import get_aws_secret

class AlienVaultAPI:
    """
    A class to interact with the AlienVault OTX API.
    """
    def __init__(self):
        secrets = get_aws_secret()
        self.api_key = secrets.get("ALIENVAULT_API_KEY")
        self.base_url = "https://otx.alienvault.com/api/v1"

    def get_all_subscribed_pulses(self):
        all_pulses = []
        page = 1
        print("Fetching pulses from AlienVault OTX...\n")

        while True:
            url = f"{self.base_url}/pulses/subscribed?page={page}"
            headers = {"X-OTX-API-KEY": self.api_key}

            try:
                print(f"Fetching page {page}...")
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
            except requests.exceptions.Timeout:
                print("Request timed out. Skipping this page.")
                break
            except requests.exceptions.RequestException as e:
                print(f"Error fetching data from AlienVault: {e}")
                break

            data = response.json()
            pulses = data.get("results", [])

            if not pulses:
                print("No more pulses found. Finished fetching.")
                break

            all_pulses.extend(pulses)
            page += 1
            time.sleep(0.5)

        print(f"\nFetched total {len(all_pulses)} pulses.")
        return all_pulses



