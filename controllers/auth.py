# controllers/auth.py - FIXED VERSION
"""
Authentication Controller
"""
from models.user import User
import re


class AuthController:
    def __init__(self):
        self.user_model = User()

    def login(self, username, password):
        """Handle login"""
        print(f"\n🎯 LOGIN ATTEMPT FROM UI:")
        print(f"   Username: {username}")
        print(f"   Password length: {len(password)} characters")

        if not username or not password:
            print("❌ Empty username or password")
            return {"success": False, "message": "Please enter username and password"}

        user = self.user_model.authenticate(username, password)

        if user:
            print(f"✅ LOGIN SUCCESS - User data: {user}")
            return {
                "success": True,
                "user": user
            }
        else:
            print("❌ LOGIN FAILED - Invalid credentials")
            return {"success": False, "message": "Invalid username or password"}

    def register(self, full_name, username, email, password, confirm_password):
        """Handle user registration"""
        # Validate inputs
        if not all([full_name, username, email, password, confirm_password]):
            return {"success": False, "message": "All fields are required"}

        if password != confirm_password:
            return {"success": False, "message": "Passwords do not match"}

        if len(password) < 6:
            return {"success": False, "message": "Password must be at least 6 characters"}

        # Validate email format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return {"success": False, "message": "Invalid email format"}

        try:
            # Create user
            user_id = self.user_model.create_user(username, password, email, full_name, "staff")

            if user_id:
                return {
                    "success": True,
                    "message": "Registration successful! Please login.",
                    "user_id": user_id
                }
            else:
                return {"success": False, "message": "Registration failed. Username may already exist."}
        except Exception as e:
            return {"success": False, "message": f"Registration failed: {str(e)}"}