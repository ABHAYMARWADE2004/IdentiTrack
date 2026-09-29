# database.py
# Handles MySQL connection and data logging for detected persons

import mysql.connector
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

def get_connection():
    """Creates and returns a connection to the MySQL database"""
    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    return connection

def save_detection(person_name):
    """Logs a detected person's name into the database with a timestamp"""
    if person_name == "Unknown":
        return

    connection = get_connection()
    cursor = connection.cursor()

    query = "INSERT INTO detections (person_name) VALUES (%s)"
    cursor.execute(query, (person_name,))

    connection.commit()
    cursor.close()
    connection.close()

def get_all_detections():
    """Fetches all detection records from the database (used by the dashboard)"""
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT person_name, detected_at FROM detections ORDER BY detected_at DESC")
    results = cursor.fetchall()

    cursor.close()
    connection.close()
    return results

def clear_all_detections():
    """Deletes all detection records (used for a fresh start)"""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM detections")
    connection.commit()
    cursor.close()
    connection.close()

if __name__ == "__main__":
    print("Testing database connection...")
    try:
        conn = get_connection()
        print("Connection successful!")
        conn.close()
    except Exception as e:
        print(f"Connection failed: {e}")