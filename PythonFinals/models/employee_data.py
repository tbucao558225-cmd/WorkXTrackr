# models/employee_data.py - COMPLETE FIXED VERSION

from database.database import Database
from datetime import datetime  # ADD THIS IMPORT
import logging


class Employee:
    def __init__(self):
        self.db = Database()

    def get_all_employees(self):
        try:
            query = """
            SELECT 
                id,
                username,
                full_name,
                email,
                role,
                'active' as status
            FROM users 
            WHERE role IN ('staff', 'manager')  # ✅ ONLY STAFF AND MANAGERS (NO ADMIN)
            ORDER BY 
                CASE role 
                    WHEN 'manager' THEN 1
                    WHEN 'staff' THEN 2
                    ELSE 3
                END,
                id
            """

            employees = self.db.execute_query(query)
            print(f"✅ Found {len(employees)} employees in users table (staff and manager only)")
            return employees

        except Exception as e:
            logging.error(f"Error getting employees: {e}")
            print(f"❌ Error in get_all_employees: {e}")
            return []

    def search_employees(self, search_term):
        try:
            query = """
            SELECT 
                id,
                username,
                full_name,
                email,
                role,
                'active' as status
            FROM users 
            WHERE role IN ('staff', 'manager') AND (  # ✅ ONLY STAFF AND MANAGERS
                full_name LIKE %s 
                OR username LIKE %s 
                OR email LIKE %s
                OR CONCAT('EMP', id) LIKE %s
                OR role LIKE %s
            )
            ORDER BY 
                CASE role 
                    WHEN 'manager' THEN 1
                    WHEN 'staff' THEN 2
                    ELSE 3
                END,
                id
            """

            search_pattern = f"%{search_term}%"
            return self.db.execute_query(query, (
                search_pattern, search_pattern, search_pattern, search_pattern, search_pattern
            ))

        except Exception as e:
            logging.error(f"Error searching employees: {e}")
            return []

    def get_employee_by_id(self, employee_id):
        query = """
        SELECT 
            id,
            username,
            full_name,
            email,
            role
        FROM users 
        WHERE id = %s AND role IN ('staff', 'manager')  # ✅ ONLY STAFF AND MANAGERS
        """
        return self.db.fetch_one(query, (employee_id,))

    def get_employee_by_user_id(self, user_id):
        """Get employee by user ID FROM USERS TABLE"""
        query = """
        SELECT 
            id,
            username,
            full_name,
            email,
            role
        FROM users 
        WHERE id = %s AND role = 'staff'
        """
        return self.db.fetch_one(query, (user_id,))

    def get_dashboard_stats(self):
        try:
            today = datetime.now().date().strftime('%Y-%m-%d')

            # Get total employees
            total_query = "SELECT COUNT(*) as total FROM users WHERE role = 'staff'"
            total_result = self.db.fetch_one(total_query)
            total_employees = total_result['total'] if total_result else 0

            # Get present today (including late)
            present_query = """
            SELECT COUNT(DISTINCT a.user_id) as present_today
            FROM attendance a
            JOIN users u ON a.user_id = u.id
            WHERE DATE(a.date) = %s 
            AND (a.status = 'present' OR a.status = 'late')
            AND u.role = 'staff'
            """
            present_result = self.db.fetch_one(present_query, (today,))
            present_today = present_result['present_today'] if present_result else 0

            # Get late today
            late_query = """
            SELECT COUNT(DISTINCT a.user_id) as late_today
            FROM attendance a
            JOIN users u ON a.user_id = u.id
            WHERE DATE(a.date) = %s 
            AND a.status = 'late'
            AND u.role = 'staff'
            """
            late_result = self.db.fetch_one(late_query, (today,))
            late_today = late_result['late_today'] if late_result else 0

            # Calculate absent today
            absent_today = max(0, total_employees - present_today)

            # Get on leave today (approved leave requests for today)
            on_leave_query = """
            SELECT COUNT(DISTINCT r.user_id) as on_leave
            FROM requests r
            JOIN users u ON r.user_id = u.id
            WHERE u.role = 'staff'
            AND r.status = 'approved'
            AND r.request_type LIKE '%Leave%'
            AND DATE(r.request_date) = %s
            """
            on_leave_result = self.db.fetch_one(on_leave_query, (today,))
            on_leave = on_leave_result['on_leave'] if on_leave_result else 0

            return {
                'total_employees': total_employees,
                'present_today': present_today,
                'late_today': late_today,
                'absent_today': absent_today,
                'on_leave': on_leave
            }

        except Exception as e:
            print(f"Error getting dashboard stats: {e}")
            return {
                'total_employees': 0,
                'present_today': 0,
                'late_today': 0,
                'absent_today': 0,
                'on_leave': 0
            }

    def update_employee_full(self, employee_id, name, username, email, role):
        """SQL logic moved from View to Model"""
        query = """
        UPDATE users 
        SET full_name = %s, username = %s, email = %s, role = %s
        WHERE id = %s
        """
        return self.db.execute_query(query, (name, username, email, role, employee_id))