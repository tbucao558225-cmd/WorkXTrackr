# controllers/staff.py

from models.attendance_data import Attendance
from datetime import datetime


class StaffController:
    def __init__(self, user_id):
        self.user_id = user_id
        self.attendance_model = Attendance()
        self.last_clock_in_id = None  # Track last clock in record

    def clock_in(self):
        try:
            print(f"\n🕒 CLOCK IN PROCESS for user {self.user_id}")
            result = self.attendance_model.clock_in(self.user_id)

            if result["success"]:
                self.last_clock_in_id = result["record_id"]
                return {
                    "success": True,
                    "status": result["status"],
                    "clock_in_time": result["clock_in_time"],
                    "record_id": result["record_id"],
                    "message": f"Clocked in at {result['clock_in_time'].strftime('%I:%M:%S %p')}"
                }
            else:
                return {"success": False, "message": "Failed to clock in"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def clock_out(self):
        try:
            print(f"\n🕒 CLOCK OUT PROCESS for user {self.user_id}")
            print(f"   Last clock in ID: {self.last_clock_in_id}")

            result = self.attendance_model.clock_out(self.user_id, self.last_clock_in_id)

            if result["success"]:
                return {
                    "success": True,
                    "clock_out_time": result["clock_out_time"],
                    "duration_hours": result["duration_hours"],
                    "message": f"Clocked out at {result['clock_out_time'].strftime('%I:%M:%S %p')}"
                }
            else:
                return {"success": False, "message": "No clock-in found without clock out"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def get_dashboard_data(self):
        try:
            print(f"\n📊 LOADING DASHBOARD DATA for user {self.user_id}")

            # Today's status
            today_status = self.attendance_model.get_today_status(self.user_id)

            # 30-day summary
            summary = self.attendance_model.get_attendance_summary(self.user_id, 30)

            return {
                "today_status": today_status or {},
                "summary": summary or {'present_days': 0, 'absent_days': 0, 'late_days': 0, 'overtime_days': 0}
            }
        except Exception as e:
            print(f"Error in get_dashboard_data: {e}")
            return {
                "today_status": {},
                "summary": {'present_days': 0, 'absent_days': 0, 'late_days': 0, 'overtime_days': 0}
            }

    def get_attendance_history(self):
        """Get attendance history"""
        print(f"\n📜 LOADING ATTENDANCE HISTORY for user {self.user_id}")
        return self.attendance_model.get_user_attendance(self.user_id, 50)