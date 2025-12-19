# main_window.py - UPDATED VERSION WITH ALL FIXES
"""
Main Window Controller - UPDATED WITH STAFF TABLE FIXES
"""
import sys
from PyQt6.QtWidgets import (QMainWindow, QApplication, QMessageBox, QTableWidget,
                             QTableWidgetItem, QLabel, QHeaderView, QVBoxLayout, QWidget)
from PyQt6.QtCore import Qt, QTimer, QStringListModel
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QColor, QBrush
from ui.ui_workxtrackr import Ui_LogIn
from controllers.auth import AuthController
from controllers.staff import StaffController
from controllers.request_controller import RequestController
from controllers.employee_controller import EmployeeController
from ui.request_dialog import RequestDialog
from datetime import datetime
import logging
from PyQt6.QtWidgets import QPushButton, QHBoxLayout
from PyQt6.QtWidgets import QTableView
from PyQt6.QtWidgets import QDialog, QStyle
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_LogIn()
        self.ui.setupUi(self)

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

        # Setup connections
        self.setup_connections()

        # Setup timer for clock
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)

        # Set default page
        self.ui.stackedWidget.setCurrentIndex(0)
        self.update_clock()

    def setup_connections(self):
        """Setup all signal-slot connections"""
        # Login Page
        self.ui.loginButton.clicked.connect(self.handle_login)
        self.ui.SignUpLoginButton.clicked.connect(self.show_registration_page)

        # Registration Page
        self.ui.CreateAccountButton.clicked.connect(self.handle_registration)
        self.ui.AlreadyHaveAccountButton.clicked.connect(self.show_login_page)


        # Staff Page Navigation
        self.ui.StaffDashboardButton.clicked.connect(lambda: self.ui.stackedWidget_3.setCurrentIndex(0))
        self.ui.staffAttendance.clicked.connect(lambda: self.ui.stackedWidget_3.setCurrentIndex(1))
        self.ui.requestButton.clicked.connect(self.show_staff_time_adjustment_page)
        self.ui.AnnouncementButton.clicked.connect(lambda: self.ui.stackedWidget_3.setCurrentIndex(3))
        self.ui.logOutButton.clicked.connect(self.handle_logout)

        # Staff Dashboard Actions
        self.ui.ClockInButton.clicked.connect(self.handle_clock_in)
        self.ui.ClockOutButton.clicked.connect(self.handle_clock_out)

        # Staff Request Actions
        self.ui.RequestingButton.clicked.connect(self.show_request_dialog)

        # Admin Page Navigation
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

        # Employee Management
        self.ui.AdminEmployeeSearchButton.clicked.connect(self.search_employees)
        self.ui.EmployeeManagementRefreshButton.clicked.connect(lambda: self.load_employees())
        self.ui.AddEmployeeButton.clicked.connect(self.add_employee)

        # Reports
        self.ui.GenerateButton.clicked.connect(self.generate_report)
        self.ui.ExportToPDFButton.clicked.connect(self.export_to_pdf)

        # System Configuration
        self.ui.SaveSettingsButton.clicked.connect(self.save_system_settings)

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

    def show_registration_page(self):
        """Show registration page"""
        self.ui.stackedWidget.setCurrentIndex(1)

    def show_login_page(self):
        """Show login page"""
        self.ui.stackedWidget.setCurrentIndex(0)

    def handle_registration(self):
        """Handle registration button click"""
        full_name = self.ui.FullNameInput.text()
        username = self.ui.UsernameSignUpInput.text()
        email = self.ui.EmailInput.text()
        password = self.ui.PasswordSignUpInput.text()
        confirm_password = self.ui.ConfirmPassSignUpInput.text()

        result = self.auth_controller.register(full_name, username, email, password, confirm_password)

        if result["success"]:
            self.show_custom_message("Success", result["message"], "success")
            self.show_login_page()
            self.clear_registration_form()
        else:
            self.show_custom_message("Registration Failed", result["message"], "error")

    def clear_registration_form(self):
        """Clear registration form fields"""
        self.ui.FullNameInput.clear()
        self.ui.UsernameSignUpInput.clear()
        self.ui.EmailInput.clear()
        self.ui.PasswordSignUpInput.clear()
        self.ui.ConfirmPassSignUpInput.clear()

    def show_staff_page(self):
        """Show staff dashboard"""
        self.ui.stackedWidget.setCurrentIndex(2)

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
        self.ui.stackedWidget.setCurrentIndex(3)

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
        dialog.setFixedSize(400, 250)
        dialog.setModal(True)

        # Main layout
        layout = QVBoxLayout(dialog)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Icon
        icon_label = QLabel()
        icon_label.setPixmap(QApplication.style().standardIcon(
            QStyle.StandardPixmap.SP_MessageBoxQuestion).pixmap(64, 64))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        # Title
        title_label = QLabel("Confirm Logout")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 16pt;
            font-weight: bold;
            color: #004c8c;
            margin-bottom: 5px;
        """)
        layout.addWidget(title_label)

        # Message
        message_label = QLabel("Are you sure you want to logout?")
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setStyleSheet("""
            font-size: 11pt;
            color: #666666;
            margin-bottom: 10px;
        """)
        layout.addWidget(message_label)

        # Info text
        info_label = QLabel("You will be returned to the login screen.")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("""
            font-size: 10pt;
            color: #888888;
            font-style: italic;
            margin-bottom: 20px;
        """)
        layout.addWidget(info_label)

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
                border: 1px solid #00aaff;
                border-radius: 10px;
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
        self.admin_request_controller = None
        self.clock_in_time = None
        self.admin_requests_data = []
        self.current_selected_request_id = None

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

                if hasattr(self.ui, 'EmployeeRequestNameOutput'):
                    self.ui.EmployeeRequestNameOutput.setText(request['full_name'])

                if hasattr(self.ui, 'EmployeeRequestTypeOutput'):
                    self.ui.EmployeeRequestTypeOutput.setText(request['type'])

                if hasattr(self.ui, 'EmployeeDateRequestOutput'):
                    self.ui.EmployeeDateRequestOutput.setText(request['date'])

                if hasattr(self.ui, 'ReasonRequestOutput'):
                    self.ui.ReasonRequestOutput.setText(request['reason'])
                    self.ui.ReasonRequestOutput.setStyleSheet("""
                        font-size: 11pt;
                        padding: 10px;
                        background-color: #f8f8f8;
                        border: 1px solid #e0e0e0;
                        border-radius: 4px;
                        min-height: 100px;
                    """)
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
        """Load employees with edit buttons"""
        try:
            print(f"🔄 Loading employees...")

            employees = []
            try:
                if search_term and search_term.strip():
                    employees = self.employee_controller.search_employees(search_term)
                    print(f"🔍 Found {len(employees)} matching '{search_term}'")
                else:
                    employees = self.employee_controller.get_all_employees()
                    print(f"📊 Found {len(employees)} staff users")
            except Exception as e:
                print(f"❌ Error getting employees: {e}")
                employees = []

            # Create table widget
            table_widget = QTableWidget()
            table_widget.setColumnCount(7)
            table_widget.setHorizontalHeaderLabels([
                'ID', 'Full Name', 'Username', 'Email', 'Role', 'Status', 'Actions'
            ])
            table_widget.setRowCount(len(employees))

            for i, emp in enumerate(employees):
                # Employee ID
                emp_id = f"EMP{emp.get('id', '')}"
                table_widget.setItem(i, 0, QTableWidgetItem(emp_id))

                # Full Name
                name = emp.get('full_name', 'N/A')
                table_widget.setItem(i, 1, QTableWidgetItem(name))

                # Username
                username = emp.get('username', 'N/A')
                table_widget.setItem(i, 2, QTableWidgetItem(username))

                # Email
                email = emp.get('email', 'N/A')
                table_widget.setItem(i, 3, QTableWidgetItem(email))

                # Role
                role = emp.get('role', 'staff').capitalize()
                table_widget.setItem(i, 4, QTableWidgetItem(role))

                # Status
                status = emp.get('status', 'active').capitalize()
                status_item = QTableWidgetItem(status)
                if status.lower() == 'active':
                    status_item.setForeground(Qt.GlobalColor.green)
                    status_item.setBackground(QBrush(QColor(230, 245, 230)))  # Light green
                elif status.lower() == 'inactive':
                    status_item.setForeground(Qt.GlobalColor.red)
                    status_item.setBackground(QBrush(QColor(255, 230, 230)))  # Light red
                elif status.lower() == 'on leave':
                    status_item.setForeground(QColor(255, 152, 0))  # Orange
                    status_item.setBackground(QBrush(QColor(255, 248, 230)))  # Light orange
                table_widget.setItem(i, 5, status_item)

                # Edit button
                edit_button = QPushButton("✏️ Edit")
                edit_button.setCursor(Qt.CursorShape.PointingHandCursor)
                edit_button.setFixedHeight(35)
                edit_button.setStyleSheet("""
                    QPushButton {
                        background-color: #f8f9fa;
                        color: #212529;
                        border: 1px solid #ced4da;
                        border-radius: 4px;
                        padding: 8px 15px;
                        font-size: 11pt;
                        font-weight: 500;
                        width: 100%;
                        height: 35px;
                    }
                    QPushButton:hover {
                        background-color: #e9ecef;
                        border: 1px solid #6c757d;
                        color: #495057;
                    }
                """)

                # Create container for button
                container = QWidget()
                layout = QHBoxLayout(container)
                layout.setContentsMargins(5, 5, 5, 5)
                layout.addWidget(edit_button)
                layout.addStretch()
                container.setLayout(layout)

                table_widget.setCellWidget(i, 6, container)

                # Center align text items
                for col in range(6):
                    item = table_widget.item(i, col)
                    if item:
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # Style the table
            table_widget.setStyleSheet("""
                QTableWidget {
                    background-color: rgb(240, 239, 239);
                    alternate-background-color: #f8f8f8;
                    gridline-color: #e0e0e0;
                    font-size: 11pt;
                    border: 1px solid black;
                }
                QTableWidget::item {
                    padding: 8px;
                }
                QHeaderView::section {
                    background-color: #A2A2A2;
                    color: black;
                    font-weight: bold;
                    padding: 10px;
                    border: 1px solid black;
                    font-size: 10pt;
                }
            """)

            # Set column widths
            table_widget.setColumnWidth(0, 100)
            table_widget.setColumnWidth(1, 200)
            table_widget.setColumnWidth(2, 150)
            table_widget.setColumnWidth(3, 250)
            table_widget.setColumnWidth(4, 100)
            table_widget.setColumnWidth(5, 100)
            table_widget.setColumnWidth(6, 160)

            table_widget.setAlternatingRowColors(True)

            # Set to scroll area
            if hasattr(self.ui, 'scrollArea_2'):
                old_widget = self.ui.scrollArea_2.takeWidget()
                if old_widget:
                    old_widget.deleteLater()

                container = QWidget()
                layout = QVBoxLayout(container)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.addWidget(table_widget)

                self.ui.scrollArea_2.setWidget(container)

            print(f"✅ Employee table loaded with {len(employees)} rows")

        except Exception as e:
            print(f"❌ Error loading employees: {e}")

    def add_employee(self):
        """Add employee in admin panel"""
        try:
            from ui.add_employee_dialog import AddEmployeeDialog

            dialog = AddEmployeeDialog(self)
            dialog.employee_added.connect(self.handle_employee_addition)
            dialog.exec()

        except Exception as e:
            print(f"❌ Error adding employee: {e}")
            self.show_custom_message("Error", f"Failed to open add employee dialog: {str(e)}", "error")

    def handle_employee_addition(self, employee_data):
        """Handle new employee addition"""
        try:
            print(f"➕ Adding new employee: {employee_data['full_name']}")

            result = self.employee_controller.add_employee(
                full_name=employee_data['full_name'],
                username=employee_data['username'],
                email=employee_data['email'],
                password=employee_data['password']
            )

            if result["success"]:
                self.show_custom_message("Success",
                                         f"Employee {employee_data['full_name']} added successfully!",
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

    def generate_report(self):
        """Generate reports"""
        try:
            print("Generating report...")
            self.show_custom_message("Info", "Report generation feature is under development", "info")
        except Exception as e:
            logging.error(f"Error generating report: {e}")

    def export_to_pdf(self):
        """Export to PDF"""
        try:
            print("Exporting to PDF...")
            self.show_custom_message("Info", "PDF export feature is under development", "info")
        except Exception as e:
            logging.error(f"Error exporting to PDF: {e}")

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
                from ui.graph_widget import GraphWidget
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
        """Connect graph buttons properly"""
        try:
            if hasattr(self, 'graph_widget') and self.graph_widget:
                print("🔗 Connecting graph buttons...")

                # Present button
                if hasattr(self.ui, 'AdminPresentButton'):
                    # Disconnect all existing connections
                    try:
                        self.ui.AdminPresentButton.clicked.disconnect()
                    except:
                        pass  # No connections to disconnect

                    # Connect new connection
                    self.ui.AdminPresentButton.clicked.connect(
                        lambda: self.safe_plot_graph('present')
                    )
                    print("✅ Connected Present button")

                # Late button
                if hasattr(self.ui, 'AdminLateButton'):
                    try:
                        self.ui.AdminLateButton.clicked.disconnect()
                    except:
                        pass

                    self.ui.AdminLateButton.clicked.connect(
                        lambda: self.safe_plot_graph('late')
                    )
                    print("✅ Connected Late button")

                # Absent button
                if hasattr(self.ui, 'AdminAbsentButton'):
                    try:
                        self.ui.AdminAbsentButton.clicked.disconnect()
                    except:
                        pass

                    self.ui.AdminAbsentButton.clicked.connect(
                        lambda: self.safe_plot_graph('absent')
                    )
                    print("✅ Connected Absent button")

                # Total employee button
                if hasattr(self.ui, 'AdminTotalEmployeeButton'):
                    try:
                        self.ui.AdminTotalEmployeeButton.clicked.disconnect()
                    except:
                        pass

                    self.ui.AdminTotalEmployeeButton.clicked.connect(
                        lambda: self.safe_plot_graph('total_employee')
                    )
                    print("✅ Connected Total Employee button")

                # On leave button
                if hasattr(self.ui, 'AdminEmployeeOnLeaveButton'):
                    try:
                        self.ui.AdminEmployeeOnLeaveButton.clicked.disconnect()
                    except:
                        pass

                    self.ui.AdminEmployeeOnLeaveButton.clicked.connect(
                        lambda: self.safe_plot_graph('on_leave')
                    )
                    print("✅ Connected On Leave button")

                print("✅ All graph buttons connected successfully")

        except Exception as e:
            print(f"⚠️  Error connecting graph buttons: {e}")
            import traceback
            traceback.print_exc()

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

    def check_graph_buttons_exist(self):
        """Check if graph buttons exist in UI"""
        print("\n🔍 Checking if graph buttons exist in UI...")

        button_names = [
            'AdminPresentButton',
            'AdminLateButton',
            'AdminAbsentButton',
            'AdminTotalEmployeeButton',
            'AdminEmployeeOnLeaveButton'
        ]

        for button_name in button_names:
            if hasattr(self.ui, button_name):
                print(f"✅ {button_name} exists")
                button = getattr(self.ui, button_name)
                print(f"   Button text: {button.text() if hasattr(button, 'text') else 'N/A'}")
            else:
                print(f"❌ {button_name} NOT FOUND in UI")

        # Also check MathPlotStackedWidget
        if hasattr(self.ui, 'MathPlotStackedWidget'):
            print(f"✅ MathPlotStackedWidget exists")
            print(f"   Widget count: {self.ui.MathPlotStackedWidget.count()}")
        else:
            print(f"❌ MathPlotStackedWidget NOT FOUND in UI")

    def test_all_graphs(self):
        """Test all graph types manually"""
        try:
            print("\n🧪 Testing all graph types...")

            if hasattr(self, 'graph_widget') and self.graph_widget:
                # Test present graph
                print("1. Testing Present graph...")
                self.graph_widget.plot_present_graph()
                print("   ✅ Present graph test passed")

                # Test late graph
                print("2. Testing Late graph...")
                self.graph_widget.plot_late_graph()
                print("   ✅ Late graph test passed")

                # Test absent graph
                print("3. Testing Absent graph...")
                self.graph_widget.plot_absent_graph()
                print("   ✅ Absent graph test passed")

                # Test total employee
                print("4. Testing Total Employee...")
                self.graph_widget.plot_total_employee_graph()
                print("   ✅ Total Employee test passed")

                # Test on leave
                print("5. Testing On Leave graph...")
                self.graph_widget.plot_on_leave_graph()
                print("   ✅ On Leave graph test passed")

                print("\n🎉 All graph tests passed!")

            else:
                print("❌ Graph widget not available for testing")

        except Exception as e:
            print(f"❌ Graph test failed: {e}")
            import traceback
            traceback.print_exc()

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
                    self.ui.EmployeeName.setText(full_name)

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

    def display_attendance_table(self, records):
        """OLD METHOD - DO NOT USE"""
        # This is the old method, we're using display_attendance_table_with_color instead
        pass

    def display_attendance_table_with_color(self, records):
        """Display attendance records in table WITH COLOR CODING"""
        try:
            if hasattr(self.ui, 'scrollArea') and self.ui.scrollArea:
                # Create table widget
                attendance_table = QTableWidget()
                attendance_table.setFixedWidth(1141)
                attendance_table.setColumnCount(5)
                attendance_table.setHorizontalHeaderLabels(['Date', 'Clock In', 'Clock Out', 'Duration', 'Status'])
                attendance_table.setRowCount(len(records))

                print(f"📋 Creating table with {len(records)} rows")

                # Set column widths
                column_widths = [200, 200, 200, 150, 150]
                for i, width in enumerate(column_widths):
                    attendance_table.setColumnWidth(i, width)

                # Adjust last column width if needed
                total_width = sum(column_widths)
                if total_width != 1141:
                    column_widths[4] += (1141 - total_width)
                    attendance_table.setColumnWidth(4, column_widths[4])

                # Fill table with data
                for i, record in enumerate(records):
                    print(f"   Row {i}: {record}")

                    attendance_table.setItem(i, 0, QTableWidgetItem(record.get('date', '')))
                    attendance_table.setItem(i, 1, QTableWidgetItem(record.get('clock_in', '')))
                    attendance_table.setItem(i, 2, QTableWidgetItem(record.get('clock_out', '')))
                    attendance_table.setItem(i, 3, QTableWidgetItem(record.get('duration', '')))

                    status_item = QTableWidgetItem(record.get('status', ''))
                    status = record.get('status', '').lower()

                    # COLOR CODING FOR STATUS
                    if 'present' in status:
                        # Green for present
                        status_item.setForeground(QColor(0, 128, 0))  # Dark green text
                        status_item.setBackground(QBrush(QColor(230, 245, 230)))  # Light green background
                    elif 'late' in status:
                        # Orange for late
                        status_item.setForeground(QColor(255, 140, 0))  # Orange text
                        status_item.setBackground(QBrush(QColor(255, 248, 230)))  # Light orange background
                    elif 'absent' in status:
                        # Red for absent
                        status_item.setForeground(QColor(220, 20, 60))  # Crimson text
                        status_item.setBackground(QBrush(QColor(255, 230, 230)))  # Light red background
                    elif 'ot' in status or 'overtime' in status:
                        # Blue for overtime
                        status_item.setForeground(QColor(0, 0, 139))  # Dark blue text
                        status_item.setBackground(QBrush(QColor(230, 240, 255)))  # Light blue background
                    else:
                        # Default gray for other statuses
                        status_item.setForeground(QColor(105, 105, 105))  # Dim gray text
                        status_item.setBackground(QBrush(QColor(245, 245, 245)))  # Light gray background

                    attendance_table.setItem(i, 4, status_item)

                    # Center align all cells
                    for col in range(attendance_table.columnCount()):
                        item = attendance_table.item(i, col)
                        if item:
                            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                # Style the table
                attendance_table.setStyleSheet("""
                    QTableWidget {
                        background-color: white;
                        alternate-background-color: #f8f8f8;
                        gridline-color: #e0e0e0;
                        font-size: 11pt;
                    }
                    QTableWidget::item {
                        padding: 5px;
                        border-bottom: 1px solid #f0f0f0;
                    }
                    QHeaderView::section {
                        background-color: #A2A2A2;
                        color: black;
                        font-weight: bold;
                        padding: 8px;
                        border: 1px solid #d0d0d0;
                    }
                """)
                attendance_table.setAlternatingRowColors(True)

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

                print("✅ Attendance table displayed with color coding")

        except Exception as e:
            print(f"❌ Error displaying attendance table: {e}")
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
        """Load time adjustment requests for admin - FIXED VERSION"""
        try:
            print("🕒 Loading time adjustment requests...")

            # Get time adjustment requests from database
            query = """
            SELECT 
                r.id,
                r.request_type,
                DATE(r.request_date) as request_date,
                r.reason,
                r.status,
                r.created_at,
                u.full_name,
                u.username
            FROM requests r
            JOIN users u ON r.user_id = u.id
            WHERE r.request_type IN ('Overtime Request', 'Undertime Request', 'Time Correction', 'Shift Change')
            ORDER BY r.created_at DESC
            LIMIT 50
            """

            from database.database import Database
            db = Database()
            requests = db.execute_query(query)

            print(f"📋 Found {len(requests)} time adjustment requests")

            if not requests:
                print("⚠️ No time adjustment requests found in database")
                # Check if requests exist at all
                check_query = "SELECT COUNT(*) as total FROM requests"
                total_result = db.fetch_one(check_query)
                print(f"📊 Total requests in database: {total_result['total'] if total_result else 0}")
                return

            # Create table widget
            table_widget = QTableWidget()
            table_widget.setColumnCount(6)
            table_widget.setHorizontalHeaderLabels(['Type', 'Employee', 'Date', 'Reason', 'Status', 'Submitted'])
            table_widget.setRowCount(len(requests))

            # Set column widths
            column_widths = [150, 150, 100, 400, 100, 150]
            total_width = sum(column_widths)
            if total_width < 1141:
                column_widths[3] += (1141 - total_width)  # Adjust reason column

            for i, width in enumerate(column_widths):
                table_widget.setColumnWidth(i, width)

            # Fill table with data
            for i, req in enumerate(requests):
                # Type
                table_widget.setItem(i, 0, QTableWidgetItem(req['request_type']))

                # Employee
                employee_name = req['full_name'] or req['username'] or 'Unknown'
                table_widget.setItem(i, 1, QTableWidgetItem(employee_name))

                # Date
                date_str = str(req['request_date']) if req['request_date'] else ''
                table_widget.setItem(i, 2, QTableWidgetItem(date_str))

                # Reason
                reason = req['reason'] or ''
                if len(reason) > 80:
                    reason = reason[:77] + "..."
                table_widget.setItem(i, 3, QTableWidgetItem(reason))

                # Status with color coding
                status = req['status'] or 'pending'
                status_item = QTableWidgetItem(status.capitalize())
                if status == 'approved':
                    status_item.setForeground(QColor(0, 128, 0))  # Green
                    status_item.setBackground(QBrush(QColor(230, 245, 230)))  # Light green
                elif status == 'declined':
                    status_item.setForeground(QColor(220, 20, 60))  # Red
                    status_item.setBackground(QBrush(QColor(255, 230, 230)))  # Light red
                elif status == 'pending':
                    status_item.setForeground(QColor(0, 0, 139))  # Dark blue
                    status_item.setBackground(QBrush(QColor(230, 240, 255)))  # Light blue
                table_widget.setItem(i, 4, status_item)

                # Submitted
                created_at = ''
                if req['created_at']:
                    if isinstance(req['created_at'], str):
                        created_at = req['created_at']
                    else:
                        created_at = req['created_at'].strftime("%Y-%m-%d %I:%M %p")
                table_widget.setItem(i, 5, QTableWidgetItem(created_at))

                # Center align all cells
                for col in range(6):
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
                }
                QTableWidget::item {
                    padding: 8px;
                }
                QHeaderView::section {
                    background-color: #A2A2A2;
                    color: black;
                    font-weight: bold;
                    padding: 10px;
                    border: 1px solid #d0d0d0;
                    font-size: 10pt;
                }
            """)

            table_widget.setAlternatingRowColors(True)
            table_widget.setWordWrap(True)
            table_widget.horizontalHeader().setStretchLastSection(True)

            # Try different scroll areas - MOST COMMON NAMES
            scroll_area_names = [
                'scrollArea_7',  # Most common for Time Adjustment
                'scrollArea_8',
                'scrollArea_9',
                'scrollArea_10',
                'timeAdjustmentScrollArea',
                'timeAdjustScrollArea',
                'adjustmentScrollArea',
                'requestsScrollArea'
            ]

            scroll_area_found = False
            for scroll_name in scroll_area_names:
                if hasattr(self.ui, scroll_name):
                    print(f"✅ Found scroll area: {scroll_name}")

                    # Remove existing widget
                    scroll_area = getattr(self.ui, scroll_name)
                    old_widget = scroll_area.takeWidget()
                    if old_widget:
                        old_widget.deleteLater()

                    # Add new table
                    container = QWidget()
                    layout = QVBoxLayout(container)
                    layout.setContentsMargins(0, 0, 0, 0)
                    layout.addWidget(table_widget)

                    scroll_area.setWidget(container)
                    scroll_area_found = True
                    print(f"✅ Table added to {scroll_name}")
                    break

            if not scroll_area_found:
                print("❌ No scroll area found for Time Adjustment!")
                print("Creating a new dialog to show data...")

                # Show data in message box as fallback
                message = f"Found {len(requests)} time adjustment requests:\n\n"
                for req in requests[:10]:  # Show first 10
                    message += f"• {req['request_type']} - {req['full_name']} - {req['status']}\n"

                if len(requests) > 10:
                    message += f"\n... and {len(requests) - 10} more"

                self.show_custom_message("Time Adjustment Requests", message, "info")

            print("✅ Time adjustment requests loaded successfully")

        except Exception as e:
            print(f"❌ Error loading time adjustment requests: {e}")
            import traceback
            traceback.print_exc()

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

                if pending_count > 0:
                    self.ui.PendingRequestOutput.setStyleSheet("""
                        font-size: 12pt;
                        font-weight: bold;
                        color: #ff9900;
                    """)
                else:
                    self.ui.PendingRequestOutput.setStyleSheet("""
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
                QHeaderView::section:checked {
                    background-color: #004c8c;
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
        """Debug method to see UI structure"""
        print("\n🔍 DEBUGGING UI STRUCTURE:")

        # Check request panel
        if hasattr(self.ui, 'requestPanel'):
            print(f"✅ requestPanel exists")
            print(f"   Children: {self.ui.requestPanel.children()}")

        # Check scroll areas
        for i in range(1, 11):
            attr_name = f'scrollArea_{i}'
            if hasattr(self.ui, attr_name):
                scroll_area = getattr(self.ui, attr_name)
                print(f"✅ {attr_name} exists")
                print(f"   Widget: {scroll_area.widget()}")
                print(f"   Object name: {scroll_area.objectName()}")

        # Check table views
        table_views = ['TimeAdjustmentRequestOutputTableView',
                       'ClockOutOutputsTableView',
                       'AnnouncementOutputTableView',
                       'EmployeeManagementTableView',
                       'ReportsTableView']

        for tv in table_views:
            if hasattr(self.ui, tv):
                table_view = getattr(self.ui, tv)
                print(f"✅ {tv} exists")
                print(f"   Parent: {table_view.parent()}")
                print(f"   Object name: {table_view.objectName()}")

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