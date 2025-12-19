# models/report_data.py
"""
Report Data Model
"""
from database.database import Database
from datetime import datetime, timedelta, date
import logging


class ReportData:
    def __init__(self):
        self.db = Database()

    def get_attendance_report(self, start_date, end_date, employee_id=None, report_type='daily'):
        """Get attendance report data"""
        try:
            # Convert string dates to datetime objects
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

            if report_type == 'daily':
                return self.get_daily_attendance_report(start_date, end_date, employee_id)
            elif report_type == 'summary':
                return self.get_summary_report(start_date, end_date, employee_id)
            elif report_type == 'employee':
                return self.get_employee_report(start_date, end_date, employee_id)
            else:
                return self.get_detailed_attendance_report(start_date, end_date, employee_id)

        except Exception as e:
            logging.error(f"Error getting attendance report: {e}")
            return []

    def get_daily_attendance_report(self, start_date, end_date, employee_id=None):
        """Get daily attendance report"""
        try:
            base_query = """
            SELECT 
                DATE(a.date) as report_date,
                DAYNAME(a.date) as day_name,
                COUNT(DISTINCT a.user_id) as total_employees,
                COUNT(DISTINCT CASE WHEN a.status = 'present' THEN a.user_id END) as present_count,
                COUNT(DISTINCT CASE WHEN a.status = 'late' THEN a.user_id END) as late_count,
                COUNT(DISTINCT CASE WHEN a.status = 'absent' THEN a.user_id END) as absent_count,
                ROUND(AVG(a.total_hours), 2) as avg_hours_worked,
                ROUND(AVG(a.overtime_minutes) / 60, 2) as avg_overtime_hours
            FROM attendance a
            JOIN users u ON a.user_id = u.id
            WHERE u.role = 'staff'
            """

            params = []

            # Add date filter
            base_query += " AND DATE(a.date) BETWEEN %s AND %s"
            params.extend([start_date, end_date])

            # Add employee filter if specified
            if employee_id:
                base_query += " AND a.user_id = %s"
                params.append(employee_id)

            # Group by date
            base_query += """
            GROUP BY DATE(a.date)
            ORDER BY a.date
            """

            results = self.db.execute_query(base_query, params)

            # Calculate percentages
            for result in results:
                total = result['total_employees']
                if total > 0:
                    result['present_percentage'] = round((result['present_count'] / total) * 100, 1)
                    result['late_percentage'] = round((result['late_count'] / total) * 100, 1)
                    result['absent_percentage'] = round((result['absent_count'] / total) * 100, 1)
                else:
                    result['present_percentage'] = 0
                    result['late_percentage'] = 0
                    result['absent_percentage'] = 0

            return results

        except Exception as e:
            logging.error(f"Error getting daily attendance report: {e}")
            return []

    def get_summary_report(self, start_date, end_date, employee_id=None):
        """Get summary report"""
        try:
            base_query = """
            SELECT 
                u.id as user_id,
                u.full_name,
                u.username,
                u.email,
                COUNT(DISTINCT DATE(a.date)) as days_recorded,
                COUNT(DISTINCT CASE WHEN a.status = 'present' THEN DATE(a.date) END) as present_days,
                COUNT(DISTINCT CASE WHEN a.status = 'late' THEN DATE(a.date) END) as late_days,
                COUNT(DISTINCT CASE WHEN a.status = 'absent' THEN DATE(a.date) END) as absent_days,
                ROUND(SUM(a.total_hours), 2) as total_hours_worked,
                ROUND(SUM(a.overtime_minutes) / 60, 2) as total_overtime_hours,
                ROUND(AVG(a.total_hours), 2) as avg_daily_hours,
                ROUND(AVG(a.late_minutes), 1) as avg_late_minutes
            FROM users u
            LEFT JOIN attendance a ON u.id = a.user_id AND DATE(a.date) BETWEEN %s AND %s
            WHERE u.role = 'staff'
            """

            params = [start_date, end_date]

            # Add employee filter if specified
            if employee_id:
                base_query += " AND u.id = %s"
                params.append(employee_id)

            # Group by employee
            base_query += """
            GROUP BY u.id, u.full_name, u.username, u.email
            ORDER BY u.full_name
            """

            results = self.db.execute_query(base_query, params)

            # Calculate percentages
            for result in results:
                days = result['days_recorded']
                if days > 0:
                    result['attendance_rate'] = round(
                        ((result['present_days'] + result['late_days']) / days) * 100, 1
                    )
                    result['punctuality_rate'] = round(
                        (result['present_days'] / (result['present_days'] + result['late_days'])) * 100, 1
                    ) if (result['present_days'] + result['late_days']) > 0 else 0
                else:
                    result['attendance_rate'] = 0
                    result['punctuality_rate'] = 0

            return results

        except Exception as e:
            logging.error(f"Error getting summary report: {e}")
            return []

    def get_employee_report(self, start_date, end_date, employee_id=None):
        """Get detailed employee report"""
        try:
            base_query = """
            SELECT 
                u.id as user_id,
                u.full_name,
                DATE(a.date) as attendance_date,
                DAYNAME(a.date) as day_name,
                a.status,
                DATE_FORMAT(a.clock_in, '%%h:%%i %%p') as clock_in_time,
                DATE_FORMAT(a.clock_out, '%%h:%%i %%p') as clock_out_time,
                a.total_hours,
                a.late_minutes,
                a.overtime_minutes,
                CASE 
                    WHEN a.late_minutes > 0 THEN CONCAT('Late by ', a.late_minutes, ' minutes')
                    WHEN a.overtime_minutes > 0 THEN CONCAT('Overtime: ', a.overtime_minutes, ' minutes')
                    ELSE 'On Time'
                END as remarks
            FROM attendance a
            JOIN users u ON a.user_id = u.id
            WHERE u.role = 'staff'
            AND DATE(a.date) BETWEEN %s AND %s
            """

            params = [start_date, end_date]

            # Add employee filter if specified
            if employee_id:
                base_query += " AND u.id = %s"
                params.append(employee_id)

            base_query += " ORDER BY u.full_name, a.date DESC"

            return self.db.execute_query(base_query, params)

        except Exception as e:
            logging.error(f"Error getting employee report: {e}")
            return []

    def get_detailed_attendance_report(self, start_date, end_date, employee_id=None):
        """Get detailed attendance report"""
        try:
            base_query = """
            SELECT 
                DATE(a.date) as date,
                u.full_name,
                u.username,
                a.status,
                DATE_FORMAT(a.clock_in, '%%h:%%i %%p') as clock_in,
                DATE_FORMAT(a.clock_out, '%%h:%%i %%p') as clock_out,
                a.total_hours,
                a.late_minutes,
                a.overtime_minutes,
                CASE 
                    WHEN a.late_minutes > 0 THEN 'Late'
                    WHEN a.overtime_minutes > 0 THEN 'Overtime'
                    WHEN a.status = 'absent' THEN 'Absent'
                    ELSE 'Normal'
                END as work_status
            FROM attendance a
            JOIN users u ON a.user_id = u.id
            WHERE u.role = 'staff'
            AND DATE(a.date) BETWEEN %s AND %s
            """

            params = [start_date, end_date]

            # Add employee filter if specified
            if employee_id:
                base_query += " AND a.user_id = %s"
                params.append(employee_id)

            base_query += " ORDER BY a.date DESC, u.full_name"

            return self.db.execute_query(base_query, params)

        except Exception as e:
            logging.error(f"Error getting detailed attendance report: {e}")
            return []

    def get_leave_report(self, start_date, end_date):
        """Get leave report"""
        try:
            query = """
            SELECT 
                u.full_name,
                u.username,
                r.request_type as leave_type,
                r.request_date,
                r.status,
                r.reason,
                r.created_at as requested_date
            FROM requests r
            JOIN users u ON r.user_id = u.id
            WHERE u.role = 'staff'
            AND r.request_type LIKE '%Leave%'
            AND r.request_date BETWEEN %s AND %s
            ORDER BY r.request_date DESC, u.full_name
            """
            return self.db.execute_query(query, (start_date, end_date))
        except Exception as e:
            logging.error(f"Error getting leave report: {e}")
            return []

    def get_late_report(self, start_date, end_date):
        """Get late attendance report"""
        try:
            query = """
            SELECT 
                u.full_name,
                u.username,
                DATE(a.date) as date,
                a.late_minutes,
                DATE_FORMAT(a.clock_in, '%%h:%%i %%p') as clock_in_time,
                CASE 
                    WHEN a.late_minutes <= 15 THEN 'Minor'
                    WHEN a.late_minutes <= 30 THEN 'Moderate'
                    ELSE 'Severe'
                END as late_severity
            FROM attendance a
            JOIN users u ON a.user_id = u.id
            WHERE u.role = 'staff'
            AND a.status = 'late'
            AND DATE(a.date) BETWEEN %s AND %s
            ORDER BY a.late_minutes DESC, a.date DESC
            """
            return self.db.execute_query(query, (start_date, end_date))
        except Exception as e:
            logging.error(f"Error getting late report: {e}")
            return []

    def get_overtime_report(self, start_date, end_date):
        """Get overtime report"""
        try:
            query = """
            SELECT 
                u.full_name,
                u.username,
                DATE(a.date) as date,
                a.overtime_minutes,
                ROUND(a.overtime_minutes / 60, 2) as overtime_hours,
                DATE_FORMAT(a.clock_out, '%%h:%%i %%p') as clock_out_time
            FROM attendance a
            JOIN users u ON a.user_id = u.id
            WHERE u.role = 'staff'
            AND a.overtime_minutes > 0
            AND DATE(a.date) BETWEEN %s AND %s
            ORDER BY a.overtime_minutes DESC, a.date DESC
            """
            return self.db.execute_query(query, (start_date, end_date))
        except Exception as e:
            logging.error(f"Error getting overtime report: {e}")
            return []

    def get_report_statistics(self, start_date, end_date):
        """Get overall statistics for the report period"""
        try:
            # Get total employees
            total_query = """
            SELECT COUNT(*) as total_employees 
            FROM users 
            WHERE role = 'staff'
            """
            total_result = self.db.fetch_one(total_query)
            total_employees = total_result['total_employees'] if total_result else 0

            # Get attendance stats
            attendance_query = """
            SELECT 
                COUNT(DISTINCT a.user_id) as employees_with_records,
                COUNT(DISTINCT DATE(a.date)) as total_days,
                COUNT(DISTINCT CASE WHEN a.status IN ('present', 'late') THEN CONCAT(a.user_id, '-', DATE(a.date)) END) as present_days,
                COUNT(DISTINCT CASE WHEN a.status = 'late' THEN CONCAT(a.user_id, '-', DATE(a.date)) END) as late_days,
                COUNT(DISTINCT CASE WHEN a.status = 'absent' THEN CONCAT(a.user_id, '-', DATE(a.date)) END) as absent_days,
                ROUND(SUM(a.total_hours), 2) as total_hours_worked,
                ROUND(SUM(a.overtime_minutes) / 60, 2) as total_overtime_hours
            FROM attendance a
            JOIN users u ON a.user_id = u.id
            WHERE u.role = 'staff'
            AND DATE(a.date) BETWEEN %s AND %s
            """
            attendance_stats = self.db.fetch_one(attendance_query, (start_date, end_date))

            # Get leave stats
            leave_query = """
            SELECT 
                COUNT(*) as total_leaves,
                COUNT(CASE WHEN status = 'approved' THEN 1 END) as approved_leaves,
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_leaves,
                COUNT(CASE WHEN status = 'declined' THEN 1 END) as declined_leaves
            FROM requests r
            JOIN users u ON r.user_id = u.id
            WHERE u.role = 'staff'
            AND r.request_type LIKE '%Leave%'
            AND r.request_date BETWEEN %s AND %s
            """
            leave_stats = self.db.fetch_one(leave_query, (start_date, end_date))

            # Calculate percentages
            total_possible_days = total_employees * max(1, (end_date - start_date).days + 1)

            if attendance_stats:
                attendance_stats['attendance_percentage'] = round(
                    (attendance_stats['present_days'] / total_possible_days) * 100, 1
                ) if total_possible_days > 0 else 0

                attendance_stats['late_percentage'] = round(
                    (attendance_stats['late_days'] / attendance_stats['present_days']) * 100, 1
                ) if attendance_stats['present_days'] > 0 else 0

            return {
                'total_employees': total_employees,
                'attendance_stats': attendance_stats or {},
                'leave_stats': leave_stats or {}
            }

        except Exception as e:
            logging.error(f"Error getting report statistics: {e}")
            return {
                'total_employees': 0,
                'attendance_stats': {},
                'leave_stats': {}
            }

    def get_all_employees_for_filter(self):
        """Get all employees for filter dropdown"""
        try:
            query = """
            SELECT id, full_name, username 
            FROM users 
            WHERE role = 'staff'
            ORDER BY full_name
            """
            return self.db.execute_query(query)
        except Exception as e:
            logging.error(f"Error getting employees for filter: {e}")
            return []