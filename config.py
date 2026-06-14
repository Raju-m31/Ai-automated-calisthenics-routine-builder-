"""
Database Configuration
Using SQLite for development (no installation needed)
Switch to MySQL by uncommenting the MySQL section below
"""

# SQLite Configuration (Default - No Installation Needed)
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "calibaf.db")}'

# MySQL Configuration (Uncomment to use MySQL)
# MYSQL_HOST = 'localhost'
# MYSQL_USER = 'root'
# MYSQL_PASSWORD = 'plancheman123'
# MYSQL_DATABASE = 'client_database'
# MYSQL_PORT = 3306
# SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}'

# Flask Configuration
DEBUG = True
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False  # Set to True for SQL query logging
