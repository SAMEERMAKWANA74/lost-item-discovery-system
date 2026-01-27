import mysql.connector

def get_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",   # default XAMPP password is empty
            database="lost_recovery" # DOUBLE CHECK THIS NAME IN PHPMYADMIN
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None