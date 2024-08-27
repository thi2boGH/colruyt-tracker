import psycopg2
from contextlib import contextmanager
from .config import DATABASE_CONFIG
import pandas as pd

class DatabaseManager:
    def __init__(self, config=DATABASE_CONFIG):
        self.config = config
        self.conn = None

    def connect(self):
        self.conn = psycopg2.connect(**self.config)

    def close(self):
        if self.conn:
            self.conn.close()

    @contextmanager
    def cursor(self):
        self.connect()
        cursor = self.conn.cursor()
        try:
            yield cursor
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cursor.close()
            self.conn.commit()  # Commit after the operation completes

    def create_tables(self):
        self.connect()
        commands = [
        """
        CREATE TABLE IF NOT EXISTS Product (
            ProductID INT PRIMARY KEY,
            Name VARCHAR(255),
            LongName VARCHAR(255),
            ShortName VARCHAR(100),
            Description TEXT,
            TopCategoryName VARCHAR(255),
            TopCategoryId INT,
            Brand VARCHAR(255),
            SeoBrand VARCHAR(255)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS Shop (
            ShopID INT PRIMARY KEY,
            ShopName VARCHAR(255) NOT NULL,
            Address VARCHAR(255),
            City VARCHAR(100)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS PriceHistory (
            Id VARCHAR(64) PRIMARY KEY,
            PriceID VARCHAR(32) ,
            EffectiveDate DATE NOT NULL,
            ProductID INT NOT NULL,
            ShopID INT NOT NULL,
            BasicPrice DECIMAL(10, 2),
            RecommendedQuantity DECIMAL(10, 2),
            QuantityPrice DECIMAL(10, 2),
            QuantityPriceQuantity DECIMAL(10, 2),
            MeasurementUnitPrice DECIMAL(10, 2),
            MeasurementUnitQuantityPrice DECIMAL(10, 2),
            MeasurementUnit VARCHAR(50),
            IsRedPrice BOOLEAN,
            PricePerUOM DECIMAL(10, 2),
            ActivationDate VARCHAR(50),
            RecordSource VARCHAR(50),
            IsPromoActive VARCHAR(50),
            PriceChangeCode VARCHAR(10),
            QuantityPricePerUOM DECIMAL(10, 2),
            QuantityActivationDate VARCHAR(50),
            QuantityPriceChangeCode VARCHAR(10),
            RedPriceReason VARCHAR(255),
            ReferencePrice DECIMAL(10, 2),
            RetentionPeriod DECIMAL(10, 2),
            Unit VARCHAR(50),
            IsAvailable BOOLEAN,
            IsPriceAvailable BOOLEAN,
            FOREIGN KEY (ProductID) REFERENCES Product(ProductID),
            FOREIGN KEY (ShopID) REFERENCES Shop(ShopID)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS ProductHistory (
            Id VARCHAR(64) PRIMARY KEY,
            ProductHistoryID VARCHAR(32),
            EffectiveDate DATE NOT NULL,
            ProductID INT NOT NULL,
            InPromo BOOLEAN,
            IsBio BOOLEAN,
            CountryOfOrigin VARCHAR(100),
            IsNew BOOLEAN,
            Content TEXT,
            NutriscoreLabel VARCHAR(10),
            EcoscoreLabel VARCHAR(10),
            EcoscoreValue DECIMAL(5, 2),
            FOREIGN KEY (ProductID) REFERENCES Product(ProductID)
        );
        """
        ]
        with self.cursor() as cursor:
            for command in commands:
                cursor.execute(command)

    def fetch_existing_data(self, table_name, column_name):
        self.connect()
        query = f"SELECT {column_name} FROM {table_name}"
        df = pd.read_sql(query, self.conn)
        return df[column_name].tolist()

    def fetch_latest_ids(self, table_name, id_column, group_columns, date_column):
        self.connect()
        group_by_clause = ", ".join(group_columns)
        query = f"""
            SELECT {id_column}
            FROM {table_name}
            WHERE ({group_by_clause}, {date_column}) IN (
                SELECT {group_by_clause}, MAX({date_column})
                FROM {table_name}
                GROUP BY {group_by_clause}
            )
        """
        return pd.read_sql(query, self.conn)
