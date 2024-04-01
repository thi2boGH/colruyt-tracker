from flask import Flask, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from flask_cors import CORS

app = Flask(__name__)

# Database connection parameters
DATABASE_URL = "dbname='colruyt_tracker' user='thibodebras' password='postgres' host='localhost' port='5432'"

# Establish a database connection
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

@app.route('/api/prices/evolution', methods=['GET'])
def get_price_evolution():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT p.ProductName, s.ShopName, pr.Price, pr.Date
        FROM price_test_2 pr
        JOIN product_test_2 p ON pr.ProductID = p.ProductID
        JOIN shop_test_2 s ON pr.ShopID = s.ShopID
        WHERE pr.Date >= current_date - interval '30 days' AND pr.productid = '192790' AND s.shopid ='459'
        ORDER BY pr.Date DESC;
    """)
    
    prices_evolution = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify(prices_evolution)

# CORS(app)
CORS(app, resources={r"/*": {"origins": "*"}})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
