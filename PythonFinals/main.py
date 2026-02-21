# main.py
"""
Main Application Entry Point
"""
import sys
import os
import traceback
from PyQt6.QtWidgets import QApplication

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check_utils_module():
    """Check if utils module is available"""
    try:
        # Try different import methods
        try:
            from utils import setup_logging
            return True
        except ImportError:
            # Try importing from utils.py directly
            import importlib.util
            spec = importlib.util.spec_from_file_location("utils", "utils.py")
            if spec is None:
                # Create basic utils if doesn't exist
                create_basic_utils()
                from utils import setup_logging
            return True
    except Exception as e:
        print(f"Error with utils module: {e}")
        return False


def create_basic_utils():
    """Create basic utils.py if it doesn't exist"""
    utils_content = '''
import logging

def setup_logging():
    """Setup basic logging"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
'''
    with open("utils.py", "w") as f:
        f.write(utils_content)
    print("Created basic utils.py file")


def main():
    """Main application function"""
    print("=" * 50)
    print("WorkXTrackr - Attendance Management System")
    print("=" * 50)

    # Check and fix utils
    if not check_utils_module():
        print("\n❌ Cannot setup logging.")
        input("Press Enter to exit...")
        sys.exit(1)

    from utils import setup_logging
    setup_logging()

    import mysql.connector
    import hashlib

    def check_and_fix_database():
        """Check and fix database issues on startup"""
        try:
            from config.settings import DB_CONFIG
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)

            print("🔍 Checking database...")

            cursor.execute("SELECT id, username, password FROM users LIMIT 5")
            users = cursor.fetchall()

            needs_hashing = False
            for user in users:
                password = user['password']
                if password and len(password) < 64:
                    needs_hashing = True
                    print(f"⚠️  User '{user['username']}' has plain text password")

            if needs_hashing:
                print("🔄 Hashing plain text passwords...")
                for user in users:
                    password = user['password']
                    if password and len(password) < 64:
                        hashed_password = hashlib.sha256(password.encode()).hexdigest()
                        cursor.execute(
                            "UPDATE users SET password = %s WHERE id = %s",
                            (hashed_password, user['id'])
                        )
                        print(f"   ✓ Hashed password for '{user['username']}'")
                conn.commit()
                print("✅ All passwords have been hashed!")
            else:
                print("✅ Passwords are already hashed")

            cursor.close()
            conn.close()
            return True
        except mysql.connector.Error as e:
            print(f"❌ Database connection failed: {e}")
            print("\nPlease check:")
            print("1. MySQL is running")
            print("2. Database 'workxtrackr' exists")
            print("3. Username/password in config/settings.py is correct")
            return False

    if not check_and_fix_database():
        print("\n❌ Cannot start application due to database issues.")
        input("Press Enter to exit...")
        sys.exit(1)

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("WorkXTrackr")
    app.setApplicationVersion("1.0.0")

    # Create and show main window
    try:
        from viewer.main_window import MainWindow
        window = MainWindow()
        window.setWindowTitle("WorkXTrackr - Attendance Management System")
        window.showMaximized()

        # Start application
        sys.exit(app.exec())

    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        traceback.print_exc()
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()