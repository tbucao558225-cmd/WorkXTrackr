add_employee_dialog.py
# ui/add_employee_dialog.py - SIMPLIFIED VERSION
"""
Add Employee Dialog - WITHOUT DEPARTMENT OR POSITION
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox,
                             QFormLayout, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import re


class AddEmployeeDialog(QDialog):
    employee_added = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_styles()

    def setup_ui(self):
        """Setup the dialog UI - ONLY BASIC FIELDS"""
        self.setWindowTitle("Add New Employee")
        self.setFixedSize(450, 450)  # Even smaller

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(20, 15, 20, 15)

        # Title
        title_label = QLabel("ADD NEW EMPLOYEE")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Employee Form Frame
        form_frame = QFrame()
        form_frame.setObjectName("formFrame")
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setContentsMargins(15, 15, 15, 15)

        # Full Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("John Doe")
        form_layout.addRow("Full Name:", self.name_input)

        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("johndoe")
        form_layout.addRow("Username:", self.username_input)

        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("john@email.com")
        form_layout.addRow("Email:", self.email_input)

        # Password
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Minimum 6 characters")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Password:", self.password_input)

        # Confirm Password
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Re-enter password")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Confirm:", self.confirm_password_input)

        form_frame.setLayout(form_layout)
        main_layout.addWidget(form_frame)

        # Button Layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.addStretch()

        # Cancel Button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        # Add Button
        add_btn = QPushButton("Add Employee")
        add_btn.setObjectName("addButton")
        add_btn.clicked.connect(self.add_employee)
        button_layout.addWidget(add_btn)

        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        main_layout.addWidget(self.status_label)

    def setup_styles(self):
        """Setup dialog styles"""
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel#titleLabel {
                font-size: 16pt;
                font-weight: bold;
                color: #004c8c;
                padding-bottom: 8px;
                border-bottom: 2px solid #00aaff;
            }
            QFrame#formFrame {
                background-color: #f9f9f9;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
            }
            QLabel {
                font-size: 11pt;
                color: #333333;
            }
            QLineEdit {
                font-size: 11pt;
                padding: 8px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                min-height: 35px;
            }
            QPushButton#addButton {
                font-size: 11pt;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 4px;
                border: 1px solid #00aaff;
                background-color: #00aaff;
                color: white;
                min-width: 120px;
            }
            QPushButton#addButton:hover {
                background-color: #0088cc;
            }
            QPushButton#cancelButton {
                font-size: 11pt;
                padding: 8px 20px;
                border-radius: 4px;
                border: 1px solid #cccccc;
                background-color: #f0f0f0;
                color: #333333;
                min-width: 100px;
            }
        """)

    def add_employee(self):
        """Handle add employee - SIMPLE VALIDATION"""
        # Get values
        full_name = self.name_input.text().strip()
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        # Clear status
        self.status_label.setText("")

        # Simple validation
        if not full_name:
            self.show_error("Please enter full name")
            self.name_input.setFocus()
            return

        if not username:
            self.show_error("Please enter username")
            self.username_input.setFocus()
            return

        if not email or "@" not in email:
            self.show_error("Please enter valid email")
            self.email_input.setFocus()
            return

        if len(password) < 6:
            self.show_error("Password must be at least 6 characters")
            self.password_input.setFocus()
            return

        if password != confirm_password:
            self.show_error("Passwords do not match")
            self.confirm_password_input.setFocus()
            return

        # Show success
        self.status_label.setText("Adding employee...")
        self.status_label.setStyleSheet("color: #0066cc; font-weight: bold;")

        # Emit signal with only basic data
        employee_data = {
            'full_name': full_name,
            'username': username,
            'email': email,
            'password': password
        }

        self.employee_added.emit(employee_data)
        self.accept()

    def show_error(self, message):
        """Show error message"""
        self.status_label.setText(f"⚠️ {message}")
        self.status_label.setStyleSheet("color: #ff0000; font-weight: bold;")