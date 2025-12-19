"""
Database Connection and Management
"""
import mysql.connector
from mysql.connector import Error
from config.settings import DB_CONFIG
import logging


class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_connection()
        return cls._instance

    def _init_connection(self):
        """Initialize database connection"""
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.connection.cursor(dictionary=True)
            logging.info("Database connection established")

        except Error as e:
            logging.error(f"Error connecting to MySQL: {e}")
            raise

    def execute_query(self, query, params=None):
        """Execute a SQL query"""
        try:
            self.cursor.execute(query, params or ())
            if query.strip().upper().startswith('SELECT'):
                return self.cursor.fetchall()
            self.connection.commit()
            return self.cursor.lastrowid
        except Error as e:
            logging.error(f"Error executing query: {e}")
            self.connection.rollback()
            raise

    def fetch_one(self, query, params=None):
        """Fetch single row"""
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchone()
        except Error as e:
            logging.error(f"Error fetching data: {e}")
            raise

    def close(self):
        """Close database connection"""
        if self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            logging.info("Database connection closed")