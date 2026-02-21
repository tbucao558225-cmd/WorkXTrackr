#database/database.py

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
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.connection.cursor(dictionary=True)
            logging.info("Database connection established")

        except Error as e:
            logging.error(f"Error connecting to MySQL: {e}")
            raise

    def execute_query(self, query, params=None):
        """Execute a database query with debugging."""
        try:
            print(f"\n🔍 DATABASE.PY - EXECUTE_QUERY:")
            print(f"   Query: {query[:100]}..." if len(query) > 100 else f"   Query: {query}")
            print(f"   Params: {params}")

            # Check if cursor exists
            if not hasattr(self, 'cursor') or self.cursor is None:
                print("   ERROR: No database cursor in database.py!")
                return []

            self.cursor.execute(query, params or ())

            # Check if it's a SELECT query
            if query.strip().upper().startswith('SELECT'):
                result = self.cursor.fetchall()
                print(f"   Result: {len(result)} rows")
                if result and len(result) > 0:
                    print(f"   First row: {result[0]}")
                return result
            else:
                self.connection.commit()
                print(f"   Non-SELECT query executed successfully")
                return True

        except Exception as e:
            print(f"   DATABASE.PY QUERY ERROR: {e}")
            import traceback
            traceback.print_exc()
            return []

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