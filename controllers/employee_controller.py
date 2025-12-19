# controllers/employee_controller.py - COMPLETE SIMPLE VERSION
"""
Employee Management Controller - SIMPLIFIED
"""
from models.employee_data import Employee
from models.user import User


class EmployeeController:
    def __init__(self):
        self.employee_model = Employee()
        self.user_model = User()

    def get_all_employees(self):
        """Get all employees"""
        return self.employee_model.get_all_employees()

    def search_employees(self, search_term):
        """Search employees"""
        if not search_term or search_term.strip() == "":
            return self.get_all_employees()
        return self.employee_model.search_employees(search_term.strip())

    def get_employee_by_id(self, employee_id):
        """Get employee by ID"""
        return self.employee_model.get_employee_by_id(employee_id)

    def update_employee_status(self, employee_id, status):
        """Update employee status"""
        return self.employee_model.update_employee_status(employee_id, status)

    def add_employee(self, full_name, username, email, password):
        """Add a new employee - JUST TO USERS TABLE"""
        try:
            print(f"➕ Adding employee to users table: {full_name}")

            # Just create user in users table
            user_id = self.user_model.create_user(
                username=username,
                password=password,
                email=email,
                full_name=full_name,
                role="staff"
            )

            if user_id:
                print(f"✅ Employee added to users table with ID: {user_id}")
                return {
                    "success": True,
                    "user_id": user_id,
                    "message": "Employee added successfully!"
                }

            return {"success": False, "message": "Failed to create user account"}

        except Exception as e:
            print(f"❌ Error adding employee: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}