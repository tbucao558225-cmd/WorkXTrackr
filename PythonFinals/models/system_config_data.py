#models/system_config_data.py
from database.database import Database
import logging


class SystemConfig:
    def __init__(self):
        self.db = Database()

    def get_work_time_settings(self):
        try:
            query = "SELECT * FROM system_config WHERE config_type = 'work_time' ORDER BY id DESC LIMIT 1"
            result = self.db.fetch_one(query)
            return result
        except Exception as e:
            logging.error(f"Error getting work time settings: {e}")
            return None

    def save_work_time_settings(self, work_start, work_end, grace_period, overtime_threshold):
        try:
            # Check if record exists
            existing = self.get_work_time_settings()

            if existing:
                # Update existing record
                query = """
                UPDATE system_config 
                SET work_start_time = %s, 
                    work_end_time = %s, 
                    grace_period_minutes = %s,
                    overtime_threshold_hours = %s,
                    updated_at = NOW()
                WHERE config_type = 'work_time'
                ORDER BY id DESC LIMIT 1
                """
                self.db.execute_query(query, (work_start, work_end, grace_period, overtime_threshold))
                print(f"✅ Updated work time settings")
                return True
            else:
                # Insert new record
                query = """
                INSERT INTO system_config 
                (config_type, work_start_time, work_end_time, grace_period_minutes, overtime_threshold_hours)
                VALUES (%s, %s, %s, %s, %s)
                """
                self.db.execute_query(query, ('work_time', work_start, work_end, grace_period, overtime_threshold))
                print(f"✅ Created new work time settings")
                return True

        except Exception as e:
            logging.error(f"Error saving work time settings: {e}")
            print(f"❌ Error saving settings: {e}")
            return False
