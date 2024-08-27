
import pandas as pd
import numpy as np
from .utils import hash_row

class DataProcessor:
    def __init__(self, raw_df):
        self.raw_df = raw_df

    def explode_and_normalize_products(self):
        exploded_products_df = self.raw_df.explode('products')

        normalized_products_df = pd.json_normalize(
            exploded_products_df['products'].apply(lambda product: product if isinstance(product, dict) else {})
        )

        exploded_products_df.drop(columns=['products'], inplace=True)
        combined_df = pd.concat([exploded_products_df.reset_index(drop=True), normalized_products_df], axis=1)
        unique_products_df = combined_df.drop_duplicates(subset=["shop_id", "productId"])

        return unique_products_df

    def process_products(self):
        product_description_mask = [
            'productId', 'name', 'LongName', 'ShortName', 'description', 
            'topCategoryName', 'topCategoryId', 'brand', 'seoBrand'
        ]
        product_description_columns = {
            'productId': 'productId', 
            'name': 'name', 
            'LongName': 'longName', 
            'ShortName': 'shortName', 
            'description': 'description', 
            'topCategoryName': 'topCategoryName', 
            'topCategoryId': 'topCategoryId', 
            'brand': 'brand', 
            'seoBrand': 'seoBrand'
        }
        products_df = (
            self.raw_df[product_description_mask]
            .drop_duplicates()
            .replace({np.nan: None})
            .rename(columns=product_description_columns)
        )
        products_df['productId'] = products_df['productId'].astype(int)
        products_df.reset_index(drop=True, inplace=True)
        return products_df

    def process_product_history(self):
        product_variables_mask = [
            'run_date', 'productId', 
            'inPromo', 'IsBio', 'CountryOfOrigin', 'IsNew', 'content', 
            'nutriscoreLabel', 'EcoscoreLabel', 'EcoscoreValue'
        ]
        product_variables_columns = {
            'run_date': "effectiveDate", 'productId': 'productId', 
            'inPromo': 'inPromo', 'IsBio': 'isBio', 
            'CountryOfOrigin': 'countryOfOrigin', 'IsNew': 'isNew', 
            'content': 'content', 'nutriscoreLabel': 'nutriscoreLabel', 
            'EcoscoreLabel': 'ecoscoreLabel', 'EcoscoreValue': 'ecoscoreValue'
        }
        products_history_df = (
            self.raw_df[product_variables_mask]
            .drop_duplicates()
            .rename(columns=product_variables_columns)
        )
        products_history_df.reset_index(drop=True, inplace=True)
        
                # Generate productHistoryId
        exclude_columns = ['effectiveDate']
        products_history_df['productHistoryId'] = products_history_df.drop(columns=exclude_columns).apply(hash_row, axis=1)
        products_history_df['id'] = products_history_df['effectiveDate'].astype(str) + products_history_df['productHistoryId'].astype(str) 
        
        return products_history_df

    def process_prices(self):
        price_mask = [
            'run_date', 'productId', 'shop_id', 'price.basicPrice', 
            'price.recommendedQuantity', 'price.quantityPrice', 
            'price.quantityPriceQuantity', 'price.measurementUnitPrice', 
            'price.measurementUnitQuantityPrice', 'price.measurementUnit', 
            'price.isRedPrice', 'price.pricePerUOM', 'price.activationDate', 
            'price.recordSource', 'price.isPromoActive', 'price.priceChangeCode', 
            'price.quantityPricePerUOM', 'price.quantityActivationDate', 
            'price.quantityPriceChangeCode', 'price.redPriceReason', 
            'price.referencePrice', 'price.retentionPeriod', 'price.unit', 'isAvailable', 'isPriceAvailable', 
            
        ]
        price_columns = {
            'price_id': "priceId", 'run_date': "effectiveDate", 'productId': 'productId', 
            'shop_id': 'shopId', 'price.basicPrice': 'basicPrice', 
            'price.recommendedQuantity': 'recommendedQuantity', 
            'price.quantityPrice': 'quantityPrice', 
            'price.quantityPriceQuantity': 'quantityPriceQuantity', 
            'price.measurementUnitPrice': 'measurementUnitPrice', 
            'price.measurementUnitQuantityPrice': 'measurementUnitQuantityPrice', 
            'price.measurementUnit': 'measurementUnit', 
            'price.isRedPrice': 'isRedPrice', 'price.pricePerUOM': 'pricePerUOM', 
            'price.activationDate': 'activationDate', 
            'price.recordSource': 'recordSource', 'price.isPromoActive': 'isPromoActive', 
            'price.priceChangeCode': 'priceChangeCode', 
            'price.quantityPricePerUOM': 'quantityPricePerUOM', 
            'price.quantityActivationDate': 'quantityActivationDate', 
            'price.quantityPriceChangeCode': 'quantityPriceChangeCode', 
            'price.redPriceReason': 'redPriceReason', 
            'price.referencePrice': 'referencePrice', 
            'price.retentionPeriod': 'retentionPeriod', 'price.unit': 'unit',
            'isAvailable': 'isAvailable', 'isPriceAvailable': 'isPriceAvailable', 
        }
        prices_df = (
            self.raw_df[price_mask]
            .rename(columns=price_columns)
            .assign(
                isRedPrice=lambda df: df['isRedPrice'].fillna(False).astype(bool),
                shopId=lambda df: df['shopId'].astype(int),
                productId=lambda df: df['productId'].astype(int)
            )
        )
        prices_df.reset_index(drop=True, inplace=True)
        
                # Generate priceId
        exclude_columns = ['effectiveDate']
        prices_df['priceId'] = prices_df.drop(columns=exclude_columns).apply(hash_row, axis=1)
        prices_df['id'] = prices_df['effectiveDate'].astype(str) + prices_df['priceId'].astype(str) 
        
        return prices_df

    def process_shops(self):
        shops_df = pd.DataFrame(self.raw_df['shop_id'].unique(), columns=['shopId'])
        shops_df = shops_df.assign(
            shopName=np.nan,
            address=np.nan,
            city=np.nan
        )
        shops_df.reset_index(drop=True, inplace=True)
        return shops_df
