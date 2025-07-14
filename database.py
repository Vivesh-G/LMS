import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('MYSQLHOST', 'localhost'),
    'user': os.getenv('MYSQLUSER', 'root'),
    'password': os.getenv('MYSQLPASSWORD', ''),
    'database': os.getenv('MYSQLDATABASE', 'snulms'),
    'port': int(os.getenv('MYSQLPORT', 3306))
}

def get_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        yield cursor
        conn.commit()
    finally:
        cursor.close()
        conn.close()
