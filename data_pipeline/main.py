from data_pipeline.database import DatabaseManager
from data_pipeline.data_ingestor import DataIngestor
from data_pipeline.data_processor import DataProcessor
import pandas as pd
import warnings # TODO need to be fixed
pd.set_option('future.no_silent_downcasting', True)
warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy connectable")
import logging


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,  # Set the logging level to INFO or DEBUG
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )

def main():
    configure_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting the data ingestion process")
    
    
    db_manager = DatabaseManager()
    db_manager.connect()
    db_manager.create_tables()

    # Example raw data loading
    with db_manager.cursor() as cursor:
        raw_data = pd.read_sql_query("SELECT * FROM raw_data_2024_04_03", db_manager.conn)
    db_manager.close()
    # Process and explode the 'products' column
    data_processor = DataProcessor(raw_data)
    processed_data = data_processor.explode_and_normalize_products()

    data_ingestor = DataIngestor(processed_data)
    data_ingestor.ingest()


if __name__ == "__main__":
    main()