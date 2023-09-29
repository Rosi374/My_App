from flask import Flask
from config import Config
import mysql.connector

app = Flask(__name__)
app.config.from_object(Config)

db = mysql.connector.connect(
    host=app.config['DB_HOST'],
    user=app.config['DB_USER'],
    password=app.config['DB_PASSWORD'],
    database=app.config['DB_NAME']
)

from app import routes
