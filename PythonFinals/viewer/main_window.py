# main_window.py - UPDATED VERSION WITH ALL FIXES

import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt6.QtWidgets import (QMainWindow, QApplication, QMessageBox, QTableWidget,
                             QTableWidgetItem, QLabel, QHeaderView, QVBoxLayout, QWidget, QFrame, QAbstractItemView)
from PyQt6.QtCore import Qt, QTimer, QStringListModel
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QColor, QBrush
from viewer.ui_workxtrackr import Ui_LogIn
from PyQt6 import QtGui
from controllers.auth import AuthController
from controllers.staff import StaffController
from controllers.request_controller import RequestController
from controllers.employee_controller import EmployeeController
from viewer.request_dialog import RequestDialog
from datetime import datetime
from datetime import datetime, date, timedelta
import logging
from PyQt6.QtWidgets import QPushButton, QHBoxLayout
from PyQt6.QtWidgets import QTableView
from PyQt6.QtWidgets import QDialog, QStyle
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import QTimer
import os
from PyQt6.QtGui import QPixmap, QIcon
from viewer.report_popup_dialog import ReportPopupDialog
from config.settings import IMAGE_PATH
from PyQt6.QtWidgets import QLineEdit
from viewer.date_selector_dialog import DateSelectorDialog
from controllers.report_controller import ReportController


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_LogIn()
        self.ui.setupUi(self)

        self.create_default_icons()
        self.fix_ui_images()

        self.ui.passwordinput.setEchoMode(self.ui.passwordinput.EchoMode.Password)

        # Initialize controllers
        self.auth_controller = AuthController()
        self.current_user = None
        self.staff_controller = None
        self.staff_request_controller = None
        self.admin_request_controller = RequestController()
        self.employee_controller = EmployeeController()
        self.clock_in_time = None
        self.admin_requests_data = []
        self.current_selected_request_id = None
        self.system_config_controller = None
        self.report_controller = ReportController()

        # Setup connections
        self.setup_connections()

        # Setup timer for clock
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)

        # Set default page
        self.ui.stackedWidget.setCurrentIndex(0)
        self.update_clock()

    def fix_ui_images(self):

        import os
        from PyQt6.QtGui import QPixmap, QIcon
        from config.settings import IMAGE_PATH

        print("\n--- 🖼️ IMAGE LOADING DEBUG ---")

        # Helper function to check path and load image
        def apply_image(ui_element, filename, is_icon=False):
            full_path = os.path.join(IMAGE_PATH, filename)
            if os.path.exists(full_path):
                if is_icon:
                    ui_element.setIcon(QIcon(full_path))
                else:
                    ui_element.setPixmap(QPixmap(full_path))
                print(f"✅ Success: {filename}")
            else:
                print(f"❌ Not Found: {filename}")

        try:
            apply_image(self.ui.logo, "reallogo.png")
            apply_image(self.ui.AdminPicture, "admin_profile.jpg")
            apply_image(self.ui.StaffPictureFrame, "Profile_user.jpg")

            # Enable scaling so images fit the labels
            self.ui.logo.setScaledContents(True)
            self.ui.AdminPicture.setScaledContents(True)
            self.ui.StaffPictureFrame.setScaledContents(True)

            apply_image(self.ui.StaffDashboardButton, "dashboard_16598868.png", is_icon=True)
            apply_image(self.ui.AdminDashboardButton, "dashboard_16598868.png", is_icon=True)

            apply_image(self.ui.ShowPasswordButton, "eye_close.png", is_icon=True)

            from PyQt6.QtCore import QSize
            self.ui.ShowPasswordButton.setIconSize(QSize(30, 30))

            apply_image(self.ui.staffAttendance, "id-card_2643097.png", is_icon=True)
            apply_image(self.ui.requestButton, "interview_15325031.png", is_icon=True)
            apply_image(self.ui.AnnouncementButton, "icons8-announcement-50.png", is_icon=True)
            apply_image(self.ui.EmployeeManagementButton, "manager_11826940.png", is_icon=True)
            apply_image(self.ui.StaffRequestButton, "interview_15325031.png", is_icon=True)
            apply_image(self.ui.ReportsButton, "analytics_1188576.png", is_icon=True)
            apply_image(self.ui.SystemConfigurationButton, "adjustment_4289046.png", is_icon=True)

            print("--- 🖼️ DEBUG COMPLETE ---\n")

        except Exception as e:
            print(f"🔴 ERROR in fix_ui_images: {e}")

    def setup_connections(self):
        # Login Page buttons
        self.ui.loginButton.clicked.connect(self.handle_login)
        self.ui.usernameinput.returnPressed.connect(self.handle_login)
        self.ui.passwordinput.returnPressed.connect(self.handle_login)

        # Staff Page Navigation buttons
        self.ui.StaffDashboardButton.clicked.connect(lambda: self.ui.stackedWidget_3.setCurrentIndex(0))
        self.ui.staffAttendance.clicked.connect(lambda: self.ui.stackedWidget_3.setCurrentIndex(1))
        self.ui.requestButton.clicked.connect(self.show_staff_time_adjustment_page)
        self.ui.AnnouncementButton.clicked.connect(self.show_staff_announcement_page)
        self.ui.logOutButton.clicked.connect(self.handle_logout)

        # Staff Dashboard Actions buttons
        self.ui.ClockInButton.clicked.connect(self.handle_clock_in)
        self.ui.ClockOutButton.clicked.connect(self.handle_clock_out)

        # Staff Request Actions buttons
        self.ui.RequestingButton.clicked.connect(self.show_request_dialog)

        # Admin Page Navigation buttons
        self.ui.AdminDashboardButton.clicked.connect(lambda: self.ui.AdminStackedWidget.setCurrentIndex(0))
        self.ui.EmployeeManagementButton.clicked.connect(self.show_employee_management)
        self.ui.StaffRequestButton.clicked.connect(lambda: self.ui.AdminStackedWidget.setCurrentIndex(2))
        self.ui.ReportsButton.clicked.connect(lambda: self.ui.AdminStackedWidget.setCurrentIndex(3))
        self.ui.SystemConfigurationButton.clicked.connect(lambda: self.ui.AdminStackedWidget.setCurrentIndex(4))
        self.ui.AdminLogOutButton.clicked.connect(self.handle_logout)

        # Admin Request Actions
        if hasattr(self.ui, 'RequestTableOfListView'):
            self.ui.RequestTableOfListView.clicked.connect(self.handle_request_selection)
        if hasattr(self.ui, 'ApprovedButton'):
            self.ui.ApprovedButton.clicked.connect(self.handle_approve_request)
        if hasattr(self.ui, 'DeclineButton'):
            self.ui.DeclineButton.clicked.connect(self.handle_decline_request)

        # Employee Management buttons
        self.ui.AdminEmployeeSearchButton.clicked.connect(self.search_employees)
        self.ui.EmployeeManagementRefreshButton.clicked.connect(lambda: self.load_employees())
        self.ui.AddEmployeeButton.clicked.connect(self.add_employee)

        # Reports buttons
        self.ui.GenerateButton.clicked.connect(self.generate_report)
        self.ui.ExportToPDFButton.clicked.connect(self.export_to_pdf)

        # System Configuration connections buttons
        self.ui.SystemConfigurationButton.clicked.connect(self.show_system_configuration)
        self.ui.SaveSettingsButton.clicked.connect(self.save_system_settings)
        self.ui.AnnounceNowButton.clicked.connect(self.create_announcement)
        self.ui.DeleteAnnoucementButton.clicked.connect(self.delete_selected_announcement)

        # Password Toggle Connections
        self.ui.ShowPasswordButton.clicked.connect(
            lambda: self.toggle_password_visibility(self.ui.passwordinput, self.ui.ShowPasswordButton))

        # --- STAFF SIDEBAR ---
        self.ui.StaffDashboardButton.clicked.connect(lambda: [
            self.ui.stackedWidget_3.setCurrentIndex(0),
            self.update_sidebar_highlight("staff", self.ui.StaffDashboardButton)
        ])
        self.ui.staffAttendance.clicked.connect(lambda: [
            self.ui.stackedWidget_3.setCurrentIndex(1),
            self.update_sidebar_highlight("staff", self.ui.staffAttendance)
        ])
        self.ui.requestButton.clicked.connect(lambda: [
            self.show_staff_time_adjustment_page(),
            self.update_sidebar_highlight("staff", self.ui.requestButton)
        ])
        self.ui.AnnouncementButton.clicked.connect(lambda: [
            self.show_staff_announcement_page(),
            self.update_sidebar_highlight("staff", self.ui.AnnouncementButton)
        ])

        # --- ADMIN SIDEBAR ---
        self.ui.AdminDashboardButton.clicked.connect(lambda: [
            self.ui.AdminStackedWidget.setCurrentIndex(0),
            self.update_sidebar_highlight("admin", self.ui.AdminDashboardButton)
        ])
        self.ui.EmployeeManagementButton.clicked.connect(lambda: [
            self.show_employee_management(),
            self.update_sidebar_highlight("admin", self.ui.EmployeeManagementButton)
        ])
        self.ui.StaffRequestButton.clicked.connect(lambda: [
            self.ui.AdminStackedWidget.setCurrentIndex(2),
            self.update_sidebar_highlight("admin", self.ui.StaffRequestButton)
        ])
        self.ui.ReportsButton.clicked.connect(lambda: [
            self.ui.AdminStackedWidget.setCurrentIndex(3),
            self.update_sidebar_highlight("admin", self.ui.ReportsButton)
        ])
        self.ui.SystemConfigurationButton.clicked.connect(lambda: [
            self.show_system_configuration(),
            self.update_sidebar_highlight("admin", self.ui.SystemConfigurationButton)
        ])

    def update_clock(self):
        """Update date and time display"""
        try:
            current_datetime = datetime.now()
            date_str = current_datetime.strftime("%Y-%m-%d")
            time_str = current_datetime.strftime("%I:%M:%S %p")

            if hasattr(self.ui, 'DateTodayOutput'):
                self.ui.DateTodayOutput.setText(date_str)
            if hasattr(self.ui, 'TimeTodayOutput'):
                self.ui.TimeTodayOutput.setText(time_str)
        except Exception as e:
            logging.error(f"Error updating clock: {e}")

    def handle_login(self):
        """Handle login button click"""
        username = self.ui.usernameinput.text()
        password = self.ui.passwordinput.text()

        if not username or not password:
            self.show_custom_message("Login Error", "Please enter username and password", "error")
            return

        result = self.auth_controller.login(username, password)

        if result["success"]:
            self.current_user = result["user"]
            self.ui.passwordinput.clear()

            print(f"DEBUG: Logged in user data: {self.current_user}")

            if self.current_user['role'] == 'admin':
                print("DEBUG: Redirecting to admin page")
                # RE-INITIALIZE admin request controller with current user
                self.admin_request_controller = RequestController()
                self.current_selected_request_id = None  # Clear any previous selection

                # Clear any stale request details UI
                try:
                    if hasattr(self.ui, 'EmployeeRequestNameOutput'):
                        self.ui.EmployeeRequestNameOutput.clear()
                    if hasattr(self.ui, 'EmployeeRequestTypeOutput'):
                        self.ui.EmployeeRequestTypeOutput.clear()
                    if hasattr(self.ui, 'EmployeeDateRequestOutput'):
                        self.ui.EmployeeDateRequestOutput.clear()
                    if hasattr(self.ui, 'ReasonRequestOutput'):
                        self.ui.ReasonRequestOutput.clear()
                except:
                    pass

                self.show_admin_page()
                self.load_admin_requests()
                self.load_employees()

            else:
                print(f"DEBUG: Creating StaffController with user_id: {self.current_user['id']}")
                try:
                    self.staff_controller = StaffController(self.current_user['id'])
                    self.staff_request_controller = RequestController(self.current_user['id'])
                    self.show_staff_page()
                    QTimer.singleShot(100, self.load_my_requests)
                except Exception as e:
                    print(f"❌ ERROR in staff login: {e}")
                    import traceback
                    traceback.print_exc()
                    self.show_custom_message("Login Error", f"Failed to load staff dashboard: {str(e)}", "error")
                    return

            full_name = self.current_user.get('full_name', self.current_user.get('username', ''))
            self.show_custom_message("Login Successful", f"Welcome back, {full_name}!", "success")
        else:
            self.show_custom_message("Login Failed", result["message"], "error")

    def toggle_password_visibility(self, line_edit, button):
        """Toggle between showing and hiding password text"""
        import os
        from PyQt6.QtGui import QIcon
        from config.settings import IMAGE_PATH
        from PyQt6.QtCore import QSize

        if line_edit.echoMode() == QLineEdit.EchoMode.Password:
            # Change to visible
            line_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            icon_name = "eye_open.png"
        else:
            # Change to hidden
            line_edit.setEchoMode(QLineEdit.EchoMode.Password)
            icon_name = "eye_close.png"

        # Update the button icon
        icon_path = os.path.join(IMAGE_PATH, icon_name)
        if os.path.exists(icon_path):
            button.setIcon(QIcon(icon_path))

    def create_default_icons(self):
        """Creates larger, thicker BLACK eye icons automatically"""
        import os
        from PyQt6.QtGui import QPainter, QColor, QPen, QPixmap
        from PyQt6.QtCore import Qt, QPoint, QRectF, QSize
        from config.settings import IMAGE_PATH

        if not os.path.exists(IMAGE_PATH):
            os.makedirs(IMAGE_PATH)

        icons = {
            "eye_open.png": True,
            "eye_close.png": False
        }

        for filename, is_open in icons.items():
            path = os.path.join(IMAGE_PATH, filename)
            # We remove the old blue ones to replace them with bigger black ones
            if os.path.exists(path):
                os.remove(path)

            # Create a 64x64 image (Larger for better resolution)
            pixmap = QPixmap(64, 64)
            pixmap.fill(Qt.GlobalColor.transparent)

            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # Draw the eye shape in BLACK with a thicker stroke
            pen = QPen(Qt.GlobalColor.darkGray)
            pen.setWidth(4)  # Thicker line
            painter.setPen(pen)

            # Larger eye curve centered in 64x64
            painter.drawArc(QRectF(8, 16, 48, 32), 0, 180 * 16)
            painter.drawArc(QRectF(8, 16, 48, 32), 0, -180 * 16)

            # Larger Pupil
            painter.setBrush(Qt.GlobalColor.darkGray)
            painter.drawEllipse(QPoint(32, 32), 8, 8)

            if not is_open:
                # Draw a thicker slash for "Hidden"
                painter.drawLine(12, 12, 52, 52)

            painter.end()
            pixmap.save(path)
            print(f"🎨 Updated icon to Larger Black version: {filename}")

    def show_custom_message(self, title, message, msg_type="info"):
        """Show custom styled message box - UPDATED FOR BETTER PERFORMANCE"""
        # Don't show message if we're in the middle of logout
        if "logout" in title.lower() and "please wait" in message.lower():
            # Process events to show the message quickly
            QApplication.processEvents()
            return

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)

        if msg_type == "success":
            msg_box.setIcon(QMessageBox.Icon.Information)
        elif msg_type == "error":
            msg_box.setIcon(QMessageBox.Icon.Warning)
        elif msg_type == "warning":
            msg_box.setIcon(QMessageBox.Icon.Warning)
        else:
            msg_box.setIcon(QMessageBox.Icon.Information)

        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: white;
                font-family: 'Segoe UI', Arial;
                font-size: 11pt;
                border: 1px solid #00aaff;
                border-radius: 8px;
            }}

            QMessageBox QLabel {{
                color: #333333;
                font-size: 11pt;
                padding: 15px;
                background-color: white;
                qproperty-alignment: AlignCenter;
            }}

            QMessageBox QPushButton {{
                background-color: #00aaff;
                color: white;
                border: 1px solid #00aaff;
                border-radius: 4px;
                padding: 10px 25px;
                font-size: 11pt;
                font-weight: bold;
                min-width: 100px;
            }}

            QMessageBox QPushButton:hover {{
                background-color: #0088cc;
                border: 1px solid #0088cc;
            }}

            QMessageBox QPushButton:pressed {{
                background-color: #006699;
            }}
        """)

        ok_button = msg_box.addButton(QMessageBox.StandardButton.Ok)
        ok_button.setCursor(Qt.CursorShape.PointingHandCursor)

        # For logout success message, auto-close after 2 seconds
        if "logged out" in title.lower():
            QTimer.singleShot(2000, msg_box.accept)

        msg_box.exec()

    def show_login_page(self):
        """Show login page"""
        self.ui.stackedWidget.setCurrentIndex(0)

    def show_staff_page(self):
        """Show staff dashboard"""
        self.ui.stackedWidget.setCurrentIndex(1)
        self.update_sidebar_highlight("staff", self.ui.StaffDashboardButton)

        # Debug UI structure first
        self.debug_ui_structure()

        # Debug request types
        QTimer.singleShot(1000, self.debug_request_types)

        # Load staff dashboard data
        self.load_staff_dashboard()

        # Load attendance history
        self.load_attendance_history()

        # Load requests
        self.load_my_requests()

        # Load time adjustment requests
        QTimer.singleShot(500, self.load_staff_time_adjustment_requests)

        print("✅ Staff page loaded with all data")

    def show_admin_page(self):
        """Show admin dashboard"""
        print("🖥️ Showing admin page...")
        self.ui.stackedWidget.setCurrentIndex(2)
        self.update_sidebar_highlight("admin", self.ui.AdminDashboardButton)

        # Display admin name
        if self.current_user and hasattr(self.ui, 'AdminName'):
            full_name = self.current_user.get('full_name', self.current_user.get('username', ''))
            self.ui.AdminName.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.ui.AdminName.setText(f"<center>{full_name}</center>")

        # Load admin data
        self.load_admin_requests()
        self.load_employees()

        # Load dashboard WITH GRAPHS
        self.load_admin_dashboard()

        print("✅ Admin page fully loaded")

    def handle_logout(self):
        """Handle logout with custom confirmation dialog"""
        # Create custom confirmation dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Confirm Logout")
        dialog.setFixedSize(450, 300)  # Increased size for better text display
        dialog.setModal(True)

        # Main layout
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 25, 30, 25)

        # Icon
        icon_label = QLabel()
        icon_label.setPixmap(QApplication.style().standardIcon(
            QStyle.StandardPixmap.SP_MessageBoxQuestion).pixmap(64, 64))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("background-color: transparent;")
        layout.addWidget(icon_label)

        # Title
        title_label = QLabel("Confirm Logout")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setWordWrap(True)  # ADD THIS
        title_label.setStyleSheet("""
            font-size: 16pt;
            font-weight: bold;
            color: #004c8c;
            margin: 5px;
            padding: 5px;
            background-color: transparent;
        """)
        layout.addWidget(title_label)

        # Message
        message_label = QLabel("Are you sure you want to logout?")
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setWordWrap(True)  # ADD THIS
        message_label.setStyleSheet("""
            font-size: 12pt;
            color: #666666;
            margin: 5px;
            padding: 5px;
            background-color: transparent;
        """)
        layout.addWidget(message_label)

        # Info text
        info_label = QLabel("You will be returned to the login screen.")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setWordWrap(True)  # ADD THIS
        info_label.setStyleSheet("""
            font-size: 10pt;
            color: #888888;
            font-style: italic;
            margin: 5px;
            padding: 5px;
            background-color: transparent;
        """)
        layout.addWidget(info_label)

        # Add stretch to push everything up
        layout.addStretch(1)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        button_layout.addStretch()

        # No button
        no_button = QPushButton("Cancel")
        no_button.setFixedSize(120, 40)
        no_button.setCursor(Qt.CursorShape.PointingHandCursor)
        no_button.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                color: #333333;
                border: 1px solid #ced4da;
                border-radius: 6px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e9ecef;
                border: 1px solid #6c757d;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        no_button.clicked.connect(dialog.reject)
        button_layout.addWidget(no_button)

        # Yes button
        yes_button = QPushButton("Logout")
        yes_button.setFixedSize(120, 40)
        yes_button.setCursor(Qt.CursorShape.PointingHandCursor)
        yes_button.setStyleSheet("""
            QPushButton {
                background-color: #00aaff;
                color: white;
                border: 1px solid #00aaff;
                border-radius: 6px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0088cc;
                border: 1px solid #0088cc;
            }
            QPushButton:pressed {
                background-color: #006699;
            }
        """)
        yes_button.clicked.connect(dialog.accept)
        button_layout.addWidget(yes_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Set dialog style
        dialog.setStyleSheet("""
            QDialog {
                background-color: white;
                border: 2px solid #00aaff;
                border-radius: 12px;
            }
            QLabel {
                background-color: transparent;
            }
        """)

        # Execute dialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            print("✅ User confirmed logout")

            # Show brief waiting message
            self.show_custom_message("Logging Out", "Please wait...", "info")

            # Perform logout
            QTimer.singleShot(500, self.perform_logout)
        else:
            print("❌ User cancelled logout")

    def perform_logout(self):
        """Actually perform the logout (called after confirmation)"""
        # Clear all user data
        self.current_user = None
        self.staff_controller = None
        self.staff_request_controller = None
        self.admin_request_controller = None  # This line already exists
        self.clock_in_time = None
        self.admin_requests_data = []
        self.current_selected_request_id = None  # ADD THIS LINE - Clear the selected request ID

        # Also clear the request details UI if it exists
        try:
            if hasattr(self.ui, 'EmployeeRequestNameOutput'):
                self.ui.EmployeeRequestNameOutput.clear()
            if hasattr(self.ui, 'EmployeeRequestTypeOutput'):
                self.ui.EmployeeRequestTypeOutput.clear()
            if hasattr(self.ui, 'EmployeeDateRequestOutput'):
                self.ui.EmployeeDateRequestOutput.clear()
            if hasattr(self.ui, 'ReasonRequestOutput'):
                self.ui.ReasonRequestOutput.clear()
        except:
            pass  # Ignore errors if UI elements don't exist

        # Show logout success message
        self.show_custom_message("Logged Out", "You have been successfully logged out.", "success")

        # Return to login page
        self.show_login_page()

        # Clear any sensitive input fields
        if hasattr(self.ui, 'passwordinput'):
            self.ui.passwordinput.clear()
        if hasattr(self.ui, 'usernameinput'):
            self.ui.usernameinput.clear()

        print("✅ Logout completed successfully")

    def show_request_dialog(self):
        """Show the request submission dialog"""
        if not self.staff_request_controller:
            self.show_custom_message("Error", "Please login first!", "error")
            return

        request_types = self.staff_request_controller.get_all_request_types_list()
        dialog = RequestDialog(
            parent=self,
            request_types=request_types,
            user_id=self.current_user['id']
        )
        dialog.request_submitted.connect(self.handle_request_submission)
        dialog.exec()

    def handle_request_submission(self, request_data):
        """Handle request submission from dialog"""
        try:
            result = self.staff_request_controller.submit_request(
                request_data['type'],
                request_data['date'],
                request_data['reason']
            )

            if result["success"]:
                self.show_custom_message("Success", result["message"], "success")
                self.load_my_requests()

                # Refresh the time adjustment table
                QTimer.singleShot(500, self.load_staff_time_adjustment_requests)
            else:
                self.show_custom_message("Request Failed", result["message"], "error")

        except Exception as e:
            self.show_custom_message("Error", f"Failed to submit request: {str(e)}", "error")

    def load_my_requests(self):
        """Load current user's requests and display in table"""
        if not self.staff_request_controller:
            return

        try:
            requests = self.staff_request_controller.get_my_requests()

            # Create table widget
            table_widget = QTableWidget()
            table_widget.setColumnCount(5)
            table_widget.setHorizontalHeaderLabels(['Type', 'Date', 'Reason', 'Status', 'Submitted'])
            table_widget.setRowCount(len(requests))
            table_widget.setFixedWidth(1141)

            # Style header
            header = table_widget.horizontalHeader()
            header.setStyleSheet("""
                QHeaderView::section {
                    background-color: #A2A2A2;
                    color: black;
                    font-weight: bold;
                    padding: 8px;
                    border: 1px solid #d0d0d0;
                }
            """)
            header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

            # Set column widths
            column_widths = [150, 100, 500, 100, 150]
            for i, width in enumerate(column_widths):
                table_widget.setColumnWidth(i, width)

            # Fill table with data
            for i, req in enumerate(requests):
                # Type
                table_widget.setItem(i, 0, QTableWidgetItem(req['type']))

                # Date
                table_widget.setItem(i, 1, QTableWidgetItem(req['date']))

                # Reason (truncate if too long)
                reason = req['reason']
                if len(reason) > 100:
                    reason = reason[:97] + "..."
                table_widget.setItem(i, 2, QTableWidgetItem(reason))

                # Status with color coding
                status_item = QTableWidgetItem(req['status'])
                if req['status'].lower() == 'approved':
                    status_item.setForeground(Qt.GlobalColor.green)
                    status_item.setBackground(QBrush(QColor(230, 245, 230)))  # Light green
                elif req['status'].lower() == 'declined':
                    status_item.setForeground(Qt.GlobalColor.red)
                    status_item.setBackground(QBrush(QColor(255, 230, 230)))  # Light red
                elif req['status'].lower() == 'pending':
                    status_item.setForeground(Qt.GlobalColor.blue)
                    status_item.setBackground(QBrush(QColor(230, 240, 255)))  # Light blue
                table_widget.setItem(i, 3, status_item)

                # Submitted date
                submitted = req.get('created_at', '')
                if submitted:
                    # Format date if needed
                    table_widget.setItem(i, 4, QTableWidgetItem(submitted))
                else:
                    table_widget.setItem(i, 4, QTableWidgetItem('--'))

                # Center align all items
                for col in range(5):
                    item = table_widget.item(i, col)
                    if item:
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # Style the table
            table_widget.setStyleSheet("""
                QTableWidget {
                    background-color: white;
                    alternate-background-color: #f8f8f8;
                    gridline-color: #e0e0e0;
                    font-size: 11pt;
                    width: 1141px;
                }
                QTableWidget::item {
                    padding: 8px;
                }
            """)
            table_widget.setAlternatingRowColors(True)
            table_widget.setWordWrap(True)
            table_widget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

            # Display in scroll area
            if hasattr(self.ui, 'scrollArea_6'):
                # Remove old widget
                old_widget = self.ui.scrollArea_6.takeWidget()
                if old_widget:
                    old_widget.deleteLater()

                # Create container
                container = QWidget()
                layout = QVBoxLayout(container)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.addWidget(table_widget)
                container.setFixedWidth(1141)

                self.ui.scrollArea_6.setWidget(container)
                self.ui.scrollArea_6.setMinimumWidth(1141)
                self.ui.scrollArea_6.setWidgetResizable(True)

            # Update pending count
            stats = self.staff_request_controller.get_request_stats()
            pending_count = stats.get('pending', 0)

            if hasattr(self.ui, 'PendingRequestOutput'):
                self.ui.PendingRequestOutput.setText(f"Request Pending ({pending_count})")

                if pending_count > 0:
                    self.ui.PendingRequestOutput.setStyleSheet("""
                        font-size: 12pt;
                        font-weight: bold;
                        color: #ff9900;
                        border: none;
                        background: transparent;
                    """)
                else:
                    self.ui.PendingRequestOutput.setStyleSheet("""
                        font-size: 12pt;
                        color: #666;
                        border: none;
                        background: transparent;
                    """)

            print(f"✅ Loaded {len(requests)} requests into table")

        except Exception as e:
            print(f"❌ Error loading requests: {e}")
            import traceback
            traceback.print_exc()

    def load_admin_requests(self):
        """Load all pending requests for admin"""
        try:
            # Clear any previous selection
            self.current_selected_request_id = None

            # Clear list view selection if it exists
            if hasattr(self.ui, 'RequestTableOfListView'):
                self.ui.RequestTableOfListView.clearSelection()

            # Clear request details display
            try:
                if hasattr(self.ui, 'EmployeeRequestNameOutput'):
                    self.ui.EmployeeRequestNameOutput.clear()
                    self.ui.EmployeeRequestNameOutput.setStyleSheet("""
                        border:1px solid #A2A2A2;
                        background-color: #f8f8f8;
                        padding: 5px;
                    """)

                if hasattr(self.ui, 'EmployeeRequestTypeOutput'):
                    self.ui.EmployeeRequestTypeOutput.clear()
                    self.ui.EmployeeRequestTypeOutput.setStyleSheet("""
                        border:1px solid #A2A2A2;
                        background-color: #f8f8f8;
                        padding: 5px;
                    """)

                if hasattr(self.ui, 'EmployeeDateRequestOutput'):
                    self.ui.EmployeeDateRequestOutput.clear()
                    self.ui.EmployeeDateRequestOutput.setStyleSheet("""
                        border:1px solid #A2A2A2;
                        background-color: #f8f8f8;
                        padding: 5px;
                    """)

                if hasattr(self.ui, 'ReasonRequestOutput'):
                    self.ui.ReasonRequestOutput.clear()
                    self.ui.ReasonRequestOutput.setStyleSheet("""
                        font-size: 11pt;
                        padding: 10px;
                        background-color: #f8f8f8;
                        border: 1px solid #e0e0e0;
                        border-radius: 4px;
                        min-height: 100px;
                    """)
            except Exception as e:
                print(f"⚠️  Error clearing request details: {e}")

            if not self.admin_request_controller:
                print("❌ Admin request controller not initialized")
                return

            requests = self.admin_request_controller.get_pending_requests()
            self.admin_requests_data = requests

            print(f"📋 Found {len(requests)} pending requests")

            model = QStringListModel()
            request_items = []

            for req in requests:
                item_text = f"{req['type']} | {req['date']} | {req['full_name']}"
                request_items.append(item_text)

            model.setStringList(request_items)

            if hasattr(self.ui, 'RequestTableOfListView'):
                self.ui.RequestTableOfListView.setModel(model)

                self.ui.RequestTableOfListView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

                self.ui.RequestTableOfListView.setStyleSheet("""
                    QListView {
                        background-color: white;
                        alternate-background-color: #f8f8f8;
                        font-size: 11pt;
                        padding: 5px;
                    }
                    QListView::item {
                        padding: 8px;
                        border-bottom: 1px solid #e0e0e0;
                    }
                    QListView::item:selected {
                        background-color: #e6f7ff;
                        color: black;
                        border-left: 4px solid #00aaff;
                    }
                """)

            if hasattr(self.ui, 'RequestDetailsLabelHeader'):
                count = len(requests)
                self.ui.RequestDetailsLabelHeader.setText(f"Request Details (Pending: {count})")

        except Exception as e:
            print(f"❌ Error loading admin requests: {e}")
            import traceback
            traceback.print_exc()

    def handle_request_selection(self, index):
        """Handle when admin selects a request from the list"""
        try:
            if not self.admin_requests_data:
                return

            selected_index = index.row()
            if 0 <= selected_index < len(self.admin_requests_data):
                request = self.admin_requests_data[selected_index]

                # Update the Detail Labels
                if hasattr(self.ui, 'EmployeeRequestNameOutput'):
                    self.ui.EmployeeRequestNameOutput.setText(request['full_name'])
                if hasattr(self.ui, 'EmployeeRequestTypeOutput'):
                    self.ui.EmployeeRequestTypeOutput.setText(request['type'])
                if hasattr(self.ui, 'EmployeeDateRequestOutput'):
                    self.ui.EmployeeDateRequestOutput.setText(request['date'])

                # Update the Reason Box
                if hasattr(self.ui, 'ReasonRequestOutput'):
                    self.ui.ReasonRequestOutput.setText(request['reason'])
                    self.ui.ReasonRequestOutput.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
                    self.ui.ReasonRequestOutput.setWordWrap(True)

                self.current_selected_request_id = request['id']

        except Exception as e:
            print(f"Error handling request selection: {e}")

    def handle_approve_request(self):
        """Handle approve request button (admin)"""
        if not self.current_selected_request_id:
            self.show_custom_message("Error", "Please select a request first!", "error")
            return

        if not self.admin_request_controller:
            self.show_custom_message("Error", "Not authorized!", "error")
            return

        confirm_dialog = QMessageBox(self)
        confirm_dialog.setWindowTitle("Confirm Approval")
        confirm_dialog.setText("Are you sure you want to approve this request?")
        confirm_dialog.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        confirm_dialog.setDefaultButton(QMessageBox.StandardButton.No)

        confirm_dialog.setStyleSheet("""
            QMessageBox {
                background-color: white;
                font-family: 'Segoe UI', Arial;
                font-size: 11pt;
            }

            QMessageBox QLabel {
                color: #333333;
                font-size: 11pt;
                padding: 15px;
                background-color: white;
            }

            QMessageBox QPushButton {
                background-color: #00aaff;
                color: white;
                border: 1px solid #00aaff;
                border-radius: 4px;
                padding: 8px 25px;
                font-size: 11pt;
                font-weight: bold;
                min-width: 80px;
                margin: 5px;
            }

            QMessageBox QPushButton:hover {
                background-color: #0088cc;
                border: 1px solid #0088cc;
            }

            QMessageBox QPushButton:pressed {
                background-color: #006699;
            }

            QMessageBox QPushButton#qt_msgbox_buttonbox QPushButton:nth-child(1) {
                background-color: #4CAF50;
                border: 1px solid #4CAF50;
            }

            QMessageBox QPushButton#qt_msgbox_buttonbox QPushButton:nth-child(1):hover {
                background-color: #45a049;
                border: 1px solid #45a049;
            }

            QMessageBox QPushButton#qt_msgbox_buttonbox QPushButton:nth-child(2) {
                background-color: #f44336;
                border: 1px solid #f44336;
            }

            QMessageBox QPushButton#qt_msgbox_buttonbox QPushButton:nth-child(2):hover {
                background-color: #d32f2f;
                border: 1px solid #d32f2f;
            }
        """)

        for button in confirm_dialog.buttons():
            button.setCursor(Qt.CursorShape.PointingHandCursor)

        if confirm_dialog.exec() == QMessageBox.StandardButton.Yes:
            result = self.admin_request_controller.approve_request(self.current_selected_request_id)

            if result["success"]:
                self.show_custom_message("Success", "✓ Request approved successfully!", "success")
                self.load_admin_requests()
                self.clear_request_details()
            else:
                self.show_custom_message("Error", f"✗ {result.get('message', 'Failed to approve request')}", "error")

    def handle_decline_request(self):
        """Handle decline request button (admin)"""
        if not self.current_selected_request_id:
            self.show_custom_message("Error", "Please select a request first!", "error")
            return

        if not self.admin_request_controller:
            self.show_custom_message("Error", "Not authorized!", "error")
            return

        confirm_dialog = QMessageBox(self)
        confirm_dialog.setWindowTitle("Confirm Decline")
        confirm_dialog.setText("Are you sure you want to decline this request?")
        confirm_dialog.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        confirm_dialog.setDefaultButton(QMessageBox.StandardButton.No)

        confirm_dialog.setStyleSheet("""
            QMessageBox {
                background-color: white;
                font-family: 'Segoe UI', Arial;
                font-size: 11pt;
            }

            QMessageBox QLabel {
                color: #333333;
                font-size: 11pt;
                padding: 15px;
                background-color: white;
            }

            QMessageBox QPushButton {
                background-color: #00aaff;
                color: white;
                border: 1px solid #00aaff;
                border-radius: 4px;
                padding: 8px 25px;
                font-size: 11pt;
                font-weight: bold;
                min-width: 80px;
                margin: 5px;
            }

            QMessageBox QPushButton:hover {
                background-color: #0088cc;
                border: 1px solid #0088cc;
            }

            QMessageBox QPushButton:pressed {
                background-color: #006699;
            }

            QMessageBox QPushButton#qt_msgbox_buttonbox QPushButton:nth-child(1) {
                background-color: #f44336;
                border: 1px solid #f44336;
            }

            QMessageBox QPushButton#qt_msgbox_buttonbox QPushButton:nth-child(1):hover {
                background-color: #d32f2f;
                border: 1px solid #d32f2f;
            }

            QMessageBox QPushButton#qt_msgbox_buttonbox QPushButton:nth-child(2) {
                background-color: #757575;
                border: 1px solid #757575;
            }

            QMessageBox QPushButton#qt_msgbox_buttonbox QPushButton:nth-child(2):hover {
                background-color: #616161;
                border: 1px solid #616161;
            }
        """)

        for button in confirm_dialog.buttons():
            button.setCursor(Qt.CursorShape.PointingHandCursor)

        if confirm_dialog.exec() == QMessageBox.StandardButton.Yes:
            result = self.admin_request_controller.decline_request(self.current_selected_request_id)

            if result["success"]:
                self.show_custom_message("Success", "✓ Request declined!", "success")
                self.load_admin_requests()
                self.clear_request_details()
            else:
                self.show_custom_message("Error", f"✗ {result.get('message', 'Failed to decline request')}", "error")

    def clear_request_details(self):
        """Clear request details panel"""
        if hasattr(self.ui, 'EmployeeRequestNameOutput'):
            self.ui.EmployeeRequestNameOutput.clear()

        if hasattr(self.ui, 'EmployeeRequestTypeOutput'):
            self.ui.EmployeeRequestTypeOutput.clear()

        if hasattr(self.ui, 'EmployeeDateRequestOutput'):
            self.ui.EmployeeDateRequestOutput.clear()

        if hasattr(self.ui, 'ReasonRequestOutput'):
            self.ui.ReasonRequestOutput.clear()

        self.current_selected_request_id = None

    def search_employees(self):
        """Search employees in admin panel"""
        try:
            search_term = ""

            if hasattr(self.ui, 'YearAdminInput_2'):
                search_term = self.ui.YearAdminInput_2.text()
                print(f"🔍 Searching for: '{search_term}'")
                self.load_employees(search_term)
            else:
                print("❌ Search input field not found!")
                self.load_employees()

        except Exception as e:
            print(f"❌ Error searching employees: {e}")

    def load_employees(self, search_term=""):
        """Load employees and enable click-to-edit (No Actions Column)"""
        try:
            print(f"🔄 Loading employees...")
            employees = []
            if search_term and search_term.strip():
                employees = self.employee_controller.search_employees(search_term)
            else:
                employees = self.employee_controller.get_all_employees()

            from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
            from PyQt6.QtCore import Qt

            employee_table = QTableWidget()
            # FIXED: Reduced to 6 columns (Deleted Actions/Edit column)
            employee_table.setColumnCount(6)
            employee_table.setHorizontalHeaderLabels(
                ['EMPLOYEE ID', 'FULL NAME', 'USERNAME', 'EMAIL', 'ROLE', 'STATUS'])
            employee_table.setRowCount(len(employees))

            # Table Behaviors
            employee_table.verticalHeader().setVisible(False)
            employee_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            employee_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            employee_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            employee_table.setAlternatingRowColors(True)
            employee_table.setCursor(Qt.CursorShape.PointingHandCursor)

            # Fill Table
            for i, emp in enumerate(employees):
                # ID
                id_item = QTableWidgetItem(f"EMP{emp.get('id', '')}")
                id_item.setData(Qt.ItemDataRole.UserRole, emp)  # Store full data object in the row
                id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                employee_table.setItem(i, 0, id_item)

                # Name
                name_item = QStandardItem(str(emp.get('full_name', '')))  # If using standard items
                employee_table.setItem(i, 1, QTableWidgetItem(emp.get('full_name', '')))

                # Others
                employee_table.setItem(i, 2, QTableWidgetItem(emp.get('username', '')))
                employee_table.setItem(i, 3, QTableWidgetItem(emp.get('email', '')))
                employee_table.setItem(i, 4, QTableWidgetItem(emp.get('role', '').capitalize()))

                status = emp.get('status', 'active').capitalize()
                status_item = QTableWidgetItem(status)
                status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                # Apply Color
                if status.lower() == 'active':
                    status_item.setForeground(QColor(0, 128, 0))
                elif status.lower() == 'on leave':
                    status_item.setForeground(QColor(255, 140, 0))
                else:
                    status_item.setForeground(QColor(220, 20, 60))
                employee_table.setItem(i, 5, status_item)

            # Column Widths (Total 1141px)
            column_widths = {0: 100, 1: 280, 2: 150, 3: 280, 4: 150, 5: 181}
            for col, width in column_widths.items():
                employee_table.setColumnWidth(col, width)

            employee_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

            # Styling
            employee_table.setStyleSheet("""
                QTableWidget { background-color: white; gridline-color: #e0e0e0; font-size: 11pt; border: 1px solid #cccccc; }
                QHeaderView::section {
                    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1C6099, stop:1 #73DFF3);
                    color: white; font-weight: bold; padding: 12px; border: 1px solid #1C6099;
                }
            """)

            # --- CONNECT CLICK TO POPUP ---
            employee_table.clicked.connect(self.handle_employee_row_click)

            # Replace in ScrollArea
            if hasattr(self.ui, 'scrollArea_2'):
                old = self.ui.scrollArea_2.takeWidget()
                if old: old.deleteLater()
                self.ui.scrollArea_2.setWidget(employee_table)

        except Exception as e:
            print(f"❌ Error: {e}")

    def show_edit_employee_dialog(self, employee_id, employee_data):
        """Professional Employee Editor - Clean borderless labels"""
        try:
            from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                         QLineEdit, QComboBox, QPushButton,
                                         QFormLayout, QFrame)
            from PyQt6.QtCore import Qt

            dialog = QDialog(self)
            dialog.setWindowTitle(f"Edit Profile - EMP{employee_id}")
            dialog.setFixedSize(500, 550)
            dialog.setStyleSheet("background-color: white; border-radius: 12px;")

            main_layout = QVBoxLayout(dialog)
            main_layout.setContentsMargins(30, 25, 30, 25)
            main_layout.setSpacing(15)

            # --- HEADER ---
            title_lbl = QLabel("EDIT EMPLOYEE PROFILE")
            title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_lbl.setStyleSheet("""
                font-size: 18pt; font-weight: bold; color: #004c8c; 
                border: none; border-bottom: 2px solid #00aaff; 
                padding-bottom: 5px; background: transparent;
            """)
            main_layout.addWidget(title_lbl)

            # --- FORM CONTAINER ---
            info_frame = QFrame()
            info_frame.setObjectName("infoFrame")

            # CSS Fix: Target labels to remove borders, but keep them on inputs
            info_frame.setStyleSheet("""
                            QFrame#infoFrame { 
                                background-color: #fcfcfc; 
                                border: 1px solid #eee; 
                                border-radius: 8px; 
                            }
                            QLabel { 
                                border: none; 
                                background: transparent; 
                                color: #333; 
                                font-size: 11pt;
                            }
                            QLineEdit, QComboBox {
                                padding: 10px; 
                                border: 1px solid #ccc; 
                                border-radius: 5px; 
                                font-size: 11pt;
                                background-color: white;
                            }
                            QComboBox QAbstractItemView {
                                background-color: white;
                                border: 1px solid #ccc;
                                selection-background-color: #e6f7ff;
                                selection-color: black;
                                outline: none;
                            }
                            QComboBox::drop-down {
                                border: none;
                                background: transparent;
                                width: 30px;
                            }
                            QComboBox::down-arrow {
                                image: none;
                                border-left: 5px solid transparent;
                                border-right: 5px solid transparent;
                                border-top: 7px solid #ffffff;
                                margin-right: 8px;
                            }
                        """)

            form_layout = QFormLayout(info_frame)
            form_layout.setSpacing(15)
            form_layout.setContentsMargins(20, 20, 20, 20)

            # Labels and Inputs
            id_val = QLabel(f"<b>Employee ID:</b> EMP{employee_id}")
            form_layout.addRow(id_val)

            self.edit_name_input = QLineEdit(str(employee_data.get('full_name', '')))
            form_layout.addRow("Full Name:", self.edit_name_input)

            self.edit_username_input = QLineEdit(str(employee_data.get('username', '')))
            form_layout.addRow("Username:", self.edit_username_input)

            self.edit_email_input = QLineEdit(str(employee_data.get('email', '')))
            form_layout.addRow("Email Address:", self.edit_email_input)

            self.edit_role_combo = QComboBox()
            self.edit_role_combo.addItems(["Staff", "Admin", "Manager"])
            self.edit_role_combo.setCurrentText(str(employee_data.get('role', 'staff')).capitalize())
            form_layout.addRow("Account Role:", self.edit_role_combo)

            self.edit_status_combo = QComboBox()
            self.edit_status_combo.addItems(["Active", "Inactive", "On Leave"])
            self.edit_status_combo.setCurrentText(str(employee_data.get('status', 'active')).capitalize())
            form_layout.addRow("Work Status:", self.edit_status_combo)

            main_layout.addWidget(info_frame)

            # --- ACTION BUTTONS ---
            btn_layout = QHBoxLayout()
            btn_layout.setSpacing(15)

            cancel_btn = QPushButton("CANCEL")
            cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            cancel_btn.setFixedHeight(45)
            cancel_btn.setStyleSheet(
                "background: #f1f1f1; color: #333; border-radius: 6px; font-weight: bold; border: none;")
            cancel_btn.clicked.connect(dialog.reject)

            save_btn = QPushButton("SAVE CHANGES")
            save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            save_btn.setFixedHeight(45)
            save_btn.setStyleSheet(
                "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1C6099, stop:1 #00aaff); color: white; border-radius: 6px; font-weight: bold; border: none;")
            save_btn.clicked.connect(lambda: self.save_employee_changes_with_role(employee_id, dialog))

            btn_layout.addWidget(cancel_btn)
            btn_layout.addWidget(save_btn)
            main_layout.addLayout(btn_layout)

            dialog.exec()

        except Exception as e:
            print(f"❌ Error showing edit dialog: {e}")

    def add_employee(self):
        """Open Add Employee dialog"""
        try:
            from viewer.add_employee_dialog import AddEmployeeDialog

            dialog = AddEmployeeDialog(self)
            dialog.employee_added.connect(self.handle_employee_addition)
            dialog.exec()

        except Exception as e:
            print(f"❌ Error opening add employee dialog: {e}")
            self.show_custom_message("Error", f"Failed to open add employee dialog: {str(e)}", "error")

    def handle_employee_addition(self, employee_data):
        """Handle new employee addition WITH ROLE"""
        try:
            print(f"➕ Adding new employee: {employee_data['full_name']}")

            result = self.employee_controller.add_employee(
                full_name=employee_data['full_name'],
                username=employee_data['username'],
                email=employee_data['email'],
                password=employee_data['password'],
                role=employee_data['role']  # ADDED ROLE PARAMETER
            )

            if result["success"]:
                self.show_custom_message("Success",
                                         f"Employee {employee_data['full_name']} added successfully!\n"
                                         f"Role: {employee_data['role'].capitalize()}",
                                         "success")
                self.load_employees()
            else:
                self.show_custom_message("Error",
                                         f"Failed to add employee: {result.get('message', 'Unknown error')}",
                                         "error")

        except Exception as e:
            print(f"❌ Error adding employee: {e}")
            self.show_custom_message("Error", f"Failed to add employee: {str(e)}", "error")

    def show_employee_management(self):
        """Show employee management page"""
        try:
            print("📋 Switching to employee management page...")
            self.ui.AdminStackedWidget.setCurrentIndex(1)

            # Clear search if exists
            if hasattr(self.ui, 'YearAdminInput_2'):
                self.ui.YearAdminInput_2.setText("")

            # Load employee data
            self.load_employees()

        except Exception as e:
            print(f"❌ Error showing employee management: {e}")

    def handle_clock_in(self):
        """Handle clock in button click"""
        if not self.staff_controller:
            return

        result = self.staff_controller.clock_in()

        if result["success"]:
            self.clock_in_time = result["clock_in_time"]
            time_str = self.clock_in_time.strftime("%I:%M:%S %p")
            self.show_custom_message("Clock In", f"Clocked in at {time_str}", "success")

            # Refresh dashboard and attendance table
            QTimer.singleShot(500, self.load_staff_dashboard)
            QTimer.singleShot(500, self.load_attendance_history)
        else:
            self.show_custom_message("Clock In Failed", result["message"], "error")

    def handle_clock_out(self):
        """Handle clock out button click - WITH IMMEDIATE TABLE UPDATE"""
        if not self.staff_controller:
            self.show_custom_message("Clock Out Failed", "Not logged in!", "error")
            return

        result = self.staff_controller.clock_out()

        if result["success"]:
            time_str = result["clock_out_time"].strftime("%I:%M:%S %p")
            duration = result.get("duration_hours", 0)
            duration_str = f"{duration:.2f} hours" if duration else ""

            message = f"Clocked out at {time_str}"
            if duration_str:
                message += f"\nDuration: {duration_str}"

            self.show_custom_message("Clock Out", message, "success")
            self.clock_in_time = None

            # IMMEDIATELY refresh dashboard and attendance table
            QTimer.singleShot(300, self.load_staff_dashboard)
            QTimer.singleShot(300, self.load_attendance_history)  # This updates the table immediately
        else:
            self.show_custom_message("Clock Out Failed", result["message"], "error")

    def save_system_settings(self):
        """Save system settings"""
        try:
            print("Saving system settings...")
            self.show_custom_message("Info", "System settings saved successfully", "success")
        except Exception as e:
            logging.error(f"Error saving system settings: {e}")

    def load_admin_dashboard(self):
        """Load admin dashboard with graphs"""
        try:
            print("📊 Loading admin dashboard...")

            # Load dashboard statistics
            self.load_admin_dashboard_stats()

            # Initialize graphs
            self.simple_initialize_graphs()

            # LOAD TIME ADJUSTMENT REQUESTS
            self.load_time_adjustment_requests()

            print("✅ Admin dashboard loaded with graphs and time adjustment")

        except Exception as e:
            print(f"❌ Error loading admin dashboard: {e}")

    def simple_initialize_graphs(self):
        """Initialize graphs"""
        try:
            print("🔄 Initializing graphs...")

            if hasattr(self.ui, 'MathPlotStackedWidget'):
                # Clear existing widgets
                while self.ui.MathPlotStackedWidget.count() > 0:
                    widget = self.ui.MathPlotStackedWidget.widget(0)
                    widget.deleteLater()
                    self.ui.MathPlotStackedWidget.removeWidget(widget)

                # Create graph widget
                from viewer.graph_widget import GraphWidget
                self.graph_widget = GraphWidget()
                self.ui.MathPlotStackedWidget.addWidget(self.graph_widget)

                # Plot initial graph
                self.graph_widget.plot_present_graph()

                # Connect buttons
                self.connect_graph_buttons()

                print("✅ Graphs loaded successfully!")

            else:
                print("❌ MathPlotStackedWidget not found")

        except Exception as e:
            print(f"❌ Error initializing graphs: {e}")
            import traceback
            traceback.print_exc()

    def connect_graph_buttons(self):
        """Maps Admin KPI cards to unique Graph functions"""
        try:
            # Disconnect old ones if any (safe-guard)
            self.ui.AdminPresentButton.clicked.connect(self.graph_widget.plot_present_graph)
            self.ui.AdminLateButton.clicked.connect(self.graph_widget.plot_late_graph)
            self.ui.AdminAbsentButton.clicked.connect(self.graph_widget.plot_absent_graph)
            self.ui.AdminTotalEmployeeButton.clicked.connect(self.graph_widget.plot_total_employee_graph)
            self.ui.AdminEmployeeOnLeaveButton.clicked.connect(self.graph_widget.plot_on_leave_graph)

            # Initial View: Present Graph
            self.graph_widget.plot_present_graph()

        except Exception as e:
            print(f"⚠️ Link error: {e}")

    def safe_plot_graph(self, graph_type):
        """Refreshes the professional view based on selection"""
        if not hasattr(self, 'graph_widget'):
            return

        if graph_type == 'present':
            self.graph_widget.plot_present_graph()
        elif graph_type == 'late':
            self.graph_widget.plot_late_graph()
        elif graph_type == 'absent':
            self.graph_widget.plot_absent_graph()
        elif graph_type == 'on_leave':
            self.graph_widget.plot_on_leave_graph()

    def safe_plot_graph(self, graph_type):
        """Safely plot a graph with better error handling"""
        try:
            print(f"📊 Attempting to plot {graph_type} graph...")

            if hasattr(self, 'graph_widget') and self.graph_widget:
                if graph_type == 'present':
                    self.graph_widget.plot_present_graph()
                    print("✅ Present graph plotted")
                elif graph_type == 'late':
                    self.graph_widget.plot_late_graph()
                    print("✅ Late graph plotted")
                elif graph_type == 'absent':
                    self.graph_widget.plot_absent_graph()
                    print("✅ Absent graph plotted")
                elif graph_type == 'total_employee':
                    self.graph_widget.plot_total_employee_graph()
                    print("✅ Total employee graph plotted")
                elif graph_type == 'on_leave':
                    self.graph_widget.plot_on_leave_graph()
                    print("✅ On leave graph plotted")
                else:
                    print(f"❌ Unknown graph type: {graph_type}")

            else:
                print("❌ Graph widget not initialized")

        except Exception as e:
            print(f"❌ Error plotting {graph_type} graph: {e}")
            import traceback
            traceback.print_exc()

    def load_admin_dashboard_stats(self):
        """Load admin dashboard statistics"""
        try:
            from models.employee_data import Employee

            employee_model = Employee()
            stats = employee_model.get_dashboard_stats()

            print(f"📊 Admin Dashboard Stats: {stats}")

            if hasattr(self.ui, 'AdminPresentOutput'):
                present = stats.get('present_today', 0)
                self.ui.AdminPresentOutput.setText(str(present))

            if hasattr(self.ui, 'AdminLateOutput'):
                late = stats.get('late_today', 0)
                self.ui.AdminLateOutput.setText(str(late))

            if hasattr(self.ui, 'AdminAbsentOutput'):
                absent = stats.get('absent_today', 0)
                self.ui.AdminAbsentOutput.setText(str(absent))

            if hasattr(self.ui, 'AdminTotalEmployeeOutput'):
                total = stats.get('total_employees', 0)
                self.ui.AdminTotalEmployeeOutput.setText(str(total))

            if hasattr(self.ui, 'AdminOnLeaveOutput'):
                on_leave = stats.get('on_leave', 0)
                self.ui.AdminOnLeaveOutput.setText(str(on_leave))

            print("✅ Admin dashboard stats updated")

        except Exception as e:
            print(f"❌ Error loading admin dashboard stats: {e}")

    def load_staff_dashboard(self):
        """Load staff dashboard data"""
        if not self.staff_controller:
            return

        try:
            print("📊 Loading staff dashboard...")
            data = self.staff_controller.get_dashboard_data()

            # Display user info
            if self.current_user:
                if hasattr(self.ui, 'EmployeeName'):
                    full_name = self.current_user.get('full_name', self.current_user.get('username', ''))
                    self.ui.EmployeeName.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.ui.EmployeeName.setText(f"<b>{full_name}</b>")

            if hasattr(self.ui, 'EmployeeIDOutput'):
                self.ui.EmployeeIDOutput.setText(f"EMP{self.current_user['id']}")

            # Display today's status
            if data["today_status"]:
                today_data = data["today_status"]
                status = today_data.get("status", "Not Clocked In")

                if hasattr(self.ui, 'StatusOutput'):
                    self.ui.StatusOutput.setText(status.capitalize())

                self.update_status_ui(status)

                print(f"📅 Today's status: {status}")
            else:
                if hasattr(self.ui, 'StatusOutput'):
                    self.ui.StatusOutput.setText("Not Clocked In")
                self.update_status_ui("Not Clocked In")

                print("📅 No attendance today")

            # Display summary statistics
            if data["summary"]:
                if hasattr(self.ui, 'PresentOutput'):
                    self.ui.PresentOutput.setText(str(data["summary"]["present_days"] or 0))
                if hasattr(self.ui, 'AbsentOutput'):
                    self.ui.AbsentOutput.setText(str(data["summary"]["absent_days"] or 0))
                if hasattr(self.ui, 'LabelOutput'):
                    self.ui.LabelOutput.setText(str(data["summary"]["late_days"] or 0))

                print(
                    f"📈 Summary: Present={data['summary']['present_days']}, Absent={data['summary']['absent_days']}, Late={data['summary']['late_days']}")

            print("✅ Staff dashboard loaded")

        except Exception as e:
            print(f"❌ Error loading staff dashboard: {e}")

    def load_attendance_history(self):
        """Load and display attendance history for staff - WITH COLOR CODING"""
        if not self.staff_controller:
            return

        try:
            records = self.staff_controller.get_attendance_history()
            self.display_attendance_table_with_color(records)  # Use new method with color coding

            print(f"📊 Loaded {len(records)} attendance records with color coding")

        except Exception as e:
            print(f"❌ Error loading attendance history: {e}")

    def load_my_requests(self):
        """Load my requests"""
        try:
            if not self.staff_request_controller:
                return

            print("📋 Loading my requests...")
            # Your existing requests code here

        except Exception as e:
            print(f"❌ Error loading my requests: {e}")

    def display_attendance_table_with_color(self, records):
        """Display attendance records in table WITH FORMAL DESIGN SIMILAR TO TIME ADJUSTMENT"""
        try:
            from PyQt6.QtWidgets import QTableView
            from PyQt6.QtGui import QStandardItemModel, QStandardItem, QFont, QColor
            from PyQt6.QtCore import Qt

            if hasattr(self.ui, 'scrollArea') and self.ui.scrollArea:
                # Create table view with formal design
                attendance_table = QTableView()
                attendance_table.setFixedWidth(1141)
                attendance_table.horizontalHeader().setHighlightSections(False)
                attendance_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

                # Hide row numbers on left side
                attendance_table.verticalHeader().setVisible(False)

                # Create model
                model = QStandardItemModel(0, 5)
                model.setHorizontalHeaderLabels(['DATE', 'CLOCK IN', 'CLOCK OUT', 'DURATION', 'STATUS'])

                print(f"📋 Creating formal table with {len(records)} rows")

                # Fill table with data
                for record in records:
                    # Date
                    date_item = QStandardItem(record.get('date', ''))
                    date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                    # Clock In
                    clock_in = record.get('clock_in', '--:--:-- --')
                    clock_in_item = QStandardItem(clock_in)
                    clock_in_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                    # Clock Out
                    clock_out = record.get('clock_out', '--:--:-- --')
                    clock_out_item = QStandardItem(clock_out)
                    clock_out_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                    # Duration
                    duration = record.get('duration', '--:--')
                    duration_item = QStandardItem(duration)
                    duration_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                    # Status with color coding
                    status_text = record.get('status', '')
                    status_item = QStandardItem(status_text.upper())
                    status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                    # Apply color based on status
                    status = record.get('status', '').lower()
                    if 'present' in status:
                        # Green for present
                        status_item.setForeground(QColor(0, 128, 0))  # Dark green text
                        status_item.setBackground(QColor(230, 245, 230))  # Light green background
                    elif 'late' in status:
                        # Orange for late
                        status_item.setForeground(QColor(255, 140, 0))  # Orange text
                        status_item.setBackground(QColor(255, 248, 230))  # Light orange background
                    elif 'absent' in status:
                        # Red for absent
                        status_item.setForeground(QColor(220, 20, 60))  # Crimson text
                        status_item.setBackground(QColor(255, 230, 230))  # Light red background
                    elif 'ot' in status or 'overtime' in status:
                        # Blue for overtime
                        status_item.setForeground(QColor(0, 0, 139))  # Dark blue text
                        status_item.setBackground(QColor(230, 240, 255))  # Light blue background
                    else:
                        # Default gray for other statuses
                        status_item.setForeground(QColor(105, 105, 105))  # Dim gray text
                        status_item.setBackground(QColor(245, 245, 245))  # Light gray background

                    # Add row to model
                    model.appendRow([date_item, clock_in_item, clock_out_item, duration_item, status_item])

                # Set model
                attendance_table.setModel(model)

                # Apply formal styling
                attendance_table.setStyleSheet("""
                    QTableView {
                        background-color: white;
                        alternate-background-color: #f9f9f9;
                        gridline-color: #e0e0e0;
                        font-size: 11pt;
                        font-family: 'Segoe UI', Arial, sans-serif;
                        selection-background-color: #e6f7ff;
                        selection-color: black;
                        border: 1px solid #cccccc;
                        border-radius: 4px;
                    }
                    QTableView::item {
                        padding: 10px 8px;
                        border-bottom: 1px solid #f0f0f0;
                    }
                    QTableView::item:selected {
                        background-color: #e6f7ff;
                        border: none;
                    }
                    QHeaderView::section {
                        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                          stop:0 #1C6099, stop:1 #73DFF3);
                        color: white;
                        font-weight: bold;
                        padding: 12px 8px;
                        border: 1px solid #1C6099;
                        font-size: 11pt;
                        font-family: 'Segoe UI', Arial, sans-serif;
                        text-align: center;
                    }
                    
                    /* Style for alternating rows */
                    QTableView QTableCornerButton::section {
                        background-color: #1C6099;
                        border: 1px solid #1C6099;
                    }
                """)

                # Enable alternating row colors
                attendance_table.setAlternatingRowColors(True)

                # Set fonts
                header_font = QFont("Segoe UI", 11, QFont.Weight.Bold)
                attendance_table.horizontalHeader().setFont(header_font)

                content_font = QFont("Segoe UI", 10)
                attendance_table.setFont(content_font)

                # FIXED: Set fixed widths for all columns
                attendance_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

                # Set specific column widths to cover full width (1141px)
                column_widths = {
                    0: 250,  # DATE - wider
                    1: 250,  # CLOCK IN
                    2: 250,  # CLOCK OUT
                    3: 150,  # DURATION
                    4: 241  # STATUS (makes total 1141)
                }

                for col, width in column_widths.items():
                    attendance_table.setColumnWidth(col, width)

                # Set selection behavior
                attendance_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
                attendance_table.setSelectionMode(QTableView.SelectionMode.SingleSelection)

                # Set grid style
                attendance_table.setGridStyle(Qt.PenStyle.SolidLine)

                # Set row height
                attendance_table.verticalHeader().setDefaultSectionSize(40)

                # Remove existing widget if any
                old_widget = self.ui.scrollArea.takeWidget()
                if old_widget:
                    old_widget.deleteLater()

                # Create container for the table
                container = QWidget()
                layout = QVBoxLayout(container)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.addWidget(attendance_table)

                container.setFixedWidth(1141)
                self.ui.scrollArea.setWidget(container)
                self.ui.scrollArea.setMinimumWidth(1141)

                print(f"✅ Formal Attendance table displayed with {len(records)} rows (no row numbers)")

        except Exception as e:
            print(f"❌ Error displaying formal attendance table: {e}")
            import traceback
            traceback.print_exc()

    def update_status_ui(self, status):
        """Update UI elements based on status"""
        print(f"🎨 Updating status UI: {status}")

        if hasattr(self.ui, 'on_off_Shift'):
            if status == "present":
                self.ui.on_off_Shift.setText("On Shift")
                self.ui.on_off_Shift.setStyleSheet("""
                    background-color: #4CAF50; 
                    color: white; 
                    font-size: 14pt; 
                    font-weight: bold;
                    text-align: center;
                    border-radius: 5px;
                    padding: 5px;
                """)
            elif status == "late":
                self.ui.on_off_Shift.setText("Late")
                self.ui.on_off_Shift.setStyleSheet("""
                    background-color: #FF9800; 
                    color: white; 
                    font-size: 14pt; 
                    font-weight: bold;
                    text-align: center;
                    border-radius: 5px;
                    padding: 5px;
                """)
            else:
                self.ui.on_off_Shift.setText("Off Shift")
                self.ui.on_off_Shift.setStyleSheet("""
                    background-color: #D75050; 
                    color: white; 
                    font-size: 14pt; 
                    font-weight: bold;
                    text-align: center;
                    border-radius: 5px;
                    padding: 5px;
                """)
            self.ui.on_off_Shift.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def load_time_adjustment_requests(self):
        """Load time adjustment requests for admin via Controller"""
        try:
            print("🕒 Loading time adjustment requests...")

            # Clean MVC Call
            requests = self.admin_request_controller.get_time_adjustments()

            if not requests:
                print("⚠️ No time adjustment requests found")
                return

            # Table widget creation
            table_widget = QTableWidget()
            table_widget.setColumnCount(6)
            table_widget.setHorizontalHeaderLabels(['Type', 'Employee', 'Date', 'Reason', 'Status', 'Submitted'])
            table_widget.setRowCount(len(requests))

            column_widths = [150, 150, 100, 400, 100, 150]
            for i, width in enumerate(column_widths):
                table_widget.setColumnWidth(i, width)

            for i, req in enumerate(requests):
                table_widget.setItem(i, 0, QTableWidgetItem(req['request_type']))
                table_widget.setItem(i, 1, QTableWidgetItem(req['full_name'] or req['username'] or 'Unknown'))
                table_widget.setItem(i, 2, QTableWidgetItem(str(req['request_date']) if req['request_date'] else ''))

                reason = req['reason'] or ''
                if len(reason) > 80: reason = reason[:77] + "..."
                table_widget.setItem(i, 3, QTableWidgetItem(reason))

                status = req['status'] or 'pending'
                status_item = QTableWidgetItem(status.capitalize())
                table_widget.setItem(i, 4, status_item)

                created_at = req['created_at'].strftime("%Y-%m-%d %I:%M %p") if req['created_at'] else ''
                table_widget.setItem(i, 5, QTableWidgetItem(created_at))

                for col in range(6):
                    item = table_widget.item(i, col)
                    if item: item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            if hasattr(self.ui, 'scrollArea_7'):
                self.ui.scrollArea_7.setWidget(table_widget)

            print("✅ Time adjustment requests loaded successfully")

        except Exception as e:
            print(f"❌ View Error: {e}")

    def load_staff_time_adjustment_requests(self):
        """Show ALL requests in the time adjustment table"""
        try:
            print("🕒 Loading ALL staff requests for time adjustment page...")

            if not self.staff_request_controller or not self.current_user:
                return

            # Get ALL requests
            requests = self.staff_request_controller.get_my_requests()

            print(f"📋 Found {len(requests)} total requests")

            # Show ALL requests in the table (not just time adjustment)
            self.setup_time_adjustment_tableview(requests)

            # Update the label to show total requests, not just pending
            if hasattr(self.ui, 'PendingRequestOutput'):
                total_requests = len(requests)
                pending_count = len([r for r in requests if r['status'].lower() == 'pending'])

                self.ui.PendingRequestOutput.setText(f"All Requests ({total_requests}) | Pending ({pending_count})")

                # Simple clean styling - NO BORDERS
                self.ui.PendingRequestOutput.setStyleSheet("border: none; background: transparent;")

                # Optional: Add font styling
                if pending_count > 0:
                    self.ui.PendingRequestOutput.setStyleSheet("""
                        border: none;
                        background: transparent;
                        font-size: 12pt;
                        font-weight: bold;
                        color: #ff9900;
                    """)
                else:
                    self.ui.PendingRequestOutput.setStyleSheet("""
                        border: none;
                        background: transparent;
                        font-size: 12pt;
                        color: #666;
                    """)

            print("✅ All requests loaded successfully into time adjustment table")

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

    def setup_time_adjustment_tableview(self, requests):
        """Setup the TimeAdjustmentRequestOutputTableView with data - FORMAL DESIGN"""
        try:
            if not hasattr(self.ui, 'TimeAdjustmentRequestOutputTableView'):
                print("❌ TimeAdjustmentRequestOutputTableView not found")
                return

            from PyQt6.QtGui import QStandardItemModel, QStandardItem, QFont
            from PyQt6.QtCore import Qt

            # Create model
            model = QStandardItemModel(0, 5)
            model.setHorizontalHeaderLabels(['REQUEST TYPE', 'DATE', 'REASON', 'STATUS', 'SUBMITTED'])

            # Add ALL requests to the table with color coding
            for req in requests:
                # Create items
                type_item = QStandardItem(req['type'])
                type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                date_item = QStandardItem(req['date'])
                date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                # Reason (truncate if too long)
                reason = req['reason']
                if len(reason) > 80:
                    reason = reason[:77] + "..."
                reason_item = QStandardItem(reason)
                reason_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

                # Status with color coding
                status_item = QStandardItem(req['status'].upper())
                status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                # Apply color based on status
                status = req['status'].lower()
                if status == 'approved':
                    status_item.setForeground(QColor(0, 128, 0))  # Green
                    status_item.setBackground(QColor(230, 255, 230))  # Light green background
                elif status == 'declined':
                    status_item.setForeground(QColor(220, 20, 60))  # Red
                    status_item.setBackground(QColor(255, 230, 230))  # Light red background
                elif status == 'pending':
                    status_item.setForeground(QColor(0, 0, 139))  # Dark blue
                    status_item.setBackground(QColor(230, 240, 255))  # Light blue background

                # Submitted date
                submitted = req.get('created_at', '--')
                submitted_item = QStandardItem(submitted)
                submitted_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                # Add row
                model.appendRow([type_item, date_item, reason_item, status_item, submitted_item])

            # Set model
            self.ui.TimeAdjustmentRequestOutputTableView.setModel(model)
            self.ui.TimeAdjustmentRequestOutputTableView.horizontalHeader().setHighlightSections(False)
            self.ui.TimeAdjustmentRequestOutputTableView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

            # HIDE ROW NUMBERS ON LEFT SIDE
            self.ui.TimeAdjustmentRequestOutputTableView.verticalHeader().setVisible(False)

            # Apply formal styling
            self.ui.TimeAdjustmentRequestOutputTableView.setStyleSheet("""
                QTableView {
                    background-color: white;
                    alternate-background-color: #f9f9f9;
                    gridline-color: #e0e0e0;
                    font-size: 11pt;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    selection-background-color: #e6f7ff;
                    selection-color: black;
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                }
                QTableView::item {
                    padding: 10px 8px;
                    border-bottom: 1px solid #f0f0f0;
                }
                QTableView::item:selected {
                    background-color: #e6f7ff;
                    border: none;
                }
                QHeaderView::section {
                    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                      stop:0 #1C6099, stop:1 #73DFF3);
                    color: white;
                    font-weight: bold;
                    padding: 12px 8px;
                    border: 1px solid #1C6099;
                    font-size: 11pt;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    text-align: center;
                }
                /* Style for alternating rows */
                QTableView QTableCornerButton::section {
                    background-color: #1C6099;
                    border: 1px solid #1C6099;
                }
            """)

            # Enable alternating row colors
            self.ui.TimeAdjustmentRequestOutputTableView.setAlternatingRowColors(True)

            # Set font for headers
            header_font = QFont("Segoe UI", 11, QFont.Weight.Bold)
            self.ui.TimeAdjustmentRequestOutputTableView.horizontalHeader().setFont(header_font)

            # Set font for content
            content_font = QFont("Segoe UI", 10)
            self.ui.TimeAdjustmentRequestOutputTableView.setFont(content_font)

            # Resize columns with better proportions
            self.ui.TimeAdjustmentRequestOutputTableView.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.Interactive)

            column_widths = {
                0: 180,  # REQUEST TYPE
                1: 120,  # DATE
                2: 400,  # REASON
                3: 120,  # STATUS
                4: 180  # SUBMITTED
            }

            for col, width in column_widths.items():
                self.ui.TimeAdjustmentRequestOutputTableView.setColumnWidth(col, width)

            # Make the last column stretch
            self.ui.TimeAdjustmentRequestOutputTableView.horizontalHeader().setStretchLastSection(True)

            # Set selection behavior
            self.ui.TimeAdjustmentRequestOutputTableView.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
            self.ui.TimeAdjustmentRequestOutputTableView.setSelectionMode(QTableView.SelectionMode.SingleSelection)

            # Set grid style
            self.ui.TimeAdjustmentRequestOutputTableView.setGridStyle(Qt.PenStyle.SolidLine)

            # Set row height
            self.ui.TimeAdjustmentRequestOutputTableView.verticalHeader().setDefaultSectionSize(40)

            print(f"✅ Formal TableView setup with {len(requests)} rows (no row numbers)")

        except Exception as e:
            print(f"❌ Error setting up TableView: {e}")
            import traceback
            traceback.print_exc()

    def debug_ui_structure(self):
        """Debug method to see UI structure - WITH ERROR HANDLING"""
        print("\n🔍 DEBUGGING UI STRUCTURE:")

        # Check request panel
        try:
            if hasattr(self.ui, 'requestPanel'):
                print(f"✅ requestPanel exists")
                # Don't access children() as they might be deleted
        except Exception as e:
            print(f"⚠️  Error checking requestPanel: {e}")

        # Check scroll areas
        for i in range(1, 11):
            try:
                attr_name = f'scrollArea_{i}'
                if hasattr(self.ui, attr_name):
                    scroll_area = getattr(self.ui, attr_name)
                    print(f"✅ {attr_name} exists")
                    print(f"   Object name: {scroll_area.objectName()}")
            except Exception as e:
                print(f"⚠️  Error checking {attr_name}: {e}")

        # Check table views - WITH SAFE ACCESS
        table_views = ['TimeAdjustmentRequestOutputTableView',
                       'ClockOutOutputsTableView',
                       'AnnouncementOutputTableView',
                       'EmployeeManagementTableView',
                       'ReportsTableView']

        for tv in table_views:
            try:
                if hasattr(self.ui, tv):
                    # Check if the object still exists by trying to access a simple property
                    table_view = getattr(self.ui, tv)
                    # Use isVisible() or objectName() which are safer than parent()
                    print(f"✅ {tv} exists")
                    print(f"   Object name: {table_view.objectName()}")
            except RuntimeError as e:
                if "wrapped C/C++ object" in str(e):
                    print(f"⚠️  {tv}: Object has been deleted (was logged out)")
                else:
                    print(f"⚠️  Error checking {tv}: {e}")
            except Exception as e:
                print(f"⚠️  Error checking {tv}: {e}")

    def debug_request_types(self):
        """Debug method to see all available request types"""
        try:
            from database.database import Database
            db = Database()

            # Get all distinct request types from database
            query = "SELECT DISTINCT request_type FROM requests ORDER BY request_type"
            result = db.execute_query(query)

            print("\n🔍 ALL REQUEST TYPES IN DATABASE:")
            for row in result:
                print(f"   - {row['request_type']}")

            # Also check what types are in the users table
            user_query = """
            SELECT id, username, 
                   (SELECT COUNT(*) FROM requests WHERE user_id = users.id) as request_count
            FROM users 
            WHERE id = %s
            """
            user_result = db.fetch_one(user_query, (self.current_user['id'],))

            if user_result:
                print(f"\n📊 User {user_result['username']} has {user_result['request_count']} total requests")

        except Exception as e:
            print(f"❌ Error debugging request types: {e}")

    def show_staff_time_adjustment_page(self):
        """Switch to staff time adjustment page and refresh data with formal design"""
        print("📋 Switching to staff time adjustment page...")
        self.ui.stackedWidget_3.setCurrentIndex(2)  # Time adjustment page

        # Apply initial styling
        if hasattr(self.ui, 'TimeAdjustmentRequestOutputTableView'):
            # Hide row numbers immediately
            self.ui.TimeAdjustmentRequestOutputTableView.verticalHeader().setVisible(False)

            # Apply basic styling
            self.ui.TimeAdjustmentRequestOutputTableView.setStyleSheet("""
                QTableView {
                    background-color: white;
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                }
            """)

        # Refresh the table with a small delay
        QTimer.singleShot(50, self.load_staff_time_adjustment_requests)

    def show_edit_employee_frame(self, employee_id, employee_name, username, email, role, status):
        """Show edit frame for employee details"""
        try:
            print(f"✏️ Opening edit frame for Employee ID: {employee_id}, Name: {employee_name}")

            # Create edit dialog/frame
            from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                         QLineEdit, QComboBox, QPushButton, QFormLayout,
                                         QMessageBox, QFrame, QWidget)
            from PyQt6.QtCore import Qt, pyqtSignal
            from PyQt6.QtGui import QFont

            # Create dialog
            edit_dialog = QDialog(self)
            edit_dialog.setWindowTitle(f"Edit Employee: {employee_name}")
            edit_dialog.setFixedSize(500, 600)
            edit_dialog.setModal(True)

            # Main layout
            main_layout = QVBoxLayout(edit_dialog)
            main_layout.setSpacing(15)
            main_layout.setContentsMargins(25, 25, 25, 25)

            # Title
            title_label = QLabel(f"EDIT EMPLOYEE: {employee_name.upper()}")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label.setStyleSheet("""
                font-size: 16pt;
                font-weight: bold;
                color: #004c8c;
                padding-bottom: 10px;
                border-bottom: 2px solid #00aaff;
                background: transparent;
            """)
            main_layout.addWidget(title_label)

            # Create form frame
            form_frame = QFrame()
            form_frame.setStyleSheet("""
                QFrame {
                    background-color: #f9f9f9;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 15px;
                }
            """)

            form_layout = QFormLayout(form_frame)
            form_layout.setSpacing(15)
            form_layout.setContentsMargins(20, 20, 20, 20)

            # Employee ID (read-only)
            id_label = QLabel("Employee ID:")
            id_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
            id_value = QLabel(f"EMP{employee_id}")
            id_value.setStyleSheet("""
                font-size: 11pt;
                padding: 8px;
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 4px;
            """)
            form_layout.addRow(id_label, id_value)

            # Full Name
            name_label = QLabel("Full Name:")
            name_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
            self.name_input = QLineEdit()
            self.name_input.setText(employee_name)
            self.name_input.setStyleSheet("""
                font-size: 11pt;
                padding: 10px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
            """)
            form_layout.addRow(name_label, self.name_input)

            # Username
            username_label = QLabel("Username:")
            username_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
            self.username_input = QLineEdit()
            self.username_input.setText(username)
            self.username_input.setStyleSheet("""
                font-size: 11pt;
                padding: 10px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
            """)
            form_layout.addRow(username_label, self.username_input)

            # Email
            email_label = QLabel("Email:")
            email_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
            self.email_input = QLineEdit()
            self.email_input.setText(email)
            self.email_input.setStyleSheet("""
                font-size: 11pt;
                padding: 10px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
            """)
            form_layout.addRow(email_label, self.email_input)

            # Role
            role_label = QLabel("Role:")
            role_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
            self.role_combo = QComboBox()
            self.role_combo.addItems(["Staff", "Admin", "Manager"])
            self.role_combo.setCurrentText(role)
            self.role_combo.setStyleSheet("""
                font-size: 11pt;
                padding: 10px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
            """)
            form_layout.addRow(role_label, self.role_combo)

            # Status
            status_label = QLabel("Status:")
            status_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
            self.status_combo = QComboBox()
            self.status_combo.addItems(["Active", "Inactive", "On Leave"])
            self.status_combo.setCurrentText(status)
            self.status_combo.setStyleSheet("""
                font-size: 11pt;
                padding: 10px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
            """)
            form_layout.addRow(status_label, self.status_combo)

            main_layout.addWidget(form_frame)

            # Button layout
            button_layout = QHBoxLayout()
            button_layout.setSpacing(20)
            button_layout.addStretch()

            # Cancel button
            cancel_button = QPushButton("Cancel")
            cancel_button.setFixedSize(120, 45)
            cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
            cancel_button.setStyleSheet("""
                QPushButton {
                    background-color: #f8f9fa;
                    color: #333333;
                    border: 1px solid #ced4da;
                    border-radius: 6px;
                    font-size: 11pt;
                    font-weight: bold;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #e9ecef;
                    border: 1px solid #6c757d;
                }
            """)
            cancel_button.clicked.connect(edit_dialog.reject)
            button_layout.addWidget(cancel_button)

            # Save button
            save_button = QPushButton("Save Changes")
            save_button.setFixedSize(150, 45)
            save_button.setCursor(Qt.CursorShape.PointingHandCursor)
            save_button.setStyleSheet("""
                QPushButton {
                    background-color: #00aaff;
                    color: white;
                    border: 1px solid #00aaff;
                    border-radius: 6px;
                    font-size: 11pt;
                    font-weight: bold;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #0088cc;
                    border: 1px solid #0088cc;
                }
            """)
            save_button.clicked.connect(lambda: self.save_employee_changes(
                employee_id, edit_dialog))
            button_layout.addWidget(save_button)

            button_layout.addStretch()
            main_layout.addLayout(button_layout)

            # Status label
            self.edit_status_label = QLabel("")
            self.edit_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.edit_status_label.setWordWrap(True)
            main_layout.addWidget(self.edit_status_label)

            # Show dialog
            edit_dialog.exec()

        except Exception as e:
            print(f"❌ Error showing edit frame: {e}")
            import traceback
            traceback.print_exc()

    def finalize_employee_save(self, dialog, employee_name):
        """Finalize employee save with success message"""
        self.edit_status_label.setText(f"✅ {employee_name} updated successfully!")
        self.edit_status_label.setStyleSheet("color: #00aa00; font-weight: bold;")

        # Close dialog after 1.5 seconds
        QTimer.singleShot(1500, dialog.accept)

        # Refresh employee table
        QTimer.singleShot(1600, lambda: self.load_employees())

    def save_employee_changes_with_role(self, employee_id, dialog):
        """Professional UI Logic - No SQL here!"""
        try:
            print(f"💾 Saving changes for Employee ID: {employee_id}")

            # 1. Collect values from UI inputs
            new_name = self.edit_name_input.text().strip()
            new_username = self.edit_username_input.text().strip()
            new_email = self.edit_email_input.text().strip()
            new_role = self.edit_role_combo.currentText().lower()

            # 2. Basic UI Validation
            if not new_name or not new_username or "@" not in new_email:
                self.show_custom_message("Validation Error", "All fields are required and email must be valid.",
                                         "error")
                return

            # 3. Clean MVC Call: Ask the controller to do the work
            result = self.employee_controller.update_employee(
                employee_id, new_name, new_username, new_email, new_role
            )

            # 4. Handle the response
            if result["success"]:
                self.show_custom_message("Success", result["message"], "success")
                dialog.accept()  # Close the popup

                # Refresh the table with a small delay to ensure DB is ready
                QTimer.singleShot(300, lambda: self.load_employees())
            else:
                self.show_custom_message("Error", result["message"], "error")

        except Exception as e:
            print(f"❌ View Error: {e}")
            self.show_custom_message("System Error", f"Failed to save changes: {str(e)}", "error")

    def generate_report(self):
        """Dispatches the correct logic using a Step-by-Step Dialog flow"""
        try:
            from viewer.report_dialogs import ReportTypeSelector, MonthlySelectorDialog, AnnualSelectorDialog
            from viewer.date_selector_dialog import DateSelectorDialog

            selector = ReportTypeSelector(self)
            if not selector.exec():
                return

            choice = selector.selected_type

            if choice == "Daily":
                date_dialog = DateSelectorDialog(self)
                if date_dialog.exec():
                    db_date, friendly_date = date_dialog.get_selected_date()
                    # SAVE THE TITLE FOR EXPORT
                    self.last_generated_report_name = f"Daily Attendance Report - {friendly_date}"
                    self.generate_daily_attendance_report(db_date, friendly_date)


            elif choice == "Monthly":
                month_dialog = MonthlySelectorDialog(self)

                if month_dialog.exec():
                    month_num, year, month_name = month_dialog.get_values()
                    self.last_generated_report_name = f"Monthly Summary Report - {month_name} {year}"
                    data = self.report_controller.get_monthly_report(month_num, year)

                    if not data:
                        self.show_custom_message("No Records", f"No data found for {month_name} {year}", "info")
                        return

                    total_presence_count = sum((int(r['present_days']) + int(r['late_days'])) for r in data)
                    stats = {
                        "total_staff": len(data),
                        "total_man_hours": round(sum(float(r['total_hours_worked']) for r in data), 1),
                        "total_presence": total_presence_count  # Added this for the popup graph
                    }
                    from viewer.report_popup_dialog import ReportPopupDialog

                    popup = ReportPopupDialog(self, self.last_generated_report_name, stats, data, "Monthly")
                    popup.exec()
                    self.display_monthly_report_data(data, month_num, int(year), "", "")

            elif choice == "Annual":
                annual_dialog = AnnualSelectorDialog(self)

                if annual_dialog.exec():
                    year = annual_dialog.get_year()
                    self.last_generated_report_name = f"Annual Summary Report - {year}"
                    data = self.report_controller.get_annual_report(year)

                    if not data:
                        self.show_custom_message("No Records", f"No data found for {year}", "info")
                        return

                    stats = {
                        "audit_year": year,
                        "total_presence": sum(int(r['total_presence']) for r in data),
                        "peak_month": max(data, key=lambda x: x['total_presence'])['month_name']
                    }

                    from viewer.report_popup_dialog import ReportPopupDialog
                    popup = ReportPopupDialog(self, self.last_generated_report_name, stats, data, "Annual")
                    popup.exec()
                    self.display_annual_report_data(data, year)

        except Exception as e:
            print(f"Error in Wizard Dispatcher: {e}")
            self.show_custom_message("System Error", f"Failed to process report: {str(e)}", "error")

    def display_annual_report_data(self, data, year):
        """Populates the main UI table with Annual Summary data and professional outline"""
        try:
            from PyQt6.QtGui import QStandardItemModel, QStandardItem
            from PyQt6.QtCore import Qt

            model = QStandardItemModel()
            headers = ['MONTH', 'PRESENT DAYS', 'LATE DAYS', 'ABSENT DAYS', 'TOTAL HOURS WORKED']
            model.setHorizontalHeaderLabels(headers)

            for record in data:
                month_item = QStandardItem(str(record.get('month_name', '')))
                present_item = QStandardItem(str(record.get('present_days', 0)))
                late_item = QStandardItem(str(record.get('late_days', 0)))
                absent_item = QStandardItem(str(record.get('absent_days', 0)))
                hours_item = QStandardItem(f"{float(record.get('total_hours_worked', 0)):.2f}")

                # Center align items
                for item in [month_item, present_item, late_item, absent_item, hours_item]:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                model.appendRow([month_item, present_item, late_item, absent_item, hours_item])

            self.ui.ReportsTableView.setModel(model)
            self.ui.ReportsTableView.verticalHeader().setVisible(False)

            # --- STYLE: ADDED BORDER OUTLINE ---
            self.ui.ReportsTableView.setStyleSheet("""
                QTableView {
                    border: 1px solid #A2A2A2;
                    background-color: white;
                    alternate-background-color: #f9f9f9;
                }
            """)

            # Re-apply Header Gradient
            self.ui.ReportsTableView.horizontalHeader().setStyleSheet("""
                QHeaderView::section {
                    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1C6099, stop:1 #73DFF3);
                    color: white; font-weight: bold; padding: 8px; border: 1px solid #1C6099;
                }
            """)
            self.ui.ReportsTableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

            print(f"✅ Main UI Table updated with Annual data for {year}")

        except Exception as e:
            print(f"Error displaying annual table: {e}")

    def generate_daily_attendance_report(self, target_date, friendly_date):
        try:
            real_data = self.report_controller.get_daily_audit(target_date)

            if not real_data:
                self.show_custom_message("No Records", f"No attendance logs found for {friendly_date}.", "info")
                return

            res = self.report_controller.get_daily_summary_stats(target_date)

            total_count = res['total'] if res else 0
            present_count = res['present'] if res else 0
            absent_count = max(0, total_count - present_count)

            real_stats = {
                'total_employees': total_count,
                'present_today': present_count,
                'late_today': res['late'] if res else 0,
                'absent_today': absent_count,
                'attendance_rate': f"{(present_count / total_count * 100) if total_count > 0 else 0 :.1f}%"
            }

            from viewer.report_popup_dialog import ReportPopupDialog
            popup = ReportPopupDialog(self, f"Daily Attendance: {friendly_date}", real_stats, real_data, "Daily")
            popup.exec()

            self.display_report_data_in_table(real_data, real_stats, target_date)

        except Exception as e:
            print(f"Error generating daily report UI: {e}")

    def show_graph_in_new_window(self, stats, month, year):
        """Show graph popup with the SPECIFIC year and month passed in."""
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel

            rate = (stats['present_today'] / stats['total_employees'] * 100) if stats['total_employees'] > 0 else 0
            summary_title = f"📊 DAILY ATTENDANCE - {month} {year}"

            graph_dialog = QDialog(self)
            graph_dialog.setWindowTitle(summary_title)
            graph_dialog.setFixedSize(850, 650)
            graph_dialog.setStyleSheet("background-color: white;")

            layout = QVBoxLayout(graph_dialog)

            # Header
            header = QLabel(summary_title)
            header.setStyleSheet("font-size: 18pt; font-weight: bold; color: #004c8c;")
            header.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(header)

            # Plotting (Simplified Bar Chart)
            fig, ax = plt.subplots(figsize=(6, 4))
            labels = ['Present', 'Late', 'Absent']
            vals = [stats['present_today'], stats['late_today'], stats['absent_today']]
            ax.bar(labels, vals, color=['#4CAF50', '#FF9800', '#F44336'])
            ax.set_ylim(bottom=0)

            canvas = FigureCanvas(fig)
            layout.addWidget(canvas)

            # Stats text using the CORRECT year/month
            info = QLabel(f"Selected Period: {month} {year}\nAttendance Rate: {rate:.1f}%")
            info.setStyleSheet("background-color: #f0f9ff; padding: 15px; border-radius: 10px; font-size: 12pt;")
            layout.addWidget(info)

            graph_dialog.exec()
        except Exception as e:
            print(f"Graph Error: {e}")

    def display_report_data_in_table(self, data, stats, date):
        """Display daily report data in the main background table with professional outline"""
        try:
            from PyQt6.QtGui import QStandardItemModel, QStandardItem, QColor
            from PyQt6.QtCore import Qt

            model = QStandardItemModel()
            headers = ['ID', 'Name', 'Email', 'Status', 'Clock In', 'Clock Out', 'Hours', 'Late (min)']
            model.setHorizontalHeaderLabels(headers)

            for record in data:
                # Employee ID
                emp_id = f"EMP{record.get('employee_id', '')}"
                id_item = QStandardItem(emp_id)

                # Name & Email
                name_item = QStandardItem(record.get('full_name') or record.get('username') or 'Unknown')
                email_item = QStandardItem(record.get('email', 'N/A'))

                # Status Logic
                status = record.get('status')
                if status is None or status == "" or status == "Not Clocked In":
                    status = "Absent"

                status_item = QStandardItem(status.capitalize())

                # Color coding status
                if status.lower() == 'present':
                    status_item.setForeground(QColor(0, 128, 0))  # Green
                elif status.lower() == 'late':
                    status_item.setForeground(QColor(255, 140, 0))  # Orange
                elif status.lower() == 'absent':
                    status_item.setForeground(QColor(220, 20, 60))  # Red

                # Time and Hours
                clock_in_item = QStandardItem(str(record.get('clock_in') or '--:-- --'))
                clock_out_item = QStandardItem(str(record.get('clock_out') or '--:-- --'))
                hours_item = QStandardItem(f"{float(record.get('hours_worked', 0)):.2f}")
                late_item = QStandardItem(str(record.get('late_minutes', 0)))

                # Apply center alignment to all
                for item in [id_item, name_item, email_item, status_item, clock_in_item, clock_out_item, hours_item,
                             late_item]:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                model.appendRow(
                    [id_item, name_item, email_item, status_item, clock_in_item, clock_out_item, hours_item, late_item])

            if hasattr(self.ui, 'ReportsTableView'):
                self.ui.ReportsTableView.setModel(model)
                self.ui.ReportsTableView.verticalHeader().setVisible(False)

                # --- STYLE: ADDED BORDER OUTLINE ---
                self.ui.ReportsTableView.setStyleSheet("""
                    QTableView {
                        border: 1px solid #A2A2A2;
                        background-color: white;
                        alternate-background-color: #f9f9f9;
                        gridline-color: #e0e0e0;
                    }
                """)

                # Gradient Header
                header_style = """
                    QHeaderView::section {
                        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1C6099, stop:1 #73DFF3);
                        color: white;
                        font-weight: bold;
                        padding: 8px;
                        border: 1px solid #1C6099;
                    }
                """
                self.ui.ReportsTableView.horizontalHeader().setStyleSheet(header_style)
                self.ui.ReportsTableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        except Exception as e:
            print(f"ERROR displaying daily report table: {e}")

    def display_empty_report_table(self):
        """Display an empty table when no data is available"""
        try:
            from PyQt6.QtGui import QStandardItemModel
            from PyQt6.QtCore import Qt

            # Create empty model
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(
                ['ID', 'Name', 'Email', 'Status', 'Clock In', 'Clock Out', 'Hours', 'Late (min)'])

            # Add one row with "No data" message
            from PyQt6.QtGui import QStandardItem
            no_data_item = QStandardItem("No attendance data available for today")
            no_data_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            model.appendRow([no_data_item])

            # Set model
            if hasattr(self.ui, 'ReportsTableView'):
                self.ui.ReportsTableView.setModel(model)
                self.ui.ReportsTableView.setColumnWidth(0, 800)

        except Exception as e:
            print(f"Error displaying empty table: {e}")

    def clear_report_cache(self):
        """Clear any cached report data"""
        try:
            # Clear any cached data in the report table
            if hasattr(self.ui, 'ReportsTableView'):
                from PyQt6.QtGui import QStandardItemModel
                empty_model = QStandardItemModel()
                self.ui.ReportsTableView.setModel(empty_model)

            # Clear graph data
            if hasattr(self, 'graph_widget') and self.graph_widget:
                if hasattr(self.graph_widget, 'figure'):
                    self.graph_widget.figure.clear()
                    self.graph_widget.canvas.draw()

            print("✅ Report cache cleared")

        except Exception as e:
            print(f"Error clearing cache: {e}")

    def show_graph_in_new_window(self, stats):
        """Show graph in a new window WITH summary below it - NO TOOLBAR."""
        try:
            from datetime import datetime
            import matplotlib
            import matplotlib.pyplot as plt

            # IMPORTANT: Disable matplotlib toolbar globally for this figure
            matplotlib.rcParams['toolbar'] = 'None'  # This prevents the toolbar

            from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel
            from PyQt6.QtCore import Qt

            # Calculate attendance rate
            attendance_rate = ((stats['present_today'] + stats['late_today']) /
                               stats['total_employees'] * 100) if stats['total_employees'] > 0 else 0

            # Create summary text
            summary = (
                f"📊 DAILY ATTENDANCE REPORT - {datetime.now().strftime('%Y-%m-%d')}\n\n"
                f"• Total Employees: {stats['total_employees']}\n"
                f"• Present: {stats['present_today']}\n"
                f"• Late: {stats['late_today']}\n"
                f"• Absent: {stats['absent_today']}\n"
                f"• On Leave: {stats['on_leave']}\n\n"
                f"📍 Attendance Rate: {attendance_rate:.1f}%"
            )

            # Create a new dialog window
            graph_dialog = QDialog(self)
            graph_dialog.setWindowTitle("✅ Daily Attendance Report")
            graph_dialog.setGeometry(100, 100, 850, 650)

            # Make sure dialog is properly deleted when closed
            graph_dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)

            # Create main layout
            main_layout = QVBoxLayout(graph_dialog)

            # ========== CREATE FIGURE WITHOUT TOOLBAR ==========
            # Create figure with specific backend settings
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

            # Disable toolbar for this specific figure
            fig.canvas.manager.toolbar = None  # Explicitly remove toolbar

            # Data for charts
            categories = ['Present', 'Late', 'Absent', 'On Leave']
            values = [
                stats['present_today'],
                stats['late_today'],
                stats['absent_today'],
                stats['on_leave']
            ]
            colors = ['#4CAF50', '#FF9800', '#F44336', '#2196F3']

            # Bar chart (left)
            bars = ax1.bar(categories, values, color=colors, edgecolor='black', linewidth=1)
            ax1.set_title('Employee Count by Status', fontsize=12, fontweight='bold')
            ax1.set_ylabel('Number of Employees')
            ax1.grid(True, alpha=0.3, linestyle='--')

            # Add value labels on bars
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width() / 2., height + 0.1,
                         f'{value}', ha='center', va='bottom', fontweight='bold')

            # Pie chart (right)
            ax2.pie(values, labels=categories, colors=colors, autopct='%1.1f%%',
                    startangle=90, shadow=True, explode=(0.05, 0, 0, 0))
            ax2.axis('equal')
            ax2.set_title('Attendance Percentage', fontsize=12, fontweight='bold')

            plt.suptitle(f'Daily Attendance Report - {datetime.now().strftime("%Y-%m-%d")}',
                         fontsize=14, fontweight='bold')
            plt.tight_layout()

            # ========== CREATE CANVAS WITHOUT TOOLBAR ==========
            # Create canvas WITHOUT parent to prevent toolbar creation
            canvas = FigureCanvas(fig)

            # ========== ADD WIDGETS TO DIALOG ==========
            main_layout.addWidget(canvas)

            # Add summary label
            summary_label = QLabel(summary)
            summary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            summary_label.setStyleSheet("""
                QLabel {
                    background-color: #e8f5e8;
                    border: 2px solid #4CAF50;
                    border-radius: 10px;
                    padding: 15px;
                    font-family: Arial;
                    font-size: 12pt;
                    margin: 10px;
                }
            """)
            summary_label.setWordWrap(True)
            main_layout.addWidget(summary_label)

            # ========== CLOSE BUTTON ==========
            from PyQt6.QtWidgets import QPushButton, QHBoxLayout

            button_layout = QHBoxLayout()

            close_btn = QPushButton("Close")
            close_btn.setStyleSheet("""
                QPushButton {
                    background-color: #6c757d;
                    color: white;
                    border-radius: 5px;
                    padding: 8px 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #545b62;
                }
            """)

            # Properly close everything
            def close_dialog():
                plt.close(fig)  # Close matplotlib figure
                graph_dialog.accept()  # Close dialog
                graph_dialog.deleteLater()  # Delete dialog

            close_btn.clicked.connect(close_dialog)

            button_layout.addStretch()
            button_layout.addWidget(close_btn)
            main_layout.addLayout(button_layout)

            # ========== SHOW DIALOG ==========
            graph_dialog.exec()

            # Clean up after dialog closes
            plt.close(fig)

            print("DEBUG: Graph with summary shown - NO TOOLBAR")

        except Exception as e:
            print(f"ERROR showing graph in new window: {e}")
            import traceback
            traceback.print_exc()

    def update_main_graph_if_exists(self, stats):
        """Try to update the main UI graph if it exists."""
        try:
            # Check if we have a MathPlotStackedWidget
            if hasattr(self.ui, 'MathPlotStackedWidget'):
                print("DEBUG: Found MathPlotStackedWidget, updating...")

                # Get the current page
                current_index = self.ui.MathPlotStackedWidget.currentIndex()
                current_widget = self.ui.MathPlotStackedWidget.widget(current_index)

                if current_widget:
                    # Clear existing widgets
                    for i in reversed(range(current_widget.layout().count())):
                        widget = current_widget.layout().itemAt(i).widget()
                        if widget:
                            widget.deleteLater()

                    # Create new graph
                    import matplotlib.pyplot as plt
                    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

                    fig, ax = plt.subplots(figsize=(8, 5))

                    categories = ['Present', 'Late', 'Absent', 'On Leave']
                    values = [
                        stats['present_today'],
                        stats['late_today'],
                        stats['absent_today'],
                        stats['on_leave']
                    ]
                    colors = ['#4CAF50', '#FF9800', '#F44336', '#2196F3']

                    bars = ax.bar(categories, values, color=colors)
                    ax.set_title('Daily Attendance', fontsize=14, fontweight='bold')
                    ax.set_ylabel('Employees')

                    for bar, value in zip(bars, values):
                        height = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width() / 2., height + 0.1,
                                f'{value}', ha='center', va='bottom')

                    plt.tight_layout()

                    # Add to widget
                    canvas = FigureCanvas(fig)
                    current_widget.layout().addWidget(canvas)
                    canvas.draw()

                    print("DEBUG: Updated main UI graph")

        except Exception as e:
            print(f"ERROR updating main graph: {e}")

    def generate_monthly_summary_report(self, month, year):
        """Generate Monthly Summary Report."""
        try:
            print(f"DEBUG: Generating monthly summary for {month} {year}")

            from database.database import Database
            from datetime import datetime

            db = Database()

            # Calculate start and end dates for the month
            start_date = f"{year}-{month:02d}-01"

            # Calculate last day of month
            if month == 12:
                end_date = f"{year}-12-31"
            else:
                next_month = month + 1
                end_date = f"{year}-{next_month:02d}-01"
                # Subtract 1 day to get last day of current month
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
                from datetime import timedelta
                end_date_obj = end_date_obj - timedelta(days=1)
                end_date = end_date_obj.strftime("%Y-%m-%d")

            print(f"DEBUG: Date range: {start_date} to {end_date}")

            # Query for monthly summary
            query = """
            SELECT 
                u.id,
                u.full_name,
                u.email,
                COUNT(DISTINCT DATE(a.date)) as days_recorded,
                COUNT(DISTINCT CASE WHEN a.status = 'present' THEN DATE(a.date) END) as present_days,
                COUNT(DISTINCT CASE WHEN a.status = 'late' THEN DATE(a.date) END) as late_days,
                COUNT(DISTINCT CASE WHEN a.status = 'absent' THEN DATE(a.date) END) as absent_days,
                COALESCE(SUM(a.total_hours), 0) as total_hours_worked,
                COALESCE(AVG(a.total_hours), 0) as avg_daily_hours,
                COALESCE(SUM(a.late_minutes), 0) as total_late_minutes
            FROM users u
            LEFT JOIN attendance a ON u.id = a.user_id AND DATE(a.date) BETWEEN %s AND %s
            WHERE u.role = 'staff'
            GROUP BY u.id, u.full_name, u.email
            ORDER BY u.full_name
            """

            monthly_data = db.execute_query(query, (start_date, end_date))

            print(f"DEBUG: Found {len(monthly_data)} records for monthly report")

            if not monthly_data:
                self.show_custom_message("No Data", f"No attendance data found for {month}/{year}", "info")
                self.display_empty_report_table()
                return

            # Display the data
            self.display_monthly_report_data(monthly_data, month, year, start_date, end_date)

            # Show success message
            month_names = ["January", "February", "March", "April", "May", "June",
                           "July", "August", "September", "October", "November", "December"]
            month_name = month_names[month - 1] if 1 <= month <= 12 else f"Month {month}"

            self.show_custom_message("Monthly Report Generated",
                                     f"Monthly summary report for {month_name} {year} generated successfully!\n"
                                     f"Found {len(monthly_data)} employee records.",
                                     "success")

        except Exception as e:
            print(f"ERROR in generate_monthly_summary_report: {e}")
            import traceback
            traceback.print_exc()
            self.show_custom_message("Error", f"Failed to generate monthly report: {str(e)}", "error")

    def display_monthly_report_data(self, data, month, year, start_date, end_date):
        try:
            from PyQt6.QtGui import QStandardItemModel, QStandardItem
            from PyQt6.QtCore import Qt

            model = QStandardItemModel()
            # Changed header to be more specific
            headers = ['EMPLOYEE NAME', 'ON-TIME', 'LATE', 'ABSENT', 'TOTAL HOURS', 'AVG HRS/DAY']
            model.setHorizontalHeaderLabels(headers)

            for record in data:
                name_item = QStandardItem(str(record.get('full_name') or 'Unknown'))
                # Accessing the keys we defined in the Model
                on_time_item = QStandardItem(str(record.get('present_days', 0)))
                late_item = QStandardItem(str(record.get('late_days', 0)))
                absent_item = QStandardItem(str(record.get('absent_days', 0)))

                total_hours = float(record.get('total_hours_worked', 0))
                hours_item = QStandardItem(f"{total_hours:.2f}")
                avg_item = QStandardItem(f"{total_hours / 22:.2f}")  # Approximation

                for item in [name_item, on_time_item, late_item, absent_item, hours_item, avg_item]:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                model.appendRow([name_item, on_time_item, late_item, absent_item, hours_item, avg_item])

            self.ui.ReportsTableView.setModel(model)
            self.ui.ReportsTableView.verticalHeader().setVisible(False)

            # --- STYLE: ADDED BORDER OUTLINE ---
            self.ui.ReportsTableView.setStyleSheet("""
                QTableView {
                    border: 1px solid #A2A2A2;
                    background-color: white;
                    alternate-background-color: #f9f9f9;
                }
            """)

            # Re-apply Header Gradient
            self.ui.ReportsTableView.horizontalHeader().setStyleSheet("""
                QHeaderView::section {
                    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1C6099, stop:1 #73DFF3);
                    color: white; font-weight: bold; padding: 8px; border: 1px solid #1C6099;
                }
            """)
            self.ui.ReportsTableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        except Exception as e:
            print(f"Error displaying monthly report: {e}")

    def execute_query(self, query, params=None):
        """Execute query via database class."""
        print(f"\n🔍 MAIN_WINDOW.PY - Calling database.execute_query")
        print(f"   Query: {query[:50]}..." if len(query) > 50 else f"   Query: {query}")

        if hasattr(self, 'db'):
            result = self.db.execute_query(query, params)
            print(f"   MAIN_WINDOW.PY - Got result from db: {len(result) if isinstance(result, list) else result}")
            return result
        else:
            print("   ERROR: No db attribute in MainWindow!")
            return []

    def update_graph_display(self, report_type):
        """Switch to the correct graph page when report type changes."""
        # Find the index of this report type
        index_map = {
            "Daily Attendance Report": 0,
            "Monthly Summary Report": 1,
        }

        if report_type in index_map:
            self.ui.MathPlotStackedWidget.setCurrentIndex(index_map[report_type])

    def export_to_pdf(self):
        """Professional UI Frame for Exporting - FIXED TO REMOVE DELETED WIDGETS"""
        try:
            from PyQt6.QtWidgets import QFileDialog, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, \
                QFrame
            from PyQt6.QtCore import Qt, QTimer
            import os

            # 1. Check if table has data
            model = self.ui.ReportsTableView.model()
            if not model or model.rowCount() == 0:
                self.show_custom_message("Export Error", "No data available. Please generate a report first.", "error")
                return

            # --- FIXED: Use the saved title instead of the deleted ComboBox ---
            report_display_title = getattr(self, 'last_generated_report_name', "Attendance Report")

            # 2. Setup Dialog
            save_dialog = QDialog(self)
            save_dialog.setWindowTitle("Export Document")
            save_dialog.setFixedSize(550, 400)
            save_dialog.setStyleSheet("background-color: white; border-radius: 10px;")

            layout = QVBoxLayout(save_dialog)
            layout.setContentsMargins(30, 30, 30, 30)
            layout.setSpacing(15)

            header_lbl = QLabel("📄 EXPORT TO PDF")
            header_lbl.setStyleSheet("font-size: 18pt; font-weight: bold; color: #004c8c; border: none;")
            header_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(header_lbl)

            # Info Summary Card
            info_card = QFrame()
            info_card.setStyleSheet("background-color: #f0f9ff; border: 1px solid #00aaff; border-radius: 8px;")
            info_layout = QVBoxLayout(info_card)
            info_title = QLabel("REPORT SUMMARY")
            info_title.setStyleSheet("font-weight: bold; color: #1C6099; border: none; font-size: 10pt;")

            details = QLabel(f"Title: {report_display_title}\nTotal Records: {model.rowCount()}")
            details.setStyleSheet("color: #333; border: none; font-size: 11pt;")

            info_layout.addWidget(info_title)
            info_layout.addWidget(details)
            layout.addWidget(info_card)

            # Filename
            layout.addWidget(QLabel("<b>File Name:</b>"))
            filename_input = QLineEdit()
            clean_name = report_display_title.replace(' ', '_').replace(':', '').replace('-', '')
            filename_input.setText(f"{clean_name}")
            filename_input.setStyleSheet("padding: 10px; border: 1px solid #ccc; border-radius: 5px;")
            layout.addWidget(filename_input)

            # Action Buttons
            btn_layout = QHBoxLayout()
            btn_layout.setSpacing(15)

            cancel_btn = QPushButton("CANCEL")
            cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            cancel_btn.setFixedHeight(45)
            cancel_btn.setStyleSheet(
                "background: #f1f1f1; color: #333; border-radius: 5px; font-weight: bold; border: none;")
            cancel_btn.clicked.connect(save_dialog.reject)

            export_btn = QPushButton("START EXPORT")
            export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            export_btn.setFixedHeight(45)
            export_btn.setStyleSheet(
                "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1C6099, stop:1 #00aaff); color: white; border-radius: 5px; font-weight: bold; border: none;")

            def do_export():
                fname = filename_input.text().strip()
                if not fname.endswith(".pdf"): fname += ".pdf"
                path, _ = QFileDialog.getSaveFileName(self, "Save PDF", fname, "PDF Files (*.pdf)")
                if path:
                    save_dialog.accept()
                    QTimer.singleShot(200, lambda: self.perform_pdf_export(path, model))

            export_btn.clicked.connect(do_export)
            btn_layout.addWidget(cancel_btn)
            btn_layout.addWidget(export_btn)
            layout.addLayout(btn_layout)

            save_dialog.exec()
        except Exception as e:
            print(f"Error showing export UI: {e}")

    def perform_pdf_export(self, file_path, model):
        """Actual PDF Generation Logic - FIXED: Proportional Column Widths"""
        try:
            from reportlab.lib.pagesizes import landscape, letter
            from reportlab.pdfgen import canvas
            from reportlab.lib import colors
            from datetime import datetime
            from PyQt6.QtCore import Qt

            c = canvas.Canvas(file_path, pagesize=landscape(letter))
            width, height = landscape(letter)
            margin = 40  # Slightly smaller margin for more space
            curr_y = height - 60
            table_width = width - (2 * margin)

            # --- 1. HEADER SECTION ---
            c.setFont("Helvetica-Bold", 20)
            c.setFillColor(colors.HexColor("#004c8c"))
            c.drawString(margin, curr_y, "WorkXTrackr - Official Attendance Report")

            c.setFont("Helvetica", 11)
            c.setFillColor(colors.black)
            curr_y -= 25
            report_title = getattr(self, 'last_generated_report_name', "Attendance Report")
            c.drawString(margin, curr_y, f"Report Type: {report_title}")

            curr_y -= 15
            c.drawString(margin, curr_y, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            curr_y -= 15
            c.drawString(margin, curr_y, f"Generated by: {self.current_user.get('full_name', 'Administrator')}")
            curr_y -= 40

            # --- 2. DYNAMIC COLUMN WIDTH LOGIC ---
            col_count = model.columnCount()
            headers = []
            for col in range(col_count):
                headers.append(str(model.headerData(col, Qt.Orientation.Horizontal)))

            # Define proportional widths based on common report types
            # Values are percentages of the total table width
            if "Daily" in report_title:
                # ID(8%), Name(18%), Email(26%), Status(10%), ClockIn(10%), ClockOut(10%), Hours(8%), Late(10%)
                proportions = [0.08, 0.18, 0.26, 0.10, 0.10, 0.10, 0.08, 0.10]
            elif "Monthly" in report_title:
                # Name(30%), Present(14%), Late(14%), Absent(14%), TotalHours(14%), Avg(14%)
                proportions = [0.30, 0.14, 0.14, 0.14, 0.14, 0.14]
            else:  # Annual
                # Month(20%), Present(20%), Late(20%), Absent(20%), Total(20%)
                proportions = [1.0 / col_count] * col_count

            # Convert percentages to actual pixel widths
            col_widths = [p * table_width for p in proportions]

            # --- 3. DRAW TABLE HEADERS ---
            c.setFillColor(colors.HexColor("#1C6099"))
            c.rect(margin, curr_y - 10, table_width, 25, fill=1, stroke=0)

            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 10)

            draw_x = margin
            for i, header in enumerate(headers):
                # Center text within its calculated width
                text_width = c.stringWidth(header, "Helvetica-Bold", 10)
                center_x = draw_x + (col_widths[i] / 2) - (text_width / 2)
                c.drawString(center_x, curr_y, header)
                draw_x += col_widths[i]

            curr_y -= 30

            # --- 4. DRAW TABLE DATA ---
            c.setFont("Helvetica", 9)
            for row in range(model.rowCount()):
                # Handle New Page
                if curr_y < 50:
                    c.showPage()
                    curr_y = height - 60
                    c.setFont("Helvetica", 9)

                # Striped Row Effect
                if row % 2 == 0:
                    c.setFillColor(colors.HexColor("#F1F8FF"))
                    c.rect(margin, curr_y - 10, table_width, 20, fill=1, stroke=0)

                c.setFillColor(colors.black)
                draw_x = margin
                for col in range(col_count):
                    text = str(model.data(model.index(row, col)) or "")

                    # Truncate text if it's still too long for the allocated width (Safety)
                    # Use a small buffer (10px) to prevent collisions
                    available_space = col_widths[col] - 10
                    while c.stringWidth(text, "Helvetica", 9) > available_space and len(text) > 3:
                        text = text[:-4] + "..."

                    # Center the data
                    text_w = c.stringWidth(text, "Helvetica", 9)
                    center_x = draw_x + (col_widths[col] / 2) - (text_w / 2)
                    c.drawString(center_x, curr_y, text)
                    draw_x += col_widths[col]

                curr_y -= 20

            c.save()
            self.show_custom_message("Success", f"Report saved successfully!\nSpacing issues resolved.", "success")

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.show_custom_message("Export Error", f"Failed to generate PDF: {str(e)}", "error")

    def update_graph_display(self, report_type):
        """Switch to the correct graph page when report type changes."""
        # Find the index of this report type
        index_map = {
            "Daily Attendance Report": 0,
            "Monthly Summary Report": 1,
            "Employee Performance Report": 2,
            "Late/Absence Pattern Report": 3,
            "Overtime Analysis Report": 4
        }

        if report_type in index_map:
            self.ui.MathPlotStackedWidget.setCurrentIndex(index_map[report_type])

    def refresh_admin_dashboard(self):
        """Refresh admin dashboard after operations like report generation"""
        try:
            print("🔄 Refreshing admin dashboard...")

            # First, ensure we're on the admin dashboard page
            if self.ui.stackedWidget.currentIndex() != 3:  # Not on admin page
                return

            # Reset graph widget to ensure it's properly initialized
            if hasattr(self.ui, 'MathPlotStackedWidget'):
                # Save current index
                current_index = self.ui.MathPlotStackedWidget.currentIndex()

                # Remove existing graph widget if it exists
                for i in reversed(range(self.ui.MathPlotStackedWidget.count())):
                    widget = self.ui.MathPlotStackedWidget.widget(i)
                    self.ui.MathPlotStackedWidget.removeWidget(widget)
                    widget.deleteLater()

                # Reinitialize graphs
                self.simple_initialize_graphs()

                # Restore previous index or set to default
                if 0 <= current_index < self.ui.MathPlotStackedWidget.count():
                    self.ui.MathPlotStackedWidget.setCurrentIndex(current_index)
                else:
                    self.ui.MathPlotStackedWidget.setCurrentIndex(0)

            # Refresh stats
            self.load_admin_dashboard_stats()

            # Reconnect graph buttons
            self.connect_graph_buttons()

            print("✅ Admin dashboard refreshed")

        except Exception as e:
            print(f"❌ Error refreshing admin dashboard: {e}")
            import traceback
            traceback.print_exc()

            # Try a simpler refresh
            try:
                if hasattr(self, 'graph_widget') and self.graph_widget:
                    self.graph_widget.plot_present_graph()
                    self.load_admin_dashboard_stats()
                    print("✅ Admin dashboard partially refreshed")
            except:
                print("❌ Could not refresh dashboard at all")

    def show_system_configuration(self):
        """Show system configuration page without deleting existing widgets"""
        try:
            self.ui.AdminStackedWidget.setCurrentIndex(4)  # Switch to System Config Page

            # Set background color to white safely
            self.ui.SystemConfigurationPage.setStyleSheet("background-color: white;")

            # Initialize controller if needed
            if not self.system_config_controller:
                from controllers.system_config_controller import SystemConfigController
                self.system_config_controller = SystemConfigController()

            # Load the data
            self.load_work_time_settings()
            self.load_announcements_table()

        except Exception as e:
            print(f"❌ Error showing system configuration: {e}")

    def delete_selected_announcement(self):
        """Professional High-End Delete Confirmation Dialog"""
        try:
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
            from PyQt6.QtCore import Qt
            from PyQt6.QtGui import QIcon

            # 1. Access the table and check selection
            table_view = self.ui.AdminAnnouncementOutputTableView
            selection_model = table_view.selectionModel()
            selected_rows = selection_model.selectedRows()

            if not selected_rows:
                self.show_custom_message("No Selection", "Please click on a row in the table first!", "warning")
                return

            # 2. Get the ID and Title for the prompt
            row_index = selected_rows[0].row()
            model = table_view.model()
            raw_id_text = model.item(row_index, 0).text()  # This is the hidden ANN ID
            ann_title = model.item(row_index, 1).text()  # Get the title to show the user
            ann_id = raw_id_text.replace("ANN", "").strip()

            # 3. CREATE THE CUSTOM PROFESSIONAL DIALOG
            confirm_dialog = QDialog(self)
            confirm_dialog.setWindowTitle("Confirm Action")
            confirm_dialog.setFixedSize(450, 280)
            confirm_dialog.setStyleSheet("background-color: white; border-radius: 12px;")

            diag_layout = QVBoxLayout(confirm_dialog)
            diag_layout.setContentsMargins(30, 25, 30, 25)
            diag_layout.setSpacing(15)

            # --- WARNING ICON & TITLE ---
            header_layout = QHBoxLayout()
            warning_icon = QLabel("⚠️")  # You can also use a QPixmap here
            warning_icon.setStyleSheet("font-size: 24pt; border: none; background: transparent;")

            title_lbl = QLabel("CONFIRM DELETION")
            title_lbl.setStyleSheet(
                "font-size: 14pt; font-weight: bold; color: #D75050; border: none; background: transparent;")

            header_layout.addWidget(warning_icon)
            header_layout.addWidget(title_lbl)
            header_layout.addStretch()
            diag_layout.addLayout(header_layout)

            # --- MESSAGE BODY ---
            msg_frame = QFrame()
            msg_frame.setStyleSheet("background-color: #fff5f5; border: 1px solid #ffebeb; border-radius: 8px;")
            msg_layout = QVBoxLayout(msg_frame)

            main_msg = QLabel(f"Are you sure you want to permanently delete this announcement?")
            main_msg.setWordWrap(True)
            main_msg.setStyleSheet(
                "font-size: 11pt; font-weight: bold; color: #333; border: none; background: transparent;")

            sub_msg = QLabel(f"Title: {ann_title}")
            sub_msg.setWordWrap(True)
            sub_msg.setStyleSheet(
                "font-size: 10pt; color: #666; border: none; background: transparent; font-style: italic;")

            msg_layout.addWidget(main_msg)
            msg_layout.addWidget(sub_msg)
            diag_layout.addWidget(msg_frame)

            # --- ACTION BUTTONS ---
            btn_layout = QHBoxLayout()
            btn_layout.setSpacing(15)

            cancel_btn = QPushButton("KEEP IT")
            cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            cancel_btn.setFixedHeight(40)
            cancel_btn.setStyleSheet("""
                QPushButton {
                    background: #f1f1f1; color: #333; border-radius: 6px; font-weight: bold; border: none;
                }
                QPushButton:hover { background: #e5e5e5; }
            """)
            cancel_btn.clicked.connect(confirm_dialog.reject)

            delete_btn = QPushButton("DELETE NOW")
            delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            delete_btn.setFixedHeight(40)
            # Using a Red-themed gradient for the destructive action
            delete_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #D75050, stop:1 #FF7676); 
                    color: white; border-radius: 6px; font-weight: bold; border: none;
                }
                QPushButton:hover { background: #C0392B; }
            """)
            delete_btn.clicked.connect(confirm_dialog.accept)

            btn_layout.addWidget(cancel_btn)
            btn_layout.addWidget(delete_btn)
            diag_layout.addLayout(btn_layout)

            # 4. EXECUTE AND DELETE
            if confirm_dialog.exec() == QDialog.DialogCode.Accepted:
                from database.database import Database
                db = Database()

                query = "DELETE FROM announcements WHERE id = %s"
                success = db.execute_query(query, (ann_id,))

                if success:
                    self.show_custom_message("Success", "The announcement has been removed.", "success")
                    self.load_announcements_table()
                else:
                    self.show_custom_message("Error", "Failed to delete from database.", "error")

        except Exception as e:
            print(f"❌ Delete Error: {e}")

    def load_work_time_settings(self):
        """Load current work time settings from database"""
        try:
            if not self.system_config_controller:
                return

            result = self.system_config_controller.get_work_time_settings()

            if result["success"]:
                # Set values in the UI
                work_start = result["work_start_time"]
                work_end = result["work_end_time"]
                grace_period = result["grace_period"]
                overtime_threshold = result["overtime_threshold"]

                # Convert string times to QTime
                from PyQt6.QtCore import QTime

                # Work Start Time
                if hasattr(self.ui, 'WorkDayStartSpinbox'):
                    if work_start:
                        try:
                            # Handle different time formats
                            if ':' in work_start:
                                hours, minutes, seconds = map(int, work_start.split(':'))
                                self.ui.WorkDayStartSpinbox.setTime(QTime(hours, minutes))
                        except:
                            # Default to 9:00 AM
                            self.ui.WorkDayStartSpinbox.setTime(QTime(9, 0))

                # Work End Time
                if hasattr(self.ui, 'WorkDayEndSpinbox'):
                    if work_end:
                        try:
                            hours, minutes, seconds = map(int, work_end.split(':'))
                            self.ui.WorkDayEndSpinbox.setTime(QTime(hours, minutes))
                        except:
                            # Default to 5:00 PM
                            self.ui.WorkDayEndSpinbox.setTime(QTime(17, 0))

                # Grace Period
                if hasattr(self.ui, 'GracePeriodSpinbox'):
                    self.ui.GracePeriodSpinbox.setValue(grace_period)

                # Overtime Threshold
                if hasattr(self.ui, 'OverTimeSpinbox'):
                    self.ui.OverTimeSpinbox.setValue(overtime_threshold)

                print("✅ Work time settings loaded from database")
            else:
                print(f"⚠️ Could not load work time settings: {result.get('message', 'Unknown error')}")

        except Exception as e:
            print(f"❌ Error loading work time settings: {e}")

    def save_system_settings(self):
        """Save system settings to database"""
        try:
            if not self.system_config_controller:
                from controllers.system_config_controller import SystemConfigController
                self.system_config_controller = SystemConfigController()

            # Get values from UI
            work_start_time = self.ui.WorkDayStartSpinbox.time().toString("HH:mm:ss")
            work_end_time = self.ui.WorkDayEndSpinbox.time().toString("HH:mm:ss")
            grace_period = self.ui.GracePeriodSpinbox.value()
            overtime_threshold = self.ui.OverTimeSpinbox.value()

            print(f"💾 Saving system settings:")
            print(f"   Work Start: {work_start_time}")
            print(f"   Work End: {work_end_time}")
            print(f"   Grace Period: {grace_period} minutes")
            print(f"   Overtime Threshold: {overtime_threshold} hours")

            # Save to database
            result = self.system_config_controller.save_work_time_settings(
                work_start_time, work_end_time, grace_period, overtime_threshold
            )

            if result["success"]:
                self.show_custom_message("✅ Settings Saved", result["message"], "success")
                print("✅ Settings saved successfully")
            else:
                self.show_custom_message("❌ Save Failed", result["message"], "error")
                print(f"❌ Failed to save settings: {result.get('message')}")

        except Exception as e:
            print(f"❌ Error saving system settings: {e}")
            self.show_custom_message("Error", f"Failed to save settings: {str(e)}", "error")

    def create_announcement(self):
        """Create a professional high-end announcement dialog - FIXED UI"""
        try:
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, \
                QDateEdit, QFrame, QCalendarWidget
            from PyQt6.QtCore import Qt, QDate
            from PyQt6.QtGui import QFont

            dialog = QDialog(self)
            dialog.setWindowTitle("New Announcement")
            dialog.setFixedSize(550, 600)
            dialog.setStyleSheet("background-color: white; border-radius: 10px;")

            layout = QVBoxLayout(dialog)
            layout.setContentsMargins(35, 30, 35, 30)
            layout.setSpacing(15)

            # --- HEADER ---
            header_lbl = QLabel("📢 CREATE ANNOUNCEMENT")
            # Explicitly set border to none for the header
            header_lbl.setStyleSheet(
                "font-size: 18pt; font-weight: bold; color: #004c8c; border: none; border-bottom: 2px solid #00aaff; padding-bottom: 5px; background: transparent;")
            header_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(header_lbl)

            # --- INPUT CONTAINER ---
            form_frame = QFrame()
            form_frame.setObjectName("formFrame")
            # This stylesheet ensures labels have NO border, but inputs DO have borders
            form_frame.setStyleSheet("""
                QFrame#formFrame { 
                    background-color: #fcfcfc; 
                    border: 1px solid #eee; 
                    border-radius: 8px; 
                }
                QLabel { 
                    border: none; 
                    background: transparent; 
                    color: #333; 
                }
                QLineEdit, QTextEdit, QDateEdit {
                    padding: 12px; 
                    border: 1px solid #ccc; 
                    border-radius: 5px; 
                    font-size: 11pt;
                    background-color: white;
                }
                QDateEdit::drop-down {
                    border: none;
                    background: transparent;
                    width: 30px;
                }
                QDateEdit::down-arrow {
                    image: none;
                    border-left: 5px solid transparent;
                    border-right: 5px solid transparent;
                    border-top: 7px solid #ffffff;
                    margin-right: 8px;
                }
            """)

            form_layout = QVBoxLayout(form_frame)
            form_layout.setContentsMargins(20, 20, 20, 20)
            form_layout.setSpacing(10)

            # Title Field
            form_layout.addWidget(QLabel("<b>Announcement Title:</b>"))
            self.announcement_title_input = QLineEdit()
            self.announcement_title_input.setPlaceholderText("e.g., Company Holiday Notice")
            form_layout.addWidget(self.announcement_title_input)

            # Date Field
            form_layout.addWidget(QLabel("<b>Effectivity/Event Date:</b>"))
            self.announcement_date_input = QDateEdit()
            self.announcement_date_input.setDate(QDate.currentDate())
            self.announcement_date_input.setCalendarPopup(True)
            self.announcement_date_input.setDisplayFormat("yyyy-MM-dd")

            self.announcement_date_input.setMinimumDate(QDate.currentDate())

            # Ensure the calendar popup itself looks professional
            calendar = self.announcement_date_input.calendarWidget()
            calendar.setStyleSheet("background-color: white; color: black;")

            form_layout.addWidget(self.announcement_date_input)

            # Content Field
            form_layout.addWidget(QLabel("<b>Message Details:</b>"))
            self.announcement_content_input = QTextEdit()
            self.announcement_content_input.setPlaceholderText("Type your announcement message here...")
            form_layout.addWidget(self.announcement_content_input)

            # Character counter
            self.announcement_char_counter = QLabel("0/1000 characters")
            self.announcement_char_counter.setAlignment(Qt.AlignmentFlag.AlignRight)
            self.announcement_char_counter.setStyleSheet("font-size: 9pt; color: #888; border: none;")
            self.announcement_content_input.textChanged.connect(lambda: self.announcement_char_counter.setText(
                f"{len(self.announcement_content_input.toPlainText())}/1000 characters"))
            form_layout.addWidget(self.announcement_char_counter)

            layout.addWidget(form_frame)

            # --- BUTTONS ---
            btn_layout = QHBoxLayout()
            btn_layout.setSpacing(15)

            cancel_btn = QPushButton("CANCEL")
            cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            cancel_btn.setFixedHeight(45)
            cancel_btn.setStyleSheet(
                "background: #f1f1f1; color: #333; border-radius: 5px; font-weight: bold; border: none;")
            cancel_btn.clicked.connect(dialog.reject)

            post_btn = QPushButton("POST ANNOUNCEMENT")
            post_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            post_btn.setFixedHeight(45)
            post_btn.setStyleSheet(
                "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1C6099, stop:1 #00aaff); color: white; border-radius: 5px; font-weight: bold; border: none;")
            post_btn.clicked.connect(lambda: self.submit_announcement_with_date(dialog))

            btn_layout.addWidget(cancel_btn)
            btn_layout.addWidget(post_btn)
            layout.addLayout(btn_layout)

            # Status label
            self.announcement_status_label = QLabel("")
            self.announcement_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.announcement_status_label.setStyleSheet("border: none; background: transparent;")
            layout.addWidget(self.announcement_status_label)

            dialog.exec()
        except Exception as e:
            print(f"Error in announcement UI: {e}")

    def submit_announcement(self, dialog):
        """Submit announcement to database"""
        try:
            title = self.announcement_title_input.text().strip()
            content = self.announcement_content_input.toPlainText().strip()

            # Validate
            if not title:
                self.announcement_status_label.setText("⚠️ Please enter a title")
                self.announcement_status_label.setStyleSheet("color: #ff0000; font-weight: bold;")
                return

            if not content:
                self.announcement_status_label.setText("⚠️ Please enter content")
                self.announcement_status_label.setStyleSheet("color: #ff0000; font-weight: bold;")
                return

            if len(content) > 1000:
                self.announcement_status_label.setText("⚠️ Content must be less than 1000 characters")
                self.announcement_status_label.setStyleSheet("color: #ff0000; font-weight: bold;")
                return

            # Show saving message
            self.announcement_status_label.setText("Creating announcement...")
            self.announcement_status_label.setStyleSheet("color: #0066cc; font-weight: bold;")

            # Create announcement
            if not self.system_config_controller:
                from controllers.system_config_controller import SystemConfigController
                self.system_config_controller = SystemConfigController()

            result = self.system_config_controller.create_announcement(title, content)

            if result:
                self.show_custom_message("✅ Announcement Created",
                                         "Announcement created successfully!",
                                         "success")
                dialog.accept()
            else:
                self.announcement_status_label.setText("❌ Failed to create announcement")
                self.announcement_status_label.setStyleSheet("color: #ff0000; font-weight: bold;")

        except Exception as e:
            print(f"❌ Error submitting announcement: {e}")
            self.announcement_status_label.setText(f"❌ Error: {str(e)}")
            self.announcement_status_label.setStyleSheet("color: #ff0000; font-weight: bold;")

    def submit_announcement_with_date(self, dialog):
        """Submit announcement to database via Controller"""
        try:
            title = self.announcement_title_input.text().strip()
            content = self.announcement_content_input.toPlainText().strip()
            ann_date = self.announcement_date_input.date().toString("yyyy-MM-dd")

            if not title or not content:
                self.announcement_status_label.setText("⚠️ Title and Content required")
                return

            # Clean MVC Call
            if not self.system_config_controller:
                from controllers.system_config_controller import SystemConfigController
                self.system_config_controller = SystemConfigController()

            result = self.system_config_controller.post_announcement(title, content, ann_date)

            if result:
                self.show_custom_message("✅ Success", "Announcement posted!", "success")
                self.load_announcements_table()
                dialog.accept()
            else:
                self.announcement_status_label.setText("❌ Database Error")

        except Exception as e:
            print(f"❌ View Error: {e}")

    def load_announcements_table(self):
        """Load and display announcements using the existing UI table with Formal Design"""
        try:
            print("📢 Loading announcements table...")
            from database.database import Database
            from PyQt6.QtGui import QStandardItemModel, QStandardItem
            db = Database()

            query = """
            SELECT 
                id,
                title,
                announcement_date,
                DATE_FORMAT(created_date, '%Y-%m-%d %H:%i') as created_date_formatted
            FROM announcements 
            ORDER BY announcement_date DESC, id DESC
            LIMIT 50
            """

            announcements = db.execute_query(query)
            table_view = self.ui.AdminAnnouncementOutputTableView

            model = QStandardItemModel(0, 4)
            model.setHorizontalHeaderLabels(['ID', 'TITLE', 'DATE', 'POSTED AT'])

            for ann in announcements:
                id_item = QStandardItem(f"ANN{ann['id']}")
                title_item = QStandardItem(str(ann['title'] or 'No Title'))
                date_item = QStandardItem(str(ann.get('announcement_date', 'N/A')))
                posted_item = QStandardItem(str(ann.get('created_date_formatted', '')))

                # Alignment
                for item in [id_item, date_item, posted_item]:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                model.appendRow([id_item, title_item, date_item, posted_item])

            table_view.setModel(model)
            table_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

            # --- FORMAL TABLE DESIGN (Matching other tables) ---
            table_view.setAlternatingRowColors(True)
            table_view.verticalHeader().setVisible(False)
            table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)

            table_view.setStyleSheet("""
                QTableView {
                    background-color: white;
                    alternate-background-color: #f9f9f9;
                    gridline-color: #e0e0e0;
                    font-size: 11pt;
                    border: 1px solid #cccccc;
                }
                QHeaderView::section {
                    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1C6099, stop:1 #73DFF3);
                    color: white;
                    font-weight: bold;
                    padding: 8px;
                    border: 1px solid #1C6099;
                }
            """)
            table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

            print("✅ Admin announcements table loaded with formal design.")

        except Exception as e:
            print(f"❌ Error loading announcements table: {e}")

    def load_announcements_table_refresh_only(self, new_table):
        # Helper to update the existing frame if it already exists
        self.ui.AnnouncementTableFrame.setModel(new_table.model())

    def show_staff_announcement_page(self):
        """Switch to staff announcement page and load data"""
        self.ui.stackedWidget_3.setCurrentIndex(3)  # Staff Announcement page index
        self.load_staff_announcements()

    def load_staff_announcements(self):
        """Load announcements for Staff with widened title and click connection"""
        try:
            from database.database import Database
            from PyQt6.QtGui import QStandardItemModel, QStandardItem
            db = Database()

            query = """
                SELECT title, content, announcement_date, DATE_FORMAT(created_date, '%Y-%m-%d %H:%i') as created_at
                FROM announcements ORDER BY announcement_date DESC LIMIT 50
            """
            announcements = db.execute_query(query)
            table_view = self.ui.AnnouncementOutputTableView

            # Disconnect previous connection to avoid multiple popups
            try:
                table_view.clicked.disconnect()
            except:
                pass

            model = QStandardItemModel(0, 4)
            model.setHorizontalHeaderLabels(['TITLE', 'MESSAGE', 'EVENT DATE', 'POSTED AT'])

            for ann in announcements:
                row = [
                    QStandardItem(str(ann['title'] or 'No Title')),
                    QStandardItem(str(ann['content'] or '')),
                    QStandardItem(str(ann.get('announcement_date', 'N/A'))),
                    QStandardItem(str(ann.get('created_at', '')))
                ]
                row[2].setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                row[3].setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                model.appendRow(row)

            table_view.setModel(model)
            table_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            table_view.verticalHeader().setVisible(False)
            table_view.setAlternatingRowColors(True)
            table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

            # --- COLUMN WIDTH ADJUSTMENTS ---
            header = table_view.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

            table_view.setColumnWidth(0, 300)  # FIXED: Widened Title column
            table_view.setColumnWidth(1, 400)  # Message preview
            table_view.setColumnWidth(2, 200)  # Event Date
            table_view.setColumnWidth(3, 241)  # Posted At (Total 1141px)

            # Connect click signal
            table_view.clicked.connect(self.show_staff_announcement_details)

            # Professional Styling
            table_view.setStyleSheet("""
                QTableView { background-color: white; gridline-color: #e0e0e0; font-size: 11pt; }
                QHeaderView::section {
                    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1C6099, stop:1 #73DFF3);
                    color: white; font-weight: bold; padding: 8px; border: 1px solid #1C6099;
                }
            """)

            print("✅ Staff announcements loaded with widened columns and click-to-view enabled.")

        except Exception as e:
            print(f"❌ Error: {e}")

    def show_staff_announcement_details(self, index):
        """Professional Popup showing full announcement details"""
        try:
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QFrame
            from PyQt6.QtCore import Qt

            # 1. Get data from the clicked row
            row = index.row()
            model = self.ui.AnnouncementOutputTableView.model()
            title = model.item(row, 0).text()
            content = model.item(row, 1).text()
            event_date = model.item(row, 2).text()
            posted_at = model.item(row, 3).text()

            # 2. Create modern Dialog
            detail_dialog = QDialog(self)
            detail_dialog.setWindowTitle("Announcement Details")
            detail_dialog.setFixedSize(600, 500)
            detail_dialog.setStyleSheet("background-color: white; border-radius: 12px;")

            layout = QVBoxLayout(detail_dialog)
            layout.setContentsMargins(30, 30, 30, 30)
            layout.setSpacing(15)

            # --- HEADER (Title) ---
            title_lbl = QLabel(title.upper())
            title_lbl.setWordWrap(True)
            title_lbl.setStyleSheet(
                "font-size: 18pt; font-weight: bold; color: #004c8c; border: none; background: transparent;")
            title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title_lbl)

            # --- DATES BAR ---
            dates_frame = QFrame()
            dates_frame.setStyleSheet("background-color: #f0f9ff; border-radius: 8px; border: 1px solid #e0f2ff;")
            dates_layout = QHBoxLayout(dates_frame)

            event_lbl = QLabel(f"<b>Event Date:</b> {event_date}")
            posted_lbl = QLabel(f"<b>Posted:</b> {posted_at}")

            dates_layout.addWidget(event_lbl)
            dates_layout.addStretch()
            dates_layout.addWidget(posted_lbl)
            layout.addWidget(dates_frame)

            # --- CONTENT AREA ---
            content_display = QTextEdit()
            content_display.setPlainText(content)
            content_display.setReadOnly(True)
            content_display.setStyleSheet("""
                QTextEdit {
                    border: 1px solid #ccc;
                    border-radius: 8px;
                    padding: 15px;
                    font-size: 12pt;
                    color: #333;
                    background-color: #fcfcfc;
                }
            """)
            layout.addWidget(content_display)

            # --- CLOSE BUTTON ---
            close_btn = QPushButton("CLOSE")
            close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            close_btn.setFixedHeight(45)
            close_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1C6099, stop:1 #00aaff); 
                    color: white; border-radius: 6px; font-weight: bold; border: none; font-size: 11pt;
                }
                QPushButton:hover { background: #0088cc; }
            """)
            close_btn.clicked.connect(detail_dialog.accept)
            layout.addWidget(close_btn)

            detail_dialog.exec()

        except Exception as e:
            print(f"Error showing details: {e}")

    def handle_employee_row_click(self, index):
        """Bridge between table click and the edit dialog"""
        try:
            # 1. Get the table and the row clicked
            table = self.sender()
            row = index.row()

            # 2. Extract the employee data we stored in the first column
            employee_data = table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            employee_id = employee_data.get('id')

            # 3. Open the existing professional edit dialog
            self.show_edit_employee_dialog(employee_id, employee_data)

        except Exception as e:
            print(f"Error handling employee click: {e}")

    def update_sidebar_highlight(self, role, active_button):
        """Resets sidebar buttons and highlights the active one"""

        # 1. Define the Styles
        normal_style = """
            QPushButton {
                background: none;
                border: none;
                border-bottom: 2px solid grey;
                color: black;
                text-align: center;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.5);
            }
        """

        active_style = """
            QPushButton {
                background-color: white;
                color: #004c8c;
                font-weight: bold;
                border-left: 2px solid #004c8c;
                border-bottom: 2px solid #004c8c;
            }
        """

        # 2. Identify which group of buttons to reset
        if role == "staff":
            buttons = [
                self.ui.StaffDashboardButton,
                self.ui.staffAttendance,
                self.ui.requestButton,
                self.ui.AnnouncementButton
            ]
        else:  # admin
            buttons = [
                self.ui.AdminDashboardButton,
                self.ui.EmployeeManagementButton,
                self.ui.StaffRequestButton,
                self.ui.ReportsButton,
                self.ui.SystemConfigurationButton
            ]

        # 3. Apply Normal style to all, then Active style to the one clicked
        for btn in buttons:
            btn.setStyleSheet(normal_style)

        active_button.setStyleSheet(active_style)

