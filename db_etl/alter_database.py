'''
import mysql.connector
from mysql.connector import pooling

from dotenv import load_dotenv
import os

load_dotenv()  # loads environment variables from .env file in your project root

# Database connection info - load from environment variables
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_PORT = os.getenv('MYSQL_PORT')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
TABLE_NAME = '311_complaints_2'

# Connect to the DB (you can use your existing pool or create a new connection)
try:
    cnx = mysql.connector.connect(
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        database=MYSQL_DATABASE
    )
    cursor = cnx.cursor()
    print("✅ Connected to the database")
except mysql.connector.Error as err:
    print(f"❌ Connection error: {err}")

# The ALTER TABLE query to change resolution_description column to TEXT
alter_query = f"""
ALTER TABLE {TABLE_NAME}
MODIFY COLUMN resolution_description TEXT;
"""

try:
    cursor.execute(alter_query)
    cnx.commit()
    print(f"✅ Column 'resolution_description' altered to TEXT")
except mysql.connector.Error as err:
    print(f"❌ Error executing query: {err}")
finally:
    cursor.close()
    cnx.close()
'''