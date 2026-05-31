"""
Database Configuration
Update these values with your MySQL connection details
"""

# MySQL Configuration
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'plancheman123'  # MySQL password
MYSQL_DATABASE = 'client_database'
MYSQL_PORT = 3306

# Flask Configuration
DEBUG = True
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False  # Set to True for SQL query logging

# Database URI
SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}'
