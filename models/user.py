# models/user.py - FIXED VERSION
"""
User Model
"""
from database.database import Database
import hashlib


class User:
    def __init__(self):
        self.db = Database()

    def authenticate(self, username, password):
        """Authenticate user with SHA256 hashing"""
        try:
            print(f"🔍 AUTHENTICATION ATTEMPT:")
            print(f"   Username: {username}")
            print(f"   Password entered: {password}")

            # Hash the entered password
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            print(f"   Hashed password: {hashed_password}")

            # Check what's actually in the database for this user
            check_query = "SELECT * FROM users WHERE username = %s"
            user_data = self.db.fetch_one(check_query, (username,))

            if user_data:
                print(f"📊 USER FOUND IN DATABASE:")
                print(f"   User ID: {user_data['id']}")
                print(f"   Username: {user_data['username']}")
                print(f"   Stored password: {user_data['password']}")
                print(f"   Role: {user_data['role']}")
                print(f"   Full name: {user_data['full_name']}")
                print(f"   Email: {user_data['email']}")

                # Compare hashes
                if hashed_password == user_data['password']:
                    print("✅ PASSWORD MATCHES!")
                    return {
                        'id': user_data['id'],
                        'username': user_data['username'],
                        'role': user_data['role'],
                        'full_name': user_data['full_name'],
                        'email': user_data['email']
                    }
                else:
                    print("❌ PASSWORD DOESN'T MATCH!")
                    print(f"   Expected: {user_data['password']}")
                    print(f"   Got: {hashed_password}")
                    return None
            else:
                print("❌ USER NOT FOUND IN DATABASE")
                return None

        except Exception as e:
            print(f"🔴 AUTHENTICATION ERROR: {e}")
            return None

    def create_user(self, username, password, email, full_name, role="staff"):
        """Create a new user with hashed password"""
        try:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            query = """
            INSERT INTO users (username, password, email, full_name, role)
            VALUES (%s, %s, %s, %s, %s)
            """
            return self.db.execute_query(query, (username, hashed_password, email, full_name, role))
        except Exception as e:
            print(f"Error creating user: {e}")
            return None

    def get_user_by_id(self, user_id):
        """Get user by ID"""
        try:
            query = "SELECT * FROM users WHERE id = %s"
            return self.db.fetch_one(query, (user_id,))
        except Exception as e:
            print(f"Error getting user: {e}")
            return None