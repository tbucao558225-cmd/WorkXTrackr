# models/report_data.py

from database.database import Database
from datetime import datetime, timedelta, date
import logging

class ReportData:
    def __init__(self):
        self.db = Database()

    def get_daily_audit_report(self, target_date):
        query = """
            SELECT u.id as employee_id, u.full_name, u.email, a.status,
                   TIME_FORMAT(a.clock_in, '%h:%i %p') as clock_in,
                   TIME_FORMAT(a.clock_out, '%h:%i %p') as clock_out,
                   COALESCE(a.total_hours, 0) as hours_worked,
                   COALESCE(a.late_minutes, 0) as late_minutes
            FROM users u
            LEFT JOIN attendance a ON u.id = a.user_id AND DATE(a.date) = %s
            WHERE u.role = 'staff'
            ORDER BY u.full_name
        """
        return self.db.execute_query(query, (target_date,))

    def count_work_days(self, year, month, up_to_day=None):
        import calendar
        from datetime import date
        year, month = int(year), int(month)
        if up_to_day is None:
            up_to_day = calendar.monthrange(year, month)[1]

        work_days = 0
        for day in range(1, up_to_day + 1):
            if date(year, month, day).weekday() < 5:  # 0-4 is Mon-Fri
                work_days += 1
        return work_days

    def fetch_monthly_report_data(self, month, year):
        query = """
            SELECT u.id as employee_id, u.full_name,
                COUNT(CASE WHEN a.status = 'present' THEN 1 END) as present_days,
                COUNT(CASE WHEN a.status = 'late' THEN 1 END) as late_days,
                COALESCE(SUM(a.total_hours), 0) as total_hours_worked
            FROM users u
            LEFT JOIN attendance a ON u.id = a.user_id AND MONTH(a.date) = %s AND YEAR(a.date) = %s
            WHERE u.role = 'staff' 
            GROUP BY u.id, u.full_name
        """
        results = self.db.execute_query(query, (month, year))

        #monthly summary report calculation
        import calendar
        from datetime import date
        days_in_month = calendar.monthrange(int(year), int(month))[1]
        work_days_count = 0

        for day in range(1, days_in_month + 1):
            if date(int(year), int(month), day).weekday() < 5:
                work_days_count += 1


        for row in results:
            attended = int(row['present_days']) + int(row['late_days'])
            row['absent_days'] = max(0, work_days_count - attended)
            row['total_presence'] = attended

        return results

    def fetch_annual_report_data(self, year):
        from datetime import datetime
        current_date = datetime.now().date()
        current_year = current_date.year
        current_month = current_date.month

        query = """
            SELECT m.month_name, m.m_num,
                COUNT(CASE WHEN a.status = 'present' THEN 1 END) as present_days,
                COUNT(CASE WHEN a.status = 'late' THEN 1 END) as late_days,
                COALESCE(SUM(a.total_hours), 0) as total_hours_worked
            FROM (
                SELECT 'Jan' AS month_name, 1 AS m_num UNION SELECT 'Feb', 2 UNION 
                SELECT 'Mar', 3 UNION SELECT 'Apr', 4 UNION SELECT 'May', 5 UNION 
                SELECT 'Jun', 6 UNION SELECT 'Jul', 7 UNION SELECT 'Aug', 8 UNION 
                SELECT 'Sep', 9 UNION SELECT 'Oct', 10 UNION SELECT 'Nov', 11 UNION SELECT 'Dec', 12
            ) AS m
            LEFT JOIN attendance a ON MONTH(a.date) = m.m_num AND YEAR(a.date) = %s
            GROUP BY m.m_num ORDER BY m.m_num
        """
        results = self.db.execute_query(query, (year,))

        staff_res = self.db.fetch_one("SELECT COUNT(*) as c FROM users WHERE role='staff'")
        staff_count = staff_res['c'] if staff_res else 1

        #annual summary report calculation
        for row in results:
            m_num = int(row['m_num'])
            target_year = int(year)

            if target_year > current_year or (target_year == current_year and m_num > current_month):
                row['absent_days'] = 0
                row['total_presence'] = 0
            else:
                if target_year == current_year and m_num == current_month:
                    days = self.count_work_days(year, m_num, up_to_day=current_date.day)
                else:
                    days = self.count_work_days(year, m_num)

                total_capacity = staff_count * days
                on_time = int(row['present_days'])
                late = int(row['late_days'])

                row['absent_days'] = max(0, total_capacity - (on_time + late))
                row['total_presence'] = on_time + late

        return results

    def get_daily_stats(self, target_date):
        query = """
            SELECT 
                (SELECT COUNT(*) FROM users WHERE role = 'staff') as total,
                COUNT(CASE WHEN status IN ('present', 'late') THEN 1 END) as present,
                COUNT(CASE WHEN status = 'late' THEN 1 END) as late
            FROM attendance WHERE DATE(date) = %s
        """
        return self.db.fetch_one(query, (target_date,))
