# controllers/employee_controller.py
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
        return self.employee_model.get_all_employees()

    def search_employees(self, search_term):
        if not search_term or search_term.strip() == "":
            return self.get_all_employees()
        return self.employee_model.search_employees(search_term.strip())

    def get_employee_by_id(self, employee_id):
        return self.employee_model.get_employee_by_id(employee_id)

    def update_employee_status(self, employee_id, status):
        return self.employee_model.update_employee_status(employee_id, status)

    def add_employee(self, full_name, username, email, password, role="staff"):
        try:
            print(f"➕ Adding employee to users table: {full_name} (Role: {role})")
            user_id = self.user_model.create_user(
                username=username,
                password=password,
                email=email,
                full_name=full_name,
                role=role
            )

            if user_id:
                print(f"✅ Employee added to users table with ID: {user_id}, Role: {role}")
                return {
                    "success": True,
                    "user_id": user_id,
                    "message": f"Employee added successfully as {role}!"
                }

            return {"success": False, "message": "Failed to create user account"}

        except Exception as e:
            print(f"❌ Error adding employee: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}

    def update_employee(self, employee_id, full_name, username, email, role):
        try:
            result = self.employee_model.update_employee_full(employee_id, full_name, username, email, role)
            if result:
                return {"success": True, "message": "Employee updated successfully!"}
            return {"success": False, "message": "Failed to update employee"}
        except Exception as e:
            return {"success": False, "message": str(e)}