
import os

class Config:
    SECRET_KEY = os.urandom(24).hex()  # Genera una clave secreta aleatoria
    DB_HOST = 'localhost'
    DB_USER = 'root'
    DB_PASSWORD = '34880277'
    DB_NAME = 'myapp'

import mysql.connector

# Configuración de la conexión a MySQL (asegúrate de ajustar estos valores)
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '34880277',
}

# Crear la conexión y el cursor
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# Crear la base de datos myapp si no existe
cursor.execute("CREATE DATABASE IF NOT EXISTS myapp")

# Usar la base de datos myapp
cursor.execute("USE myapp")

# Crear la tabla usuarios si no existe
cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        avatar VARCHAR(255)
    )
""")

# Cerrar la conexión
conn.close()