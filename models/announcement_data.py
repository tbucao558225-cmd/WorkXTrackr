# models/announcement_data.py - UPDATED FOR YOUR TABLE STRUCTURE
"""
Announcement Model
"""
from database.database import Database
from datetime import datetime
import logging


class Announcement:
    def __init__(self):
        self.db = Database()

    def create_announcement(self, title, content):
        """Create a new announcement"""
        try:
            query = """
            INSERT INTO announcements (title, content, created_date)
            VALUES (%s, %s, NOW())
            """
            return self.db.execute_query(query, (title, content))
        except Exception as e:
            logging.error(f"Error creating announcement: {e}")
            return None

    def get_all_announcements(self, limit=50):
        """Get all announcements"""
        try:
            query = """
            SELECT 
                id,
                title,
                content,
                DATE_FORMAT(created_date, '%%Y-%%m-%%d %%H:%%i') as created_date
            FROM announcements 
            ORDER BY created_date DESC
            LIMIT %s
            """
            return self.db.execute_query(query, (limit,))
        except Exception as e:
            logging.error(f"Error getting announcements: {e}")
            return []

    def get_announcement_by_id(self, announcement_id):
        """Get announcement by ID"""
        try:
            query = """
            SELECT 
                id,
                title,
                content,
                DATE_FORMAT(created_date, '%%Y-%%m-%%d %%H:%%i') as created_date
            FROM announcements 
            WHERE id = %s
            """
            return self.db.fetch_one(query, (announcement_id,))
        except Exception as e:
            logging.error(f"Error getting announcement by ID: {e}")
            return None

    def update_announcement(self, announcement_id, title, content):
        """Update an announcement"""
        try:
            query = """
            UPDATE announcements 
            SET title = %s, content = %s
            WHERE id = %s
            """
            self.db.execute_query(query, (title, content, announcement_id))
            return True
        except Exception as e:
            logging.error(f"Error updating announcement: {e}")
            return False

    def delete_announcement(self, announcement_id):
        """Delete an announcement"""
        try:
            query = "DELETE FROM announcements WHERE id = %s"
            self.db.execute_query(query, (announcement_id,))
            return True
        except Exception as e:
            logging.error(f"Error deleting announcement: {e}")
            return False

    def get_recent_announcements(self, limit=5):
        """Get recent announcements for dashboard"""
        try:
            query = """
            SELECT 
                id,
                title,
                LEFT(content, 100) as preview,  -- Get first 100 chars as preview
                DATE_FORMAT(created_date, '%%b %%d, %%Y') as formatted_date
            FROM announcements 
            ORDER BY created_date DESC
            LIMIT %s
            """
            return self.db.execute_query(query, (limit,))
        except Exception as e:
            logging.error(f"Error getting recent announcements: {e}")
            return []