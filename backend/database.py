# database.py
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()  # Carga variables del .env

def get_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "mysql_db"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "root_password"),
            database=os.getenv("DB_NAME", "my_database")
        )
        return connection
    except Error as e:
        print("Error al conectar a MySQL:", e)
        return None

