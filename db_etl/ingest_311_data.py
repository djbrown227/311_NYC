'''
import requests
import mysql.connector
from mysql.connector import pooling
import json
import time
import logging
from datetime import datetime
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

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# DB connection pool
try:
    cnxpool = pooling.MySQLConnectionPool(
        pool_name="mypool",
        pool_size=5,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        database=MYSQL_DATABASE
    )
    logging.info("✅ Database connection pool created successfully.")
except mysql.connector.Error as err:
    logging.error(f"❌ Database connection failed: {err}")
    exit(1)

def fetch_data(offset=0, limit=1000):
    url = (
        "https://data.cityofnewyork.us/resource/erm2-nwe9.json?"
        f"$limit={limit}&$offset={offset}&$order=created_date"
        f"&$where=created_date between '2024-01-01T00:00:00' and '2024-12-31T23:59:59'"
    )
    headers = {"X-App-Token": APP_TOKEN}
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            logging.info(f"📦 Fetched batch at offset {offset}")
            return response.json()
        else:
            logging.error(f"❌ Failed API request: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        logging.error(f"❌ Request error: {e}")
        return []

def is_within_date_range(record):
    try:
        date = datetime.strptime(record['created_date'][:10], "%Y-%m-%d")
        return datetime(2024, 1, 1) <= date <= datetime(2024, 12, 31)
    except Exception as e:
        logging.warning(f"⚠️ Failed to parse date: {e}")
        return False

def flatten_record(record):
    try:
        human_address_str = record.get('location', {}).get('human_address', '')
        human_address = json.loads(human_address_str) if human_address_str else {}
    except Exception:
        human_address = {}

    return {
        'unique_key': record.get('unique_key'),
        'created_date': record.get('created_date'),
        'closed_date': record.get('closed_date'),
        'agency': record.get('agency'),
        'agency_name': record.get('agency_name'),
        'complaint_type': record.get('complaint_type'),
        'descriptor': record.get('descriptor'),
        'location_type': record.get('location_type'),
        'incident_zip': record.get('incident_zip'),
        'incident_address': record.get('incident_address'),
        'street_name': record.get('street_name'),
        'cross_street_1': record.get('cross_street_1'),
        'cross_street_2': record.get('cross_street_2'),
        'address_type': record.get('address_type'),
        'city': record.get('city'),
        'facility_type': record.get('facility_type'),
        'status': record.get('status'),
        'resolution_description': record.get('resolution_description'),
        'resolution_action_updated_date': record.get('resolution_action_updated_date'),
        'community_board': record.get('community_board'),
        'bbl': record.get('bbl'),
        'borough': record.get('borough'),
        'x_coordinate_state_plane': float(record.get('x_coordinate_state_plane')) if record.get('x_coordinate_state_plane') else None,
        'y_coordinate_state_plane': float(record.get('y_coordinate_state_plane')) if record.get('y_coordinate_state_plane') else None,
        'open_data_channel_type': record.get('open_data_channel_type'),
        'park_facility_name': record.get('park_facility_name'),
        'park_borough': record.get('park_borough'),
        'vehicle_type': record.get('vehicle_type'),
        'latitude': float(record.get('latitude')) if record.get('latitude') else None,
        'longitude': float(record.get('longitude')) if record.get('longitude') else None,
        'location': json.dumps(record.get('location')) if record.get('location') else None,
        'computed_region_efsh_h5xi': record.get('computed_region_efsh_h5xi'),
        'computed_region_f5dn_yrer': record.get('computed_region_f5dn_yrer'),
        'computed_region_yeji_bk3q': record.get('computed_region_yeji_bk3q'),
        'computed_region_92fq_4b7q': record.get('computed_region_92fq_4b7q'),
        'computed_region_sbqj_enih': record.get('computed_region_sbqj_enih'),
        'computed_region_7mpf_4k6g': record.get('computed_region_7mpf_4k6g'),
        'bridge_highway_name': record.get('bridge_highway_name'),
        'bridge_highway_segment': record.get('bridge_highway_segment'),
        'bridge_highway_direction': record.get('bridge_highway_direction'),
        'road_ramp': record.get('road_ramp')
    }


def insert_records(records):
    if not records:
        logging.info("⚠️ No records to insert.")
        return

    try:
        conn = cnxpool.get_connection()
        cursor = conn.cursor()

        insert_query = f"""
        INSERT INTO {TABLE_NAME} (
            unique_key, created_date, closed_date, agency, agency_name, complaint_type, descriptor, 
            location_type, incident_zip, incident_address, street_name, cross_street_1, cross_street_2, 
            address_type, city, facility_type, status, resolution_description, 
            resolution_action_updated_date, community_board, bbl, borough, x_coordinate_state_plane, 
            y_coordinate_state_plane, open_data_channel_type, park_facility_name, park_borough, 
            vehicle_type, latitude, longitude, location, computed_region_efsh_h5xi, computed_region_f5dn_yrer, 
            computed_region_yeji_bk3q, computed_region_92fq_4b7q, computed_region_sbqj_enih, computed_region_7mpf_4k6g,
            bridge_highway_name, bridge_highway_segment, bridge_highway_direction, road_ramp
        ) VALUES (
            %(unique_key)s, %(created_date)s, %(closed_date)s, %(agency)s, %(agency_name)s, %(complaint_type)s, 
            %(descriptor)s, %(location_type)s, %(incident_zip)s, %(incident_address)s, %(street_name)s, 
            %(cross_street_1)s, %(cross_street_2)s, %(address_type)s, %(city)s, %(facility_type)s, %(status)s, %(resolution_description)s, %(resolution_action_updated_date)s, %(community_board)s, 
            %(bbl)s, %(borough)s, %(x_coordinate_state_plane)s, %(y_coordinate_state_plane)s, %(open_data_channel_type)s, 
            %(park_facility_name)s, %(park_borough)s, %(vehicle_type)s, %(latitude)s, %(longitude)s, %(location)s, %(computed_region_efsh_h5xi)s, %(computed_region_f5dn_yrer)s, 
            %(computed_region_yeji_bk3q)s, %(computed_region_92fq_4b7q)s, %(computed_region_sbqj_enih)s, %(computed_region_7mpf_4k6g)s,
            %(bridge_highway_name)s, %(bridge_highway_segment)s, %(bridge_highway_direction)s, %(road_ramp)s
        )
        ON DUPLICATE KEY UPDATE
            closed_date=VALUES(closed_date),
            status=VALUES(status),
            resolution_description=VALUES(resolution_description),
            resolution_action_updated_date=VALUES(resolution_action_updated_date)
        """

        cursor.executemany(insert_query, records)
        conn.commit()
        logging.info(f"✅ Inserted/Updated {cursor.rowcount} rows.")
    except mysql.connector.Error as err:
        logging.error(f"❌ Insert failed: {err}")
    finally:
        cursor.close()
        conn.close()

def main():
    offset = 654000
    limit = 1000
    max_empty_fetches = 5
    empty_fetch_count = 0

    while True:
        logging.info(f"📤 Fetching from offset {offset}")
        data = fetch_data(offset, limit)

        if not data:
            empty_fetch_count += 1
            logging.warning(f"⚠️ Empty fetch count: {empty_fetch_count}")
            if empty_fetch_count >= max_empty_fetches:
                logging.info("🛑 Too many empty results. Stopping.")
                break
            offset += limit
            continue

        filtered = [flatten_record(r) for r in data if is_within_date_range(r)]
        logging.info(f"🧹 Filtered {len(filtered)} records within date range.")
        insert_records(filtered)

        # Stop if all records are outside the range
        if all(not is_within_date_range(r) for r in data):
            logging.info("📅 All records are out of date range. Stopping.")
            break

        offset += limit
        time.sleep(1)

if __name__ == "__main__":
    logging.info("🚀 Starting 311 scraper.")
    main()
    
'''