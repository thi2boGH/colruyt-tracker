import unittest
from unittest.mock import patch, MagicMock, ANY
import scraper.product_data_fetcher as pdf
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class TestProductDataFetcher(unittest.TestCase): 

    @classmethod
    def setUpClass(cls):
        super(TestProductDataFetcher, cls).setUpClass()
        cls.base_url = "https://apip.colruyt.be/gateway/ictmgmt.emarkecom.cgproductretrsvc.v2/v2/v2/fr/products"
        cls.data_fetcher = pdf.ProductDataFetcher(cls.base_url, 3, 30)
        logging.info('ProductDataFetcher setup for all tests.')


    @patch('requests.get')
    def test_api_call_failure(self, mock_get):
        # Mock an unsuccessful API response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        # Call the method
        shop_id, page = '459', 1
        response, status_code = self.data_fetcher.fetch_product_data(shop_id, page)

        # Check that the response is None and the status code is correct
        self.assertIsNone(response)
        self.assertEqual(status_code, 500)
        logging.info('Proper handling of failed API call verified.')
        
    def test_fetch_product_data_with_real_call(self):
        # Call the method with real API endpoint
        shop_id, page = '459', 1
        response, status_code = self.data_fetcher.fetch_product_data(shop_id, page)

        # Validate the response
        self.assertIsNotNone(response, "API call returned None response")
        self.assertIn('products', response, "Response JSON does not contain 'products' key")
        self.assertEqual(status_code, 200, f"Expected status code 200, got {status_code}")

        # Log the success
        logging.info('Valid response received for real API call.')


if __name__ == '__main__':
    unittest.main()
