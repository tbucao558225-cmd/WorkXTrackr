# controllers/auth.py
from models.user import User
import re


class AuthController:
    def __init__(self):
        self.user_model = User()


    def login(self, username, password):

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

