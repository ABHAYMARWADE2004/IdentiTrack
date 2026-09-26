# database.py
# Ye file MySQL database se connect karne aur data save karne ka kaam karti hai

import mysql.connector   # MySQL se connect karne wali library
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME   # config.py se settings le rahe hain

def get_connection():
    """MySQL database se connection banata hai"""
    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    return connection

def save_detection(person_name):
    """
    Jab bhi koi banda detect ho, uska naam database me save karo
    person_name: jis banda ka naam save karna hai
    """
    # "Unknown" ko save nahi karenge, sirf pehchane hue logo ko
    if person_name == "Unknown":
        return

    connection = get_connection()
    cursor = connection.cursor()

    # Naya record insert karo (detected_at automatic current time le lega)
    query = "INSERT INTO detections (person_name) VALUES (%s)"
    cursor.execute(query, (person_name,))

    connection.commit()   # Changes ko permanently save karo
    cursor.close()
    connection.close()

def get_all_detections():
    """Database se saare records nikalo (dashboard me use hoga baad me)"""
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT person_name, detected_at FROM detections ORDER BY detected_at DESC")
    results = cursor.fetchall()

    cursor.close()
    connection.close()
    return results

# Test karne ke liye - agar ye file directly run karo

def clear_all_detections():
    """Saare detection records delete kar deta hai (fresh start ke liye)"""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM detections")
    connection.commit()
    cursor.close()
    connection.close()
if __name__ == "__main__":
    print("Database connection test kar rahe hain...")
    try:
        conn = get_connection()
        print("✓ Connection successful!")
        conn.close()
    except Exception as e:
        print(f"✗ Connection failed: {e}")