import scrapper.database_manager as dm
import scrapper.product_data_fetcher as pdf
from datetime import datetime
# from dotenv import load_dotenv

# load_dotenv()

# Database configuration
dbname = "colruyt_tracker"
user = "thibodebras"
password = "postgres"
host = "localhost"

# API configuration
base_url = "https://apip.colruyt.be/gateway/ictmgmt.emarkecom.cgproductretrsvc.v2/v2/v2/fr/products"
max_retries = 3
retry_delay = 30  # seconds

# Shop IDs
shops = {
    101:"TEST"
    # 459: "AUDERGHEM (COLRUYT)",
    # 1825: "SINT-DENIJS-WESTREM (COLRUYT)",
    # 471: "ETTERBEEK (RUE GRAY) COLRUYT)",
    # 1671: "DINANT (COLRUYT)"
}

def main():
    # Initialize and connect to the database
    db_manager = dm.DatabaseManager(dbname, user, password, host)
    db_manager.connect()

    # Create table for today's data
    run_date = datetime.now().date()
    table_name = f"raw_data_{str(run_date).replace('-', '_')}_todelete"
    db_manager.create_table(table_name)

    # Initialize the product data fetcher
    data_fetcher = pdf.ProductDataFetcher(base_url, max_retries, retry_delay)

    # Fetch and store data for each shop and page
    for shop_id in shops.keys():
        for page in range(1, 60):  # Assuming we want to fetch data from 60 pages
            data, status_code = data_fetcher.fetch_product_data(shop_id, page)
            if data:
                products = data.get("products", [])
                if not products:
                    print(f"No products returned for shop {shop_id} on page {page}. Moving to next shop.")
                    break  # No products found, move to the next shop.
                db_manager.insert_data(table_name, shop_id, page, products, run_date)
                # TODO add list of fails and rerun them

    # Close the database connection
    db_manager.close()

if __name__ == "__main__":
    main()
