# controllers/report_controller.py
"""
Report Controller
"""
from models.report_data import ReportData
from datetime import datetime, timedelta


class ReportController:
    def __init__(self):
        self.report_model = ReportData()

    def generate_report(self, report_type, start_date, end_date, employee_id=None, format='pdf'):
        """Generate report based on parameters"""
        try:
            print(f"📊 Generating {report_type} report from {start_date} to {end_date}")

            # Get report data
            if report_type == 'attendance_daily':
                report_data = self.report_model.get_daily_attendance_report(start_date, end_date, employee_id)
                report_title = "Daily Attendance Report"
            elif report_type == 'attendance_summary':
                report_data = self.report_model.get_summary_report(start_date, end_date, employee_id)
                report_title = "Attendance Summary Report"
            elif report_type == 'attendance_detailed':
                report_data = self.report_model.get_detailed_attendance_report(start_date, end_date, employee_id)
                report_title = "Detailed Attendance Report"
            elif report_type == 'employee':
                report_data = self.report_model.get_employee_report(start_date, end_date, employee_id)
                report_title = "Employee Report"
            elif report_type == 'leave':
                report_data = self.report_model.get_leave_report(start_date, end_date)
                report_title = "Leave Report"
            elif report_type == 'late':
                report_data = self.report_model.get_late_report(start_date, end_date)
                report_title = "Late Attendance Report"
            elif report_type == 'overtime':
                report_data = self.report_model.get_overtime_report(start_date, end_date)
                report_title = "Overtime Report"
            else:
                return {"success": False, "message": "Invalid report type"}

            # Get report statistics
            report_stats = self.report_model.get_report_statistics(start_date, end_date)

            # Get employee name if filtering by employee
            employee_name = None
            if employee_id:
                employees = self.report_model.get_all_employees_for_filter()
                for emp in employees:
                    if str(emp['id']) == str(employee_id):
                        employee_name = emp['full_name']
                        break

            return {
                "success": True,
                "report_type": report_type,
                "report_title": report_title,
                "start_date": start_date,
                "end_date": end_date,
                "employee_name": employee_name,
                "data": report_data,
                "statistics": report_stats,
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

        except Exception as e:
            return {"success": False, "message": f"Error generating report: {str(e)}"}

    def get_available_employees(self):
        """Get list of all employees for filters"""
        return self.report_model.get_all_employees_for_filter()

    def get_default_date_range(self):
        """Get default date range (last 30 days)"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        return {
            'start_date': start_date.strftime("%Y-%m-%d"),
            'end_date': end_date.strftime("%Y-%m-%d")
        }

    def get_report_types(self):
        """Get available report types"""
        return [
            {'id': 'attendance_daily', 'name': 'Daily Attendance', 'description': 'Daily attendance overview'},
            {'id': 'attendance_summary', 'name': 'Attendance Summary', 'description': 'Summary by employee'},
            {'id': 'attendance_detailed', 'name': 'Detailed Attendance', 'description': 'Detailed daily records'},
            {'id': 'employee', 'name': 'Employee Report', 'description': 'Individual employee report'},
            {'id': 'leave', 'name': 'Leave Report', 'description': 'Leave requests and approvals'},
            {'id': 'late', 'name': 'Late Report', 'description': 'Late attendance analysis'},
            {'id': 'overtime', 'name': 'Overtime Report', 'description': 'Overtime hours report'}
        ]