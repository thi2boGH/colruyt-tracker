import psycopg2
import json

class DatabaseManager:
    """
    This class handles interactions with the PostgreSQL database.
    """

    def __init__(self, dbname, user, password, host):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.conn = None
        self.cur = None

    def connect(self):
        """Establish a connection to the database."""
        self.conn = psycopg2.connect(dbname=self.dbname, user=self.user, password=self.password, host=self.host)
        self.cur = self.conn.cursor()

    def create_table(self, table_name):
        """Create a table if it does not exist."""
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            run_date DATE,
            shop_id VARCHAR(255),
            page INT,
            products JSON
        );
        """
        self.cur.execute(create_table_query)
        self.conn.commit()

    def insert_data(self, table_name, shop_id, page, products, run_date):
        """Insert data into the table."""
        try:
            insert_query = f"INSERT INTO {table_name} (shop_id, page, products, run_date) VALUES (%s, %s, %s, %s)"
            self.cur.execute(insert_query, (shop_id, page, json.dumps(products), run_date))
            self.conn.commit()
        except psycopg2.Error as e:
            print(f"Database error: {e}")
            self.conn.rollback()

    def close(self):
        """Close the database connection."""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
