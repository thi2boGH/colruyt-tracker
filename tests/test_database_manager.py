import unittest
from unittest.mock import patch, MagicMock
import scrapper.database_manager as dm

class TestDatabaseManager(unittest.TestCase):

    @patch('psycopg2.connect') # patch replace the .connect form database_manager with a mock object
    def test_connect(self, mock_connect):
        db_manager = dm.DatabaseManager('dbname', 'user', 'password', 'host')
        db_manager.connect()
        mock_connect.assert_called_with(dbname='dbname', user='user', password='password', host='host')

    @patch('psycopg2.connect')
    def test_insert_data(self, mock_connect):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur

        db_manager = dm.DatabaseManager('dbname', 'user', 'password', 'host')
        db_manager.connect()
        db_manager.insert_data('table_name', 'shop_id', 1, {}, 'run_date')

        mock_cur.execute.assert_called()
        mock_conn.commit.assert_called()

if __name__ == '__main__':
    unittest.main()
