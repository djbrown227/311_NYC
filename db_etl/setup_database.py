'''

import os
import time
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MySQL connection config from .env
CONFIG = {
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'host': os.getenv('MYSQL_HOST', '127.0.0.1'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'database': os.getenv('MYSQL_DATABASE'),
}

TABLE_NAME = '311_complaints_2'
VERBOSE = True

def log(message):
    if VERBOSE:
        print(message)

def create_database(cursor, db_name):
    log(f"Ensuring database '{db_name}' exists...")
    start = time.time()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
    log(f"Database check complete. Time taken: {time.time() - start:.2f} seconds.")

def create_table(cursor, table_name):
    log(f"Creating table '{table_name}' if it doesn't exist...")
    start = time.time()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            unique_key VARCHAR(50) PRIMARY KEY,
            created_date DATETIME,
            agency VARCHAR(255),
            agency_name VARCHAR(255),
            complaint_type VARCHAR(255),
            descriptor VARCHAR(255),
            location_type VARCHAR(255),
            incident_zip VARCHAR(50),
            incident_address VARCHAR(255),
            street_name VARCHAR(255),
            cross_street_1 VARCHAR(255),
            cross_street_2 VARCHAR(255),
            intersection_street_1 VARCHAR(255),
            intersection_street_2 VARCHAR(255),
            address_type VARCHAR(50),
            city VARCHAR(255),
            landmark VARCHAR(255),
            status VARCHAR(50),
            community_board VARCHAR(50),
            bbl VARCHAR(50),
            borough VARCHAR(50),
            x_coordinate_state_plane FLOAT,
            y_coordinate_state_plane FLOAT,
            open_data_channel_type VARCHAR(50),
            park_facility_name VARCHAR(255),
            park_borough VARCHAR(50),
            vehicle_type VARCHAR(50),
            latitude FLOAT,
            longitude FLOAT,
            location VARCHAR(255),
            computed_region_efsh_h5xi VARCHAR(50),
            computed_region_f5dn_yrer VARCHAR(50),
            computed_region_yeji_bk3q VARCHAR(50),
            computed_region_92fq_4b7q VARCHAR(50),
            computed_region_sbqj_enih VARCHAR(50),
            computed_region_7mpf_4k6g VARCHAR(50),
            resolution_action_updated_date DATETIME,
            resolution_description VARCHAR(255),
            closed_date DATETIME,
            bridge_highway_name VARCHAR(255),
            bridge_highway_segment VARCHAR(255),
            facility_type VARCHAR(255),
            bridge_highway_direction VARCHAR(50),
            road_ramp VARCHAR(50)
        )
    """)
    log(f"Table '{table_name}' creation complete. Time taken: {time.time() - start:.2f} seconds.")

def main():
    total_start = time.time()
    try:
        log("Connecting to MySQL server...")
        connection = mysql.connector.connect(
            host=CONFIG['host'],
            user=CONFIG['user'],
            port=CONFIG['port'],
            password=CONFIG['password']
        )

        if connection.is_connected():
            log(f"Connected to MySQL Server version {connection.get_server_info()}")
            cursor = connection.cursor()

            create_database(cursor, CONFIG['database'])
            connection.database = CONFIG['database']
            log(f"Using database '{CONFIG['database']}'")

            create_table(cursor, TABLE_NAME)

    except Error as e:
        log(f"Error: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            log("MySQL connection closed.")
        log(f"Total execution time: {time.time() - total_start:.2f} seconds.")

if __name__ == '__main__':
    main()

'''