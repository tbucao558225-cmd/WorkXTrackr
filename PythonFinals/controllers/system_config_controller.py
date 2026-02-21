#controllers/system_config_controller.py

from models.system_config_data import SystemConfig
from models.announcement_data import Announcement


class SystemConfigController:
    def __init__(self):
        self.system_config_model = SystemConfig()
        self.announcement_model = Announcement()

    def get_work_time_settings(self):
        """Get work time settings"""
        try:
            settings = self.system_config_model.get_work_time_settings()

            if settings:
                return {
                    "success": True,
                    "work_start_time": settings.get('work_start_time', '09:00:00'),
                    "work_end_time": settings.get('work_end_time', '17:00:00'),
                    "grace_period": settings.get('grace_period_minutes', 15),
                    "overtime_threshold": settings.get('overtime_threshold_hours', 8)
                }
            else:
                return {
                    "success": True,
                    "work_start_time": '09:00:00',
                    "work_end_time": '17:00:00',
                    "grace_period": 15,
                    "overtime_threshold": 8
                }
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def save_work_time_settings(self, work_start, work_end, grace_period, overtime_threshold):
        """Save work time settings"""
        try:
            # Validate inputs
            if not work_start or not work_end:
                return {"success": False, "message": "Work start and end times are required"}

            if grace_period < 0 or grace_period > 60:
                return {"success": False, "message": "Grace period must be between 0 and 60 minutes"}

            if overtime_threshold < 1 or overtime_threshold > 12:
                return {"success": False, "message": "Overtime threshold must be between 1 and 12 hours"}

            # Save to database
            success = self.system_config_model.save_work_time_settings(
                work_start, work_end, grace_period, overtime_threshold
            )

            if success:
                return {
                    "success": True,
                    "message": "Work time settings saved successfully!"
                }
            else:
                return {"success": False, "message": "Failed to save settings"}

        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
