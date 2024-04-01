import requests
import time
import scrapper.header_generator as hg

class ProductDataFetcher:
    """
    This class is responsible for fetching product data from the API.
    """

    def __init__(self, base_url, max_retries, retry_delay):
        self.base_url = base_url
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.header_generator = hg.HeaderGenerator()

    def fetch_product_data(self, shop_id, page):
        """Fetch product data for a specific shop ID and page number, handling retries."""
        for attempt in range(self.max_retries):
            headers = self.header_generator.generate()
            response = requests.get(f"{self.base_url}?clientCode=CLP&page={page}&placeId={shop_id}&size=250&sort=popularity%20asc", headers=headers)
            print(f"{shop_id} {page} {response.status_code}")

            if response.status_code == 200:
                return response.json(), response.status_code  # Return the JSON response if successful.

            if response.status_code == 456 and attempt < self.max_retries - 1:
                print(f"Received status code 456 for shop {shop_id} on page {page}. Retrying after {self.retry_delay} seconds.")
                time.sleep(self.retry_delay)
            else:
                # Return None and the status code to indicate a failure that should not be retried.
                return None, response.status_code

        # Return None and the last status code after exhausting all retries.
        return None, response.status_code
