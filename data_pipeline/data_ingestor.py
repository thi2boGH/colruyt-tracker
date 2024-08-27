import logging
import time
from .database import DatabaseManager
from .data_processor import DataProcessor
import pandas as pd

class DataIngestor:
    def __init__(self, raw_df):
        self.raw_df = raw_df
        self.db_manager = DatabaseManager()
        self.data_processor = DataProcessor(raw_df)
        self.metrics = {
            'total_shop_added': 0,
            'total_product_added': 0,
            'total_price_updates': 0,
            'total_product_updates': 0
        }
        self.logger = logging.getLogger(__name__)

    def ingest(self):
        start_time = time.time()

        products_df = self.data_processor.process_products()
        products_history_df = self.data_processor.process_product_history()
        prices_df = self.data_processor.process_prices()
        shops_df = self.data_processor.process_shops()

        self.logger.info("Processed dataframes - Products: %d, ProductHistory: %d, Prices: %d, Shops: %d",
                        len(products_df), len(products_history_df), len(prices_df), len(shops_df))

        existing_products = self.db_manager.fetch_existing_data('Product', 'productid')
        existing_shops = self.db_manager.fetch_existing_data('Shop', 'shopid')

        new_products = products_df[~products_df['productId'].astype(int).isin(existing_products)]
        new_shops = shops_df[~shops_df['shopId'].astype(int).isin(existing_shops)]

        with self.db_manager.cursor() as cursor:
            for _, row in new_products.iterrows():
                cursor.execute("""
                    INSERT INTO Product (productId, name, longName, shortName, description, topCategoryName, topCategoryId, brand, seoBrand)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    row['productId'], row['name'], row['longName'], row['shortName'], 
                    row['description'], row['topCategoryName'], row['topCategoryId'], 
                    row['brand'], row['seoBrand']
                ))

            for shop_id in new_shops['shopId'].unique():
                cursor.execute("""
                    INSERT INTO Shop (shopId, shopName, address, city)
                    VALUES (%s, %s, %s, %s)
                """, (shop_id, 'Unknown name', 'Unknown address', 'Unknown city'))

            self.metrics['total_shop_added'] += len(new_shops)
            self.metrics['total_product_added'] += len(new_products)
            self.logger.info("Added new shops: %d, new products: %d", len(new_shops), len(new_products))


        existing_price_ids = self.db_manager.fetch_latest_ids(
            table_name='PriceHistory',
            id_column='PriceId',
            group_columns=['ProductID', 'ShopID'],
            date_column='EffectiveDate'
        )
        price_changes = prices_df[~prices_df['priceId'].isin(existing_price_ids['priceid'])]
        self.logger.info("Number of price changes detected: %d", len(price_changes))
        print(price_changes.head(10))
        
        # Process price updates
        batch_size = 1000
        for i in range(0, len(price_changes), batch_size):
            batch = price_changes.iloc[i:i+batch_size]
            values = [
                (
                    row['effectiveDate'], row['productId'], row['shopId'], row['basicPrice'],
                    row['recommendedQuantity'], row['quantityPrice'], row['quantityPriceQuantity'],
                    row['measurementUnitPrice'], row['measurementUnitQuantityPrice'], row['measurementUnit'],
                    row['isRedPrice'], row['pricePerUOM'], row['activationDate'], row['recordSource'],
                    row['isPromoActive'], row['priceChangeCode'], row['quantityPricePerUOM'],
                    row['quantityActivationDate'], row['quantityPriceChangeCode'], row['redPriceReason'],
                    row['referencePrice'], row['retentionPeriod'], row['unit'], row['isAvailable'], row['isPriceAvailable'], row['priceId'], row['id']
                )
                for _, row in batch.iterrows()
            ]

            with self.db_manager.cursor() as cursor:
                cursor.executemany("""
                    INSERT INTO PriceHistory (EffectiveDate, ProductID, ShopID, BasicPrice, RecommendedQuantity, QuantityPrice,
                                            QuantityPriceQuantity, MeasurementUnitPrice, MeasurementUnitQuantityPrice,
                                            MeasurementUnit, IsRedPrice, PricePerUOM, ActivationDate, RecordSource,
                                            IsPromoActive, PriceChangeCode, QuantityPricePerUOM, QuantityActivationDate,
                                            QuantityPriceChangeCode, RedPriceReason, ReferencePrice, RetentionPeriod,
                                            Unit, IsAvailable, IsPriceAvailable, PriceId, Id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s)
                """, values)
                self.db_manager.conn.commit()

            self.metrics['total_price_updates'] += len(batch)
            self.logger.info("Processed batch %d/%d for price updates", i//batch_size + 1, (len(price_changes) + batch_size - 1)//batch_size)

        # Process product history updates
        existing_product_history_ids = self.db_manager.fetch_latest_ids(
            table_name='ProductHistory',
            id_column='ProductHistoryId',
            group_columns=['ProductID'],
            date_column='EffectiveDate'
        )
        product_changes = products_history_df[~products_history_df['productHistoryId'].isin(existing_product_history_ids['producthistoryid'])]
        self.logger.info("Number of product history changes detected: %d", len(product_changes))
        print(product_changes.head(10))
        
        for i in range(0, len(product_changes), batch_size):
            batch = product_changes.iloc[i:i+batch_size]
            values = [
                (
                    row['effectiveDate'], row['productId'], 
                    row['inPromo'], row['isBio'], row['countryOfOrigin'], row['isNew'],
                    row['content'], row['nutriscoreLabel'], row['ecoscoreLabel'], row['ecoscoreValue'], row['productHistoryId'], row['id']
                )
                for _, row in batch.iterrows()
            ]

            with self.db_manager.cursor() as cursor:
                cursor.executemany("""
                    INSERT INTO ProductHistory (EffectiveDate, ProductID,  InPromo, IsBio,
                                                CountryOfOrigin, IsNew, Content, NutriscoreLabel, EcoscoreLabel, EcoscoreValue, ProductHistoryId, Id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, values)
                self.db_manager.conn.commit()

            self.metrics['total_product_updates'] += len(batch)
            self.logger.info("Processed batch %d/%d for product history updates", i//batch_size + 1, (len(product_changes) + batch_size - 1)//batch_size)

        end_time = time.time()
        elapsed_time = end_time - start_time
        self.logger.info("Data ingestion completed in %.2f seconds", elapsed_time)
        self.logger.info("Metrics: %s", self.metrics)
